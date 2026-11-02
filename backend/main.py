import os
import io
import asyncio
import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    Query,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
import pandas as pd
import zipfile
import mimetypes
from dotenv import load_dotenv

load_dotenv()

from .database import init_db, get_async_db, AsyncSessionLocal
from .models import (
    DatasetModel,
    SimulationRunModel,
    CopilotMessageModel,
    SimulationRunCreate,
    EDADataResponse,
    CrossValidationRequest,
    CrossValidationResponse,
    CohortFilterRequest,
    CohortProjectionResponse,
    CopilotChatRequest,
    CopilotChatResponse,
)
from .copilot_service import execute_copilot_query, CopilotServiceError
from .copilot_tools import get_simulation_metrics
from .ml_engine import (
    compute_eda,
    run_stratified_cv,
    predict_cohort_transition,
    load_real_country_microdata,
    scan_real_microdatasets,
    DATA_STORE_DIR,
)
from .simulation_engine import (
    SimulationEngine,
    calculate_structural_metrics,
    load_outputs_data,
    SCENARIO_CONFIGS,
    get_model_firms,
    get_historical_ilostat_series,
    get_simulated_monthly_trajectory,
)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("labortwin.server")

# In-memory cached active dataset
ACTIVE_DATASET_CACHE: Dict[str, Any] = {
    "df": None,
    "filename": None,
    "records_count": 0,
    "model_id": None,
}

# Models Leaderboard Registry & Active Deployed Champion Model
MODELS_REGISTRY: List[Dict[str, Any]] = []

ACTIVE_DEPLOYED_MODEL: Dict[str, Any] = {
    "active_model_id": None,
    "active_model": None,
    "status": "Sin microdatos reales cargados"
}


def load_benchmark_models_into_registry(country: str = "india"):
    """Carga los modelos entrenados competitivamente desde outputs/motor_ia/ sin inventar métricas."""
    global MODELS_REGISTRY, ACTIVE_DEPLOYED_MODEL
    outputs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "motor_ia")
    c_clean = country.lower().strip()
    c_file = "india" if "ind" in c_clean else ("nigeria" if "nig" in c_clean else "india")
    json_path = os.path.join(outputs_dir, f"metricas_modelos_{c_file}.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            models = []
            champ_name = data.get("champion_name", "")
            for name, m in data.get("models_benchmark", {}).items():
                is_champ = (name == champ_name)
                slug = name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(".", "")
                model_entry = {
                    "id": f"algo-{slug}",
                    "name": name,
                    "algorithm": slug,
                    "accuracy": round(m["accuracy"], 2),
                    "precision": round(m["precision"], 2),
                    "recall": round(m["recall"], 2),
                    "f1Score": round(m["f1_score"], 2),
                    "rocAuc": round(m["roc_auc"], 2),
                    "brierScore": round(m["brier_score"], 4),
                    "latencyMs": round(m["latency_ms_per_obs"], 5),
                    "isDeployed": is_champ,
                    "metricsWomen": m.get("metrics_women", {}),
                    "metricsMen": m.get("metrics_men", {}),
                    "confusionMatrix": m.get("confusion_matrix", []),
                    "rocCurve": m.get("roc_curve", {}),
                }
                models.append(model_entry)
                if is_champ:
                    import datetime
                    ACTIVE_DEPLOYED_MODEL = {
                        **model_entry,
                        "deployedBy": "LaborTwin Benchmark Engine (StratifiedGroupKFold OIT)",
                        "deployedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "status": "active",
                        "country": data.get("country", c_file.upper()),
                        "totalObservations": data.get("total_observations", 0),
                        "weightedInformalityRate": data.get("weighted_informality_rate", 0.0),
                    }
            MODELS_REGISTRY = models
            logger.info(f"Loaded {len(models)} real benchmarked models for {c_file.upper()}. Champion: {champ_name}")
        except Exception as e:
            logger.warning(f"Error loading {json_path}: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize database schema
    await init_db()
    
    # 2. Check for active microdataset in database or data/microdatos_reales/
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(DatasetModel).where(DatasetModel.is_active == True).order_by(desc(DatasetModel.created_at))
        )
        active_ds = result.scalars().first()

        if active_ds is not None and getattr(active_ds, "filepath", None):
            filepath_str = str(active_ds.filepath)
            if os.path.exists(filepath_str) and "_archivado" not in filepath_str and not os.path.basename(filepath_str).startswith("SINTETICO_"):
                logger.info(f"Loading existing active real dataset from {filepath_str}")
                ACTIVE_DATASET_CACHE["df"] = pd.read_csv(filepath_str)
                ACTIVE_DATASET_CACHE["filename"] = active_ds.filename
                ACTIVE_DATASET_CACHE["records_count"] = active_ds.records_count
            else:
                ACTIVE_DATASET_CACHE["df"] = None
                ACTIVE_DATASET_CACHE["filename"] = None
                ACTIVE_DATASET_CACHE["records_count"] = 0
            # Check if any official microdata exists in data/microdatos_reales/
            real_data = None
            for c_try in ["india", "nigeria", "kenya"]:
                real_data = load_real_country_microdata(c_try)
                if real_data is not None:
                    break

            if real_data is not None:
                df, fname, inst = real_data
                ACTIVE_DATASET_CACHE["df"] = df
                ACTIVE_DATASET_CACHE["filename"] = fname
                ACTIVE_DATASET_CACHE["records_count"] = len(df)
                ACTIVE_DATASET_CACHE["institution"] = inst
                c_name = "india" if "cperv1" in fname.lower() else ("nigeria" if "nlfs" in fname.lower() else "india")
                load_benchmark_models_into_registry(c_name)
                logger.info(f"Microdatos reales cargados ({fname}): {len(df):,} filas. Modelos sincronizados.")
            else:
                logger.info("Sin microdatos reales cargados en data/microdatos_reales/. Motor IA en espera.")
                ACTIVE_DATASET_CACHE["df"] = None
                ACTIVE_DATASET_CACHE["filename"] = None
                ACTIVE_DATASET_CACHE["records_count"] = 0
            
    yield
    logger.info("Shutting down LaborTwin API server.")

# FastAPI App Instance
app = FastAPI(
    title="Gemelo Digital 3D del Mercado Laboral - API & ML Engine",
    version="2.4.0",
    description="Backend modular en Python con FastAPI, PostgreSQL async, XGBoost, SHAP y WebSocket de alta frecuencia.",
    lifespan=lifespan,
)

# CORS Configuration
raw_cors = os.getenv("CORS_ORIGINS", "")
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if raw_cors and raw_cors.strip():
    for orig in raw_cors.split(","):
        if orig.strip() and orig.strip() not in allowed_origins:
            allowed_origins.append(orig.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get("/")
async def health_check():
    """Health check endpoint for Render, Docker, and reverse proxies."""
    return {
        "status": "healthy",
        "service": "labortwin-backend",
        "version": "2.4.0",
        "active_dataset": ACTIVE_DATASET_CACHE.get("filename"),
    }


# =====================================================================
# 1. DATASETS ENDPOINTS
# =====================================================================

@app.post("/api/v1/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Uploads, validates mandatory labor columns, stores the CSV,
    sets it as active in the database and updates in-memory cache.
    """
    if not file.filename or not file.filename.endswith(('.csv', '.tsv')):
        raise HTTPException(status_code=400, detail="Formato no soportado. Debe ser un archivo .csv o .tsv")

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error al parsear archivo CSV: {str(exc)}")

    # Strict Validation of Mandatory Columns
    required_cols = {"ESTADO_LABORAL", "INGRESO_NETO_DIA", "CAPITAL_HUMANO"}
    # Case-insensitive column matching fallback
    df.columns = [c.strip().upper() for c in df.columns]
    
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise HTTPException(
            status_code=422,
            detail=f"El dataset carece de columnas obligatorias: {', '.join(missing_cols)}. Columnas requeridas: {', '.join(required_cols)}"
        )

    # Save to disk
    file_path = os.path.join(DATA_STORE_DIR, f"{int(time.time())}_{file.filename}")
    df.to_csv(file_path, index=False)

    # Deactivate previous datasets
    await db.execute(update(DatasetModel).values(is_active=False))

    # Register new active dataset
    new_dataset = DatasetModel(
        filename=file.filename,
        filepath=file_path,
        records_count=len(df),
        features_list=list(df.columns),
        is_active=True,
    )
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)

    # Update in-memory reference
    ACTIVE_DATASET_CACHE["df"] = df
    ACTIVE_DATASET_CACHE["filename"] = file.filename
    ACTIVE_DATASET_CACHE["records_count"] = len(df)
    ACTIVE_DATASET_CACHE["institution"] = "Microdatos de Encuesta Subida por Usuario"

    logger.info(f"Dataset '{file.filename}' uploaded successfully. Total rows: {len(df)}")
    return {
        "status": "success",
        "message": f"Dataset '{file.filename}' validado y cargado en memoria exitosamente.",
        "dataset": new_dataset.to_dict(),
    }


@app.post("/api/v1/datasets/select-preset")
async def select_preset_dataset(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db)
):
    """
    Carga microdatos reales desde data/microdatos_reales/<pais>/.
    Si no existen archivos reales cargados, retorna 'Sin microdatos reales cargados'.
    """
    preset_id = payload.get("dataset_id") or payload.get("id") or "india"
    real_data = load_real_country_microdata(preset_id)
    if real_data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Sin microdatos reales cargados para '{preset_id}' en data/microdatos_reales/. "
                   "Consulte data/microdatos_reales/README.md para las instrucciones de carga."
        )

    df, filename, institution = real_data
    file_path = os.path.join(DATA_STORE_DIR, filename)
    df.to_csv(file_path, index=False)

    await db.execute(update(DatasetModel).values(is_active=False))
    new_dataset = DatasetModel(
        filename=filename,
        filepath=file_path,
        records_count=len(df),
        features_list=df.columns.tolist(),
        is_active=True,
    )
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)

    ACTIVE_DATASET_CACHE["df"] = df
    ACTIVE_DATASET_CACHE["filename"] = filename
    ACTIVE_DATASET_CACHE["records_count"] = len(df)
    ACTIVE_DATASET_CACHE["institution"] = institution

    # Sincronizar registro de modelos del país seleccionado
    load_benchmark_models_into_registry(preset_id)

    logger.info(f"Microdatos reales '{filename}' activados ({len(df)} registros).")
    return {
        "status": "success",
        "message": f"Microdatos reales '{filename}' cargados exitosamente ({len(df):,} observaciones).",
        "dataset": new_dataset.to_dict(),
        "institution": institution,
    }


@app.get("/api/v1/datasets/preview")
async def preview_dataset():
    """Returns top rows, columns, and data types of currently active dataset."""
    df = ACTIVE_DATASET_CACHE["df"]
    if df is None:
        raise HTTPException(status_code=400, detail="No hay ningún dataset activo cargado en memoria.")
    
    sample_rows = df.head(10).replace({float('nan'): None}).to_dict(orient="records")
    return {
        "filename": ACTIVE_DATASET_CACHE["filename"],
        "records_count": ACTIVE_DATASET_CACHE["records_count"],
        "institution": ACTIVE_DATASET_CACHE.get("institution", "Microdatos Armonizados"),
        "columns": df.columns.tolist(),
        "sample": sample_rows,
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


@app.get("/api/v1/datasets/active")
async def get_active_dataset(db: AsyncSession = Depends(get_async_db)):
    """Returns metadata of currently active dataset in memory."""
    result = await db.execute(
        select(DatasetModel).where(DatasetModel.is_active == True).order_by(desc(DatasetModel.created_at))
    )
    active_ds = result.scalars().first()
    
    return {
        "is_loaded": ACTIVE_DATASET_CACHE["df"] is not None,
        "filename": ACTIVE_DATASET_CACHE["filename"],
        "records_count": ACTIVE_DATASET_CACHE["records_count"],
        "institution": ACTIVE_DATASET_CACHE.get("institution", "Microdatos Armonizados"),
        "dataset": active_ds.to_dict() if active_ds else None,
    }


@app.get("/api/v1/datasets")
@app.get("/api/v1/datasets/list")
async def list_datasets(db: AsyncSession = Depends(get_async_db)):
    """Lists all uploaded datasets with active ID."""
    result = await db.execute(select(DatasetModel).order_by(desc(DatasetModel.created_at)))
    datasets = result.scalars().all()
    active_id = ""
    for ds in datasets:
        if getattr(ds, "is_active", False):
            active_id = str(ds.id)
            break
    ds_list = [ds.to_dict() for ds in datasets]
    return {"datasets": ds_list, "active_id": active_id}


# =====================================================================
# 2. MACHINE LEARNING ENGINE ENDPOINTS (CPU-BOUND OFFLOADED VIA THREADS)
# =====================================================================

@app.get("/api/v1/ml/eda", response_model=EDADataResponse)
async def get_eda():
    """
    Runs Exploratory Data Analysis (EDA) on active dataset outside the main event loop.
    """
    df = ACTIVE_DATASET_CACHE["df"]
    if df is None:
        raise HTTPException(status_code=400, detail="No hay ningún dataset activo cargado en memoria.")

    institution = ACTIVE_DATASET_CACHE.get("institution")
    # Offload heavy CPU work to threadpool
    eda_result = await asyncio.to_thread(compute_eda, df, institution)
    return eda_result


@app.post("/api/v1/ml/cross-validation", response_model=CrossValidationResponse)
async def perform_cross_validation(req: CrossValidationRequest):
    """
    Runs Stratified K-Fold CV with XGBoost outside the main event loop and persists model.
    """
    df = ACTIVE_DATASET_CACHE["df"]
    if df is None:
        raise HTTPException(status_code=400, detail="No hay ningún dataset activo cargado en memoria.")

    cv_result = await asyncio.to_thread(
        run_stratified_cv,
        df=df,
        n_folds=req.n_folds,
        target_col=req.target_col,
        algorithm=req.algorithm
    )
    ACTIVE_DATASET_CACHE["model_id"] = cv_result["model_id"]
    return cv_result


@app.get("/api/v1/ml/models")
async def get_ml_models():
    """Returns the benchmarked model leaderboard with the active champion model flagged."""
    return {
        "models": MODELS_REGISTRY,
        "active_model_id": ACTIVE_DEPLOYED_MODEL.get("id"),
        "active_model": ACTIVE_DEPLOYED_MODEL
    }


@app.get("/api/v1/ml/active-model")
async def get_active_ml_model():
    """Returns the currently deployed champion model powering the 3D Digital Twin and front-end."""
    return {
        "status": "ok",
        "active_model": ACTIVE_DEPLOYED_MODEL
    }


@app.post("/api/v1/ml/deploy-model")
async def deploy_ml_model(payload: Dict[str, Any]):
    """
    Deploys a selected model as the production champion model.
    Updates the active state so the 3D Digital Twin and React Frontend synchronize in real-time.
    """
    global ACTIVE_DEPLOYED_MODEL
    target_id = payload.get("model_id") or payload.get("id")
    deployed_by = payload.get("deployed_by", "Streamlit AI Studio")

    found = None
    for m in MODELS_REGISTRY:
        if m["id"] == target_id or m["algorithm"] == target_id:
            m["isDeployed"] = True
            found = m
        else:
            m["isDeployed"] = False

    if not found:
        raise HTTPException(
            status_code=404,
            detail=f"Modelo '{target_id}' no encontrado en el leaderboard de microdatos reales."
        )

    import datetime
    ACTIVE_DEPLOYED_MODEL = {
        **found,
        "deployedBy": deployed_by,
        "deployedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "active"
    }
    logger.info(f"Deployed new champion model: {found['name']} ({found['id']}) by {deployed_by}")

    return {
        "status": "success",
        "message": f"Modelo {found['name']} desplegado exitosamente al Gemelo Digital 3D.",
        "active_model": ACTIVE_DEPLOYED_MODEL
    }


@app.post("/api/v1/ml/proyeccion-cohorte", response_model=CohortProjectionResponse)
async def get_cohort_projections(req: CohortFilterRequest):
    """
    Calculates 1, 3 and 5-year cohort transition projections with SHAP explainability.
    """
    model_id = req.model_id or ACTIVE_DEPLOYED_MODEL.get("id", "model-xgboost-prod-opt")
    projections = await asyncio.to_thread(
        predict_cohort_transition,
        model_id=model_id,
        cohort_filters=req.cohort_filters,
        policy_params=req.policy_params
    )
    return projections


# =====================================================================
# 3. SIMULATION RUNS PERSISTENCE ENDPOINTS
# =====================================================================

@app.get("/api/v1/simulations/history")
async def get_simulation_history(db: AsyncSession = Depends(get_async_db)):
    """Returns past simulation runs from PostgreSQL."""
    result = await db.execute(select(SimulationRunModel).order_by(desc(SimulationRunModel.created_at)).limit(25))
    runs = result.scalars().all()
    return {"runs": [r.to_dict() for r in runs]}


@app.post("/api/v1/simulations/save")
async def save_simulation_run(
    run_data: SimulationRunCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Persists a completed simulation run summary."""
    new_run = SimulationRunModel(
        country=run_data.country,
        scenario=run_data.scenario,
        policy_params=run_data.policy_params,
        final_metrics=run_data.final_metrics,
        duration_sec=run_data.duration_sec,
    )
    db.add(new_run)
    await db.commit()
    await db.refresh(new_run)
    return {"status": "saved", "run": new_run.to_dict()}


@app.get("/api/v1/simulation/scenarios")
@app.get("/api/v1/simulations/scenarios")
async def get_simulation_scenarios():
    """
    Retorna la configuración y definiciones de los escenarios canónicos
    A, B1, B2, C y D del artículo, acompañados de las estimaciones en outputs/.
    """
    outputs = load_outputs_data()
    return {
        "scenarios": SCENARIO_CONFIGS,
        "table5_levels": outputs.get("table5_levels", []),
        "table6_changes": outputs.get("table6_changes", []),
        "table7_contrasts": outputs.get("table7_contrasts", []),
    }


@app.get("/api/v1/simulation/metrics")
@app.get("/api/v1/simulations/metrics")
async def get_structural_metrics_endpoint(
    country: str = Query(default="KENYA"),
    scenario: str = Query(default="A"),
    month: int = Query(default=0),
):
    """
    Calcula y expone métricas macroeconómicas auténticas generadas directamente
    por itdt.model.ITDTModel para el país, escenario y mes seleccionados.
    """
    return calculate_structural_metrics(country_code=country, scenario=scenario, month=month)


@app.get("/api/v1/simulation/trajectories")
@app.get("/api/v1/simulations/trajectories")
async def get_trajectories_endpoint(
    country: str = Query(default="KENYA"),
    scenario: str = Query(default="A"),
):
    """
    Expone la parte histórica (datos reales de ILOSTAT) y la simulación ITDT
    (meses 1 a 120 de la política) sin inventar ni interpolar datos ausentes.
    """
    historical = get_historical_ilostat_series(country_code=country)
    simulation = get_simulated_monthly_trajectory(country_code=country, scenario=scenario)
    return {
        "country": country,
        "scenario": scenario,
        "historical": historical,
        "simulation": simulation,
    }


@app.get("/api/v1/simulation/firms")
@app.get("/api/v1/simulations/firms")
async def get_firms_endpoint(
    country: str = Query(default="KENYA"),
    scenario: str = Query(default="A"),
    month: int = Query(default=0),
):
    """
    Expone las empresas del propio ITDTModel para el país y escenario seleccionados.
    """
    return get_model_firms(country_code=country, scenario=scenario, month=month)


@app.get("/api/v1/simulation/historical")
@app.get("/api/v1/simulations/historical")
async def get_historical_endpoint(
    country: str = Query(default="KENYA"),
):
    """
    Expone la serie histórica de ILOSTAT leída directamente de data/ilostat_series_historicas.csv
    con metadatos y fuente original sin inventar nombres ni cifras.
    """
    return get_historical_ilostat_series(country_code=country)


# =====================================================================
# 3.5. OUTPUTS ASSETS & SCIENTIFIC FIGURES DOWNLOAD ENDPOINTS
# =====================================================================

OUTPUTS_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs"))

KNOWN_IMAGE_METADATA = {
    "figure4_calibration.png": {
        "title": "Figura 4: Calibración SMM del Modelo ITDT",
        "category": "paper_figures",
        "categoryLabel": "Figuras del Paper",
        "description": "Momentos simulados vs. momentos observados de ILOSTAT para informalidad laboral y dispersión salarial.",
    },
    "figure5_sanctions_sweep.png": {
        "title": "Figura 5: Barrido de Sanciones e Intensidad GovTech",
        "category": "paper_figures",
        "categoryLabel": "Figuras del Paper",
        "description": "Elasticidad de la informalidad ante variaciones de 1× a 5× en sanciones (μ0, μ1) y fiscalización digital.",
    },
    "figure6_trajectories.png": {
        "title": "Figura 6: Trayectorias Dinámicas de Transición (Meses 1-120)",
        "category": "paper_figures",
        "categoryLabel": "Figuras del Paper",
        "description": "Evolución mensual continua de la informalidad y brecha de género por escenario canónico (A, B1, B2, C, D).",
    },
    "figure7_policy_effects.png": {
        "title": "Figura 7: Efectos Netos y Contrastes Estructurales",
        "category": "paper_figures",
        "categoryLabel": "Figuras del Paper",
        "description": "Comparativa de largo plazo del impacto macroeconómico, recaudación fiscal y equidad de género entre políticas.",
    },
    "capturas/fig_dashboard_kenia_escenarioA.png": {
        "title": "Captura HD: Tablero Ejecutivo - Escenario A (Status Quo)",
        "category": "capturas_hd",
        "categoryLabel": "Capturas HD (4800×2700 px)",
        "description": "Tablero ejecutivo en ultra-alta resolución al mes 120 de la política en Kenia (Régimen inercial).",
    },
    "capturas/fig_dashboard_kenia_escenarioD.png": {
        "title": "Captura HD: Tablero Ejecutivo - Escenario D (Integrado)",
        "category": "capturas_hd",
        "categoryLabel": "Capturas HD (4800×2700 px)",
        "description": "Tablero ejecutivo con paquete sinérgico de GovTech intensivo y corresponsabilidad de cuidados.",
    },
    "capturas/fig_gemelo3d_kenia_escenarioA.png": {
        "title": "Captura HD: Gemelo Digital 3D - Escenario A (Mes 120)",
        "category": "capturas_hd",
        "categoryLabel": "Capturas HD (4800×2700 px)",
        "description": "Render espacial fidedigno de torres formales e informales al horizonte final (mes 120).",
    },
    "capturas/fig_gemelo3d_kenia_escenarioA_m60.png": {
        "title": "Captura HD: Gemelo Digital 3D - Escenario A (Mes 60)",
        "category": "capturas_hd",
        "categoryLabel": "Capturas HD (4800×2700 px)",
        "description": "Estado de transición a mitad de ciclo (mes 60) del escenario inercial.",
    },
    "capturas/fig_gemelo3d_kenia_escenarioB2.png": {
        "title": "Captura HD: Gemelo Digital 3D - Escenario B2 (GovTech 3×, Mes 120)",
        "category": "capturas_hd",
        "categoryLabel": "Capturas HD (4800×2700 px)",
        "description": "Visualización 3D con sanciones triplicadas y fiscalización algorítmica intensiva al mes 120.",
    },
    "capturas/fig_gemelo3d_kenia_escenarioB2_m60.png": {
        "title": "Captura HD: Gemelo Digital 3D - Escenario B2 (GovTech 3×, Mes 60)",
        "category": "capturas_hd",
        "categoryLabel": "Capturas HD (4800×2700 px)",
        "description": "Estado de transición intermedio (mes 60) bajo régimen de sanciones elevadas.",
    },
    "reproduce/figura5_intensidad_sanciones.png": {
        "title": "Figura 5 (Replicación): Intensidad de Sanciones",
        "category": "reproduce",
        "categoryLabel": "Figuras de Replicación",
        "description": "Gráfico generado por el pipeline de reproducción científica del artículo para barrido de sanciones.",
    },
    "reproduce/figura6_informalidad_sexo.png": {
        "title": "Figura 6 (Replicación): Informalidad por Sexo",
        "category": "reproduce",
        "categoryLabel": "Figuras de Replicación",
        "description": "Gráfico de replicación directa con trayectorias de informalidad desagregadas para hombres y mujeres.",
    },
    "reproduce/figura5_intensidad_sanciones.pdf": {
        "title": "Figura 5 Vectorial (PDF): Intensidad de Sanciones",
        "category": "reproduce",
        "categoryLabel": "Figuras de Replicación",
        "description": "Gráfico vectorial de alta fidelidad listo para imprenta o publicación académica.",
    },
    "reproduce/figura6_informalidad_sexo.pdf": {
        "title": "Figura 6 Vectorial (PDF): Informalidad por Sexo",
        "category": "reproduce",
        "categoryLabel": "Figuras de Replicación",
        "description": "Gráfico vectorial de alta fidelidad listo para imprenta o publicación académica.",
    },
}


def _format_size_bytes(size_bytes: int) -> str:
    """Formatea bytes a KB o MB legibles."""
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.0f} KB"
    return f"{size_bytes} B"


def _resolve_safe_output_path(rel_path: str) -> str:
    """Verifica y resuelve la ruta de un archivo dentro de outputs/ previniendo path traversal."""
    clean_rel = rel_path.replace("\\", "/").strip().lstrip("/")
    abs_path = os.path.abspath(os.path.join(OUTPUTS_ROOT_DIR, clean_rel))
    if not abs_path.startswith(OUTPUTS_ROOT_DIR):
        raise HTTPException(status_code=400, detail="Acceso denegado: ruta fuera del directorio outputs.")
    if not os.path.isfile(abs_path):
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado en outputs/: {clean_rel}")
    return abs_path


def _scan_output_images() -> List[Dict[str, Any]]:
    """Escanea la carpeta outputs/ y subdirectorios recopilando imágenes existentes."""
    images = []
    if not os.path.isdir(OUTPUTS_ROOT_DIR):
        return images

    valid_extensions = {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".webp"}
    allowed_dirs = ["", "capturas", "reproduce"]

    for sub_rel in allowed_dirs:
        curr_dir = os.path.join(OUTPUTS_ROOT_DIR, sub_rel) if sub_rel else OUTPUTS_ROOT_DIR
        if not os.path.isdir(curr_dir):
            continue

        for fname in sorted(os.listdir(curr_dir)):
            full_path = os.path.join(curr_dir, fname)
            if not os.path.isfile(full_path):
                continue

            _, ext = os.path.splitext(fname.lower())
            if ext not in valid_extensions:
                continue

            rel_key = f"{sub_rel}/{fname}" if sub_rel else fname
            meta = KNOWN_IMAGE_METADATA.get(rel_key, {})
            
            # Categoría por defecto según carpeta si no está en metadatos conocidos
            cat = meta.get("category")
            if not cat:
                if sub_rel == "capturas":
                    cat = "capturas_hd"
                elif sub_rel == "reproduce":
                    cat = "reproduce"
                else:
                    cat = "paper_figures"

            title = meta.get("title") or fname.replace("_", " ").replace("-", " ").capitalize()
            desc = meta.get("description") or f"Salida gráfica oficial del sistema: {fname}."
            cat_label = meta.get("categoryLabel") or ("Capturas HD" if cat == "capturas_hd" else ("Replicación" if cat == "reproduce" else "Figuras del Paper"))

            try:
                stat = os.stat(full_path)
                size_bytes = stat.st_size
                mtime = stat.st_mtime
            except Exception:
                size_bytes = 0
                mtime = 0

            images.append({
                "filename": fname,
                "relativePath": rel_key,
                "category": cat,
                "categoryLabel": cat_label,
                "title": title,
                "description": desc,
                "sizeBytes": size_bytes,
                "sizeFormatted": _format_size_bytes(size_bytes),
                "extension": ext.lstrip("."),
                "lastModified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)),
                "downloadUrl": f"/api/v1/outputs/download-image?path={rel_key}",
                "previewUrl": f"/api/v1/outputs/preview-image?path={rel_key}",
            })

    return images


@app.get("/api/v1/outputs/images")
async def list_output_images():
    """
    Lista el catálogo completo de figuras científicas, capturas de ultra-alta fidelidad
    y gráficos de reproducción generados en la carpeta outputs/.
    """
    images = _scan_output_images()
    categories = [
        {"id": "all", "label": "Todas las Figuras", "count": len(images)},
        {"id": "paper_figures", "label": "Figuras del Paper (Fig. 4-7)", "count": sum(1 for img in images if img["category"] == "paper_figures")},
        {"id": "capturas_hd", "label": "Capturas HD (Gemelo 3D & Tablero)", "count": sum(1 for img in images if img["category"] == "capturas_hd")},
        {"id": "reproduce", "label": "Figuras de Replicación", "count": sum(1 for img in images if img["category"] == "reproduce")},
    ]
    return {
        "status": "success",
        "total": len(images),
        "categories": categories,
        "images": images,
    }


@app.get("/api/v1/outputs/download-image")
async def download_output_image(path: str = Query(..., description="Ruta relativa del archivo dentro de outputs/")):
    """
    Descarga una imagen específica de outputs/ con cabeceras de Content-Disposition attachment.
    """
    abs_path = _resolve_safe_output_path(path)
    filename = os.path.basename(abs_path)
    mime_type, _ = mimetypes.guess_type(abs_path)
    if not mime_type:
        mime_type = "image/png" if filename.endswith(".png") else "application/octet-stream"

    return FileResponse(
        path=abs_path,
        filename=filename,
        media_type=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.get("/api/v1/outputs/preview-image")
async def preview_output_image(path: str = Query(..., description="Ruta relativa del archivo dentro de outputs/")):
    """
    Permite previsualizar una imagen en el frontend (inline) sin forzar descarga inmediata.
    """
    abs_path = _resolve_safe_output_path(path)
    filename = os.path.basename(abs_path)
    mime_type, _ = mimetypes.guess_type(abs_path)
    if not mime_type:
        mime_type = "image/png" if filename.endswith(".png") else "application/octet-stream"

    return FileResponse(
        path=abs_path,
        media_type=mime_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'}
    )


@app.get("/api/v1/outputs/download-all-zip")
async def download_all_output_images_zip(
    category: Optional[str] = Query(default=None, description="Filtrar por categoría (paper_figures, capturas_hd, reproduce) o all")
):
    """
    Empaqueta y descarga en tiempo real todas las imágenes de outputs/ como archivo ZIP estructurado.
    """
    all_images = _scan_output_images()
    if category and category != "all":
        all_images = [img for img in all_images if img["category"] == category]

    if not all_images:
        raise HTTPException(status_code=404, detail="No se encontraron imágenes en outputs/ para empaquetar.")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        manifest_lines = [
            "=================================================================",
            "PAQUETE DE SALIDAS GRÁFICAS Y FIGURAS DEL MODELO ITDT",
            "Gemelo Digital 3D del Mercado Laboral y Políticas GovTech",
            f"Fecha de Generación: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total de Archivos Incluidos: {len(all_images)}",
            "=================================================================\n",
            "ARCHIVOS CONTENIDOS:\n",
        ]

        for item in all_images:
            abs_path = os.path.join(OUTPUTS_ROOT_DIR, item["relativePath"].replace("/", os.sep))
            if os.path.isfile(abs_path):
                # Organizar dentro del ZIP en carpetas por categoría
                folder_in_zip = item["category"]
                arcname = f"{folder_in_zip}/{os.path.basename(abs_path)}"
                zf.write(abs_path, arcname=arcname)
                manifest_lines.append(f"- {arcname} ({item['sizeFormatted']})")
                manifest_lines.append(f"  Título: {item['title']}")
                manifest_lines.append(f"  Descripción: {item['description']}\n")

        manifest_lines.append("\n=================================================================")
        manifest_lines.append("Fuente metodológica: itdt.model.ITDTModel y series observadas de ILOSTAT.")
        manifest_content = "\n".join(manifest_lines)
        zf.writestr("MANIFESTO_FIGURAS.txt", manifest_content.encode("utf-8"))

    zip_buffer.seek(0)
    zip_filename = f"Outputs_Imagenes_ITDT_{category or 'Todas'}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'}
    )

@app.websocket("/ws/simulation")
async def websocket_simulation_endpoint(websocket: WebSocket):
    """
    High-frequency full-duplex WebSocket orchestrating monthly boid kinematics
    and dynamic macro equilibrium without blocking the main event loop.
    Conectado a itdt.model.ITDTModel para escenarios A, B1, B2, C y D.
    """
    await websocket.accept()
    logger.info("WebSocket client connected to /ws/simulation")

    sim = SimulationEngine(country="KENYA", scenario="A")
    sim.is_playing = False
    is_connected = True

    async def incoming_messages_listener():
        nonlocal is_connected
        try:
            while is_connected:
                text_msg = await websocket.receive_text()
                try:
                    data = json.loads(text_msg)
                    action = data.get("action")

                    if action == "play":
                        sim.is_playing = True
                    elif action == "pause":
                        sim.is_playing = False
                    elif action == "set_speed":
                        sim.playback_speed = float(data.get("speed", 1.0))
                    elif action == "seek":
                        sim.month = max(0, min(120, int(data.get("month", 0))))
                    elif action == "set_country":
                        sim.set_country(data.get("country", "KENYA"))
                    elif action == "set_scenario":
                        sim.set_scenario(data.get("scenario", "A"))
                    elif action == "set_policy":
                        sim.set_policy_params(data.get("policy_params", {}))
                    elif action == "reset":
                        sim.month = 0
                        sim.is_playing = False


                    # Immediately send an updated snapshot on interactive user seek/change (without advancing month)
                    if action in ("seek", "set_country", "set_scenario", "set_policy", "reset"):
                        frame_data = await asyncio.to_thread(sim.step, False)
                        await websocket.send_text(json.dumps(frame_data))

                except json.JSONDecodeError:
                    pass
        except WebSocketDisconnect:
            is_connected = False
        except Exception as e:
            logger.debug(f"Incoming listener terminated: {e}")
            is_connected = False

    # Start client receiver task
    listener_task = asyncio.create_task(incoming_messages_listener())

    try:
        # Initial snapshot frame at month 0 (do not advance month yet)
        initial_frame = await asyncio.to_thread(sim.step, False)
        await websocket.send_text(json.dumps(initial_frame))

        while is_connected:
            if sim.is_playing:
                # Interval paced by playback speed: 1x = 750ms, 2x = 375ms, 4x = 185ms
                interval = max(0.08, 0.75 / max(0.25, sim.playback_speed))
                await asyncio.sleep(interval)
                
                if not is_connected:
                    break

                # Execute kinematic step in threadpool to prevent any event loop stalls (advance month)
                frame_data = await asyncio.to_thread(sim.step, True)
                await websocket.send_text(json.dumps(frame_data))

                # If simulation reaches month 120, persist summary to PostgreSQL
                if sim.month == 120:
                    try:
                        async with AsyncSessionLocal() as db_session:
                            final_run = SimulationRunModel(
                                country=sim.country,
                                scenario=sim.scenario,
                                policy_params=sim.policy_params,
                                final_metrics=frame_data["metrics"],
                                duration_sec=round(120 * interval, 1),
                            )
                            db_session.add(final_run)
                            await db_session.commit()
                            logger.info(f"Persisted final simulation cycle in DB for {sim.country}")
                    except Exception as db_err:
                        logger.warning(f"Could not persist simulation run: {db_err}")
            else:
                await asyncio.sleep(0.15)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as exc:
        logger.warning(f"WebSocket session ended: {exc}")
    finally:
        is_connected = False
        listener_task.cancel()


# =====================================================================
# 5. COPILOT IA INTEGRATION ENDPOINTS (LANGFLOW V1)
# =====================================================================

@app.post("/api/v1/copilot/chat", response_model=CopilotChatResponse)
async def copilot_chat_endpoint(req: CopilotChatRequest):
    """
    Endpoint principal del Copiloto IA de Economía Laboral (V1).
    Orquesta la consulta a través de Langflow y Gemini garantizando
    que las respuestas utilicen datos reales y verificados de simulación,
    e inserta de forma persistente cada mensaje y respuesta en PostgreSQL.
    """
    session_id = req.session_id or "default-session"
    country = req.country or "KENYA"
    scenario = req.scenario or "BASELINE"
    month = req.month or 0

    try:
        # Recuperar memoria conversacional reciente desde PostgreSQL para enriquecer el contexto
        history_records = []
        try:
            async with AsyncSessionLocal() as db_session:
                hist_stmt = (
                    select(CopilotMessageModel)
                    .where(CopilotMessageModel.session_id == session_id)
                    .order_by(desc(CopilotMessageModel.created_at))
                    .limit(3)
                )
                hist_res = await db_session.execute(hist_stmt)
                history_records = [r.to_dict() for r in reversed(hist_res.scalars().all())]
        except Exception as h_err:
            logger.debug(f"Historial previo de PostgreSQL no recuperado: {h_err}")

        result = await execute_copilot_query(
            user_query=req.message,
            session_id=session_id,
            country=country,
            scenario=scenario,
            month=month,
            policy_params=req.policy_params,
            history=history_records,
        )

        # Inserción asíncrona de trazabilidad y memoria en PostgreSQL (copilot_chat_history)
        try:
            async with AsyncSessionLocal() as db_session:
                chat_record = CopilotMessageModel(
                    session_id=session_id,
                    country=country,
                    scenario=scenario,
                    month=month,
                    user_message=req.message.strip(),
                    assistant_response=result.get("response", ""),
                    source=result.get("source", "langflow"),
                    flow_id=result.get("flow_id", "labortwin-copilot-v1"),
                    verified_metrics=result.get("verified_metrics", {}),
                    policy_params=req.policy_params or {},
                )
                db_session.add(chat_record)
                await db_session.commit()
                logger.info(f"Interacción de Copilot IA persistida exitosamente en PostgreSQL ({chat_record.id})")
        except Exception as db_save_err:
            logger.warning(f"No se pudo registrar la conversación en PostgreSQL: {db_save_err}")

        return result
    except CopilotServiceError as cse:
        logger.warning(f"Error controlado en Copiloto IA: {cse.message}")
        raise HTTPException(status_code=cse.status_code, detail=cse.message)
    except Exception as exc:
        logger.error(f"Error inesperado en copilot_chat_endpoint: {exc}")
        raise HTTPException(status_code=500, detail="Error interno al procesar la consulta con el Copiloto IA.")


@app.get("/api/v1/copilot/history")
async def get_copilot_chat_history(
    session_id: str = Query(default="default-session"),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Recupera el historial cronológico de conversaciones del Copiloto IA desde PostgreSQL.
    """
    stmt = (
        select(CopilotMessageModel)
        .where(CopilotMessageModel.session_id == session_id)
        .order_by(CopilotMessageModel.created_at.asc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()
    return [r.to_dict() for r in records]


@app.delete("/api/v1/copilot/history")
async def delete_copilot_chat_history(
    session_id: str = Query(default="default-session"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Elimina o reinicia el historial de conversación para una sesión en PostgreSQL.
    """
    from sqlalchemy import delete
    stmt = delete(CopilotMessageModel).where(CopilotMessageModel.session_id == session_id)
    result = await db.execute(stmt)
    await db.commit()
    deleted_rows = getattr(result, "rowcount", 0)
    return {"status": "ok", "deleted_rows": deleted_rows}


@app.get("/api/v1/copilot/simulation-metrics")
async def get_copilot_simulation_metrics(
    country: str = Query(default="KENYA"),
    scenario: str = Query(default="BASELINE"),
    month: int = Query(default=0),
):
    """
    Endpoint de solo lectura que expone las métricas verificadas de simulación
    para consumo seguro del Copiloto o herramientas de diagnóstico.
    """
    return get_simulation_metrics(country=country, scenario=scenario, month=month)


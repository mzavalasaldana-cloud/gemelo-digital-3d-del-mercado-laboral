"""
streamlit_app.data.mock_data: Registros base, perfiles empíricos de países y datos de demostración.
- COUNTRY_PROFILES se construye dinámicamente a partir de itdt.parameters.COUNTRY_DATABASE y data/ilostat_s_F.csv.
- Las corridas de simulación se consultan desde la base de datos (/api/v1/simulations/history).
- Los elementos de demostración (usuarios) están claramente identificados con el prefijo DEMO_.
"""

import json
import logging
from typing import Dict, Any, List
from itdt.parameters import COUNTRY_DATABASE

logger = logging.getLogger("labortwin.mock_data")

# ==============================================================================
# 1. PERFILES DE PAÍSES (Fuente Real: COUNTRY_DATABASE y data/ilostat_s_F.csv)
# ==============================================================================

_UI_COUNTRY_METADATA: Dict[str, Dict[str, Any]] = {
    "KENYA": {
        "flag": "🇰🇪",
        "currency": "KES",
    },
    "NIGERIA": {
        "flag": "🇳🇬",
        "currency": "NGN",
    },
    "INDIA": {
        "flag": "🇮🇳",
        "currency": "INR",
    },
    "BANGLADESH": {
        "flag": "🇧🇩",
        "currency": "BDT",
    },
}


def build_country_profiles() -> Dict[str, Dict[str, Any]]:
    """
    Construye los perfiles de países derivando todas las métricas empíricas de
    itdt.parameters.COUNTRY_DATABASE (calibrado con data/ilostat_s_F.csv e ILOSTAT oficial).
    """
    profiles: Dict[str, Dict[str, Any]] = {}
    for c_key, c_info in COUNTRY_DATABASE.items():
        ui = _UI_COUNTRY_METADATA.get(c_key, {})
        profiles[c_key] = {
            "code": c_key,
            "name": f"{c_info['name']} (ILOSTAT {c_info.get('year', 2024)})",
            "country_name": c_info["name"],
            "country_code": c_info["country_code"],
            "flag": ui.get("flag", "🌐"),
            "currency": ui.get("currency", "USD"),
            "year": c_info.get("year", 2024),
            "baseInformalityRate": c_info["T_obs"],
            "baseInformalityFemale": c_info["F_obs"],
            "baseInformalityMale": c_info["M_obs"],
            "genderGap": round(c_info["F_obs"] - c_info["M_obs"], 2),
            "s_F": c_info["s_F"],
        }
    return profiles


COUNTRY_PROFILES: Dict[str, Dict[str, Any]] = build_country_profiles()

INITIAL_POLICY_STATE: Dict[str, Any] = {
    "scenario": "A",
}


# ==============================================================================
# 2. HISTORIAL DE CORRIDAS DE SIMULACIÓN (Fuente Real: DB /api/v1/simulations/history)
# ==============================================================================

def get_simulation_runs() -> List[Dict[str, Any]]:
    """
    Carga el historial de corridas de simulación desde la base de datos a través
    del endpoint /api/v1/simulations/history o consulta directa a PostgreSQL.
    """
    # 1. Consulta al backend FastAPI
    try:
        import os
        import urllib.request
        raw_b_url = os.getenv("BACKEND_URL")
        backend_url = raw_b_url.strip().rstrip("/") if raw_b_url and raw_b_url.strip() else "http://127.0.0.1:8000"
        req = urllib.request.Request(f"{backend_url}/api/v1/simulations/history", headers={"User-Agent": "StreamlitTwin"})
        with urllib.request.urlopen(req, timeout=1.2) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                runs = data.get("runs", [])
                if runs:
                    return runs
    except Exception:
        pass

    # 2. Fallback: consulta directa a la base de datos PostgreSQL
    try:
        from backend.database import DATABASE_URL
        from sqlalchemy import create_engine, text
        sync_url = DATABASE_URL.replace("+asyncpg", "")
        sync_engine = create_engine(sync_url)
        with sync_engine.connect() as conn:
            res = conn.execute(text("SELECT id, country, scenario, policy_params, final_metrics, duration_sec, created_at FROM simulation_runs ORDER BY created_at DESC LIMIT 25"))
            rows = res.fetchall()
            if rows:
                return [
                    {
                        "id": row[0],
                        "country": row[1],
                        "scenario": row[2],
                        "policy_params": row[3],
                        "final_metrics": row[4],
                        "duration_sec": row[5],
                        "created_at": str(row[6]),
                    }
                    for row in rows
                ]
    except Exception:
        pass

    return []


MOCK_SIM_RUNS: List[Dict[str, Any]] = get_simulation_runs()


# ==============================================================================
# 3. USUARIOS INSTITUCIONALES (Datos de Demostración RBAC)
# ==============================================================================

DEMO_USERS: List[Dict[str, Any]] = [
    {
        "id": "usr-001",
        "name": "Dra. Elena Rostova (Demostración)",
        "email": "elena.rostova@example.org",
        "role": "ADMIN",
        "department": "Dirección de Modelado Macroeconómico",
        "lastActive": "Activo ahora",
        "avatar": "👩‍💼",
        "permissions": {
            "editPolicies": True,
            "retrainAI": True,
            "manageDatasets": True,
            "manageUsers": True,
            "exportReports": True,
        },
        "isDemo": True,
    },
    {
        "id": "usr-002",
        "name": "Carlos Mendoza (Demostración)",
        "email": "carlos.mendoza@example.org",
        "role": "POLICY_ANALYST",
        "department": "Análisis de Políticas de Empleo",
        "lastActive": "Hace 15 min",
        "avatar": "👨‍💼",
        "permissions": {
            "editPolicies": True,
            "retrainAI": False,
            "manageDatasets": True,
            "manageUsers": False,
            "exportReports": True,
        },
        "isDemo": True,
    },
    {
        "id": "usr-003",
        "name": "Dr. Kwame Achebe (Demostración)",
        "email": "kwame.achebe@example.org",
        "role": "RESEARCHER",
        "department": "Investigación Laboral (Demostración)",
        "lastActive": "Hace 2 horas",
        "avatar": "🧑‍🔬",
        "permissions": {
            "editPolicies": False,
            "retrainAI": True,
            "manageDatasets": True,
            "manageUsers": False,
            "exportReports": True,
        },
        "isDemo": True,
    },
    {
        "id": "usr-004",
        "name": "Sofia Lindqvist (Demostración)",
        "email": "sofia.lindqvist@example.org",
        "role": "AUDITOR",
        "department": "Auditoría de Modelado (Demostración)",
        "lastActive": "Ayer",
        "avatar": "🕵️‍♀️",
        "permissions": {
            "editPolicies": False,
            "retrainAI": False,
            "manageDatasets": False,
            "manageUsers": False,
            "exportReports": True,
        },
        "isDemo": True,
    },
]

# Alias de compatibilidad
MOCK_USERS = DEMO_USERS

DEMO_DATASETS: List[Dict[str, Any]] = []
PRELOADED_DATASETS = DEMO_DATASETS

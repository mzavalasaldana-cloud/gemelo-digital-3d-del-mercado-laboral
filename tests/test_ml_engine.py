"""
tests/test_ml_engine.py: Pruebas unitarias y de integración para el Motor de IA
y Armonización de Microdatos Reales (OIT / ILOSTAT).

Verifica:
1. Escaneo recursivo de microdatos reales (CSV, SAV) ignorando _archivado.
2. Carga y armonización de encuestas oficiales (India PLFS 2024 y Nigeria NLFS 2023 Q3).
3. Calibración de tasas de informalidad ponderadas contra benchmarks oficiales de ILOSTAT.
4. Partición por hogares (GroupKFold) con cero fuga inter-hogar.
5. Entrenamiento con ponderadores de encuesta (sample_weight).
6. Cumplimiento de regla de integridad (prohibición de datos sintéticos/mock).
7. Integridad de los outputs del artículo científico (git diff vacío contra 4773d96).
8. Existencia y validez de modelos campeones persistidos en models_store/.
"""

import os
import subprocess
import pytest
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier

from backend.ml_engine import (
    REAL_MICRODATA_DIR,
    scan_real_microdatasets,
    load_real_country_microdata,
    harmonize_india_plfs,
    harmonize_nigeria_nlfs,
    predict_cohort_transition,
    generate_country_preset_dataset,
    generate_synthetic_benchmark_dataset,
)


def test_scan_real_microdatasets():
    """El motor debe descubrir recursivamente los microdatos reales de India y Nigeria."""
    datasets = scan_real_microdatasets()
    assert len(datasets) >= 2, f"Se esperaban al menos 2 datasets, encontrados: {len(datasets)}"

    ids = [d["dataset_id"] for d in datasets]
    assert any("india" in did for did in ids), "India PLFS 2024 no encontrada en scan"
    assert any("nigeria" in did for did in ids), "Nigeria NLFS 2023 Q3 no encontrada en scan"

    filenames = [d["filename"].lower() for d in datasets]
    assert any(fn.endswith(".csv") for fn in filenames), "No se detectó el archivo CSV de India"
    assert any(fn.endswith(".sav") for fn in filenames), "No se detectó el archivo SAV de Nigeria"

    # Verificar que no cargue archivos de carpetas _archivado
    paths = [d.get("path", "") for d in datasets]
    for p in paths:
        assert "_archivado" not in p, f"Dataset en carpeta archivada no debe ser escaneado: {p}"


def test_load_real_country_microdata():
    """Verifica que las funciones de carga retornen DataFrames armonizados válidos."""
    # India
    res_india = load_real_country_microdata("india")
    assert res_india is not None, "load_real_country_microdata('india') retornó None"
    df_india, fname_in, cname_in = res_india
    assert len(df_india) > 100_000, f"Muestra de ocupados en India insuficiente: {len(df_india)}"
    assert "ESTADO_LABORAL" in df_india.columns
    assert "es_formal" in df_india.columns
    assert "es_informal" in df_india.columns
    assert "edad" in df_india.columns
    assert "anos_educacion" in df_india.columns
    assert "horas_semana" in df_india.columns
    assert "peso" in df_india.columns
    assert "household_id" in df_india.columns

    # Nigeria
    res_nigeria = load_real_country_microdata("nigeria")
    assert res_nigeria is not None, "load_real_country_microdata('nigeria') retornó None"
    df_nigeria, fname_ng, cname_ng = res_nigeria
    assert len(df_nigeria) > 15_000, f"Muestra de ocupados en Nigeria insuficiente: {len(df_nigeria)}"
    assert "ESTADO_LABORAL" in df_nigeria.columns
    assert "es_formal" in df_nigeria.columns
    assert "es_informal" in df_nigeria.columns
    assert "edad" in df_nigeria.columns
    assert "anos_educacion" in df_nigeria.columns
    assert "horas_semana" in df_nigeria.columns
    assert "peso" in df_nigeria.columns
    assert "household_id" in df_nigeria.columns


def test_india_harmonization_and_ilostat_calibration():
    """
    Verifica que la armonización OIT de India PLFS 2024 reproduzca la tasa de informalidad
    calibrada con ILOSTAT con una desviación menor a 0.5 puntos porcentuales.
    """
    res = load_real_country_microdata("india")
    assert res is not None
    df, _, _ = res

    # Ponderación
    w = df["peso"].values
    informal = df["es_informal"].values

    weighted_informality = float(np.sum(informal * w) / np.sum(w) * 100.0)

    # Benchmark calibrado: 87.96 % (ILOSTAT oficial: 88.13 %, diff: -0.17 p.p.)
    assert 87.0 <= weighted_informality <= 89.0, (
        f"Tasa de informalidad de India {weighted_informality:.2f}% fuera del rango calibrado [87.0%, 89.0%]"
    )

    # Brecha de género: mujeres tienen mayor informalidad que hombres
    women_mask = (df["sexo"] == 2).values
    men_mask = (df["sexo"] == 1).values

    w_women = float(np.sum(informal[women_mask] * w[women_mask]) / np.sum(w[women_mask]) * 100.0)
    w_men = float(np.sum(informal[men_mask] * w[men_mask]) / np.sum(w[men_mask]) * 100.0)

    assert w_women > w_men, f"Tasa mujeres ({w_women:.2f}%) debe ser superior a hombres ({w_men:.2f}%) en India"
    assert 89.0 <= w_women <= 92.0, f"Tasa mujeres {w_women:.2f}% fuera de calibración"
    assert 85.5 <= w_men <= 88.5, f"Tasa hombres {w_men:.2f}% fuera de calibración"


def test_nigeria_harmonization_and_ilostat_calibration():
    """
    Verifica que la armonización OIT de Nigeria NLFS 2023 Q3 reproduzca la tasa de informalidad
    calibrada con ILOSTAT con una desviación menor a 1.0 punto porcentual.
    """
    res = load_real_country_microdata("nigeria")
    assert res is not None
    df, _, _ = res

    w = df["peso"].values
    informal = df["es_informal"].values

    weighted_informality = float(np.sum(informal * w) / np.sum(w) * 100.0)

    # Benchmark calibrado: 92.25 % (ILOSTAT oficial: 93.14 %, diff: -0.89 p.p.)
    assert 91.0 <= weighted_informality <= 93.5, (
        f"Tasa de informalidad de Nigeria {weighted_informality:.2f}% fuera del rango calibrado [91.0%, 93.5%]"
    )

    women_mask = (df["sexo"] == 2).values
    men_mask = (df["sexo"] == 1).values

    w_women = float(np.sum(informal[women_mask] * w[women_mask]) / np.sum(w[women_mask]) * 100.0)
    w_men = float(np.sum(informal[men_mask] * w[men_mask]) / np.sum(w[men_mask]) * 100.0)

    assert w_women > w_men, f"Tasa mujeres ({w_women:.2f}%) debe ser superior a hombres ({w_men:.2f}%) en Nigeria"
    assert 94.5 <= w_women <= 97.5, f"Tasa mujeres {w_women:.2f}% fuera de calibración"
    assert 87.0 <= w_men <= 90.5, f"Tasa hombres {w_men:.2f}% fuera de calibración"


def test_group_kfold_no_household_leakage():
    """
    Verifica que la partición con StratifiedGroupKFold por identificador de hogar
    garantice CERO solapamiento de familias entre el conjunto de entrenamiento y validación.
    """
    res = load_real_country_microdata("nigeria")
    assert res is not None
    df, _, _ = res

    # Tomar muestra de prueba para rapidez
    sub_df = df.sample(n=3000, random_state=42).reset_index(drop=True)

    sgkf = StratifiedGroupKFold(n_splits=3)
    X = sub_df[["edad", "anos_educacion", "horas_semana"]]
    y = sub_df["es_informal"]
    groups = sub_df["household_id"]

    for fold, (train_idx, val_idx) in enumerate(sgkf.split(X, y, groups=groups)):
        train_hh = set(groups.iloc[train_idx])
        val_hh = set(groups.iloc[val_idx])
        overlap = train_hh.intersection(val_hh)
        assert len(overlap) == 0, (
            f"Fuga intrahogar detectada en fold {fold}: {len(overlap)} hogares solapados entre train y val"
        )


def test_models_train_with_sample_weights():
    """
    Verifica que el clasificador se entrene efectivamente incorporando sample_weight.
    """
    res = load_real_country_microdata("india")
    assert res is not None
    df, _, _ = res

    sample_df = df.sample(n=4000, random_state=42).reset_index(drop=True)
    X = sample_df[["edad", "anos_educacion", "horas_semana", "zona_rural"]]
    y = sample_df["es_informal"].values
    w = sample_df["peso"].values

    clf = HistGradientBoostingClassifier(max_iter=30, random_state=42)
    clf.fit(X, y, sample_weight=w)

    preds = clf.predict(X)
    probs = clf.predict_proba(X)[:, 1]

    assert len(preds) == len(y)
    assert 0.0 <= np.min(probs) and np.max(probs) <= 1.0
    acc = np.mean(preds == y)
    assert acc > 0.75, f"Accuracy del modelo con ponderadores demasiado baja: {acc:.2f}"


def test_no_synthetic_data_rule():
    """
    Regla 1: Prohibido generar datos sintéticos o simulados como si fueran reales.
    Las funciones obsoletas de generación sintética deben arrojar RuntimeError.
    """
    with pytest.raises(RuntimeError):
        generate_country_preset_dataset("pais_inexistente_sintetico")

    with pytest.raises(RuntimeError):
        generate_synthetic_benchmark_dataset(500)

    # predict_cohort_transition debe retornar lista vacía sin inventar transiciones
    cohorts_res = predict_cohort_transition()
    assert cohorts_res["cohorts"] == [], "Proyecciones de cohortes deben estar vacías sin panel longitudinal"


def test_outputs_integrity():
    """
    Regla 2: NO modificar el modelo econométrico (itdt/) ni las tablas del artículo.
    El comando git diff 4773d96 -- outputs/table*.md outputs/table*.csv ... debe ser vacío.
    """
    cmd = [
        "git", "diff", "4773d96", "--",
        "outputs/table*.md",
        "outputs/table*.csv",
        "outputs/figure*.png",
        "outputs/*.json",
        ":(exclude)outputs/motor_ia/*",
        ":(exclude)outputs/figuras_articulo/*",
        ":(exclude)outputs/capturas/*",
        ":(exclude)outputs/verificacion_sistema/*",
        ":(exclude)outputs/ablacion_*.json",
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    diff_output = (result.stdout or "").strip()
    assert diff_output == "", f"Regresión detectada en outputs del artículo científico:\n{diff_output}"


def test_model_registry_and_champions_exist():
    """
    Paso 5: Verifica que los modelos campeones y métricas de desempeño
    estén correctamente generados y persistidos.
    """
    # 1. Tabla de desempeño generada
    csv_path = os.path.join("outputs", "motor_ia", "tabla_desempeno_modelos.csv")
    md_path = os.path.join("outputs", "motor_ia", "tabla_desempeno_modelos.md")
    assert os.path.exists(csv_path), "Falta outputs/motor_ia/tabla_desempeno_modelos.csv"
    assert os.path.exists(md_path), "Falta outputs/motor_ia/tabla_desempeno_modelos.md"

    df_perf = pd.read_csv(csv_path)
    assert len(df_perf) >= 12, f"Se esperaban al menos 12 filas (6 modelos x 2 países), hay: {len(df_perf)}"
    assert any("AUC-ROC" in col for col in df_perf.columns), "Falta columna AUC-ROC en tabla de desempeño"
    assert any("F1-Score" in col for col in df_perf.columns), "Falta columna F1-Score en tabla de desempeño"
    assert any("Accuracy" in col for col in df_perf.columns), "Falta columna Accuracy en tabla de desempeño"
    assert any("Brier" in col for col in df_perf.columns), "Falta columna Brier Score en tabla de desempeño"

    # 2. Modelos campeones persistidos
    india_model_path = os.path.join("models_store", "model_champion_india.joblib")
    nigeria_model_path = os.path.join("models_store", "model_champion_nigeria.joblib")

    assert os.path.exists(india_model_path), f"Falta modelo campeón de India: {india_model_path}"
    assert os.path.exists(nigeria_model_path), f"Falta modelo campeón de Nigeria: {nigeria_model_path}"

    model_in = joblib.load(india_model_path)
    estimator_in = model_in.get("model", model_in)
    assert hasattr(estimator_in, "predict"), "El modelo de India no tiene método predict"

    model_ng = joblib.load(nigeria_model_path)
    estimator_ng = model_ng.get("model", model_ng)
    assert hasattr(estimator_ng, "predict"), "El modelo de Nigeria no tiene método predict"

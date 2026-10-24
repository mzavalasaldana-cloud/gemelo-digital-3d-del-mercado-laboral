# -*- coding: utf-8 -*-
"""
Entrenamiento y Benchmarking Oficial del Motor de IA sobre Microdatos Reales
=============================================================================
Este script entrena y evalúa competitivamente los modelos de Machine Learning:
  - Regresión Logística L2 (Pipeline con StandardScaler + sample_weight)
  - Random Forest (100 Trees)
  - HistGradientBoosting
  - XGBoost Classifier
  - LightGBM Classifier
  - CatBoost Classifier
  - MLP Neural Net (Pipeline con StandardScaler)

Sobre las encuestas laborales reales oficiales:
  - India PLFS 2024 (MoSPI, 163,973 observaciones ocupadas)
  - Nigeria NLFS 2023 Q3 (NBS, 18,808 observaciones ocupadas)

Garantías Metodológicas y de Integridad:
1. Partición por cluster de hogar: 20% como prueba final (GroupShuffleSplit, random_state=42).
2. En el 80% restante: StratifiedGroupKFold completo de 5 pliegues (los 5 pliegues).
3. Reporte de media ± DE de la validación cruzada y métricas en la prueba final.
4. Regla del ganador: mayor AUC medio en validación cruzada; si la diferencia es <0.5 puntos
   de AUC, gana el de menor Brier Score. Sin textos fijos ni inventados.
5. StandardScaler en Pipeline para Regresión Logística y MLP.
6. Uso de sample_weight en todos los modelos que lo admiten (indicado explícitamente en la tabla).
7. Importancia de variables con permutation_importance del modelo ganador sobre la prueba final.
8. Eliminación de sufijos de versión tipo "v3.4".
9. Determinismo estricto (semilla 42 en todos los procesos estocásticos).
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, brier_score_loss, confusion_matrix, roc_curve, precision_recall_curve
)

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    xgb = None
    HAS_XGB = False

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    lgb = None
    HAS_LGB = False

try:
    import catboost as cb
    HAS_CATBOOST = True
except ImportError:
    cb = None
    HAS_CATBOOST = False

try:
    import pyreadstat
    HAS_PYREADSTAT = True
except ImportError:
    pyreadstat = None
    HAS_PYREADSTAT = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("entrenar_motor_ia")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs", "motor_ia")
MODELS_DIR = os.path.join(BASE_DIR, "models_store")
MICRODATA_DIR = os.path.join(BASE_DIR, "data", "microdatos_reales")

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


# -----------------------------------------------------------------------------
# 1. Armonización de Microdatos Reales
# -----------------------------------------------------------------------------

def harmonize_india_plfs(df: pd.DataFrame) -> pd.DataFrame:
    """Armoniza microdatos India PLFS 2024 (cperv1.csv)."""
    mask = (df['Age'] >= 15) & (df['Principal_Status_Code'].isin([11, 12, 21, 31, 41, 51]))
    df_emp = df[mask].copy()

    same_ns = df_emp['Ns_Count_Sector_Stratum_Substratum_Subsample'] == df_emp['Ns_Count_Sector_Stratum_Substratum']
    df_emp['sample_weight'] = np.where(same_ns, df_emp['Subsample_Multiplier'] / 100.0, df_emp['Subsample_Multiplier'] / 200.0)

    is_helper = df_emp['Principal_Status_Code'] == 21
    is_self = df_emp['Principal_Status_Code'].isin([11, 12])
    is_inf_ent = df_emp['Principal_Enterprise_Type'].isin([1, 2, 3, 4, 12, 19, '01', '02', '03', '04', '12', '19'])
    is_wage = df_emp['Principal_Status_Code'].isin([31, 41, 51])
    no_soc = df_emp['Principal_Social_Security'].astype(str).str.strip().isin(['8', '8.0'])

    df_emp['es_informal'] = (is_helper | (is_self & is_inf_ent) | (is_wage & no_soc)).astype(int)
    df_emp['es_formal'] = 1 - df_emp['es_informal']
    df_emp['ESTADO_LABORAL'] = df_emp['es_formal']

    df_emp['household_id'] = df_emp['FSU'].astype(str) + '_' + df_emp['Sample_Household_Number'].astype(str)

    df_emp['pais'] = 'INDIA'
    df_emp['edad'] = df_emp['Age'].astype(float)
    df_emp['sexo'] = df_emp['Sex'].astype(int)
    df_emp['es_mujer'] = (df_emp['Sex'] == 2).astype(int)
    df_emp['genero'] = np.where(df_emp['es_mujer'] == 1, 'Mujer', 'Hombre')
    df_emp['anos_educacion'] = pd.to_numeric(df_emp['Years_Formal_Education'], errors='coerce').fillna(0).clip(0, 25)
    df_emp['zona_rural'] = (df_emp['Sector'] == 1).astype(int)
    df_emp['zona'] = np.where(df_emp['zona_rural'] == 1, 'Rural', 'Urbana')
    
    hour_cols = [f'Day{i}_Total_Hours' for i in range(1, 8) if f'Day{i}_Total_Hours' in df_emp.columns]
    if hour_cols:
        df_emp['horas_semana'] = df_emp[hour_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1).clip(0, 112)
    else:
        df_emp['horas_semana'] = 40.0

    sal_earn = pd.to_numeric(df_emp.get('CWS_Earnings_Salaried', 0), errors='coerce').fillna(0)
    self_earn = pd.to_numeric(df_emp.get('CWS_Earnings_SelfEmployed', 0), errors='coerce').fillna(0)
    df_emp['ingreso_laboral'] = (sal_earn + self_earn).clip(lower=0)

    def map_nic(code):
        if pd.isna(code): return 'Otros Servicios'
        try:
            val = int(str(int(code)).zfill(5)[:2])
            if 1 <= val <= 3: return 'Agricultura'
            if 10 <= val <= 33: return 'Manufactura'
            if 41 <= val <= 43: return 'Construcción'
            if 45 <= val <= 47: return 'Comercio'
            if 49 <= val <= 53: return 'Transporte'
            if 84 <= val <= 88: return 'Servicios Públicos/Salud/Educación'
            return 'Otros Servicios'
        except Exception:
            return 'Otros Servicios'

    df_emp['sector_actividad'] = df_emp['Principal_Industry_Code'].apply(map_nic)
    df_emp['estado_civil'] = pd.to_numeric(df_emp.get('Marital_Status', 1), errors='coerce').fillna(1).astype(int)

    out_cols = [
        'pais', 'es_formal', 'es_informal', 'ESTADO_LABORAL',
        'edad', 'sexo', 'es_mujer', 'genero', 'anos_educacion',
        'zona_rural', 'zona', 'horas_semana', 'ingreso_laboral',
        'sector_actividad', 'estado_civil', 'sample_weight', 'household_id'
    ]
    return df_emp[out_cols]


def harmonize_nigeria_nlfs(df: pd.DataFrame) -> pd.DataFrame:
    """Armoniza microdatos Nigeria NLFS 2023 Q3 (NLFS_2023Q3_INDIVIDUAL.sav)."""
    mask = (df['dc5'] >= 15) & (df['mjj4'].notnull())
    df15 = df[mask].copy()

    df15['sample_weight'] = df15['weight_nlfs_q4'].fillna(1.0).astype(float)

    is_helper = df15['mjj4'].isin([3.0, 5.0])
    is_own_inf = (df15['mjj4'] == 2.0) & (df15['mjj9c'] != 1.0)
    is_emp = df15['mjj4'].isin([1.0, 4.0])

    has_contrib = (df15['mjj8l_1'] == 1.0) | (df15['mjj8l_2'] == 1.0)
    no_resp = (df15['mjj8l_1'].isna() | df15['mjj8l_1'].isin([97.0, 99.0])) & (df15['mjj8l_2'].isna() | df15['mjj8l_2'].isin([97.0, 99.0]))
    has_leave = (df15['mjj8m'] == 1.0) & (df15['mjj8n'] == 1.0)

    is_formal_emp = is_emp & (has_contrib | (no_resp & has_leave))
    df15['es_informal'] = (is_helper | is_own_inf | (is_emp & ~is_formal_emp)).astype(int)
    df15['es_formal'] = 1 - df15['es_informal']
    df15['ESTADO_LABORAL'] = df15['es_formal']

    df15['household_id'] = df15['interview_key'].astype(str)

    df15['pais'] = 'NIGERIA'
    df15['edad'] = df15['dc5'].astype(float)
    df15['sexo'] = df15['dc3'].astype(int)
    df15['es_mujer'] = (df15['dc3'] == 2.0).astype(int)
    df15['genero'] = np.where(df15['es_mujer'] == 1, 'Mujer', 'Hombre')
    
    ed_map = {1.0: 0, 2.0: 6, 3.0: 9, 4.0: 12, 5.0: 14, 6.0: 16, 7.0: 18}
    df15['anos_educacion'] = df15['ed6'].map(ed_map).fillna(0).astype(float)
    
    df15['zona_rural'] = (df15['id5_sector'] == 2.0).astype(int)
    df15['zona'] = np.where(df15['zona_rural'] == 1, 'Rural', 'Urbana')

    df15['horas_semana'] = 42.0
    df15['ingreso_laboral'] = 0.0

    def map_isic(sec):
        if pd.isna(sec): return 'Otros Servicios'
        val = int(sec)
        if val == 1: return 'Agricultura'
        if val in [2, 3, 4, 5]: return 'Manufactura'
        if val == 6: return 'Construcción'
        if val in [7, 9]: return 'Comercio'
        if val == 8: return 'Transporte'
        if val in [15, 16]: return 'Servicios Públicos/Salud/Educación'
        return 'Otros Servicios'

    df15['sector_actividad'] = df15['mjj3ccleansection'].apply(map_isic)
    df15['estado_civil'] = 1

    out_cols = [
        'pais', 'es_formal', 'es_informal', 'ESTADO_LABORAL',
        'edad', 'sexo', 'es_mujer', 'genero', 'anos_educacion',
        'zona_rural', 'zona', 'horas_semana', 'ingreso_laboral',
        'sector_actividad', 'estado_civil', 'sample_weight', 'household_id'
    ]
    return df15[out_cols]


# -----------------------------------------------------------------------------
# 2. Configuración de Modelos y Soporte de Ponderadores
# -----------------------------------------------------------------------------

def build_model_catalog() -> Dict[str, Dict[str, Any]]:
    """Construye el catálogo de modelos competitivos con hiperparámetros reproducibles."""
    catalog = {}

    # 1. Regresión Logística L2 con StandardScaler en Pipeline
    catalog["Regresión Logística L2"] = {
        "factory": lambda: Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=500, random_state=42))
        ]),
        "supports_sample_weight": True,
        "fit_kw": lambda w: {"clf__sample_weight": w},
        "weight_note": "Sí (en paso clasificador del Pipeline)"
    }

    # 2. Random Forest
    catalog["Random Forest (100 Trees)"] = {
        "factory": lambda: RandomForestClassifier(n_estimators=100, max_depth=7, random_state=42, n_jobs=2),
        "supports_sample_weight": True,
        "fit_kw": lambda w: {"sample_weight": w},
        "weight_note": "Sí"
    }

    # 3. HistGradientBoosting
    catalog["HistGradientBoosting"] = {
        "factory": lambda: HistGradientBoostingClassifier(max_iter=100, max_depth=5, random_state=42),
        "supports_sample_weight": True,
        "fit_kw": lambda w: {"sample_weight": w},
        "weight_note": "Sí"
    }

    # 4. XGBoost Classifier (sin versiones arbitrarias)
    if HAS_XGB:
        catalog["XGBoost Classifier"] = {
            "factory": lambda: xgb.XGBClassifier(
                n_estimators=100, max_depth=5, learning_rate=0.08,
                eval_metric="logloss", random_state=42, n_jobs=2
            ),
            "supports_sample_weight": True,
            "fit_kw": lambda w: {"sample_weight": w},
            "weight_note": "Sí"
        }

    # 5. LightGBM Classifier
    if HAS_LGB:
        catalog["LightGBM Classifier"] = {
            "factory": lambda: lgb.LGBMClassifier(
                n_estimators=100, max_depth=5, learning_rate=0.08,
                random_state=42, n_jobs=2, verbose=-1
            ),
            "supports_sample_weight": True,
            "fit_kw": lambda w: {"sample_weight": w},
            "weight_note": "Sí"
        }

    # 6. CatBoost Classifier
    if HAS_CATBOOST:
        catalog["CatBoost Classifier"] = {
            "factory": lambda: cb.CatBoostClassifier(
                iterations=100, depth=5, learning_rate=0.08,
                verbose=0, random_seed=42
            ),
            "supports_sample_weight": True,
            "fit_kw": lambda w: {"sample_weight": w},
            "weight_note": "Sí"
        }

    # 7. Red Neuronal MLP con StandardScaler en Pipeline
    catalog["MLP Neural Net"] = {
        "factory": lambda: Pipeline([
            ("scaler", StandardScaler()),
            ("clf", MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=150, random_state=42))
        ]),
        "supports_sample_weight": False,
        "fit_kw": lambda w: {},
        "weight_note": "No (limitación de scikit-learn MLPClassifier)"
    }

    return catalog


# -----------------------------------------------------------------------------
# 3. Pipeline de Validación Cruzada Agrupada y Ponderada (5 Pliegues) + Prueba Final
# -----------------------------------------------------------------------------

def evaluate_and_benchmark(df_h: pd.DataFrame, country_code: str) -> Dict[str, Any]:
    """
    Ejecuta el protocolo de validación real:
    1. Partición 20% hogares como prueba final (GroupShuffleSplit, random_state=42).
    2. En el 80% restante, StratifiedGroupKFold completo de 5 pliegues.
    3. Evaluación en prueba final y selección de ganador por regla determinista:
       - Mayor AUC medio de validación cruzada.
       - Si la diferencia de AUC medio es < 0.5 puntos, gana el de menor Brier Score.
    4. Permutation importance del ganador sobre la prueba final.
    """
    logger.info(f"[{country_code}] Iniciando protocolo de validación con {len(df_h):,} observaciones...")

    feature_cols = ['edad', 'es_mujer', 'anos_educacion', 'zona_rural', 'horas_semana', 'sector_actividad']
    X_raw = df_h[feature_cols].copy()
    X = pd.get_dummies(X_raw, drop_first=True)
    feature_names = X.columns.tolist()

    y = df_h['es_informal'].values
    w = df_h['sample_weight'].values
    groups = df_h['household_id'].values

    # 1. Partición 80% Train+Val / 20% Test Final por Cluster de Hogares
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_val_idx, test_idx = next(gss.split(X, y, groups))

    # Comprobación estricta de no fuga en prueba final
    overlap_test = len(set(groups[train_val_idx]).intersection(set(groups[test_idx])))
    if overlap_test > 0:
        raise RuntimeError(f"Fuga detectada: {overlap_test} hogares compartidos con el conjunto de prueba final!")

    X_tv, y_tv, w_tv, grp_tv = X.iloc[train_val_idx], y[train_val_idx], w[train_val_idx], groups[train_val_idx]
    X_test, y_test, w_test = X.iloc[test_idx], y[test_idx], w[test_idx]

    logger.info(f"[{country_code}] Muestra Train+Val: {len(X_tv):,} obs ({len(set(grp_tv)):,} hogares) | Test Final: {len(X_test):,} obs ({len(set(groups[test_idx])):,} hogares)")

    # 2. StratifiedGroupKFold de 5 pliegues COMPLETO sobre el 80% Train+Val
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    cv_splits = list(sgkf.split(X_tv, y_tv, grp_tv))
    assert len(cv_splits) == 5, f"Se esperaban 5 pliegues, obtenidos {len(cv_splits)}"

    # Verificar no fuga inter-pliegues
    for f_idx, (f_tr, f_va) in enumerate(cv_splits):
        f_overlap = len(set(grp_tv[f_tr]).intersection(set(grp_tv[f_va])))
        if f_overlap > 0:
            raise RuntimeError(f"Fuga en pliegue CV {f_idx + 1}: {f_overlap} hogares compartidos!")

    catalog = build_model_catalog()
    models_benchmark = {}
    fitted_test_models = {}

    for name, cfg in catalog.items():
        logger.info(f"[{country_code}] Entrenando y evaluando en 5 pliegues CV: {name}...")

        # Métricas por pliegue
        fold_accs, fold_precs, fold_recs, fold_f1s, fold_aucs, fold_briers = [], [], [], [], [], []
        fold_w_f1s, fold_w_aucs = [], []
        fold_m_f1s, fold_m_aucs = [], []

        cv_t0 = time.perf_counter()
        for f_idx, (f_tr_idx, f_va_idx) in enumerate(cv_splits):
            f_X_tr, f_y_tr, f_w_tr = X_tv.iloc[f_tr_idx], y_tv[f_tr_idx], w_tv[f_tr_idx]
            f_X_va, f_y_va, f_w_va = X_tv.iloc[f_va_idx], y_tv[f_va_idx], w_tv[f_va_idx]

            fold_model = cfg["factory"]()
            fit_kwargs = cfg["fit_kw"](f_w_tr)
            fold_model.fit(f_X_tr, f_y_tr, **fit_kwargs)

            f_preds = fold_model.predict(f_X_va)
            if hasattr(fold_model, "predict_proba"):
                f_probs = fold_model.predict_proba(f_X_va)[:, 1]
            else:
                f_probs = f_preds

            f_acc = accuracy_score(f_y_va, f_preds, sample_weight=f_w_va) * 100.0
            f_prec = precision_score(f_y_va, f_preds, sample_weight=f_w_va, zero_division=0) * 100.0
            f_rec = recall_score(f_y_va, f_preds, sample_weight=f_w_va, zero_division=0) * 100.0
            f_f1 = f1_score(f_y_va, f_preds, sample_weight=f_w_va, zero_division=0) * 100.0
            f_auc = roc_auc_score(f_y_va, f_probs, sample_weight=f_w_va) * 100.0
            f_brier = brier_score_loss(f_y_va, f_probs, sample_weight=f_w_va)

            fold_accs.append(f_acc)
            fold_precs.append(f_prec)
            fold_recs.append(f_rec)
            fold_f1s.append(f_f1)
            fold_aucs.append(f_auc)
            fold_briers.append(f_brier)

            # Desagregación por sexo en validación
            is_w = f_X_va['es_mujer'] == 1
            if is_w.sum() > 0:
                fold_w_f1s.append(f1_score(f_y_va[is_w], f_preds[is_w], sample_weight=f_w_va[is_w], zero_division=0) * 100.0)
                fold_w_aucs.append(roc_auc_score(f_y_va[is_w], f_probs[is_w], sample_weight=f_w_va[is_w]) * 100.0)
            
            is_m = ~is_w
            if is_m.sum() > 0:
                fold_m_f1s.append(f1_score(f_y_va[is_m], f_preds[is_m], sample_weight=f_w_va[is_m], zero_division=0) * 100.0)
                fold_m_aucs.append(roc_auc_score(f_y_va[is_m], f_probs[is_m], sample_weight=f_w_va[is_m]) * 100.0)

        cv_duration = time.perf_counter() - cv_t0

        # Ajuste del modelo sobre el 80% Train+Val y evaluación en la prueba final del 20%
        final_test_model = cfg["factory"]()
        fit_kw_tv = cfg["fit_kw"](w_tv)
        t_fit0 = time.perf_counter()
        final_test_model.fit(X_tv, y_tv, **fit_kw_tv)
        fit_time_sec = time.perf_counter() - t_fit0

        t_inf0 = time.perf_counter()
        test_preds = final_test_model.predict(X_test)
        latency_ms = (time.perf_counter() - t_inf0) * 1000.0 / len(X_test)

        if hasattr(final_test_model, "predict_proba"):
            test_probs = final_test_model.predict_proba(X_test)[:, 1]
        else:
            test_probs = test_preds

        te_acc = float(accuracy_score(y_test, test_preds, sample_weight=w_test) * 100.0)
        te_prec = float(precision_score(y_test, test_preds, sample_weight=w_test, zero_division=0) * 100.0)
        te_rec = float(recall_score(y_test, test_preds, sample_weight=w_test, zero_division=0) * 100.0)
        te_f1 = float(f1_score(y_test, test_preds, sample_weight=w_test, zero_division=0) * 100.0)
        te_auc = float(roc_auc_score(y_test, test_probs, sample_weight=w_test) * 100.0)
        te_brier = float(brier_score_loss(y_test, test_probs, sample_weight=w_test))

        # Desagregado por sexo en prueba final
        is_w_te = X_test['es_mujer'] == 1
        te_w_f1 = float(f1_score(y_test[is_w_te], test_preds[is_w_te], sample_weight=w_test[is_w_te], zero_division=0) * 100.0)
        te_w_auc = float(roc_auc_score(y_test[is_w_te], test_probs[is_w_te], sample_weight=w_test[is_w_te]) * 100.0)

        is_m_te = ~is_w_te
        te_m_f1 = float(f1_score(y_test[is_m_te], test_preds[is_m_te], sample_weight=w_test[is_m_te], zero_division=0) * 100.0)
        te_m_auc = float(roc_auc_score(y_test[is_m_te], test_probs[is_m_te], sample_weight=w_test[is_m_te]) * 100.0)

        cm = confusion_matrix(y_test, test_preds, sample_weight=w_test)
        fpr, tpr, _ = roc_curve(y_test, test_probs, sample_weight=w_test)
        pr_p, pr_r, _ = precision_recall_curve(y_test, test_probs, sample_weight=w_test)

        # Consolidar métricas completas
        models_benchmark[name] = {
            "name": name,
            "supports_sample_weight": cfg["supports_sample_weight"],
            "sample_weight_note": cfg["weight_note"],
            # 1. Validación Cruzada (media ± DE de los 5 pliegues)
            "cv_metrics": {
                "roc_auc_mean": round(float(np.mean(fold_aucs)), 2),
                "roc_auc_std": round(float(np.std(fold_aucs)), 2),
                "f1_score_mean": round(float(np.mean(fold_f1s)), 2),
                "f1_score_std": round(float(np.std(fold_f1s)), 2),
                "brier_score_mean": round(float(np.mean(fold_briers)), 4),
                "brier_score_std": round(float(np.std(fold_briers)), 4),
                "accuracy_mean": round(float(np.mean(fold_accs)), 2),
                "accuracy_std": round(float(np.std(fold_accs)), 2),
                "precision_mean": round(float(np.mean(fold_precs)), 2),
                "precision_std": round(float(np.std(fold_precs)), 2),
                "recall_mean": round(float(np.mean(fold_recs)), 2),
                "recall_std": round(float(np.std(fold_recs)), 2),
                "women_f1_mean": round(float(np.mean(fold_w_f1s)), 2),
                "women_auc_mean": round(float(np.mean(fold_w_aucs)), 2),
                "men_f1_mean": round(float(np.mean(fold_m_f1s)), 2),
                "men_auc_mean": round(float(np.mean(fold_m_aucs)), 2),
            },
            # 2. Prueba Final (20% holdout)
            "test_metrics": {
                "accuracy": round(te_acc, 2),
                "precision": round(te_prec, 2),
                "recall": round(te_rec, 2),
                "f1_score": round(te_f1, 2),
                "roc_auc": round(te_auc, 2),
                "brier_score": round(te_brier, 4),
                "latency_ms_per_obs": round(latency_ms, 5),
                "training_time_sec": round(fit_time_sec, 2),
                "metrics_women": {"f1_score": round(te_w_f1, 2), "roc_auc": round(te_w_auc, 2)},
                "metrics_men": {"f1_score": round(te_m_f1, 2), "roc_auc": round(te_m_auc, 2)},
                "confusion_matrix": cm.tolist(),
                "roc_curve": {"fpr": fpr[::max(1, len(fpr)//50)].tolist(), "tpr": tpr[::max(1, len(tpr)//50)].tolist()},
            },
            # Campos retrocompatibles con la API del frontend
            "accuracy": round(te_acc, 2),
            "precision": round(te_prec, 2),
            "recall": round(te_rec, 2),
            "f1_score": round(te_f1, 2),
            "roc_auc": round(te_auc, 2),
            "brier_score": round(te_brier, 4),
            "latency_ms_per_obs": round(latency_ms, 5),
            "training_time_sec": round(fit_time_sec, 2),
            "metrics_women": {"f1_score": round(te_w_f1, 2), "roc_auc": round(te_w_auc, 2)},
            "metrics_men": {"f1_score": round(te_m_f1, 2), "roc_auc": round(te_m_auc, 2)},
            "confusion_matrix": cm.tolist(),
            "roc_curve": {"fpr": fpr[::max(1, len(fpr)//50)].tolist(), "tpr": tpr[::max(1, len(tpr)//50)].tolist()},
        }
        fitted_test_models[name] = final_test_model

    # 4. REGLA DEL GANADOR DETERMINISTA:
    # Mayor AUC medio de la validación cruzada; si la diferencia es < 0.5 puntos, gana el de menor Brier.
    max_cv_auc = max(m["cv_metrics"]["roc_auc_mean"] for m in models_benchmark.values())
    candidates = [
        name for name, m in models_benchmark.items()
        if (max_cv_auc - m["cv_metrics"]["roc_auc_mean"]) < 0.50
    ]

    if len(candidates) > 1:
        # Entre los modelos dentro del margen de 0.5 puntos de AUC, desempatar por menor Brier Score medio en CV
        winner_name = min(candidates, key=lambda n: models_benchmark[n]["cv_metrics"]["brier_score_mean"])
        winner_reason = f"Menor Brier Score ({models_benchmark[winner_name]['cv_metrics']['brier_score_mean']:.4f}) por empate técnico en AUC CV (<0.50 p.p. respecto al máximo {max_cv_auc:.2f}%)"
    else:
        winner_name = candidates[0]
        winner_reason = f"Mayor AUC-ROC medio en validación cruzada ({models_benchmark[winner_name]['cv_metrics']['roc_auc_mean']:.2f}%)"

    logger.info(f"[{country_code}] Modelo ganador seleccionado según regla: {winner_name} ({winner_reason})")

    # 5. Permutation Importance del modelo ganador sobre la PRUEBA FINAL
    winner_test_model = fitted_test_models[winner_name]
    logger.info(f"[{country_code}] Calculando permutation_importance del ganador ({winner_name}) en prueba final...")
    
    perm_sample_weight = w_test if catalog[winner_name]["supports_sample_weight"] else None
    perm = permutation_importance(
        winner_test_model, X_test, y_test,
        n_repeats=5, random_state=42,
        sample_weight=perm_sample_weight,
        n_jobs=2
    )

    perm_raw = {}
    pos_imps = np.maximum(0, perm.importances_mean)
    tot_pos = np.sum(pos_imps) or 1.0
    normalized_importances = {}

    for idx, f_name in enumerate(feature_names):
        perm_raw[f_name] = {
            "mean": round(float(perm.importances_mean[idx]), 5),
            "std": round(float(perm.importances_std[idx]), 5),
        }
        normalized_importances[f_name] = round(float(pos_imps[idx] / tot_pos * 100.0), 2)

    # Ordenar características por importancia
    normalized_importances = dict(sorted(normalized_importances.items(), key=lambda x: x[1], reverse=True))

    # 6. Re-entrenar modelo campeón sobre el 100% de datos con sample_weight para inferencia en producción
    logger.info(f"[{country_code}] Serializando modelo campeón ({winner_name}) sobre el 100% de datos...")
    prod_model = catalog[winner_name]["factory"]()
    fit_kw_prod = catalog[winner_name]["fit_kw"](w)
    prod_model.fit(X, y, **fit_kw_prod)

    model_dump_data = {
        "country": country_code,
        "champion_algorithm": winner_name,
        "selection_rule": winner_reason,
        "model": prod_model,
        "feature_names": feature_names,
        "metrics": models_benchmark[winner_name],
        "feature_importances": normalized_importances,
        "permutation_importance_details": perm_raw,
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_observations": len(df_h),
        "unweighted_informal_count": int((y == 1).sum()),
        "unweighted_formal_count": int((y == 0).sum()),
        "weighted_informality_rate": round(float((y * w).sum() / w.sum() * 100.0), 2),
    }

    champion_path = os.path.join(MODELS_DIR, f"model_champion_{country_code.lower()}.joblib")
    joblib.dump(model_dump_data, champion_path)
    logger.info(f"[{country_code}] Modelo campeón persistido en {champion_path}")

    # Estructura del JSON de resultados
    payload = {
        "country": country_code,
        "champion_name": winner_name,
        "champion_rule": winner_reason,
        "champion_metrics": models_benchmark[winner_name],
        "models_benchmark": models_benchmark,
        "feature_importances": normalized_importances,
        "permutation_importance_details": perm_raw,
        "total_observations": len(df_h),
        "train_val_observations": len(X_tv),
        "test_observations": len(X_test),
        "weighted_informality_rate": round(float((y * w).sum() / w.sum() * 100.0), 2),
    }

    json_path = os.path.join(OUTPUTS_DIR, f"metricas_modelos_{country_code.lower()}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    logger.info(f"[{country_code}] Métricas completas guardadas en {json_path}")

    return payload


# -----------------------------------------------------------------------------
# 4. Generación de Tablas Oficiales de Rendimiento (CSV y Markdown)
# -----------------------------------------------------------------------------

def generate_comparison_tables(india_res: Dict[str, Any], nigeria_res: Dict[str, Any]):
    """Genera tabla_desempeno_modelos.csv y .md con media ± DE en CV y prueba final."""
    csv_rows = []
    
    country_tuples = [
        ("India (PLFS 2024)", india_res),
        ("Nigeria (NLFS 2023 Q3)", nigeria_res),
    ]

    for country_label, res in country_tuples:
        winner = res["champion_name"]
        for mod_name, mod_data in res["models_benchmark"].items():
            cv = mod_data["cv_metrics"]
            te = mod_data["test_metrics"]
            
            is_winner = (mod_name == winner)
            winner_col = f"Sí ({res['champion_rule']})" if is_winner else "No"

            csv_rows.append({
                "País": country_label,
                "Modelo": mod_name,
                "Acepta sample_weight": mod_data["sample_weight_note"],
                "AUC-ROC CV (media ± DE)": f"{cv['roc_auc_mean']:.2f} ± {cv['roc_auc_std']:.2f}",
                "AUC-ROC Test (%)": te["roc_auc"],
                "F1-Score CV (media ± DE)": f"{cv['f1_score_mean']:.2f} ± {cv['f1_score_std']:.2f}",
                "F1-Score Test (%)": te["f1_score"],
                "Accuracy CV (media ± DE)": f"{cv['accuracy_mean']:.2f} ± {cv['accuracy_std']:.2f}",
                "Accuracy Test (%)": te["accuracy"],
                "Precision CV (media ± DE)": f"{cv['precision_mean']:.2f} ± {cv['precision_std']:.2f}",
                "Precision Test (%)": te["precision"],
                "Recall CV (media ± DE)": f"{cv['recall_mean']:.2f} ± {cv['recall_std']:.2f}",
                "Recall Test (%)": te["recall"],
                "Brier Score CV (media ± DE)": f"{cv['brier_score_mean']:.4f} ± {cv['brier_score_std']:.4f}",
                "Brier Score Test": te["brier_score"],
                "F1 Mujeres Test (%)": te["metrics_women"]["f1_score"],
                "AUC Mujeres Test (%)": te["metrics_women"]["roc_auc"],
                "F1 Hombres Test (%)": te["metrics_men"]["f1_score"],
                "AUC Hombres Test (%)": te["metrics_men"]["roc_auc"],
                "Latencia Test (ms)": te["latency_ms_per_obs"],
                "Ganador": winner_col
            })

    df_table = pd.DataFrame(csv_rows)
    csv_path = os.path.join(OUTPUTS_DIR, "tabla_desempeno_modelos.csv")
    df_table.to_csv(csv_path, index=False, encoding="utf-8")
    logger.info(f"Tabla de desempeño guardada en CSV: {csv_path}")

    # Generar versión Markdown
    md_lines = [
        "# Tabla Oficial de Benchmarking y Validación de Modelos de IA",
        "**Fecha de generación:** " + time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "**Metodología:** Partición 20% hogares en prueba final (GroupShuffleSplit, random_state=42) y 5-Fold StratifiedGroupKFold sobre el 80% restante.",
        "**Regla de Selección del Ganador:** Mayor AUC-ROC medio en validación cruzada; si la diferencia es <0.50 puntos, desempata por menor Brier Score.",
        "",
        df_table.to_markdown(index=False),
        "",
        "### Notas Técnicas Metodológicas:",
        "- **sample_weight:** Todos los modelos basados en árboles y la Regresión Logística (mediante paso en Pipeline) fueron ajustados y evaluados utilizando ponderadores de diseño muestral oficial.",
        "- **MLPClassifier:** No admite `sample_weight` en la implementación oficial de scikit-learn; se entrenó con ponderación uniforme tras estandarización con `StandardScaler`.",
        "- **Sin Fuga Intrahogar:** Las particiones respetaron estrictamente la agrupación familiar (`household_id`).",
        "- **Importancia de Características:** Calculada mediante `permutation_importance` (5 permutaciones por variable) del modelo ganador exclusivamente sobre la prueba final independiente."
    ]

    md_path = os.path.join(OUTPUTS_DIR, "tabla_desempeno_modelos.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    logger.info(f"Tabla de desempeño guardada en Markdown: {md_path}")


# -----------------------------------------------------------------------------
# 5. Función Principal
# -----------------------------------------------------------------------------

def find_microdata_file(country: str, pattern: str) -> str:
    """Busca recursivamente archivos de microdatos ignorando carpetas archivadas."""
    country_dir = os.path.join(MICRODATA_DIR, country.lower())
    for root, dirs, files in os.walk(country_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "_archivado"]
        for f in files:
            if pattern.lower() in f.lower():
                return os.path.join(root, f)
    raise FileNotFoundError(f"No se encontró archivo con patrón '{pattern}' en {country_dir}")


def main():
    logger.info("================================================================================")
    logger.info(" EJECUTANDO ENTRENAMIENTO Y BENCHMARKING DE MODELOS DE MACHINE LEARNING (OIT)  ")
    logger.info("================================================================================")

    # 1. Cargar India PLFS 2024
    india_csv = find_microdata_file("india", "cperv1.csv")
    logger.info(f"Cargando {india_csv}...")
    df_raw_in = pd.read_csv(india_csv, low_memory=False)
    df_india = harmonize_india_plfs(df_raw_in)
    del df_raw_in

    # 2. Cargar Nigeria NLFS 2023 Q3
    nigeria_sav = find_microdata_file("nigeria", "NLFS_2023Q3_INDIVIDUAL.sav")
    logger.info(f"Cargando {nigeria_sav}...")
    df_raw_ng, _ = pyreadstat.read_sav(nigeria_sav, encoding="latin1")
    df_nigeria = harmonize_nigeria_nlfs(df_raw_ng)
    del df_raw_ng

    # 3. Ejecutar benchmarking para India y Nigeria
    res_india = evaluate_and_benchmark(df_india, "INDIA")
    res_nigeria = evaluate_and_benchmark(df_nigeria, "NIGERIA")

    # 4. Generar tablas consolidadas
    generate_comparison_tables(res_india, res_nigeria)

    logger.info("================================================================================")
    logger.info(" ENTRENAMIENTO Y VALIDACIÓN COMPLETADOS EXITOSAMENTE                           ")
    logger.info(f" Ganador India:   {res_india['champion_name']} ({res_india['champion_rule']})")
    logger.info(f" Ganador Nigeria: {res_nigeria['champion_name']} ({res_nigeria['champion_rule']})")
    logger.info("================================================================================")


if __name__ == "__main__":
    main()

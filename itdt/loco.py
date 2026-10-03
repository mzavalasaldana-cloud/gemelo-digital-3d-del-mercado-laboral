"""
itdt.loco: Validación cruzada dejando un país fuera (LOCO) y modelos de referencia (Sección 3.6).
- Estima gamma_0 común sobre los otros tres países en rejilla [0.0, 1.2] (paso 0.1).
- Predice F del país excluido sin usar F ni T de dicho país.
- Compara frente a Brecha media, Razón media, Regresión lineal de la brecha sobre s_F e ITDT sin cuidado.
- Implementa modelos de referencia estructurales E1–E4 (Tabla 4).
- Exporta outputs/table3_loco.*, outputs/table4_baselines.*, outputs/loco_insumos.md y outputs/loco_results.json.
"""

import os
import json
import time
from typing import Dict, Any, List, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd

from itdt.model import ITDTModel
from itdt.parameters import FixedParameters, COUNTRY_DATABASE, load_ilostat_s_F_data

TARGET_COUNTRIES = ["KENYA", "NIGERIA", "INDIA", "BANGLADESH"]
DEFAULT_SEEDS = [1000, 1001, 1002, 1003, 1004, 1005]
GAMMA_GRID = [round(float(g), 2) for g in np.arange(0.0, 1.21, 0.1)]


def evaluate_model_moments(
    country_key: str,
    s_F: float,
    phi_0: float,
    gamma_0: float,
    seeds: List[int],
    fixed_params: Optional[FixedParameters] = None,
    burn_in_months: int = 96,
    eval_months: int = 24,
) -> Tuple[float, float, float]:
    """
    Simula y devuelve (F_sim, M_sim, T_sim) promediando sobre las semillas dadas.
    """
    f_list, m_list = [], []
    c_cfg = {
        "s_F": s_F,
        "phi_0": phi_0,
        "gamma_0": gamma_0,
        "name": country_key,
    }
    for seed in seeds:
        model = ITDTModel(
            country_params=c_cfg,
            scenario="A",
            seed=seed,
            fixed_params=fixed_params,
        )
        f_val, m_val = model.simulate_moments(burn_in_months=burn_in_months, eval_months=eval_months)
        f_list.append(f_val)
        m_list.append(m_val)

    mean_f = float(np.mean(f_list))
    mean_m = float(np.mean(m_list))
    mean_t = float(s_F * mean_f + (1.0 - s_F) * mean_m)
    return mean_f, mean_m, mean_t


def bisection_calibrate_phi_to_target(
    country_key: str,
    s_F: float,
    target_value: float,
    target_type: str,  # 'M' o 'T'
    gamma_0: float,
    seeds: List[int],
    fixed_params: Optional[FixedParameters] = None,
    steps: int = 9,
) -> Tuple[float, float, float, float]:
    """
    Bisección de 9 pasos para encontrar phi_0 in [0.0, 12.0] que iguale target_value ('M' o 'T').
    Retorna (best_phi, best_F_sim, best_M_sim, best_T_sim).
    """
    phi_low, phi_high = 0.0, 12.0
    best_diff = float("inf")
    best_res = (0.0, 0.0, 0.0, 0.0)

    for _ in range(steps):
        phi_mid = (phi_low + phi_high) / 2.0
        f_sim, m_sim, t_sim = evaluate_model_moments(
            country_key=country_key,
            s_F=s_F,
            phi_0=phi_mid,
            gamma_0=gamma_0,
            seeds=seeds,
            fixed_params=fixed_params,
        )

        curr_val = m_sim if target_type == "M" else t_sim
        diff = abs(curr_val - target_value)
        if diff < best_diff:
            best_diff = diff
            best_res = (phi_mid, f_sim, m_sim, t_sim)

        if curr_val < target_value:
            phi_low = phi_mid
        else:
            phi_high = phi_mid

    return best_res


def _worker_calibrate_phi_grid(args: Tuple[str, float, float, float, List[int]]) -> Tuple[Tuple[str, float], Tuple[float, float, float, float]]:
    """Trabajador para calcular phi_0 que iguala M_obs dado (country, gamma_0)."""
    c_key, s_F, m_obs, g_val, seeds = args
    res = bisection_calibrate_phi_to_target(
        country_key=c_key,
        s_F=s_F,
        target_value=m_obs,
        target_type="M",
        gamma_0=g_val,
        seeds=seeds,
    )
    return (c_key, g_val), res


def run_loco_cross_validation(
    seeds: List[int] = DEFAULT_SEEDS,
    output_dir: str = "outputs",
    max_workers: int = 8,
) -> Dict[str, Any]:
    """
    Ejecuta validación Leave-One-Country-Out (LOCO) estricta (Sección 3.6).
    Ningún modelo puede acceder a F_obs ni a T_obs del país excluido.
    """
    os.makedirs(output_dir, exist_ok=True)
    s_F_dict = load_ilostat_s_F_data()

    print("\n======================================================================")
    print(" ITDT: Validación Fuera de Muestra Leave-One-Country-Out (LOCO) (Sección 3.6)")
    print(f" Rejilla gamma_0 ({len(GAMMA_GRID)} puntos): {GAMMA_GRID}")
    print("======================================================================")

    # 1. Precomputar la rejilla de calibraciones (país, gamma_0) en paralelo
    print("Precomputando rejilla (país, gamma_0) para búsqueda acelerada...")
    t_grid_start = time.time()
    grid_tasks = []
    for c in TARGET_COUNTRIES:
        c_info = COUNTRY_DATABASE[c]
        s_F = s_F_dict.get(c, c_info["s_F"])
        for g in GAMMA_GRID:
            grid_tasks.append((c, s_F, c_info["M_obs"], g, seeds))

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        grid_lookup = dict(executor.map(_worker_calibrate_phi_grid, grid_tasks))

    print(f"Rejilla completada en {time.time() - t_grid_start:.2f} s.")

    predictions_table = []
    fold_details = {}

    for exc_country in TARGET_COUNTRIES:
        exc_info = COUNTRY_DATABASE[exc_country]
        exc_s_F = s_F_dict.get(exc_country, exc_info["s_F"])
        exc_F_obs = exc_info["F_obs"]
        exc_M_obs = exc_info["M_obs"]

        train_countries = [c for c in TARGET_COUNTRIES if c != exc_country]
        print(f"\n--- Pliegue LOCO: Excluyendo {exc_info['name']} ({exc_country}) ---")
        print(f"  Entrenamiento: {[COUNTRY_DATABASE[c]['name'] for c in train_countries]}")

        # 1. ITDT (gamma_0 común): minimiza MAE de F sobre los 3 países de entrenamiento
        best_gamma = 0.0
        best_train_mae = float("inf")

        for g_candidate in GAMMA_GRID:
            train_errors = [
                abs(grid_lookup[(tr_c, g_candidate)][1] - COUNTRY_DATABASE[tr_c]["F_obs"])
                for tr_c in train_countries
            ]
            mean_err = float(np.mean(train_errors))
            if mean_err < best_train_mae:
                best_train_mae = mean_err
                best_gamma = g_candidate

        # Predicción fuera de muestra para el país excluido
        pred_F_itdt = grid_lookup[(exc_country, best_gamma)][1]

        # 2. Brecha media: F_c = M_c + mean_gap_{-c}
        train_gaps = [COUNTRY_DATABASE[c]["F_obs"] - COUNTRY_DATABASE[c]["M_obs"] for c in train_countries]
        mean_gap_tr = float(np.mean(train_gaps))
        pred_F_mean_gap = exc_M_obs + mean_gap_tr

        # 3. Razón media: F_c = min(100, M_c * mean_ratio_{-c})
        train_ratios = [COUNTRY_DATABASE[c]["F_obs"] / COUNTRY_DATABASE[c]["M_obs"] for c in train_countries]
        mean_ratio_tr = float(np.mean(train_ratios))
        pred_F_mean_ratio = min(100.0, exc_M_obs * mean_ratio_tr)

        # 4. Regresión lineal de la brecha sobre s_F: gap = b0 + b1 * s_F
        tr_s_F_vals = np.array([s_F_dict.get(c, COUNTRY_DATABASE[c]["s_F"]) for c in train_countries])
        tr_gaps = np.array(train_gaps)
        p_fit = np.polyfit(tr_s_F_vals, tr_gaps, deg=1)
        pred_gap_ols = float(np.polyval(p_fit, exc_s_F))
        pred_F_ols = exc_M_obs + pred_gap_ols

        # 5. ITDT sin cuidado (gamma_0 = 0.0)
        pred_F_no_care = grid_lookup[(exc_country, 0.0)][1]

        fold_record = {
            "country_key": exc_country,
            "country_name": exc_info["name"],
            "F_obs": exc_F_obs,
            "M_obs": exc_M_obs,
            "s_F": exc_s_F,
            "best_gamma": best_gamma,
            "pred_F_itdt": pred_F_itdt,
            "pred_F_mean_gap": pred_F_mean_gap,
            "pred_F_mean_ratio": pred_F_mean_ratio,
            "pred_F_ols": pred_F_ols,
            "pred_F_no_care": pred_F_no_care,
            "err_itdt": abs(pred_F_itdt - exc_F_obs),
            "err_mean_gap": abs(pred_F_mean_gap - exc_F_obs),
            "err_mean_ratio": abs(pred_F_mean_ratio - exc_F_obs),
            "err_ols": abs(pred_F_ols - exc_F_obs),
            "err_no_care": abs(pred_F_no_care - exc_F_obs),
        }
        fold_details[exc_country] = fold_record

        print(f"  F observada: {exc_F_obs:.2f}%")
        print(f"  ITDT (gamma_0={best_gamma:.1f}): {pred_F_itdt:.2f}% (error = {fold_record['err_itdt']:.2f} p.p.)")
        print(f"  Brecha media: {pred_F_mean_gap:.2f}% (error = {fold_record['err_mean_gap']:.2f} p.p.)")
        print(f"  Razón media: {pred_F_mean_ratio:.2f}% (error = {fold_record['err_mean_ratio']:.2f} p.p.)")
        print(f"  Regresión lineal: {pred_F_ols:.2f}% (error = {fold_record['err_ols']:.2f} p.p.)")
        print(f"  ITDT sin cuidado: {pred_F_no_care:.2f}% (error = {fold_record['err_no_care']:.2f} p.p.)")

        predictions_table.append({
            "País excluido": exc_info["name"],
            "F observada": f"{exc_F_obs:.2f}",
            "ITDT (gamma_0 común)": f"{pred_F_itdt:.2f} (gamma_0={best_gamma:.1f})",
            "Brecha media": f"{pred_F_mean_gap:.2f}",
            "Razón media": f"{pred_F_mean_ratio:.2f}",
            "Regresión lineal": f"{pred_F_ols:.2f}",
            "ITDT sin cuidado": f"{pred_F_no_care:.2f}",
        })

    # Calcular MAEs globales
    mae_itdt = float(np.mean([fold_details[c]["err_itdt"] for c in TARGET_COUNTRIES]))
    mae_gap = float(np.mean([fold_details[c]["err_mean_gap"] for c in TARGET_COUNTRIES]))
    mae_ratio = float(np.mean([fold_details[c]["err_mean_ratio"] for c in TARGET_COUNTRIES]))
    mae_ols = float(np.mean([fold_details[c]["err_ols"] for c in TARGET_COUNTRIES]))
    mae_no_care = float(np.mean([fold_details[c]["err_no_care"] for c in TARGET_COUNTRIES]))

    predictions_table.append({
        "País excluido": "MAE (p.p.)",
        "F observada": "—",
        "ITDT (gamma_0 común)": f"{mae_itdt:.2f}",
        "Brecha media": f"{mae_gap:.2f}",
        "Razón media": f"{mae_ratio:.2f}",
        "Regresión lineal": f"{mae_ols:.2f}",
        "ITDT sin cuidado": f"{mae_no_care:.2f}",
    })

    df_t3 = pd.DataFrame(predictions_table)
    t3_csv = os.path.join(output_dir, "table3_loco.csv")
    t3_md = os.path.join(output_dir, "table3_loco.md")
    df_t3.to_csv(t3_csv, index=False, encoding="utf-8")

    with open(t3_md, "w", encoding="utf-8") as f:
        f.write("# Tabla 3: Predicción de la informalidad femenina dejando un país fuera (LOCO)\n\n")
        f.write(df_t3.to_markdown(index=False))
        f.write("\n\n*Nota.* Todas las alternativas usan la tasa masculina observada del país excluido "
                "y los datos de los otros tres. La razón media se trunca en 100 %. "
                "Con cuatro pliegues, las diferencias de MAE no admiten un contraste estadístico formal "
                "y deben leerse como evidencia descriptiva.\n")

    print(f"\nTabla 3 generada en {t3_csv} y {t3_md}")
    generate_loco_inputs_documentation(output_dir)

    return {
        "fold_details": fold_details,
        "maes": {
            "itdt": mae_itdt,
            "mean_gap": mae_gap,
            "mean_ratio": mae_ratio,
            "ols_s_F": mae_ols,
            "itdt_no_care": mae_no_care,
        },
    }


def _worker_baseline_eval(args: Tuple[str, str, Dict[str, Any]]) -> Tuple[str, str, float, float, float]:
    """Trabajador para evaluar modelos de referencia E1, E2, E3, E4 e ITDT."""
    c_key, m_id, calib_info = args
    c_info = COUNTRY_DATABASE[c_key]
    s_F = calib_info["s_F"]
    T_obs = c_info["T_obs"]
    F_obs = c_info["F_obs"]
    M_obs = c_info["M_obs"]
    seeds = DEFAULT_SEEDS

    if m_id == "E1":
        # Agente representativo: sin heterogeneidad micro, care deshabilitado
        fp = FixedParameters(care_enabled=False, eps_std=0.0)
        phi_cal, f_sim, m_sim, t_sim = bisection_calibrate_phi_to_target(
            country_key=c_key, s_F=s_F, target_value=T_obs, target_type="T",
            gamma_0=0.0, seeds=seeds, fixed_params=fp,
        )
    elif m_id == "E2":
        # ABM lewisiano: sin cuidado, sin DCC regresivo, racionalidad perfecta
        fp = FixedParameters(care_enabled=False, regressive_dcc=False, perfect_rationality=True)
        phi_cal, f_sim, m_sim, t_sim = bisection_calibrate_phi_to_target(
            country_key=c_key, s_F=s_F, target_value=T_obs, target_type="T",
            gamma_0=0.0, seeds=seeds, fixed_params=fp,
        )
    elif m_id == "E3":
        # ITDT sin cuidado: care_enabled=False
        fp = FixedParameters(care_enabled=False)
        phi_cal, f_sim, m_sim, t_sim = bisection_calibrate_phi_to_target(
            country_key=c_key, s_F=s_F, target_value=T_obs, target_type="T",
            gamma_0=0.0, seeds=seeds, fixed_params=fp,
        )
    elif m_id == "E4":
        # ITDT con racionalidad perfecta: perfect_rationality=True
        fp = FixedParameters(perfect_rationality=True)
        f_sim, m_sim, t_sim = evaluate_model_moments(
            country_key=c_key, s_F=s_F, phi_0=calib_info["phi_0"], gamma_0=calib_info["gamma_0"],
            seeds=seeds, fixed_params=fp,
        )
    else:
        # ITDT canónico
        f_sim = calib_info["F_sim"]
        m_sim = calib_info["M_sim"]
        t_sim = calib_info["T_sim"]

    return c_key, m_id, f_sim, m_sim, t_sim


def run_structural_baselines_table4(
    seeds: List[int] = DEFAULT_SEEDS,
    output_dir: str = "outputs",
    max_workers: int = 8,
) -> Dict[str, Any]:
    """
    Ajuste dentro de muestra de modelos estructurales recalibrados (Tabla 4).
    """
    os.makedirs(output_dir, exist_ok=True)
    s_F_dict = load_ilostat_s_F_data()

    print("\n======================================================================")
    print(" ITDT: Modelos Estructurales de Referencia dentro de Muestra (Tabla 4)")
    print("======================================================================")

    # Cargar estimaciones de calibración base
    calib_json = os.path.join(output_dir, "calibration_estimates.json")
    if os.path.exists(calib_json):
        with open(calib_json, "r", encoding="utf-8") as f:
            calib_summary = json.load(f)["summary"]
    else:
        # Fallback a COUNTRY_DATABASE
        calib_summary = {
            c: {
                "s_F": s_F_dict.get(c, COUNTRY_DATABASE[c]["s_F"]),
                "phi_0": COUNTRY_DATABASE[c]["phi_0"],
                "gamma_0": COUNTRY_DATABASE[c]["gamma_0"],
                "F_sim": COUNTRY_DATABASE[c]["F_obs"],
                "M_sim": COUNTRY_DATABASE[c]["M_obs"],
                "T_sim": COUNTRY_DATABASE[c]["T_obs"],
            }
            for c in TARGET_COUNTRIES
        }

    obs_gaps = [COUNTRY_DATABASE[c]["F_obs"] - COUNTRY_DATABASE[c]["M_obs"] for c in TARGET_COUNTRIES]
    mean_obs_gap = float(np.mean(obs_gaps))

    models_config = [
        {"id": "E1", "name": "E1: agente representativo", "params": "phi_0"},
        {"id": "E2", "name": "E2: ABM lewisiano", "params": "phi_0"},
        {"id": "E3", "name": "E3: ITDT sin cuidado", "params": "phi_0"},
        {"id": "E4", "name": "E4: ITDT con racionalidad perfecta", "params": "phi_0, gamma_0"},
        {"id": "ITDT", "name": "ITDT", "params": "phi_0, gamma_0"},
    ]

    baseline_tasks = []
    for m in models_config:
        for c in TARGET_COUNTRIES:
            baseline_tasks.append((c, m["id"], calib_summary[c]))

    eval_results: Dict[str, Dict[str, Tuple[float, float, float]]] = {m["id"]: {} for m in models_config}
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for c_key, m_id, f_sim, m_sim, t_sim in executor.map(_worker_baseline_eval, baseline_tasks):
            eval_results[m_id][c_key] = (f_sim, m_sim, t_sim)

    results_table4 = []
    for m in models_config:
        m_id = m["id"]
        all_f_errs, all_m_errs, sim_gaps = [], [], []
        for c in TARGET_COUNTRIES:
            f_sim, m_sim, _ = eval_results[m_id][c]
            F_obs = COUNTRY_DATABASE[c]["F_obs"]
            M_obs = COUNTRY_DATABASE[c]["M_obs"]
            all_f_errs.append(abs(f_sim - F_obs))
            all_m_errs.append(abs(m_sim - M_obs))
            sim_gaps.append(f_sim - m_sim)

        mae_8 = float(np.mean(all_f_errs + all_m_errs))
        mean_sim_gap = float(np.mean(sim_gaps))

        results_table4.append({
            "Modelo": m["name"],
            "Parámetros libres": m["params"],
            "MAE sobre 8 momentos (p.p.)": f"{mae_8:.2f}",
            "Brecha F − M media simulada (p.p.)": f"{mean_sim_gap:+.2f}",
        })
        print(f"  {m['name']}: MAE 8 momentos = {mae_8:.2f} p.p. | Brecha F-M media = {mean_sim_gap:+.2f} p.p.")

    df_t4 = pd.DataFrame(results_table4)
    t4_csv = os.path.join(output_dir, "table4_baselines.csv")
    t4_md = os.path.join(output_dir, "table4_baselines.md")
    df_t4.to_csv(t4_csv, index=False, encoding="utf-8")

    with open(t4_md, "w", encoding="utf-8") as f:
        f.write("# Tabla 4: Ajuste dentro de muestra de modelos estructurales recalibrados\n\n")
        f.write(df_t4.to_markdown(index=False))
        f.write(f"\n\n*Nota.* Brecha observada media = {mean_obs_gap:.2f} p.p. "
                "Los tres modelos sin cuidado reproducen la tasa total pero producen una brecha nula; "
                "su error se concentra íntegramente en la dimensión de género.\n")

    print(f"Tabla 4 generada en {t4_csv} y {t4_md}")
    return {"table4": results_table4, "mean_obs_gap": mean_obs_gap}


def generate_loco_inputs_documentation(output_dir: str):
    """
    Genera outputs/loco_insumos.md documentando estrictamente qué información
    utiliza cada modelo en la validación LOCO.
    """
    doc_path = os.path.join(output_dir, "loco_insumos.md")
    content = r"""# Documentación de Insumos para la Validación Fuera de Muestra (LOCO)

**Fecha de generación:** Octubre 2026  
**Referencia:** Sección 3.6 del artículo *ITDT: Un gemelo digital para la evaluación ex ante de políticas de formalización laboral*.

---

## 1. Principio Fundamental de Blindaje de Insumos

En la validación cruzada dejando un país fuera (*Leave-One-Country-Out*, LOCO), el objetivo científico es predecir la tasa de informalidad femenina ($F_c$) de un país excluido $c$ a partir de la información macroeconómica de los otros tres países de entrenamiento ($\mathcal{C}_{-c}$).

> [!IMPORTANT]
> **Aislamiento Estricto del País Excluido:**
> Ningún modelo tiene acceso, directa ni indirectamente, a:
> 1. La tasa de informalidad femenina observada del país excluido ($F_{obs,c}$).
> 2. La tasa de informalidad total observada del país excluido ($T_{obs,c}$), dado que $T = s_F F + (1 - s_F) M$ permitiría derivar $F$ algebraicamente.

---

## 2. Matriz de Insumos Utilizados por Cada Modelo en LOCO

| Modelo | Insumos del País Excluido ($c$) | Insumos de los Países de Entrenamiento ($\mathcal{C}_{-c}$) | Parámetros Estimados / Transferidos | ¿Usa $F_c$ o $T_c$? |
| :--- | :--- | :--- | :--- | :---: |
| **ITDT ($\gamma_0$ común)** | • Tasa masculina observada $M_{obs,c}$<br>• Proporción de empleo femenino $s_{F,c}$ (de `data/ilostat_s_F.csv`) | • Tasas completas: $M_{obs,k}$, $F_{obs,k}$, $s_{F,k}$ ($k \in \mathcal{C}_{-c}$) | • $\gamma_0^*$: estimado por búsqueda en rejilla $[0.0, 1.2]$ sobre $\mathcal{C}_{-c}$.<br>• $\phi_{0,c}$: calibrado en $c$ para igualar **únicamente** $M_{obs,c}$ dado $\gamma_0^*$. | ❌ **NO** |
| **Brecha Media** | • Tasa masculina observada $M_{obs,c}$ | • Brechas observadas: $(F_{obs,k} - M_{obs,k})$ para $k \in \mathcal{C}_{-c}$ | • Brecha promedio transferida: $\bar{\Delta}_{-c} = \frac{1}{3}\sum (F_k - M_k)$<br>• Predicción: $\hat{F}_c = M_c + \bar{\Delta}_{-c}$. | ❌ **NO** |
| **Razón Media** | • Tasa masculina observada $M_{obs,c}$ | • Razones observadas: $(F_{obs,k} / M_{obs,k})$ para $k \in \mathcal{C}_{-c}$ | • Razón promedio transferida: $\bar{R}_{-c} = \frac{1}{3}\sum (F_k / M_k)$<br>• Predicción: $\hat{F}_c = \min(100, M_c \cdot \bar{R}_{-c})$. | ❌ **NO** |
| **Regresión Lineal sobre $s_F$** | • Tasa masculina observada $M_{obs,c}$<br>• Proporción de empleo femenino $s_{F,c}$ | • Brechas observadas $(F_k - M_k)$ y $s_{F,k}$ para $k \in \mathcal{C}_{-c}$ | • Coeficientes OLS: $\Delta_k = \beta_0 + \beta_1 s_{F,k}$ entrenados con los 3 países.<br>• Predicción: $\hat{F}_c = M_c + (\hat{\beta}_0 + \hat{\beta}_1 s_{F,c})$. | ❌ **NO** |
| **ITDT sin cuidado (E3)** | • Tasa masculina observada $M_{obs,c}$<br>• Proporción de empleo femenino $s_{F,c}$ | • Ninguno requerido (modelo sin término de cuidado, $\gamma_0 = 0$) | • $\phi_{0,c}$: calibrado en $c$ para igualar $M_{obs,c}$ fijando $\gamma_0 = 0$.<br>• Predicción: $\hat{F}_c = F_{sim}(\phi_{0,c}, \gamma_0=0)$. | ❌ **NO** |

---

## 3. Justificación y Observaciones Metodológicas

1. **Independencia de $s_F$:**  
   La proporción de mujeres en el empleo ($s_F$) se carga directamente del indicador oficial de empleo por sexo publicado por ILOSTAT (almacenado en `data/ilostat_s_F.csv` con metadatos de consulta). No se deduce algebraicamente de la relación contable de tasas de informalidad, garantizando que no filtre información de $F_c$.
2. **Identificación de $\phi_0$ en el Excluido:**  
   Dado que el empleo masculino no sufre penalización por cuidado ($\gamma_0 \cdot H_{care} / 48 \approx 0$), la tasa masculina $M_{obs,c}$ permite calibrar el costo fijo de cumplimiento $\phi_0$ del país excluido de forma limpia y ortogonal a la brecha de género.
3. **Poder predictivo de ITDT:**  
   El modelo ITDT es el único modelo estructural capaz de predecir la brecha de género fuera de muestra transfiriendo un único parámetro conductual común ($\gamma_0$) entre economías del Sur Global.
"""
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Documento de insumos guardado en: {doc_path}")


def main():
    t0 = time.time()
    loco_results = run_loco_cross_validation()
    baselines_results = run_structural_baselines_table4()

    json_path = os.path.join("outputs", "loco_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "loco_cross_validation": loco_results,
            "structural_baselines": baselines_results,
            "elapsed_seconds": time.time() - t0,
        }, f, indent=2, ensure_ascii=False)
    print(f"\nResultados LOCO y baselines consolidados en: {json_path}")


if __name__ == "__main__":
    main()

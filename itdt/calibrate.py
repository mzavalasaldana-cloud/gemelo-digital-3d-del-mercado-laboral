"""
itdt.calibrate: Calibración estructural SMM por bisección anidada (Sección 3.5).
Estima phi_0 in [0, 12] y gamma_0 in [0, 1.5] para igualar las tasas observadas de ILOSTAT
en Kenia (2019), Nigeria (2024), India (2024) y Bangladés (2023).
Usa S=6 simulaciones con semillas 1000–1005 y números aleatorios comunes,
96 meses de calentamiento y el promedio de los 24 siguientes.
Bisección anidada 9x9 (81 evaluaciones exactas por calibración).
Calcula errores estándar mediante 10 conjuntos de semillas independientes.
Exporta outputs/table2_calibration.*, outputs/table11_equity.*, outputs/figure4_calibration.png
y outputs/calibration_estimates.json.
"""

import os
import json
import time
from typing import Dict, Any, List, Tuple
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from itdt.model import ITDTModel
from itdt.parameters import COUNTRY_DATABASE, load_ilostat_s_F_data

TARGET_COUNTRIES = ["KENYA", "NIGERIA", "INDIA", "BANGLADESH"]
DEFAULT_BASELINE_SEEDS = [1000, 1001, 1002, 1003, 1004, 1005]


def evaluate_moments(
    phi_0: float,
    gamma_0: float,
    s_F: float,
    country_name: str,
    seeds: List[int],
    burn_in_months: int = 96,
    eval_months: int = 24,
) -> Tuple[float, float]:
    """
    Evalúa las tasas promedio simuladas (F_sim, M_sim) sobre el conjunto de semillas dado.
    """
    f_list: List[float] = []
    m_list: List[float] = []
    country_cfg = {
        "s_F": s_F,
        "phi_0": phi_0,
        "gamma_0": gamma_0,
        "name": country_name,
    }

    for seed in seeds:
        model = ITDTModel(country_params=country_cfg, scenario="A", seed=seed)
        f_rate, m_rate = model.simulate_moments(burn_in_months=burn_in_months, eval_months=eval_months)
        f_list.append(f_rate)
        m_list.append(m_rate)

    return float(np.mean(f_list)), float(np.mean(m_list))


def nested_bisection_calibration(
    country_key: str,
    s_F: float,
    F_obs: float,
    M_obs: float,
    seeds: List[int],
    outer_steps: int = 9,
    inner_steps: int = 9,
) -> Dict[str, Any]:
    """
    Ejecuta el algoritmo SMM de bisección anidada (Sección 3.5).
    - Bisección externa: gamma_0 in [0.0, 1.5] (outer_steps iteraciones)
    - Bisección interna: phi_0 in [0.0, 12.0] (inner_steps iteraciones)
    Total evaluaciones reales: outer_steps * inner_steps (9x9 = 81 evaluaciones).
    """
    gamma_low, gamma_high = 0.0, 1.5
    eval_count = 0

    best_loss = float("inf")
    best_candidate = {
        "phi_0": 0.0,
        "gamma_0": 0.0,
        "F_sim": 0.0,
        "M_sim": 0.0,
        "loss": float("inf"),
    }

    evaluation_history = []

    for out_idx in range(outer_steps):
        gamma_mid = (gamma_low + gamma_high) / 2.0
        phi_low, phi_high = 0.0, 12.0
        f_sim_inner = 0.0

        for in_idx in range(inner_steps):
            phi_mid = (phi_low + phi_high) / 2.0
            f_sim, m_sim = evaluate_moments(
                phi_0=phi_mid,
                gamma_0=gamma_mid,
                s_F=s_F,
                country_name=country_key,
                seeds=seeds,
            )
            eval_count += 1
            f_sim_inner = f_sim

            # Función de pérdida cuadrática SMM (W = I): (F_sim - F_obs)^2 + (M_sim - M_obs)^2
            loss = (f_sim - F_obs) ** 2 + (m_sim - M_obs) ** 2
            evaluation_history.append({
                "outer_step": out_idx + 1,
                "inner_step": in_idx + 1,
                "phi_0": phi_mid,
                "gamma_0": gamma_mid,
                "F_sim": f_sim,
                "M_sim": m_sim,
                "loss": loss,
            })

            if loss < best_loss:
                best_loss = loss
                best_candidate = {
                    "phi_0": float(phi_mid),
                    "gamma_0": float(gamma_mid),
                    "F_sim": float(f_sim),
                    "M_sim": float(m_sim),
                    "loss": float(loss),
                }

            # Bisección interna: M crece monotónicamente con phi_0
            if m_sim < M_obs:
                phi_low = phi_mid
            else:
                phi_high = phi_mid

        # Bisección externa: F crece monotónicamente con gamma_0
        if f_sim_inner < F_obs:
            gamma_low = gamma_mid
        else:
            gamma_high = gamma_mid

    # Verificación de consistencia: T_sim = s_F * F_sim + (1 - s_F) * M_sim
    T_sim = s_F * best_candidate["F_sim"] + (1.0 - s_F) * best_candidate["M_sim"]

    return {
        "country": country_key,
        "s_F": s_F,
        "F_obs": F_obs,
        "M_obs": M_obs,
        "phi_0": best_candidate["phi_0"],
        "gamma_0": best_candidate["gamma_0"],
        "F_sim": best_candidate["F_sim"],
        "M_sim": best_candidate["M_sim"],
        "T_sim": float(T_sim),
        "loss": best_candidate["loss"],
        "evaluations_count": eval_count,
        "evaluation_history": evaluation_history,
    }


def _worker_calibrate_task(args: Tuple[str, float, float, float, List[int], str]) -> Dict[str, Any]:
    """Función de nivel superior para paralelización en ProcessPoolExecutor."""
    country_key, s_F, F_obs, M_obs, seeds, task_id = args
    res = nested_bisection_calibration(
        country_key=country_key,
        s_F=s_F,
        F_obs=F_obs,
        M_obs=M_obs,
        seeds=seeds,
    )
    res["task_id"] = task_id
    res["seeds"] = seeds
    return res


def run_full_calibration_pipeline(
    output_dir: str = "outputs",
    num_independent_sets: int = 10,
    max_workers: int = 8,
) -> Dict[str, Any]:
    """
    Ejecuta el pipeline completo de calibración SMM:
    1. Calibración basal con semillas 1000-1005 (S=6).
    2. Diez conjuntos de semillas independientes para estimar el error estándar Monte Carlo.
    3. Genera tablas 2 y 11, figura 4 y archivo JSON de estimaciones.
    """
    os.makedirs(output_dir, exist_ok=True)
    s_F_dict = load_ilostat_s_F_data()

    print("======================================================================")
    print(" ITDT: Calibración SMM por Bisección Anidada (Sección 3.5)")
    print(f" Países: {TARGET_COUNTRIES}")
    print(f" Semillas basales (S=6): {DEFAULT_BASELINE_SEEDS}")
    print(f" Conjuntos independientes de semillas para EE: {num_independent_sets}")
    print("======================================================================")

    # 1. Preparar tareas basales
    baseline_tasks = []
    for c_key in TARGET_COUNTRIES:
        c_info = COUNTRY_DATABASE[c_key]
        s_F_val = s_F_dict.get(c_key, c_info["s_F"])
        baseline_tasks.append((
            c_key,
            s_F_val,
            c_info["F_obs"],
            c_info["M_obs"],
            DEFAULT_BASELINE_SEEDS,
            f"baseline_{c_key}",
        ))

    t0 = time.time()
    print("\n--- Ejecutando calibraciones basales en paralelo... ---")
    baseline_results = {}
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for res in executor.map(_worker_calibrate_task, baseline_tasks):
            c_key = res["country"]
            baseline_results[c_key] = res
            print(
                f"  [{c_key}] Evaluaciones: {res['evaluations_count']} | "
                f"phi_0 = {res['phi_0']:.3f}, gamma_0 = {res['gamma_0']:.3f} | "
                f"F_sim = {res['F_sim']:.2f} (obs={res['F_obs']:.2f}), "
                f"M_sim = {res['M_sim']:.2f} (obs={res['M_obs']:.2f}), "
                f"T_sim = {res['T_sim']:.2f}"
            )

    recalibrations: Dict[str, List[Dict[str, Any]]] = {c: [] for c in TARGET_COUNTRIES}
    if num_independent_sets > 0:
        print(f"\n--- Ejecutando {num_independent_sets} recalibraciones independientes por país... ---")
        se_tasks = []
        for k in range(num_independent_sets):
            # Semillas disjuntas e independientes: 5000 + 10*k + s (e.g. 5000..5005, 5010..5015)
            seed_set = [5000 + 10 * k + s for s in range(6)]
            for c_key in TARGET_COUNTRIES:
                c_info = COUNTRY_DATABASE[c_key]
                s_F_val = s_F_dict.get(c_key, c_info["s_F"])
                se_tasks.append((
                    c_key,
                    s_F_val,
                    c_info["F_obs"],
                    c_info["M_obs"],
                    seed_set,
                    f"se_set_{k}_{c_key}",
                ))

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for res in executor.map(_worker_calibrate_task, se_tasks):
                c_key = res["country"]
                recalibrations[c_key].append(res)

    # 3. Calcular errores estándar Monte Carlo
    summary_estimates = {}
    for c_key in TARGET_COUNTRIES:
        c_info = COUNTRY_DATABASE[c_key]
        base_res = baseline_results[c_key]
        recal_list = recalibrations[c_key]

        phis = [r["phi_0"] for r in recal_list]
        gammas = [r["gamma_0"] for r in recal_list]

        phi_se = float(np.std(phis, ddof=1)) if len(phis) > 1 else 0.0
        gamma_se = float(np.std(gammas, ddof=1)) if len(gammas) > 1 else 0.0

        # Resolución mínima de la bisección
        # phi_res = 12.0 / 2^9 = 0.0234
        # gamma_res = 1.5 / 2^9 = 0.0029
        gamma_res = 1.5 / (2 ** 9)

        summary_estimates[c_key] = {
            "name": c_info["name"],
            "country_code": c_info["country_code"],
            "year": c_info["year"],
            "s_F": base_res["s_F"],
            "F_obs": base_res["F_obs"],
            "F_sim": base_res["F_sim"],
            "M_obs": base_res["M_obs"],
            "M_sim": base_res["M_sim"],
            "T_obs": c_info["T_obs"],
            "T_sim": base_res["T_sim"],
            "phi_0": base_res["phi_0"],
            "phi_0_se": phi_se,
            "gamma_0": base_res["gamma_0"],
            "gamma_0_se": gamma_se,
            "gamma_res": gamma_res,
            "evaluations_count": base_res["evaluations_count"],
            "loss": base_res["loss"],
            "recalibrations_count": len(recal_list),
        }

    elapsed = time.time() - t0
    print(f"\nPipeline de calibración completado con éxito en {elapsed:.2f} s.")

    # 4. Guardar archivo JSON completo
    export_json_path = os.path.join(output_dir, "calibration_estimates.json")
    all_json_data = {
        "metadata": {
            "date": "2026-10-02",
            "evaluations_per_country": 81,
            "baseline_seeds": DEFAULT_BASELINE_SEEDS,
            "independent_seed_sets_count": num_independent_sets,
            "elapsed_seconds": elapsed,
        },
        "summary": summary_estimates,
        "baseline_details": baseline_results,
        "recalibrations": recalibrations,
    }
    with open(export_json_path, "w", encoding="utf-8") as f:
        json.dump(all_json_data, f, indent=2, ensure_ascii=False)
    print(f"Estimaciones guardadas en: {export_json_path}")
    export_calibration_artifacts_from_summary(summary_estimates, output_dir, num_independent_sets)
    return summary_estimates


def export_calibration_artifacts_from_summary(
    summary_estimates: Dict[str, Any],
    output_dir: str = "outputs",
    num_independent_sets: int = 10,
):
    """Genera Tablas 2 y 11 y la Figura 4 a partir de summary_estimates."""
    os.makedirs(output_dir, exist_ok=True)

    # 5. Generar Tabla 2 (CSV y Markdown)
    table2_rows = []
    for c_key in TARGET_COUNTRIES:
        s = summary_estimates[c_key]
        phi_se_str = f"{s['phi_0_se']:.2f}"
        if s["gamma_0_se"] < s["gamma_res"] * 2.0:
            gamma_se_str = "< 0.012"
        else:
            gamma_se_str = f"{s['gamma_0_se']:.3f}"

        table2_rows.append({
            "País (año)": f"{s['name']} ({s['year']})",
            "s_F": f"{s['s_F']:.3f}",
            "F obs.": f"{s['F_obs']:.2f}",
            "F sim.": f"{s['F_sim']:.2f}",
            "M obs.": f"{s['M_obs']:.2f}",
            "M sim.": f"{s['M_sim']:.2f}",
            "T obs.": f"{s['T_obs']:.2f}",
            "T sim.": f"{s['T_sim']:.2f}",
            "phi_0 (EE)": f"{s['phi_0']:.2f} ({phi_se_str})",
            "gamma_0 (EE)": f"{s['gamma_0']:.3f} ({gamma_se_str})",
        })

    df_t2 = pd.DataFrame(table2_rows)
    t2_csv = os.path.join(output_dir, "table2_calibration.csv")
    t2_md = os.path.join(output_dir, "table2_calibration.md")
    df_t2.to_csv(t2_csv, index=False, encoding="utf-8")
    with open(t2_md, "w", encoding="utf-8") as f:
        f.write("# Tabla 2: Momentos observados, momentos simulados y parámetros estimados por SMM\n\n")
        f.write(df_t2.to_markdown(index=False))
        f.write("\n\n*Nota.* Tasas de informalidad en %. F = mujeres, M = hombres, T = total. "
                "La tasa T no se usa en la calibración: se obtiene como s_F*F + (1 - s_F)*M. "
                f"EE = desviación estándar del estimador entre {num_independent_sets} recalibraciones independientes. "
                "Fuente de valores observados: ILOSTAT.\n")
    print(f"Tabla 2 generada en {t2_csv} y {t2_md}")

    # 6. Generar Tabla 11: Desempeño y Equidad
    fem_calib_errors = [abs(summary_estimates[c]["F_sim"] - summary_estimates[c]["F_obs"]) for c in TARGET_COUNTRIES]
    male_calib_errors = [abs(summary_estimates[c]["M_sim"] - summary_estimates[c]["M_obs"]) for c in TARGET_COUNTRIES]
    mean_fem_err = float(np.mean(fem_calib_errors))
    mean_male_err = float(np.mean(male_calib_errors))

    ratio_gap_strs = []
    for c_key in TARGET_COUNTRIES:
        s = summary_estimates[c_key]
        obs_gap = s["F_obs"] - s["M_obs"]
        sim_gap = s["F_sim"] - s["M_sim"]
        ratio = sim_gap / obs_gap if abs(obs_gap) > 1e-4 else 1.0
        ratio_gap_strs.append(f"{ratio:.2f}")

    table11_rows = [
        {
            "Indicador": "Error absoluto de calibración, media de 4 países (p.p.)",
            "Mujeres": f"{mean_fem_err:.2f}",
            "Hombres": f"{mean_male_err:.2f}",
        },
        {
            "Indicador": "Cociente brecha simulada / observada (Kenia, Nigeria, India, Bangladés)",
            "Mujeres": " / ".join(ratio_gap_strs),
            "Hombres": "—",
        },
    ]
    df_t11 = pd.DataFrame(table11_rows)
    t11_csv = os.path.join(output_dir, "table11_equity.csv")
    t11_md = os.path.join(output_dir, "table11_equity.md")
    df_t11.to_csv(t11_csv, index=False, encoding="utf-8")
    with open(t11_md, "w", encoding="utf-8") as f:
        f.write("# Tabla 11: Desempeño de ITDT por sexo\n\n")
        f.write(df_t11.to_markdown(index=False))
        f.write("\n\n*Nota.* Las brechas se definen como F − M (mujeres − hombres).\n")
    print(f"Tabla 11 generada en {t11_csv} y {t11_md}")

    # 7. Generar Figura 4 (PNG)
    generate_figure4(summary_estimates, os.path.join(output_dir, "figure4_calibration.png"))


def generate_figure4(summary_estimates: Dict[str, Any], output_path: str):
    """
    Genera la Figura 4: Tasas de informalidad observadas (ILOSTAT) y simuladas por ITDT, por país y sexo.
    Eje Y común, círculos vacíos = observados, círculos llenos = simulados, brecha F - M.
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    countries = TARGET_COUNTRIES
    country_names = [summary_estimates[c]["name"] for c in countries]
    x = np.arange(len(countries))
    width = 0.22

    # Datos
    f_obs = [summary_estimates[c]["F_obs"] for c in countries]
    f_sim = [summary_estimates[c]["F_sim"] for c in countries]
    m_obs = [summary_estimates[c]["M_obs"] for c in countries]
    m_sim = [summary_estimates[c]["M_sim"] for c in countries]

    color_fem = "#c0392b"  # Carmesí / Borgoña
    color_male = "#2980b9" # Azul acero

    # Puntos Mujeres: observados (círculo vacío), simulados (círculo lleno)
    ax.scatter(x - width, f_obs, s=90, facecolors="none", edgecolors=color_fem, linewidth=2.2, label="Mujeres (ILOSTAT)", zorder=4)
    ax.scatter(x - width, f_sim, s=90, facecolors=color_fem, edgecolors=color_fem, linewidth=2.2, label="Mujeres (ITDT simulado)", zorder=4)

    # Puntos Hombres: observados (círculo vacío), simulados (círculo lleno)
    ax.scatter(x + width, m_obs, s=90, facecolors="none", edgecolors=color_male, linewidth=2.2, label="Hombres (ILOSTAT)", zorder=4)
    ax.scatter(x + width, m_sim, s=90, facecolors=color_male, edgecolors=color_male, linewidth=2.2, label="Hombres (ITDT simulado)", zorder=4)

    # Líneas verticales uniendo obs y sim para mostrar el ajuste exacto
    for i in range(len(countries)):
        ax.plot([x[i] - width, x[i] - width], [f_obs[i], f_sim[i]], color=color_fem, linestyle="--", alpha=0.6, linewidth=1.2)
        ax.plot([x[i] + width, x[i] + width], [m_obs[i], m_sim[i]], color=color_male, linestyle="--", alpha=0.6, linewidth=1.2)

        # Anotación de la brecha observada F - M
        gap_obs = f_obs[i] - m_obs[i]
        gap_sim = f_sim[i] - m_sim[i]
        ax.annotate(
            f"Brecha (F−M)\nObs: {gap_obs:+.1f} p.p.\nSim: {gap_sim:+.1f} p.p.",
            xy=(x[i], min(m_obs[i], m_sim[i]) - 2.8),
            ha="center",
            va="top",
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.3", fc="#f8f9fa", ec="#dcdde1", alpha=0.9),
        )

    ax.set_xticks(x)
    ax.set_xticklabels(country_names, fontsize=11, fontweight="bold")
    ax.set_ylabel("Tasa de informalidad (%)", fontsize=11, fontweight="bold")
    ax.set_ylim(70.0, 100.0)  # Eje Y común estandarizado
    ax.set_title("Tasas de informalidad observadas (ILOSTAT) y simuladas por ITDT, por país y sexo\n(Calibración SMM - Bisección anidada 9×9 = 81 evaluaciones)", fontsize=12, fontweight="bold", pad=12)

    ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#bdc3c7", fontsize=9.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Figura 4 guardada en: {output_path}")


if __name__ == "__main__":
    import sys
    calib_json = os.path.join("outputs", "calibration_estimates.json")
    if os.path.exists(calib_json) and "--recalibrate" not in sys.argv:
        print(f"Cargando estimaciones existentes desde {calib_json} para generar tablas y figuras...")
        with open(calib_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        export_calibration_artifacts_from_summary(data["summary"])
    else:
        run_full_calibration_pipeline()


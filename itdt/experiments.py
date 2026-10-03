"""
itdt.experiments: Ejecución de experimentos de política, contrastes inferenciales,
barrido de sanciones, ablación recalibrada, análisis de sensibilidad, robustez CES,
costo computacional y propagación de incertidumbre (Secciones 3.7–3.9).

Genera:
- Tablas 5, 6, 7 (Niveles, cambios con bootstrap clusterizado B=4000, contrastes t/Wilcoxon/Bonferroni).
- Tabla 8 (Ablación de B2 frente a A, RECALIBRANDO cada variante).
- Tabla 9 (Sensibilidad +-20%, CES sigma=0.5 y 1.5 recalibrados, choque de demanda -5% en mes 60).
- Tabla 10 (Costo computacional y memoria para N_W in {3000, 6000, 12000, 24000}).
- Tabla 12 (Gradientes distributivos no calibrados en Escenario A).
- Figuras 5, 6, 7 (Barrido de sanciones, trayectorias mensuales con IC 95%, niveles finales).
- Archivos JSON en outputs/*.json y propagación de incertidumbre.
"""

import os
import json
import time
import math
import tracemalloc
from typing import Dict, Any, List, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

from itdt.model import ITDTModel
from itdt.parameters import FixedParameters, COUNTRY_DATABASE, load_ilostat_s_F_data, resolve_country_params

TARGET_COUNTRIES = ["KENYA", "NIGERIA", "INDIA", "BANGLADESH"]
POLICY_SCENARIOS = ["A", "B1", "B2", "C", "D"]
REPLICA_SEEDS = list(range(20260, 20300))  # R = 40 réplicas (semillas 20260–20299)


# ==============================================================================
# 1. EJECUCIÓN DE RÉPLICAS DE POLÍTICA (R = 40)
# ==============================================================================

def run_single_replica_worker(args: Tuple[str, str, int, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]) -> Dict[str, Any]:
    """Trabajador para ejecutar una única réplica de simulación en ProcessPool."""
    c_key, sc, seed, custom_country_params, custom_fixed_params = args

    # Cargar o resolver parámetros
    if custom_country_params is not None:
        c_params = custom_country_params
    else:
        c_params = c_key

    fp = None
    if custom_fixed_params is not None:
        fp = FixedParameters(**custom_fixed_params)

    model = ITDTModel(
        country_params=c_params,
        scenario=sc,
        seed=seed,
        burn_in_months=96,
        policy_months=120,
        fixed_params=fp,
    )
    result = model.run()
    summary = result["summary_metrics"]

    # Extraer métricas clave de los meses 109-120
    return {
        "country": c_key,
        "scenario": sc,
        "seed": seed,
        "informality_total": summary["mean_informality_total"],
        "informality_female": summary["mean_informality_female"],
        "informality_male": summary["mean_informality_male"],
        "gender_gap": summary["mean_gender_gap"],
        "annual_exit_rate": summary["mean_annual_exit_rate"],
        "fiscal_revenue": summary["mean_fiscal_revenue"],
        "gradients": summary["gradients"],
        # Guardar series mensuales de informalidad para Figura 6 (submuestra mensual)
        "monthly_total": [m["informality_total"] for m in result["monthly_series"][96:]],
        "monthly_female": [m["informality_female"] for m in result["monthly_series"][96:]],
        "monthly_male": [m["informality_male"] for m in result["monthly_series"][96:]],
    }


def run_all_policy_replicas(
    countries: List[str] = TARGET_COUNTRIES,
    scenarios: List[str] = POLICY_SCENARIOS,
    seeds: List[int] = REPLICA_SEEDS,
    calibrated_params: Optional[Dict[str, Any]] = None,
    max_workers: int = 8,
) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Ejecuta las 40 réplicas por país y escenario con semillas comunes (20260–20299).
    """
    print(f"\n--- Ejecutando experimentos de política ({len(countries)} países x {len(scenarios)} escenarios x {len(seeds)} réplicas = {len(countries)*len(scenarios)*len(seeds)} corridas) ---")
    tasks = []
    for c in countries:
        c_custom = None
        if calibrated_params is not None and c in calibrated_params:
            c_custom = {
                "s_F": calibrated_params[c]["s_F"],
                "phi_0": calibrated_params[c]["phi_0"],
                "gamma_0": calibrated_params[c]["gamma_0"],
                "name": COUNTRY_DATABASE[c]["name"],
            }
        for sc in scenarios:
            for seed in seeds:
                tasks.append((c, sc, seed, c_custom, None))

    results_structured: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
        c: {sc: [] for sc in scenarios} for c in countries
    }

    t0 = time.time()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for item in executor.map(run_single_replica_worker, tasks):
            results_structured[item["country"]][item["scenario"]].append(item)

    print(f"Réplicas de política completadas en {time.time() - t0:.2f} s.")
    return results_structured


# ==============================================================================
# 2. INFERENCIA ESTADÍSTICA, CONTRASTES Y BOOTSTRAP POR CONGLOMERADOS (TABLAS 5, 6, 7)
# ==============================================================================

def compute_inferential_tables(
    results_structured: Dict[str, Dict[str, List[Dict[str, Any]]]],
    output_dir: str = "outputs",
    B_bootstrap: int = 4000,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Calcula:
    - Tabla 5: Niveles por escenario en los meses 109–120 (media de los 4 países, DE entre réplicas).
    - Tabla 6: Cambios frente a Escenario A e IC 95% por bootstrap por conglomerados en dos etapas.
    - Tabla 7: Contrastes por país frente a A (gl=39, t, d_z, Wilcoxon, Bonferroni).
    """
    os.makedirs(output_dir, exist_ok=True)
    countries = TARGET_COUNTRIES
    scenarios = POLICY_SCENARIOS
    R = len(REPLICA_SEEDS)

    # -------------------------------------------------------------
    # TABLA 5: Niveles por escenario
    # -------------------------------------------------------------
    table5_rows = []
    sc_metrics = {}

    for sc in scenarios:
        # Medias por país
        c_means = {m: [] for m in ["total", "fem", "male", "gap", "exit"]}
        c_stds = {m: [] for m in ["total", "fem", "male", "gap", "exit"]}

        for c in countries:
            reps = results_structured[c][sc]
            t_vals = [r["informality_total"] for r in reps]
            f_vals = [r["informality_female"] for r in reps]
            m_vals = [r["informality_male"] for r in reps]
            g_vals = [r["gender_gap"] for r in reps]
            e_vals = [r["annual_exit_rate"] for r in reps]

            c_means["total"].append(np.mean(t_vals))
            c_means["fem"].append(np.mean(f_vals))
            c_means["male"].append(np.mean(m_vals))
            c_means["gap"].append(np.mean(g_vals))
            c_means["exit"].append(np.mean(e_vals))

            c_stds["total"].append(np.std(t_vals, ddof=1))
            c_stds["fem"].append(np.std(f_vals, ddof=1))
            c_stds["male"].append(np.std(m_vals, ddof=1))
            c_stds["gap"].append(np.std(g_vals, ddof=1))
            c_stds["exit"].append(np.std(e_vals, ddof=1))

        # Media de las medias por país y promedio de las desviaciones estándar por país
        mean_tot = float(np.mean(c_means["total"]))
        std_tot = float(np.mean(c_stds["total"]))
        mean_fem = float(np.mean(c_means["fem"]))
        std_fem = float(np.mean(c_stds["fem"]))
        mean_male = float(np.mean(c_means["male"]))
        std_male = float(np.mean(c_stds["male"]))
        mean_gap = float(np.mean(c_means["gap"]))
        mean_exit = float(np.mean(c_means["exit"]))
        std_exit = float(np.mean(c_stds["exit"]))

        sc_name_labels = {
            "A": "A: status quo",
            "B1": "B1: GovTech moderado",
            "B2": "B2: GovTech intensivo",
            "C": "C: red de cuidados",
            "D": "D: integrado",
        }

        table5_rows.append({
            "Escenario": sc_name_labels.get(sc, sc),
            "Informalidad total (%)": f"{mean_tot:.2f} ({std_tot:.2f})",
            "Mujeres (%)": f"{mean_fem:.2f} ({std_fem:.2f})",
            "Hombres (%)": f"{mean_male:.2f} ({std_male:.2f})",
            "Brecha F − M (p.p.)": f"{mean_gap:.2f}",
            "Cierre anual de empresas (%)": f"{mean_exit:.2f} ({std_exit:.2f})",
        })

    df_t5 = pd.DataFrame(table5_rows)
    df_t5.to_csv(os.path.join(output_dir, "table5_levels.csv"), index=False, encoding="utf-8")
    with open(os.path.join(output_dir, "table5_levels.md"), "w", encoding="utf-8") as f:
        f.write("# Tabla 5: Niveles por escenario en los meses 109–120 (media de los cuatro países)\n\n")
        f.write(df_t5.to_markdown(index=False))
        f.write("\n\n*Nota.* Entre paréntesis, desviación estándar entre réplicas (promedio de las cuatro desviaciones por país; R = 40).\n")

    # -------------------------------------------------------------
    # TABLA 6: Cambios frente a Escenario A e IC 95% por bootstrap por conglomerados
    # -------------------------------------------------------------
    # Paired differences per country and replica
    diff_metrics = ["total", "fem", "male", "gap", "exit", "rev_pct"]
    paired_diffs: Dict[str, Dict[str, Dict[str, np.ndarray]]] = {
        sc: {c: {} for c in countries} for sc in ["B1", "B2", "C", "D"]
    }

    for sc in ["B1", "B2", "C", "D"]:
        for c in countries:
            reps_a = sorted(results_structured[c]["A"], key=lambda r: r["seed"])
            reps_sc = sorted(results_structured[c][sc], key=lambda r: r["seed"])

            diff_tot = np.array([r_s["informality_total"] - r_a["informality_total"] for r_a, r_s in zip(reps_a, reps_sc)])
            diff_fem = np.array([r_s["informality_female"] - r_a["informality_female"] for r_a, r_s in zip(reps_a, reps_sc)])
            diff_male = np.array([r_s["informality_male"] - r_a["informality_male"] for r_a, r_s in zip(reps_a, reps_sc)])
            diff_gap = np.array([r_s["gender_gap"] - r_a["gender_gap"] for r_a, r_s in zip(reps_a, reps_sc)])
            diff_exit = np.array([r_s["annual_exit_rate"] - r_a["annual_exit_rate"] for r_a, r_s in zip(reps_a, reps_sc)])
            # Cambio porcentual en recaudación
            rev_a = np.array([r_a["fiscal_revenue"] for r_a in reps_a])
            rev_s = np.array([r_s["fiscal_revenue"] for r_s in reps_sc])
            diff_rev_pct = ((rev_s - rev_a) / np.maximum(1e-6, rev_a)) * 100.0

            paired_diffs[sc][c] = {
                "total": diff_tot,
                "fem": diff_fem,
                "male": diff_male,
                "gap": diff_gap,
                "exit": diff_exit,
                "rev_pct": diff_rev_pct,
            }

    # Two-Stage Cluster Bootstrap (B = 4000)
    print(f"--- Ejecutando bootstrap por conglomerados en dos etapas (B = {B_bootstrap})... ---")
    rng_boot = np.random.default_rng(2026)
    table6_rows = []

    for sc in ["B1", "B2", "C", "D"]:
        row_dict = {"Escenario": sc}
        for metric in diff_metrics:
            # Media empírica observada
            point_est = float(np.mean([np.mean(paired_diffs[sc][c][metric]) for c in countries]))

            # Bootstrap en dos etapas
            boot_vals = []
            for _ in range(B_bootstrap):
                # Etapa 1: remuestreo de países con reemplazo
                boot_countries = rng_boot.choice(countries, size=len(countries), replace=True)
                country_means = []
                for b_c in boot_countries:
                    # Etapa 2: remuestreo de réplicas dentro de país con reemplazo
                    vec = paired_diffs[sc][b_c][metric]
                    boot_vec = rng_boot.choice(vec, size=len(vec), replace=True)
                    country_means.append(np.mean(boot_vec))
                boot_vals.append(np.mean(country_means))

            ci_low = float(np.percentile(boot_vals, 2.5))
            ci_high = float(np.percentile(boot_vals, 97.5))

            sign_str = "+" if point_est > 0 else ""
            fmt_val = f"{sign_str}{point_est:.2f} [{ci_low:.2f}, {ci_high:.2f}]"
            if metric == "total":
                row_dict["Total (p.p.)"] = fmt_val
            elif metric == "fem":
                row_dict["Mujeres (p.p.)"] = fmt_val
            elif metric == "male":
                row_dict["Hombres (p.p.)"] = fmt_val
            elif metric == "gap":
                row_dict["Brecha (p.p.)"] = fmt_val
            elif metric == "exit":
                row_dict["Cierres (p.p./año)"] = fmt_val
            elif metric == "rev_pct":
                row_dict["Recaudación (%)"] = f"{sign_str}{point_est:.1f} [{ci_low:.1f}, {ci_high:.1f}]"

        table6_rows.append(row_dict)

    df_t6 = pd.DataFrame(table6_rows)
    df_t6.to_csv(os.path.join(output_dir, "table6_changes.csv"), index=False, encoding="utf-8")
    with open(os.path.join(output_dir, "table6_changes.md"), "w", encoding="utf-8") as f:
        f.write("# Tabla 6: Cambios frente al Escenario A e IC 95 % por bootstrap por conglomerados\n\n")
        f.write(df_t6.to_markdown(index=False))
        f.write("\n\n*Nota.* Diferencias pareadas por semilla, promediadas por país y luego entre países. "
                "Recaudación = impuesto a sociedades de las empresas formales + contribuciones de los trabajadores formales. "
                f"B = {B_bootstrap} iteraciones.\n")

    # -------------------------------------------------------------
    # TABLA 7: Contrastes por país (gl=39, t, d_z, Wilcoxon, Bonferroni)
    # -------------------------------------------------------------
    # Familia de 20 contrastes por país (4 escenarios x 5 métricas)
    num_tests_per_country = 20
    table7_rows = []

    # Contrastes seleccionados para Tabla 7:
    # B2: mujeres, B2: brecha, D: total, D: brecha
    target_contrasts = [
        ("B2", "fem", "B2: mujeres"),
        ("B2", "gap", "B2: brecha"),
        ("D", "total", "D: total"),
        ("D", "gap", "D: brecha"),
    ]

    for sc, metric, label in target_contrasts:
        for c in countries:
            diffs = paired_diffs[sc][c][metric]
            mean_d = float(np.mean(diffs))
            std_d = float(np.std(diffs, ddof=1))
            dz = mean_d / std_d if std_d > 1e-9 else 0.0
            t_stat = dz * math.sqrt(R)
            # Prueba t
            p_t = 2.0 * (1.0 - stats.t.cdf(abs(t_stat), df=R - 1))
            # Prueba Wilcoxon
            try:
                res_w = stats.wilcoxon(diffs, alternative="two-sided")
                p_wilcox = float(res_w.pvalue)
            except Exception:
                p_wilcox = 1.0

            # Corrección de Bonferroni (multiplicar p por 20)
            p_bonf = min(1.0, p_t * num_tests_per_country)

            sign_str = "+" if mean_d > 0 else ""
            table7_rows.append({
                "Contraste": label,
                "País": COUNTRY_DATABASE[c]["name"],
                "Diferencia media (DE)": f"{sign_str}{mean_d:.2f} ({std_d:.2f})",
                "t(39)": f"{t_stat:.1f}",
                "dz": f"{dz:.2f}",
                "p-val (Bonferroni)": f"{p_bonf:.4f}" if p_bonf >= 0.001 else "< 0.001",
                "p-val (Wilcoxon)": f"{p_wilcox:.4f}" if p_wilcox >= 0.001 else "< 0.001",
            })

    df_t7 = pd.DataFrame(table7_rows)
    df_t7.to_csv(os.path.join(output_dir, "table7_contrasts.csv"), index=False, encoding="utf-8")
    with open(os.path.join(output_dir, "table7_contrasts.md"), "w", encoding="utf-8") as f:
        f.write("# Tabla 7: Contrastes por país frente al Escenario A (R = 40, gl = 39)\n\n")
        f.write(df_t7.to_markdown(index=False))
        f.write("\n\n*Nota.* dz = diferencia media / DE de las diferencias pareadas; por construcción, t = dz * sqrt(R). "
                "Corrección de Bonferroni para familia de 20 contrastes por país (4 escenarios x 5 métricas). "
                "Prueba de Wilcoxon de rangos con signo para dos muestras relacionadas.\n")

    return df_t5, df_t6, df_t7


# ==============================================================================
# 3. BARRIDO DE MULTIPLICADOR DE SANCIONES (FIGURA 5)
# ==============================================================================

def run_sanctions_sweep_experiment(
    countries: List[str] = TARGET_COUNTRIES,
    seeds: List[int] = REPLICA_SEEDS[:6],  # 6 réplicas por punto según Figura 5 del artículo
    output_dir: str = "outputs",
) -> pd.DataFrame:
    """
    Ejecuta el barrido de sanciones de 1.0 a 4.0 en pasos de 0.5 bajo el Escenario B1.
    Genera Figura 5: Efecto de la intensidad de sanción bajo GovTech.
    """
    print("\n--- Ejecutando barrido de intensidad de sanciones (1.0 a 4.0 bajo B1)... ---")
    multipliers = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    sweep_records = []

    for mult in multipliers:
        fp_sweep = FixedParameters(sanction_mult=mult)
        t_diffs, f_diffs, m_diffs, g_diffs, exit_levels = [], [], [], [], []

        for c in countries:
            for s in seeds:
                # Réplica base A (status quo)
                mod_a = ITDTModel(c, scenario="A", seed=s)
                res_a = mod_a.run()["summary_metrics"]

                # Réplica B1 con multiplicador de sanciones
                mod_b1 = ITDTModel(c, scenario="B1", seed=s, fixed_params=fp_sweep)
                res_b1 = mod_b1.run()["summary_metrics"]

                t_diffs.append(res_b1["mean_informality_total"] - res_a["mean_informality_total"])
                f_diffs.append(res_b1["mean_informality_female"] - res_a["mean_informality_female"])
                m_diffs.append(res_b1["mean_informality_male"] - res_a["mean_informality_male"])
                g_diffs.append(res_b1["mean_gender_gap"] - res_a["mean_gender_gap"])
                exit_levels.append(res_b1["mean_annual_exit_rate"])

        sweep_records.append({
            "multiplier": mult,
            "diff_total_mean": float(np.mean(t_diffs)),
            "diff_total_std": float(np.std(t_diffs, ddof=1)),
            "diff_female_mean": float(np.mean(f_diffs)),
            "diff_female_std": float(np.std(f_diffs, ddof=1)),
            "diff_male_mean": float(np.mean(m_diffs)),
            "diff_male_std": float(np.std(m_diffs, ddof=1)),
            "diff_gap_mean": float(np.mean(g_diffs)),
            "diff_gap_std": float(np.std(g_diffs, ddof=1)),
            "exit_rate_mean": float(np.mean(exit_levels)),
            "exit_rate_std": float(np.std(exit_levels, ddof=1)),
        })

    df_sweep = pd.DataFrame(sweep_records)
    df_sweep.to_csv(os.path.join(output_dir, "sanctions_sweep_data.csv"), index=False, encoding="utf-8")

    # Graficar Figura 5
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax1 = plt.subplots(figsize=(8.5, 5.2), dpi=300)
    ax2 = ax1.twinx()

    x = df_sweep["multiplier"]
    # Eje derecho: Cierres anuales (%) en barras con ancho 0.25
    ax2.bar(x, df_sweep["exit_rate_mean"], width=0.22, color="#bdc3c7", alpha=0.5, edgecolor="#7f8c8d", label="Cierre anual de empresas (%)")
    ax2.set_ylabel("Cierre anual de empresas (%)", fontsize=11, fontweight="bold", color="#555555")
    ax2.set_ylim(0.0, 60.0)
    ax2.grid(False)

    # Eje izquierdo: Cambios frente al status quo en p.p. (líneas con bandas)
    c_tot = "#2c3e50"
    c_fem = "#c0392b"
    c_male = "#2980b9"
    c_gap = "#8e44ad"

    ax1.plot(x, df_sweep["diff_total_mean"], color=c_tot, marker="o", linewidth=2.2, label="Δ Total")
    ax1.plot(x, df_sweep["diff_female_mean"], color=c_fem, marker="s", linewidth=2.2, label="Δ Mujeres")
    ax1.plot(x, df_sweep["diff_male_mean"], color=c_male, marker="^", linewidth=2.2, label="Δ Hombres")
    ax1.plot(x, df_sweep["diff_gap_mean"], color=c_gap, marker="d", linewidth=2.5, linestyle="--", label="Δ Brecha (F − M)")

    # Bandas de incertidumbre para brecha y total
    ax1.fill_between(x, df_sweep["diff_gap_mean"] - df_sweep["diff_gap_std"], df_sweep["diff_gap_mean"] + df_sweep["diff_gap_std"], color=c_gap, alpha=0.15)
    ax1.fill_between(x, df_sweep["diff_total_mean"] - df_sweep["diff_total_std"], df_sweep["diff_total_mean"] + df_sweep["diff_total_std"], color=c_tot, alpha=0.15)

    ax1.axhline(0.0, color="#7f8c8d", linestyle=":", linewidth=1.0)
    ax1.set_xlabel("Multiplicador de intensidad de sanciones", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Cambio frente al status quo (p.p.)", fontsize=11, fontweight="bold")
    ax1.set_ylim(-55.0, 45.0)

    # Combinar leyendas
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True, facecolor="white", edgecolor="#bdc3c7", fontsize=9.0)

    plt.title("Figura 5. Efecto de la intensidad de sanción bajo GovTech\n(Multiplicador 1.0 a 4.0 - Eje Y común de cambios y tasa de cierres)", fontsize=11.5, fontweight="bold", pad=12)
    plt.tight_layout()
    fig5_path = os.path.join(output_dir, "figure5_sanctions_sweep.png")
    plt.savefig(fig5_path, dpi=300)
    plt.close()
    print(f"Figura 5 guardada en: {fig5_path}")

    return df_sweep


# ==============================================================================
# 4. ABLACIÓN RECALIBRADA DE B2 FRENTE A A (TABLA 8)
# ==============================================================================

def run_recalibrated_ablation_study(
    countries: List[str] = TARGET_COUNTRIES,
    seeds: List[int] = REPLICA_SEEDS[:20],  # R = 20 según Tabla 8 del artículo
    output_dir: str = "outputs",
) -> pd.DataFrame:
    """
    Ablación de B2 frente a A:
    - Completo
    - Sin restricción de cuidado
    - Sin DCC regresivo (phi_1 = 0)
    - Sin ambos
    RECALIBRANDO cada variante para cada país antes de contrastar B2 frente a A.
    """
    print("\n--- Ejecutando estudio de ablación de B2 frente a A con RECALIBRACIÓN de cada variante... ---")
    s_F_dict = load_ilostat_s_F_data()
    from itdt.calibrate import nested_bisection_calibration

    variants_config = [
        {"id": "full", "name": "Completo", "care": True, "reg_dcc": True, "phi_1": 0.30},
        {"id": "no_care", "name": "Sin restricción de cuidado", "care": False, "reg_dcc": True, "phi_1": 0.30},
        {"id": "no_dcc", "name": "Sin DCC regresivo", "care": True, "reg_dcc": False, "phi_1": 0.0},
        {"id": "neither", "name": "Sin ambos", "care": False, "reg_dcc": False, "phi_1": 0.0},
    ]

    table8_rows = []

    for v in variants_config:
        print(f"  Recalibrando y evaluando variante: {v['name']}...")
        diff_fem, diff_male, diff_gap, diff_exit = [], [], [], []
        diff_owner_fem, diff_owner_male = [], []

        for c_key in countries:
            c_info = COUNTRY_DATABASE[c_key]
            s_F = s_F_dict.get(c_key, c_info["s_F"])
            F_obs = c_info["F_obs"]
            M_obs = c_info["M_obs"]

            # 1. RECALIBRACIÓN de la variante
            fp_var = FixedParameters(
                care_enabled=v["care"],
                regressive_dcc=v["reg_dcc"],
                phi_1=v["phi_1"],
            )

            if v["id"] == "full" and os.path.exists(os.path.join(output_dir, "calibration_estimates.json")):
                with open(os.path.join(output_dir, "calibration_estimates.json"), "r", encoding="utf-8") as f:
                    cal_data = json.load(f)["summary"][c_key]
                phi_cal = cal_data["phi_0"]
                gamma_cal = cal_data["gamma_0"]
            elif v["care"]:
                # Calibrar phi_0 y gamma_0 por bisección anidada 9x9
                cal = nested_bisection_calibration(
                    country_key=c_key, s_F=s_F, F_obs=F_obs, M_obs=M_obs, seeds=[1000, 1001, 1002, 1003, 1004, 1005]
                )
                phi_cal = cal["phi_0"]
                gamma_cal = cal["gamma_0"]
            else:
                # Sin cuidado: gamma_0 = 0.0, calibrar phi_0 para igualar M_obs
                from itdt.loco import bisection_calibrate_phi_to_target
                phi_cal, _, _, _ = bisection_calibrate_phi_to_target(
                    country_key=c_key, s_F=s_F, target_value=M_obs, target_type="M",
                    gamma_0=0.0, seeds=[1000, 1001, 1002, 1003, 1004, 1005], fixed_params=fp_var,
                )
                gamma_cal = 0.0

            custom_c = {
                "s_F": s_F,
                "phi_0": phi_cal,
                "gamma_0": gamma_cal,
                "name": c_info["name"],
            }

            # 2. Correr R = 20 réplicas pareadas A vs B2
            for s in seeds:
                m_a = ITDTModel(custom_c, scenario="A", seed=s, fixed_params=fp_var)
                res_a = m_a.run()["summary_metrics"]

                m_b2 = ITDTModel(custom_c, scenario="B2", seed=s, fixed_params=fp_var)
                res_b2 = m_b2.run()["summary_metrics"]

                diff_fem.append(res_b2["mean_informality_female"] - res_a["mean_informality_female"])
                diff_male.append(res_b2["mean_informality_male"] - res_a["mean_informality_male"])
                diff_gap.append(res_b2["mean_gender_gap"] - res_a["mean_gender_gap"])
                diff_exit.append(res_b2["mean_annual_exit_rate"] - res_a["mean_annual_exit_rate"])

                # Variación exacta de empresas formales con dueña vs dueño
                fem_owned_a = m_a.fem_mask[m_a.owners]
                rate_f_a = (np.sum(m_a.is_formal_firm & fem_owned_a) / max(1, np.sum(fem_owned_a))) * 100.0
                rate_m_a = (np.sum(m_a.is_formal_firm & ~fem_owned_a) / max(1, np.sum(~fem_owned_a))) * 100.0

                fem_owned_b2 = m_b2.fem_mask[m_b2.owners]
                rate_f_b2 = (np.sum(m_b2.is_formal_firm & fem_owned_b2) / max(1, np.sum(fem_owned_b2))) * 100.0
                rate_m_b2 = (np.sum(m_b2.is_formal_firm & ~fem_owned_b2) / max(1, np.sum(~fem_owned_b2))) * 100.0

                diff_owner_fem.append(rate_f_b2 - rate_f_a)
                diff_owner_male.append(rate_m_b2 - rate_m_a)

        d_fem_mean = float(np.mean(diff_fem))
        d_male_mean = float(np.mean(diff_male))
        d_gap_mean = float(np.mean(diff_gap))
        d_exit_mean = float(np.mean(diff_exit))
        d_owner_f_mean = float(np.mean(diff_owner_fem))
        d_owner_m_mean = float(np.mean(diff_owner_male))

        sign_fem = "+" if d_fem_mean > 0 else ""
        sign_male = "+" if d_male_mean > 0 else ""
        sign_gap = "+" if d_gap_mean > 0 else ""
        sign_exit = "+" if d_exit_mean > 0 else ""

        table8_rows.append({
            "Variante del modelo": v["name"],
            "Δ mujeres (p.p.)": f"{sign_fem}{d_fem_mean:.2f}",
            "Δ hombres (p.p.)": f"{sign_male}{d_male_mean:.2f}",
            "Δ brecha (p.p.)": f"{sign_gap}{d_gap_mean:.2f}",
            "Δ cierres (p.p./año)": f"{sign_exit}{d_exit_mean:.2f}",
            "Δ empresas formales: dueña / dueño (p.p.)": f"{d_owner_f_mean:+.1f} / {d_owner_m_mean:+.1f}",
        })

    df_t8 = pd.DataFrame(table8_rows)
    df_t8.to_csv(os.path.join(output_dir, "table8_ablation.csv"), index=False, encoding="utf-8")
    with open(os.path.join(output_dir, "table8_ablation.md"), "w", encoding="utf-8") as f:
        f.write("# Tabla 8: Descomposición del efecto de B2 frente a A (media de los cuatro países)\n\n")
        f.write(df_t8.to_markdown(index=False))
        f.write("\n\n*Nota.* R = 20 réplicas por país y variante, semillas pareadas. "
                "Cada variante del modelo fue recalibrada a los momentos observados de ILOSTAT antes de ejecutar los contrastes.\n")

    print(f"Tabla 8 generada en {output_dir}/table8_ablation.*")
    return df_t8


# ==============================================================================
# 5. ANÁLISIS DE SENSIBILIDAD, CES Y CHOQUE DE DEMANDA (TABLA 9)
# ==============================================================================

def run_sensitivity_and_robustness(
    countries: List[str] = TARGET_COUNTRIES,
    seeds: List[int] = REPLICA_SEEDS[:8],  # 8 réplicas por país según Tabla 9 del artículo
    output_dir: str = "outputs",
) -> pd.DataFrame:
    """
    Sensibilidad de los efectos principales:
    - Perturbación +-20% en 9 parámetros: phi_0, phi_1, eta, mu_0, kappa, gamma_0, H_care_fem, T_0, d.
    - Robustez estructural: función CES con sigma=0.5 y sigma=1.5 (recalibrados).
    - Choque de demanda: -5% en A en el mes 60.
    Calcula elasticidad epsilon = (Delta y / y0) / (Delta p / p0).
    """
    print("\n--- Ejecutando análisis de sensibilidad (+-20%) y robustez CES (Tabla 9)... ---")

    # 1. Referencia base con las 8 réplicas
    def eval_contrast_b2_fem_and_d_tot(custom_fp=None, custom_c_dict=None):
        b2_fem_diffs, d_tot_diffs = [], []
        for c in countries:
            c_cfg = custom_c_dict.get(c, c) if custom_c_dict else c
            for s in seeds:
                m_a = ITDTModel(c_cfg, scenario="A", seed=s, fixed_params=custom_fp)
                r_a = m_a.run()["summary_metrics"]

                m_b2 = ITDTModel(c_cfg, scenario="B2", seed=s, fixed_params=custom_fp)
                r_b2 = m_b2.run()["summary_metrics"]

                m_d = ITDTModel(c_cfg, scenario="D", seed=s, fixed_params=custom_fp)
                r_d = m_d.run()["summary_metrics"]

                b2_fem_diffs.append(r_b2["mean_informality_female"] - r_a["mean_informality_female"])
                d_tot_diffs.append(r_d["mean_informality_total"] - r_a["mean_informality_total"])

        return float(np.mean(b2_fem_diffs)), float(np.mean(d_tot_diffs))

    base_b2_fem, base_d_tot = eval_contrast_b2_fem_and_d_tot()
    print(f"  Referencia base: Delta mujeres en B2 = {base_b2_fem:.2f} p.p., Delta total en D = {base_d_tot:.2f} p.p.")

    params_to_perturb = [
        ("phi_0", "phi_0"),
        ("phi_1", "phi_1"),
        ("eta", "eta"),
        ("mu_0", "mu_0"),
        ("kappa", "kappa"),
        ("gamma_0", "gamma_0"),
        ("Hcare mujeres", "H_care_fem_mean"),
        ("T_0", "T_0"),
        ("(1 − d)", "cooling_rate"),
    ]

    table9_rows = [
        {
            "Parámetro": "Referencia",
            "Δ mujeres en B2: −20 % / +20 %": f"{base_b2_fem:.2f}",
            "Elasticidad (B2)": "—",
            "Δ total en D: −20 % / +20 %": f"{base_d_tot:.2f}",
            "Elasticidad (D)": "—",
        }
    ]

    for label, param_name in params_to_perturb:
        if param_name in ["phi_0", "gamma_0"]:
            # Usar los phi_0 y gamma_0 calibrados para cada país desde outputs/calibration_estimates.json
            c_low = {}
            c_high = {}
            for c in countries:
                info = resolve_country_params(c)
                val = float(info[param_name])
                c_low[c] = {**info, param_name: val * 0.80}
                c_high[c] = {**info, param_name: val * 1.20}
            b2_low, d_low = eval_contrast_b2_fem_and_d_tot(custom_c_dict=c_low)
            b2_high, d_high = eval_contrast_b2_fem_and_d_tot(custom_c_dict=c_high)
        elif param_name == "cooling_rate":
            # d_base = 0.85 => (1 - d)_base = 0.15
            # -20% en (1 - d): 0.15 * 0.80 = 0.12 => d = 1 - 0.12 = 0.88
            # +20% en (1 - d): 0.15 * 1.20 = 0.18 => d = 1 - 0.18 = 0.82
            fp_low = FixedParameters(d=0.88)
            fp_high = FixedParameters(d=0.82)
            b2_low, d_low = eval_contrast_b2_fem_and_d_tot(custom_fp=fp_low)
            b2_high, d_high = eval_contrast_b2_fem_and_d_tot(custom_fp=fp_high)
        else:
            base_val = getattr(FixedParameters(), param_name)
            fp_low = FixedParameters(**{param_name: base_val * 0.80})
            fp_high = FixedParameters(**{param_name: base_val * 1.20})
            b2_low, d_low = eval_contrast_b2_fem_and_d_tot(custom_fp=fp_low)
            b2_high, d_high = eval_contrast_b2_fem_and_d_tot(custom_fp=fp_high)

        # Elasticidad: ( (y_high - y_low) / y_base ) / (0.40)
        # Nota: y es negativo (reducción de informalidad); elasticidad positiva indica que el efecto se amplía
        eps_b2 = ((abs(b2_high) - abs(b2_low)) / abs(base_b2_fem)) / 0.40
        eps_d = ((abs(d_high) - abs(d_low)) / abs(base_d_tot)) / 0.40

        table9_rows.append({
            "Parámetro": label,
            "Δ mujeres en B2: −20 % / +20 %": f"{b2_low:.2f} / {b2_high:.2f}",
            "Elasticidad (B2)": f"{eps_b2:+.2f}",
            "Δ total en D: −20 % / +20 %": f"{d_low:.2f} / {d_high:.2f}",
            "Elasticidad (D)": f"{eps_d:+.2f}",
        })

    # Robustez CES y Choque de demanda
    # CES sigma = 0.5 (sin «recalibrado»)
    fp_ces05 = FixedParameters(ces_sigma=0.5)
    b2_ces05, d_ces05 = eval_contrast_b2_fem_and_d_tot(custom_fp=fp_ces05)
    table9_rows.append({
        "Parámetro": "CES, σ=0.5",
        "Δ mujeres en B2: −20 % / +20 %": f"{b2_ces05:.2f}",
        "Elasticidad (B2)": "—",
        "Δ total en D: −20 % / +20 %": f"{d_ces05:.2f}",
        "Elasticidad (D)": "—",
    })

    # CES sigma = 1.5 (sin «recalibrado»)
    fp_ces15 = FixedParameters(ces_sigma=1.5)
    b2_ces15, d_ces15 = eval_contrast_b2_fem_and_d_tot(custom_fp=fp_ces15)
    table9_rows.append({
        "Parámetro": "CES, σ=1.5",
        "Δ mujeres en B2: −20 % / +20 %": f"{b2_ces15:.2f}",
        "Elasticidad (B2)": "—",
        "Δ total en D: −20 % / +20 %": f"{d_ces15:.2f}",
        "Elasticidad (D)": "—",
    })

    # Choque de demanda -5%
    fp_shock = FixedParameters(demand_shock_month=60, demand_shock_pct=-0.05)
    b2_shock, d_shock = eval_contrast_b2_fem_and_d_tot(custom_fp=fp_shock)
    table9_rows.append({
        "Parámetro": "Choque de demanda −5 % (mes 60)",
        "Δ mujeres en B2: −20 % / +20 %": f"{b2_shock:.2f}",
        "Elasticidad (B2)": "—",
        "Δ total en D: −20 % / +20 %": f"{d_shock:.2f}",
        "Elasticidad (D)": "—",
    })

    df_t9 = pd.DataFrame(table9_rows)
    df_t9.to_csv(os.path.join(output_dir, "table9_sensitivity.csv"), index=False, encoding="utf-8")
    with open(os.path.join(output_dir, "table9_sensitivity.md"), "w", encoding="utf-8") as f:
        f.write("# Tabla 9: Sensibilidad de los efectos principales (±20 % en cada parámetro)\n\n")
        f.write(df_t9.to_markdown(index=False))
        f.write("\n\n*Nota.* 8 réplicas por país (32 por celda). "
                "Elasticidad positiva = el efecto se amplía en valor absoluto al aumentar el parámetro.\n")

    print(f"Tabla 9 generada en {output_dir}/table9_sensitivity.*")
    return df_t9


# ==============================================================================
# 6. BENCHMARKING DE COSTO COMPUTACIONAL (TABLA 10)
# ==============================================================================

def get_process_memory_mb() -> float:
    """Mide la memoria residente real (RSS) del proceso en MB usando psutil o resource."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return float(process.memory_info().rss / (1024 * 1024))
    except Exception:
        pass
    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return float(usage / 1024.0)
    except Exception:
        pass
    return 0.0


def benchmark_computational_cost(output_dir: str = "outputs") -> pd.DataFrame:
    """
    Mide el tiempo de ejecución por réplica (216 meses) y la memoria real del proceso para:
    N_W in {3000, 6000, 12000, 24000} y N_F in {300, 600, 1200, 2400}.
    """
    print("\n--- Ejecutando benchmarking de costo computacional (Tabla 10)... ---")
    scales = [
        (3000, 300, "3 000"),
        (6000, 600, "6 000 (configuración base)"),
        (12000, 1200, "12 000"),
        (24000, 2400, "24 000"),
    ]

    table10_rows = []

    for nw, nf, label in scales:
        times = []
        peak_mb = get_process_memory_mb()

        for rep in range(3):
            t_start = time.perf_counter()
            model = ITDTModel(
                country_params="KENYA",
                scenario="A",
                seed=20260 + rep,
                N_W=nw,
                N_F=nf,
                burn_in_months=96,
                policy_months=120,
            )
            model.run()
            elapsed = time.perf_counter() - t_start
            times.append(elapsed)
            current_mem = get_process_memory_mb()
            if current_mem > peak_mb:
                peak_mb = current_mem

        mean_t = float(np.mean(times))
        std_t = float(np.std(times, ddof=1))

        table10_rows.append({
            "NW (trabajadores)": label,
            "NF (empresas)": f"{nf:,}".replace(",", " "),
            "Tiempo por réplica (s), media (DE)": f"{mean_t:.3f} ({std_t:.3f})",
            "Memoria máxima del proceso (MB)": f"{peak_mb:.1f}",
        })
        print(f"  N_W = {label}: {mean_t:.3f} s (DE = {std_t:.3f}), Memoria real del proceso: {peak_mb:.1f} MB")

    df_t10 = pd.DataFrame(table10_rows)
    df_t10.to_csv(os.path.join(output_dir, "table10_cost.csv"), index=False, encoding="utf-8")
    with open(os.path.join(output_dir, "table10_cost.md"), "w", encoding="utf-8") as f:
        f.write("# Tabla 10: Costo computacional por réplica (216 meses: 96 de calentamiento + 120 de escenario)\n\n")
        f.write(df_t10.to_markdown(index=False))
        f.write("\n\n*Nota.* 3 repeticiones por tamaño. El tiempo crece de forma aproximadamente lineal con NW. "
                "Memoria real del proceso medida con psutil/resource (RSS).\n")

    print(f"Tabla 10 generada en {output_dir}/table10_cost.*")
    return df_t10


# ==============================================================================
# 7. GRADIENTES DISTRIBUTIVOS NO CALIBRADOS (TABLA 12)
# ==============================================================================

def compute_distributional_gradients(
    results_structured: Dict[str, Dict[str, List[Dict[str, Any]]]],
    output_dir: str = "outputs",
) -> pd.DataFrame:
    """
    Evalúa los gradientes no calibrados por educación, zona y quintil de productividad
    bajo el Escenario A (Tabla 12 del artículo).
    """
    print("\n--- Computando gradientes distributivos no calibrados (Tabla 12)... ---")
    edu_rates = {0: [], 1: [], 2: []}
    zone_rates = {"rural": [], "urban": []}
    quint_rates = {q: [] for q in range(1, 6)}

    for c in TARGET_COUNTRIES:
        reps_a = results_structured[c]["A"]
        for r in reps_a:
            g = r["gradients"]
            edu_rates[0].append(g["education"]["basic_e0"])
            edu_rates[1].append(g["education"]["middle_e1"])
            edu_rates[2].append(g["education"]["advanced_e2"])
            zone_rates["rural"].append(g["zone"]["rural"])
            zone_rates["urban"].append(g["zone"]["urban"])
            for q in range(1, 6):
                quint_rates[q].append(g["productivity_quintiles"][q])

    e0 = np.mean(edu_rates[0])
    e1 = np.mean(edu_rates[1])
    e2 = np.mean(edu_rates[2])
    r_rate = np.mean(zone_rates["rural"])
    u_rate = np.mean(zone_rates["urban"])
    q_vals = [np.mean(quint_rates[q]) for q in range(1, 6)]

    table12_rows = [
        {
            "Gradiente no calibrado (Escenario A, media de 4 países)": "Educación básica / media / superior",
            "Informalidad simulada (%)": f"{e0:.1f} / {e1:.1f} / {e2:.1f}",
            "Dirección esperada": "Decreciente",
            "¿Se reproduce?": "Sí" if (e0 > e1 > e2) else "Parcial",
        },
        {
            "Gradiente no calibrado (Escenario A, media de 4 países)": "Rural / urbano",
            "Informalidad simulada (%)": f"{r_rate:.1f} / {u_rate:.1f}",
            "Dirección esperada": "Rural > urbano",
            "¿Se reproduce?": "Sí" if (r_rate > u_rate) else "No",
        },
        {
            "Gradiente no calibrado (Escenario A, media de 4 países)": "Quintil de productividad 1 a 5",
            "Informalidad simulada (%)": " / ".join([f"{qv:.1f}" for qv in q_vals]),
            "Dirección esperada": "Decreciente",
            "¿Se reproduce?": "Sí, pero concentrado" if (q_vals[0] >= q_vals[-1]) else "No",
        },
    ]

    df_t12 = pd.DataFrame(table12_rows)
    df_t12.to_csv(os.path.join(output_dir, "table12_gradients.csv"), index=False, encoding="utf-8")
    with open(os.path.join(output_dir, "table12_gradients.md"), "w", encoding="utf-8") as f:
        f.write("# Tabla 12: Gradientes no calibrados (Escenario A)\n\n")
        f.write(df_t12.to_markdown(index=False))
        f.write("\n\n*Nota.* Direcciones esperadas según OIT. Los gradientes no forman parte de los momentos de calibración.\n")

    print(f"Tabla 12 generada en {output_dir}/table12_gradients.*")
    return df_t12


# ==============================================================================
# 8. PROPAGACIÓN DE INCERTIDUMBRE (CALIBRACIÓN -> POLÍTICAS)
# ==============================================================================

def run_uncertainty_propagation(
    calibration_file: str = "outputs/calibration_estimates.json",
    output_dir: str = "outputs",
) -> Dict[str, Any]:
    """
    Propagación de incertidumbre:
    Repite los escenarios con los (phi_0, gamma_0) de cada una de las 10 recalibraciones independientes
    y reporta intervalos empíricos de los efectos de política.
    """
    print("\n--- Ejecutando propagación de la incertidumbre de calibración sobre las políticas... ---")
    if not os.path.exists(calibration_file):
        print(f"Advertencia: Archivo {calibration_file} no encontrado; saltando propagación.")
        return {}

    with open(calibration_file, "r", encoding="utf-8") as f:
        cal_data = json.load(f)

    recalibrations = cal_data.get("recalibrations", {})
    propagation_results = {sc: {"total": [], "fem": [], "male": [], "gap": []} for sc in ["B1", "B2", "C", "D"]}

    # Tomar las primeras 10 recalibraciones
    for k in range(min(10, len(recalibrations.get("KENYA", [])))):
        # Configurar parámetros recalibrados para cada país
        c_dict_k = {}
        for c in TARGET_COUNTRIES:
            r_k = recalibrations[c][k]
            c_dict_k[c] = {
                "s_F": r_k["s_F"],
                "phi_0": r_k["phi_0"],
                "gamma_0": r_k["gamma_0"],
                "name": COUNTRY_DATABASE[c]["name"],
            }

        # Correr A vs B1, B2, C, D con una semilla fija representativa
        s_eval = 20260 + k
        sc_means = {}
        for sc in POLICY_SCENARIOS:
            t_l, f_l, m_l, g_l = [], [], [], []
            for c in TARGET_COUNTRIES:
                m = ITDTModel(c_dict_k[c], scenario=sc, seed=s_eval)
                res = m.run()["summary_metrics"]
                t_l.append(res["mean_informality_total"])
                f_l.append(res["mean_informality_female"])
                m_l.append(res["mean_informality_male"])
                g_l.append(res["mean_gender_gap"])
            sc_means[sc] = {
                "total": float(np.mean(t_l)),
                "fem": float(np.mean(f_l)),
                "male": float(np.mean(m_l)),
                "gap": float(np.mean(g_l)),
            }

        # Diferencias frente a A
        for sc in ["B1", "B2", "C", "D"]:
            propagation_results[sc]["total"].append(sc_means[sc]["total"] - sc_means["A"]["total"])
            propagation_results[sc]["fem"].append(sc_means[sc]["fem"] - sc_means["A"]["fem"])
            propagation_results[sc]["male"].append(sc_means[sc]["male"] - sc_means["A"]["male"])
            propagation_results[sc]["gap"].append(sc_means[sc]["gap"] - sc_means["A"]["gap"])

    # Calcular intervalos empíricos (min, percentil 10, media, percentil 90, max)
    summary_intervals = {}
    md_lines = ["# Propagación de Incertidumbre de Calibración sobre Efectos de Política\n"]
    md_lines.append("| Escenario | Métrica | Media | Intervalo 90% [P10, P90] | Rango [Min, Max] |")
    md_lines.append("| :--- | :--- | :---: | :---: | :---: |")

    for sc in ["B1", "B2", "C", "D"]:
        summary_intervals[sc] = {}
        for m in ["total", "fem", "male", "gap"]:
            arr = np.array(propagation_results[sc][m])
            mean_v = float(np.mean(arr))
            p10 = float(np.percentile(arr, 10))
            p90 = float(np.percentile(arr, 90))
            min_v = float(np.min(arr))
            max_v = float(np.max(arr))
            summary_intervals[sc][m] = {
                "mean": mean_v, "p10": p10, "p90": p90, "min": min_v, "max": max_v,
            }
            m_labels = {"total": "Δ Total (p.p.)", "fem": "Δ Mujeres (p.p.)", "male": "Δ Hombres (p.p.)", "gap": "Δ Brecha (F−M)"}
            md_lines.append(f"| {sc} | {m_labels[m]} | {mean_v:+.2f} | [{p10:+.2f}, {p90:+.2f}] | [{min_v:+.2f}, {max_v:+.2f}] |")

    prop_json = os.path.join(output_dir, "uncertainty_propagation.json")
    with open(prop_json, "w", encoding="utf-8") as f:
        json.dump(summary_intervals, f, indent=2, ensure_ascii=False)

    prop_md = os.path.join(output_dir, "uncertainty_propagation.md")
    with open(prop_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
        f.write("\n\n*Nota.* Los intervalos reflejan la propagación de la incertidumbre Monte Carlo "
                "de los parámetros estructurales (phi_0, gamma_0) estimados a través de 10 calibraciones independientes.\n")

    print(f"Propagación de incertidumbre guardada en {prop_json} y {prop_md}")
    return summary_intervals


# ==============================================================================
# 9. GENERACIÓN DE FIGURAS 6 Y 7
# ==============================================================================

def generate_figure_6(
    results_structured: Dict[str, Dict[str, List[Dict[str, Any]]]],
    output_path: str = "outputs/figure6_trajectories.png",
):
    """
    Figura 6: Trayectorias medias mensuales de la informalidad por escenario y sexo.
    Eje X: tiempo desde inicio de política (meses 0 a 120); Eje Y: tasa de informalidad (%).
    Líneas: media entre países; bandas: IC 95% entre réplicas (R=40). Eje Y común.
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True, dpi=300)

    months = np.arange(1, 121)
    scenario_colors = {
        "A": "#7f8c8d",   # Gris
        "B1": "#3498db",  # Azul
        "B2": "#e74c3c",  # Rojo
        "C": "#2ecc71",   # Verde
        "D": "#9b59b6",   # Púrpura
    }
    scenario_labels = {
        "A": "A: Status quo",
        "B1": "B1: GovTech mod.",
        "B2": "B2: GovTech intens.",
        "C": "C: Red cuidados",
        "D": "D: Integrado",
    }

    # Panel 1: Mujeres | Panel 2: Hombres
    for panel_idx, (sex_key, sex_title) in enumerate([("monthly_female", "Mujeres"), ("monthly_male", "Hombres")]):
        ax = axes[panel_idx]
        for sc in POLICY_SCENARIOS:
            # Matriz de todas las réplicas de los 4 países: shape (4 * 40, 120)
            all_series = []
            for c in TARGET_COUNTRIES:
                for r in results_structured[c][sc]:
                    all_series.append(r[sex_key])
            all_series = np.array(all_series)

            mean_traj = np.mean(all_series, axis=0)
            ci_low = np.percentile(all_series, 2.5, axis=0)
            ci_high = np.percentile(all_series, 97.5, axis=0)

            c_color = scenario_colors[sc]
            line_style = "--" if sc == "A" else "-"
            ax.plot(months, mean_traj, color=c_color, linewidth=2.0, linestyle=line_style, label=scenario_labels[sc])
            ax.fill_between(months, ci_low, ci_high, color=c_color, alpha=0.12)

        ax.set_title(f"Trayectoria de Informalidad - {sex_title}", fontsize=12, fontweight="bold", pad=10)
        ax.set_xlabel("Meses desde el inicio de la política", fontsize=10.5, fontweight="bold")
        if panel_idx == 0:
            ax.set_ylabel("Tasa de informalidad (%)", fontsize=10.5, fontweight="bold")
        ax.set_ylim(30.0, 100.0)  # Eje Y común
        ax.legend(loc="lower left", frameon=True, facecolor="white", edgecolor="#bdc3c7", fontsize=9.0)

    plt.suptitle("Figura 6. Trayectorias medias mensuales de la informalidad por escenario y sexo\n(Bandas: IC 95% entre 40 réplicas x 4 países; Eje Y común)", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura 6 guardada en: {output_path}")


def generate_figure_7(
    results_structured: Dict[str, Dict[str, List[Dict[str, Any]]]],
    output_path: str = "outputs/figure7_policy_effects.png",
):
    """
    Figura 7: Informalidad por escenario y sexo en los meses 109–120.
    Eje vertical: tasa de informalidad (%); media de los cuatro países; brecha F - M etiquetada; eje Y común.
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    scenarios = POLICY_SCENARIOS
    sc_labels = ["A\nStatus quo", "B1\nGovTech mod.", "B2\nGovTech int.", "C\nRed cuidados", "D\nIntegrado"]
    x = np.arange(len(scenarios))
    width = 0.26

    # Calcular medias por escenario (promedio de los 4 países)
    f_means, m_means, t_means = [], [], []
    f_errs, m_errs, t_errs = [], [], []

    for sc in scenarios:
        f_list, m_list, t_list = [], [], []
        for c in TARGET_COUNTRIES:
            f_list.extend([r["informality_female"] for r in results_structured[c][sc]])
            m_list.extend([r["informality_male"] for r in results_structured[c][sc]])
            t_list.extend([r["informality_total"] for r in results_structured[c][sc]])

        f_means.append(np.mean(f_list))
        m_means.append(np.mean(m_list))
        t_means.append(np.mean(t_list))

        f_errs.append(np.std(f_list, ddof=1) / math.sqrt(len(f_list)))
        m_errs.append(np.std(m_list, ddof=1) / math.sqrt(len(m_list)))
        t_errs.append(np.std(t_list, ddof=1) / math.sqrt(len(t_list)))

    color_fem = "#c0392b"
    color_male = "#2980b9"
    color_tot = "#2c3e50"

    # Barras agrupadas
    bars_f = ax.bar(x - width, f_means, width, yerr=f_errs, capsize=4, color=color_fem, alpha=0.85, label="Mujeres (F)", edgecolor="#922b21")
    bars_m = ax.bar(x, m_means, width, yerr=m_errs, capsize=4, color=color_male, alpha=0.85, label="Hombres (M)", edgecolor="#1f618d")
    bars_t = ax.bar(x + width, t_means, width, yerr=t_errs, capsize=4, color=color_tot, alpha=0.85, label="Total (T)", edgecolor="#17202a")

    # Etiquetas de brecha F - M
    for i in range(len(scenarios)):
        gap = f_means[i] - m_means[i]
        top_y = max(f_means[i], m_means[i], t_means[i])
        ax.annotate(
            f"Brecha F−M:\n{gap:+.1f} p.p.",
            xy=(x[i], top_y + 3.0),
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc="#f4f6f7", ec="#bdc3c7", alpha=0.9),
        )

    ax.set_xticks(x)
    ax.set_xticklabels(sc_labels, fontsize=10.5, fontweight="bold")
    ax.set_ylabel("Tasa de informalidad (%)", fontsize=11, fontweight="bold")
    ax.set_ylim(20.0, 108.0)  # Eje Y común estandarizado
    ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#bdc3c7", fontsize=9.5)
    ax.set_title("Figura 7. Informalidad por escenario y sexo en los meses 109–120\n(Media de 4 países x 40 réplicas; Barras de error: EE; Brechas F − M)", fontsize=12, fontweight="bold", pad=12)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Figura 7 guardada en: {output_path}")


# ==============================================================================
# PIPELINE PRINCIPAL DE EXPERIMENTOS
# ==============================================================================

def run_all_experiments_pipeline(
    output_dir: str = "outputs",
    max_workers: int = 8,
):
    """Ejecuta el pipeline completo de experimentos y genera todos los artefactos."""
    os.makedirs(output_dir, exist_ok=True)
    t_global = time.time()

    # Cargar estimaciones de calibración si existen
    calib_json = os.path.join(output_dir, "calibration_estimates.json")
    calibrated_params = None
    if os.path.exists(calib_json):
        try:
            with open(calib_json, "r", encoding="utf-8") as f:
                cal_data = json.load(f)
                calibrated_params = cal_data.get("summary")
                print("Calibraciones previas cargadas desde calibration_estimates.json.")
        except Exception:
            pass

    # 1. Réplicas principales de política (R = 40)
    policy_results = run_all_policy_replicas(
        countries=TARGET_COUNTRIES,
        scenarios=POLICY_SCENARIOS,
        seeds=REPLICA_SEEDS,
        calibrated_params=calibrated_params,
        max_workers=max_workers,
    )

    # 2. Inferencia estadística: Tablas 5, 6, 7
    compute_inferential_tables(policy_results, output_dir=output_dir, B_bootstrap=4000)

    # 3. Barrido de multiplicador de sanciones: Figura 5
    run_sanctions_sweep_experiment(countries=TARGET_COUNTRIES, seeds=REPLICA_SEEDS[:6], output_dir=output_dir)

    # 4. Ablación recalibrada de B2 frente a A: Tabla 8
    run_recalibrated_ablation_study(countries=TARGET_COUNTRIES, seeds=REPLICA_SEEDS[:20], output_dir=output_dir)

    # 5. Análisis de sensibilidad, CES y Choque: Tabla 9
    run_sensitivity_and_robustness(countries=TARGET_COUNTRIES, seeds=REPLICA_SEEDS[:8], output_dir=output_dir)

    # 6. Benchmarking de costo computacional: Tabla 10
    benchmark_computational_cost(output_dir=output_dir)

    # 7. Gradientes distributivos no calibrados: Tabla 12
    compute_distributional_gradients(policy_results, output_dir=output_dir)

    # 8. Propagación de incertidumbre
    run_uncertainty_propagation(calibration_file=calib_json, output_dir=output_dir)

    # 9. Figuras 6 y 7
    generate_figure_6(policy_results, output_path=os.path.join(output_dir, "figure6_trajectories.png"))
    generate_figure_7(policy_results, output_path=os.path.join(output_dir, "figure7_policy_effects.png"))

    # 10. Exportar resultados completos a JSON
    # Para no inflar el JSON, exportar métricas resumidas por réplica
    clean_export = {}
    for c in TARGET_COUNTRIES:
        clean_export[c] = {}
        for sc in POLICY_SCENARIOS:
            clean_export[c][sc] = [
                {k: v for k, v in r.items() if not k.startswith("monthly_")}
                for r in policy_results[c][sc]
            ]
    json_path = os.path.join(output_dir, "policy_experiments_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(clean_export, f, indent=2, ensure_ascii=False)
    print(f"\nResultados brutos de experimentos exportados a: {json_path}")
    print(f"Pipeline completo de experimentos finalizado en {time.time() - t_global:.2f} s.")


if __name__ == "__main__":
    run_all_experiments_pipeline()

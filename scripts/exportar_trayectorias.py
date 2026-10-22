#!/usr/bin/env python3
"""
scripts/exportar_trayectorias.py

Ejecuta el modelo ITDT canónico para los 4 países x 5 escenarios con las 40 réplicas (R=40, semillas 20260-20299)
y exporta en outputs/trayectorias_mensuales.json las series mensuales reales (meses 1 a 120 de la política)
con su media e Intervalo de Confianza al 95%.

Comprueba estrictamente que la media de los meses 109-120 coincide con policy_experiments_results.json (+-0.01 p.p.).
NO MODIFICA itdt/.
"""

import os
import json
import time
import math
from typing import Dict, Any, List, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor
import sys
sys.path.insert(0, os.path.abspath("."))
import numpy as np

from itdt.model import ITDTModel
from itdt.parameters import COUNTRY_DATABASE

TARGET_COUNTRIES = ["KENYA", "NIGERIA", "INDIA", "BANGLADESH"]
POLICY_SCENARIOS = ["A", "B1", "B2", "C", "D"]
REPLICA_SEEDS = list(range(20260, 20300))  # R = 40 réplicas


def run_replica_task(args: Tuple[str, str, int, Dict[str, Any]]) -> Dict[str, Any]:
    c_key, sc, seed, c_params = args
    model = ITDTModel(
        country_params=c_params,
        scenario=sc,
        seed=seed,
        burn_in_months=96,
        policy_months=120,
    )
    result = model.run()
    
    # Extraer los 120 meses de política (meses 96 a 215 del histórico)
    policy_history = result["monthly_series"][96:]
    assert len(policy_history) == 120, f"Se esperaban 120 meses de política, se obtuvieron {len(policy_history)}"
    
    records = []
    for m_idx, m_data in enumerate(policy_history, start=1):
        f_count = m_data.get("formal_firms_count", 0)
        # N_F = 600 firmas en el modelo canónico (parameters.py)
        formal_firms_ratio = f_count / 600.0
        records.append({
            "month": m_idx,
            "informality_total": m_data["informality_total"],
            "informality_female": m_data["informality_female"],
            "informality_male": m_data["informality_male"],
            "gender_gap": m_data["gender_gap"],
            "formal_firms_ratio": formal_firms_ratio,
            "annual_exit_rate": m_data["annual_exit_rate"],
            "fiscal_revenue": m_data["fiscal_revenue"],
            "corporate_tax_revenue": m_data.get("corporate_tax_revenue", 0.0),
            "labor_contributions_revenue": m_data.get("labor_contributions_revenue", 0.0),
            "gini_index": m_data.get("gini_index", 0.0),
        })
        
    return {
        "country": c_key,
        "scenario": sc,
        "seed": seed,
        "records": records,
        "summary_informality_total": result["summary_metrics"]["mean_informality_total"],
    }


def compute_ci(data: List[float], confidence: float = 0.95) -> Tuple[float, float, float]:
    """Calcula media e IC 95% usando distribución normal/t asintótica."""
    arr = np.array(data, dtype=float)
    mean = float(np.mean(arr))
    n = len(arr)
    if n < 2:
        return mean, mean, mean
    std = float(np.std(arr, ddof=1))
    sem = std / math.sqrt(n)
    h = 1.96 * sem
    return mean, mean - h, mean + h


def main():
    t0 = time.time()
    print("=== EXPORTADOR DE TRAYECTORIAS MENSUALES DEL MODELO ITDT ===")
    
    calib_path = "outputs/calibration_estimates.json"
    if not os.path.exists(calib_path):
        raise FileNotFoundError(f"No se encontró {calib_path}")
        
    with open(calib_path, "r", encoding="utf-8") as f:
        calib_data = json.load(f)["summary"]
        
    tasks = []
    for c in TARGET_COUNTRIES:
        c_params = {
            "s_F": calib_data[c]["s_F"],
            "phi_0": calib_data[c]["phi_0"],
            "gamma_0": calib_data[c]["gamma_0"],
            "name": COUNTRY_DATABASE[c]["name"],
        }
        for sc in POLICY_SCENARIOS:
            for seed in REPLICA_SEEDS:
                tasks.append((c, sc, seed, c_params))
                
    total_runs = len(tasks)
    print(f"Total de simulaciones a ejecutar: {total_runs} (4 países x 5 escenarios x 40 réplicas)")
    
    max_workers = min(14, os.cpu_count() or 4)
    print(f"Ejecutando en paralelo con {max_workers} procesos...")
    
    # Agrupar resultados por (country, scenario)
    grouped: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
        c: {sc: [] for sc in POLICY_SCENARIOS} for c in TARGET_COUNTRIES
    }
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for idx, res in enumerate(executor.map(run_replica_task, tasks), start=1):
            grouped[res["country"]][res["scenario"]].append(res)
            if idx % 80 == 0 or idx == total_runs:
                print(f"  Progreso: {idx}/{total_runs} corridas completadas ({idx/total_runs*100:.1f}%)")
                
    print(f"Simulaciones finalizadas en {time.time() - t0:.2f} s. Procesando agregaciones mensuales...")
    
    # Cargar policy_experiments_results.json para la verificación obligatoria (+-0.01 p.p.)
    exp_path = "outputs/policy_experiments_results.json"
    with open(exp_path, "r", encoding="utf-8") as f:
        official_results = json.load(f)
        
    output_trajectories: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
        c: {sc: [] for sc in POLICY_SCENARIOS} for c in TARGET_COUNTRIES
    }
    
    validation_failures = []
    
    for c in TARGET_COUNTRIES:
        for sc in POLICY_SCENARIOS:
            replicas = grouped[c][sc]
            assert len(replicas) == 40
            
            # Para cada mes de 1 a 120
            monthly_aggregated = []
            for m in range(1, 121):
                # Recopilar valores de las 40 réplicas en el mes m
                inf_totals = [r["records"][m-1]["informality_total"] for r in replicas]
                inf_females = [r["records"][m-1]["informality_female"] for r in replicas]
                inf_males = [r["records"][m-1]["informality_male"] for r in replicas]
                gaps = [r["records"][m-1]["gender_gap"] for r in replicas]
                firm_ratios = [r["records"][m-1]["formal_firms_ratio"] for r in replicas]
                exit_rates = [r["records"][m-1]["annual_exit_rate"] for r in replicas]
                revenues = [r["records"][m-1]["fiscal_revenue"] for r in replicas]
                corp_revs = [r["records"][m-1]["corporate_tax_revenue"] for r in replicas]
                labor_revs = [r["records"][m-1]["labor_contributions_revenue"] for r in replicas]
                ginis = [r["records"][m-1]["gini_index"] for r in replicas]
                
                m_tot, m_tot_l, m_tot_h = compute_ci(inf_totals)
                m_f, m_f_l, m_f_h = compute_ci(inf_females)
                m_m, m_m_l, m_m_h = compute_ci(inf_males)
                m_gap, m_gap_l, m_gap_h = compute_ci(gaps)
                m_fr, m_fr_l, m_fr_h = compute_ci(firm_ratios)
                m_ex, m_ex_l, m_ex_h = compute_ci(exit_rates)
                m_rev, m_rev_l, m_rev_h = compute_ci(revenues)
                m_corp, m_corp_l, m_corp_h = compute_ci(corp_revs)
                m_lab, m_lab_l, m_lab_h = compute_ci(labor_revs)
                m_gi, m_gi_l, m_gi_h = compute_ci(ginis)
                
                monthly_aggregated.append({
                    "month": m,
                    "informality_total": round(m_tot, 2),
                    "informality_total_ci": [round(m_tot_l, 2), round(m_tot_h, 2)],
                    "informality_female": round(m_f, 2),
                    "informality_female_ci": [round(m_f_l, 2), round(m_f_h, 2)],
                    "informality_male": round(m_m, 2),
                    "informality_male_ci": [round(m_m_l, 2), round(m_m_h, 2)],
                    "gender_gap": round(m_gap, 2),
                    "gender_gap_ci": [round(m_gap_l, 2), round(m_gap_h, 2)],
                    "formal_firms_ratio": round(m_fr, 4),
                    "formal_firms_ratio_ci": [round(m_fr_l, 4), round(m_fr_h, 4)],
                    "annual_exit_rate": round(m_ex, 2),
                    "annual_exit_rate_ci": [round(m_ex_l, 2), round(m_ex_h, 2)],
                    "fiscal_revenue": round(m_rev, 2),
                    "fiscal_revenue_ci": [round(m_rev_l, 2), round(m_rev_h, 2)],
                    "corporate_tax_revenue": round(m_corp, 2),
                    "corporate_tax_revenue_ci": [round(m_corp_l, 2), round(m_corp_h, 2)],
                    "labor_contributions_revenue": round(m_lab, 2),
                    "labor_contributions_revenue_ci": [round(m_lab_l, 2), round(m_lab_h, 2)],
                    "gini_index": round(m_gi, 4),
                    "gini_index_ci": [round(m_gi_l, 4), round(m_gi_h, 4)],
                })
                
            output_trajectories[c][sc] = monthly_aggregated
            
            # Verificación meses 109 a 120 (últimos 12 meses)
            # Calcular la media sobre meses 109-120
            last12_means = [monthly_aggregated[m-1]["informality_total"] for m in range(109, 121)]
            sim_last12_mean = float(np.mean(last12_means))
            
            # Cifra oficial en policy_experiments_results.json
            official_rep_totals = [r["informality_total"] for r in official_results[c][sc]]
            official_mean = float(np.mean(official_rep_totals))
            
            diff = abs(sim_last12_mean - official_mean)
            print(f"[{c} - {sc}] Media M109-120: {sim_last12_mean:.2f} % | Oficial: {official_mean:.2f} % | Diff: {diff:.4f} p.p.")
            
            if diff > 0.01:
                validation_failures.append((c, sc, sim_last12_mean, official_mean, diff))
                
    if validation_failures:
        print("\nERRORES DE CONGRUENCIA DETECTADOS (> 0.01 p.p.):")
        for f in validation_failures:
            print(f"  {f[0]} Escenario {f[1]}: Simulado={f[2]:.4f}%, Oficial={f[3]:.4f}%, Diff={f[4]:.4f} p.p.")
        raise RuntimeError("Fallo la verificación de congruencia con policy_experiments_results.json")
        
    print("\nTODAS LAS 20 COMBINACIONES (4 países x 5 escenarios) COINCIDEN DENTRO DE +-0.01 p.p.")
    
    out_file = "outputs/trayectorias_mensuales.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_trajectories, f, indent=2, ensure_ascii=False)
        
    print(f"Archivo exportado con éxito: {out_file} ({os.path.getsize(out_file) / 1024:.1f} KB)")
    print(f"Tiempo total: {time.time() - t0:.2f} s")


if __name__ == "__main__":
    main()

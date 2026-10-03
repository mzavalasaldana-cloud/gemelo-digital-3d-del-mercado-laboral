"""
itdt.cli: Interfaz unificada de línea de comandos para orquestar la replicación del modelo ITDT.
Soporta todos los objetivos del Makefile:
smoke, calibrate, calib_se, loco, baselines, sweep, scenarios, mechanism, sensitivity, cost y all.
"""

import sys
import os
import shutil
import time
from typing import Dict, Any

from itdt.calibrate import (
    run_full_calibration_pipeline,
    export_calibration_artifacts_from_summary,
)
from itdt.loco import (
    run_loco_cross_validation,
    run_structural_baselines_table4,
    generate_loco_inputs_documentation,
)
from itdt.experiments import (
    run_all_policy_replicas,
    compute_inferential_tables,
    run_sanctions_sweep_experiment,
    run_recalibrated_ablation_study,
    run_sensitivity_and_robustness,
    benchmark_computational_cost,
    compute_distributional_gradients,
    run_uncertainty_propagation,
    generate_figure_6,
    generate_figure_7,
    TARGET_COUNTRIES,
    POLICY_SCENARIOS,
    REPLICA_SEEDS,
)
from itdt.model import ITDTModel


def cmd_smoke():
    """Ejecuta una corrida corta y los tests unitarios en menos de 1 minuto."""
    print("=== [ITDT: SMOKE TEST] ===")
    t0 = time.time()
    import pytest
    ret = pytest.main(["-q", "tests/test_itdt.py"])
    if ret != 0:
        print("Falla en pruebas unitarias.")
        sys.exit(ret)

    # Corrida rápida de integración
    print("Simulando réplica de prueba rápida (12 meses)...")
    m = ITDTModel(
        country_params="KENYA",
        scenario="A",
        seed=101,
        burn_in_months=6,
        policy_months=6,
        N_W=1000,
        N_F=100,
    )
    res = m.run()
    assert "summary_metrics" in res
    elapsed = time.time() - t0
    print(f"[OK] Smoke test completado con éxito en {elapsed:.2f} s (< 1 minuto).")


def cmd_calibrate():
    """Ejecuta la calibración SMM baseline (bisección anidada 9x9, S=6)."""
    print("=== [ITDT: CALIBRATE (Tabla 2, Tabla 11, Figura 4)] ===")
    t0 = time.time()
    run_full_calibration_pipeline(output_dir="outputs", num_independent_sets=0)
    print(f"[OK] Calibración baseline finalizada en {time.time() - t0:.2f} s.")


def cmd_calib_se():
    """Ejecuta la estimación de errores estándar (10 conjuntos independientes de semillas)."""
    print("=== [ITDT: CALIB_SE (10 calibraciones independientes)] ===")
    t0 = time.time()
    run_full_calibration_pipeline(output_dir="outputs", num_independent_sets=10)
    print(f"[OK] Calibración con errores estándar finalizada en {time.time() - t0:.2f} s.")


def cmd_loco():
    """Ejecuta la validación fuera de muestra Leave-One-Country-Out (Tabla 3 y loco_insumos.md)."""
    print("=== [ITDT: LOCO (Tabla 3)] ===")
    t0 = time.time()
    run_loco_cross_validation(output_dir="outputs")
    generate_loco_inputs_documentation(output_dir="outputs")
    print(f"[OK] Validación LOCO finalizada en {time.time() - t0:.2f} s.")


def cmd_baselines():
    """Ejecuta los modelos estructurales de referencia dentro de muestra E1–E4 (Tabla 4)."""
    print("=== [ITDT: BASELINES (Tabla 4)] ===")
    t0 = time.time()
    run_structural_baselines_table4(output_dir="outputs")
    print(f"[OK] Modelos de referencia E1–E4 finalizados en {time.time() - t0:.2f} s.")


def cmd_sweep():
    """Ejecuta el barrido de sanciones 1.0 a 4.0 bajo B1 (Figura 5 y sanctions_sweep_data.csv)."""
    print("=== [ITDT: SWEEP (Figura 5)] ===")
    t0 = time.time()
    run_sanctions_sweep_experiment(output_dir="outputs")
    print(f"[OK] Barrido de sanciones finalizado en {time.time() - t0:.2f} s.")


def cmd_scenarios():
    """Ejecuta los escenarios de política A, B1, B2, C, D (Tablas 5, 6, 7, Figuras 6 y 7)."""
    print("=== [ITDT: SCENARIOS (Tablas 5, 6, 7, Figuras 6 y 7)] ===")
    t0 = time.time()
    # Cargar parámetros calibrados
    import json
    calib_json = os.path.join("outputs", "calibration_estimates.json")
    calibrated_params = None
    if os.path.exists(calib_json):
        with open(calib_json, "r", encoding="utf-8") as f:
            calibrated_params = json.load(f).get("summary")

    policy_results = run_all_policy_replicas(
        countries=TARGET_COUNTRIES,
        scenarios=POLICY_SCENARIOS,
        seeds=REPLICA_SEEDS,
        calibrated_params=calibrated_params,
        max_workers=8,
    )
    compute_inferential_tables(policy_results, output_dir="outputs", B_bootstrap=4000)
    generate_figure_6(policy_results, output_path="outputs/figure6_trajectories.png")
    generate_figure_7(policy_results, output_path="outputs/figure7_policy_effects.png")
    print(f"[OK] Escenarios de política finalizados en {time.time() - t0:.2f} s.")
    return policy_results


def cmd_mechanism():
    """Ejecuta la ablación de B2 frente a A con recalibración de cada variante (Tabla 8)."""
    print("=== [ITDT: MECHANISM / ABLATION (Tabla 8)] ===")
    t0 = time.time()
    run_recalibrated_ablation_study(output_dir="outputs")
    print(f"[OK] Estudio de mecanismo y ablación finalizado en {time.time() - t0:.2f} s.")


def cmd_sensitivity():
    """Ejecuta el análisis de sensibilidad +-20%, CES y choque de demanda (Tabla 9)."""
    print("=== [ITDT: SENSITIVITY (Tabla 9)] ===")
    t0 = time.time()
    run_sensitivity_and_robustness(output_dir="outputs")
    print(f"[OK] Análisis de sensibilidad y robustez finalizado en {time.time() - t0:.2f} s.")


def cmd_cost():
    """Ejecuta el benchmarking de costo computacional (Tabla 10)."""
    print("=== [ITDT: COST (Tabla 10)] ===")
    t0 = time.time()
    benchmark_computational_cost(output_dir="outputs")
    print(f"[OK] Benchmarking de costo computacional finalizado en {time.time() - t0:.2f} s.")


def cmd_all():
    """
    Regenera outputs/ desde cero ejecutando el pipeline de replicación completo
    e informa cuánto tardó en total.
    """
    print("======================================================================")
    print(" ITDT: REPLICACIÓN COMPLETA DESDE CERO (make all)")
    print("======================================================================")
    t_global_start = time.time()

    # 1. Limpieza rigurosa de outputs/
    output_dir = "outputs"
    if os.path.exists(output_dir):
        print("Limpiando directorio outputs/ previo...")
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # 2. Calibración SMM baseline + EE (Tablas 2 y 11, Figura 4)
    cmd_calib_se()

    # 3. Validación fuera de muestra LOCO y modelos de referencia (Tablas 3 y 4)
    cmd_loco()
    cmd_baselines()

    # 4. Escenarios de política principales (Tablas 5, 6, 7, Figuras 6 y 7)
    policy_results = cmd_scenarios()

    # 5. Barrido de multiplicador de sanciones (Figura 5)
    cmd_sweep()

    # 6. Estudio de mecanismo / ablación recalibrada (Tabla 8)
    cmd_mechanism()

    # 7. Sensibilidad, CES y choque de demanda (Tabla 9)
    cmd_sensitivity()

    # 8. Costo computacional (Tabla 10)
    cmd_cost()

    # 9. Gradientes no calibrados (Tabla 12) y propagación de incertidumbre
    import json
    compute_distributional_gradients(policy_results, output_dir=output_dir)
    run_uncertainty_propagation(calibration_file="outputs/calibration_estimates.json", output_dir=output_dir)

    # Exportar JSON bruto consolidado
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

    total_elapsed = time.time() - t_global_start
    mins = int(total_elapsed // 60)
    secs = int(total_elapsed % 60)

    print("======================================================================")
    print(f" REPLICACIÓN COMPLETA FINALIZADA CON ÉXITO")
    print(f" Tiempo total de ejecución: {total_elapsed:.2f} s ({mins} min {secs} s)")
    print(f" Todos los artefactos fueron regenerados desde cero en: outputs/")
    print("======================================================================")


CLI_DISPATCH = {
    "smoke": cmd_smoke,
    "calibrate": cmd_calibrate,
    "calib_se": cmd_calib_se,
    "loco": cmd_loco,
    "baselines": cmd_baselines,
    "sweep": cmd_sweep,
    "scenarios": cmd_scenarios,
    "mechanism": cmd_mechanism,
    "sensitivity": cmd_sensitivity,
    "cost": cmd_cost,
    "all": cmd_all,
}


def main():
    if len(sys.argv) < 2:
        print("Uso: python -m itdt.cli <target>")
        print(f"Objetivos válidos: {list(CLI_DISPATCH.keys())}")
        sys.exit(1)

    target = sys.argv[1].strip().lower()
    if target not in CLI_DISPATCH:
        print(f"Error: Objetivo desconocido '{target}'.")
        print(f"Objetivos válidos: {list(CLI_DISPATCH.keys())}")
        sys.exit(1)

    CLI_DISPATCH[target]()


if __name__ == "__main__":
    main()

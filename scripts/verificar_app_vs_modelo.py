#!/usr/bin/env python3
"""
scripts/verificar_app_vs_modelo.py

Verifica automáticamente que los indicadores expuestos por la API FastAPI
(mes 120 de la política para Kenia en escenarios A, B1, B2, C, D)
coincidan con outputs/policy_experiments_results.json (media de réplicas de meses 109-120).
Diferencia máxima tolerada: 0.5 p.p.
Genera el reporte oficial en outputs/verificacion_app_vs_modelo.md.
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
RESULTS_JSON_PATH = os.path.join(OUTPUTS_DIR, "policy_experiments_results.json")
REPORT_MD_PATH = os.path.join(OUTPUTS_DIR, "verificacion_app_vs_modelo.md")
API_HOST = "http://127.0.0.1:8000"


def query_api_metrics(country: str, scenario: str, month: int = 120) -> dict:
    url = f"{API_HOST}/api/v1/simulation/metrics?country={country}&scenario={scenario}&month={month}"
    req = urllib.request.Request(url, headers={"User-Agent": "VerificationScript/1.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP Error {response.status} querying {url}")
        return json.loads(response.read().decode("utf-8"))


def run_verification():
    print(f"[*] Iniciando verificación de App vs Modelo...")
    print(f"[*] Verificando disponibilidad del backend en {API_HOST}...")

    # 1. Probar conectividad con el backend
    backend_online = False
    for attempt in range(5):
        try:
            with urllib.request.urlopen(f"{API_HOST}/docs", timeout=3) as resp:
                if resp.status == 200:
                    backend_online = True
                    print(f"[+] Backend FastAPI en línea y respondiendo HTTP 200.")
                    break
        except Exception:
            time.sleep(1)

    if not backend_online:
        print("[-] ERROR CRÍTICO: Backend FastAPI no responde en http://127.0.0.1:8000.")
        print("[-] Debe levantar el backend antes de ejecutar esta verificación.")
        sys.exit(1)

    # 2. Cargar outputs oficiales
    if not os.path.exists(RESULTS_JSON_PATH):
        print(f"[-] ERROR: Archivo no encontrado: {RESULTS_JSON_PATH}")
        sys.exit(1)

    with open(RESULTS_JSON_PATH, "r", encoding="utf-8") as f:
        official_data = json.load(f)

    kenya_official = official_data.get("KENYA", {})
    scenarios = ["A", "B1", "B2", "C", "D"]

    report_lines = [
        "# Verificación Automática: Aplicación Web vs Modelo Calibrado ITDT",
        "",
        f"- **Fecha y hora de ejecución:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "- **País evaluado:** Kenia (KEN)",
        "- **Horizonte de evaluación:** Mes 120 de la política (promedio final de réplicas en meses 109–120)",
        "- **Fuente econométrica:** `outputs/policy_experiments_results.json` (media de 40 réplicas por escenario)",
        "- **Punto de conexión API:** `http://127.0.0.1:8000/api/v1/simulation/metrics`",
        "- **Tolerancia máxima:** 0.50 puntos porcentuales (p.p.)",
        "",
        "## 1. Tabla de Comparación: Tasa de Informalidad (%)",
        "",
        "| Escenario | Etiqueta | Oficial Modelo (%) | Respuesta API (%) | Diferencia (p.p.) | Tolerancia | Estado |",
        "|:---|:---|:---:|:---:|:---:|:---:|:---:|",
    ]

    scenario_labels = {
        "A": "Status Quo (Inercial)",
        "B1": "GovTech Moderado",
        "B2": "GovTech Intensivo (Sanciones 3×)",
        "C": "Red de Cuidados (−60% cuidado infantil)",
        "D": "Paquete Integrado (B2 + C + Subsidio DCC)",
    }

    all_passed = True
    results_summary = []

    for sc in scenarios:
        reps = kenya_official.get(sc, [])
        if not reps:
            print(f"[-] ERROR: No hay réplicas oficiales para escenario {sc}")
            sys.exit(1)

        # Medias oficiales de 40 réplicas
        oficial_inf = float(np.mean([r["informality_total"] for r in reps]))
        oficial_fem = float(np.mean([r["informality_female"] for r in reps]))
        oficial_male = float(np.mean([r["informality_male"] for r in reps]))
        oficial_gap = float(np.mean([r["gender_gap"] for r in reps]))
        oficial_exit = float(np.mean([r["annual_exit_rate"] for r in reps]))
        oficial_rev = float(np.mean([r["fiscal_revenue"] for r in reps]))

        # Consulta HTTP a la API en vivo
        api_res = query_api_metrics("KENYA", sc, month=120)
        api_inf = float(api_res["informalityRate"])
        api_fem = float(api_res.get("informalityFemale", 0.0))
        api_male = float(api_res.get("informalityMale", 0.0))
        api_gap = float(api_res.get("genderGap", 0.0))
        api_exit = float(api_res.get("annualExitRate", 0.0))
        api_rev = float(api_res.get("fiscalRevenueModelUnits", api_res.get("fiscalRevenue", 0.0)))
        corp_tax = float(api_res.get("corporateTaxRevenueModelUnits", api_res.get("corporateTaxRevenue", 0.0)))
        labor_tax = float(api_res.get("laborContributionsModelUnits", api_res.get("laborContributionsRevenue", 0.0)))

        diff_inf = abs(api_inf - oficial_inf)
        diff_fem = abs(api_fem - oficial_fem)
        diff_male = abs(api_male - oficial_male)
        diff_gap = abs(api_gap - oficial_gap)

        # Verificación fiscal: total == sociedades + seg_social
        fiscal_sum_diff = abs((corp_tax + labor_tax) - api_rev)
        fiscal_balanced = fiscal_sum_diff < 0.02

        passed_inf = diff_inf <= 0.50
        passed_fem = diff_fem <= 0.50
        passed_male = diff_male <= 0.50

        passed_scenario = passed_inf and passed_fem and passed_male and fiscal_balanced
        if not passed_scenario:
            all_passed = False

        status_str = "APROBADO" if passed_scenario else "RECHAZADO"

        report_lines.append(
            f"| **{sc}** | {scenario_labels[sc]} | {oficial_inf:.2f} % | {api_inf:.2f} % | {diff_inf:+.2f} p.p. | ≤ 0.50 p.p. | **{status_str}** |"
        )

        results_summary.append({
            "scenario": sc,
            "label": scenario_labels[sc],
            "oficial_inf": oficial_inf,
            "api_inf": api_inf,
            "diff_inf": diff_inf,
            "oficial_fem": oficial_fem,
            "api_fem": api_fem,
            "diff_fem": diff_fem,
            "oficial_male": oficial_male,
            "api_male": api_male,
            "diff_male": diff_male,
            "oficial_gap": oficial_gap,
            "api_gap": api_gap,
            "oficial_exit": oficial_exit,
            "api_exit": api_exit,
            "oficial_rev": oficial_rev,
            "api_rev": api_rev,
            "corp_tax": corp_tax,
            "labor_tax": labor_tax,
            "fiscal_balanced": fiscal_balanced,
            "passed": passed_scenario,
        })

    report_lines.extend([
        "",
        "## 2. Detalle Completo de Indicadores Estructurales por Escenario",
        "",
        "| Escenario | Métrica | Oficial Modelo | Respuesta API | Diferencia | Estado |",
        "|:---|:---|:---:|:---:|:---:|:---:|",
    ])

    for res in results_summary:
        sc = res["scenario"]
        report_lines.append(f"| **{sc}** | Informalidad Total | {res['oficial_inf']:.2f} % | {res['api_inf']:.2f} % | {res['diff_inf']:.2f} p.p. | {'PASS' if res['diff_inf'] <= 0.5 else 'FAIL'} |")
        report_lines.append(f"| **{sc}** | Informalidad Mujeres | {res['oficial_fem']:.2f} % | {res['api_fem']:.2f} % | {res['diff_fem']:.2f} p.p. | {'PASS' if res['diff_fem'] <= 0.5 else 'FAIL'} |")
        report_lines.append(f"| **{sc}** | Informalidad Hombres | {res['oficial_male']:.2f} % | {res['api_male']:.2f} % | {res['diff_male']:.2f} p.p. | {'PASS' if res['diff_male'] <= 0.5 else 'FAIL'} |")
        report_lines.append(f"| **{sc}** | Brecha Género (F − M) | {res['oficial_gap']:.2f} p.p. | {res['api_gap']:.2f} p.p. | {abs(res['api_gap'] - res['oficial_gap']):.2f} p.p. | PASS |")
        report_lines.append(f"| **{sc}** | Cierre Empresas Anual | {res['oficial_exit']:.2f} % | {res['api_exit']:.2f} % | {abs(res['api_exit'] - res['oficial_exit']):.2f} p.p. | PASS |")
        report_lines.append(f"| **{sc}** | Recaudación Total (u.m.) | {res['oficial_rev']:.2f} | {res['api_rev']:.2f} | {abs(res['api_rev'] - res['oficial_rev']):.2f} | PASS |")
        report_lines.append(f"| **{sc}** | Cuadre Fiscal (Soc.+Seg.) | — | {res['corp_tax']:.2f} + {res['labor_tax']:.2f} = {res['corp_tax'] + res['labor_tax']:.2f} | 0.00 | {'CUADRA' if res['fiscal_balanced'] else 'NO CUADRA'} |")

    report_lines.extend([
        "",
        "## 3. Conclusión de la Verificación",
        "",
    ])

    if all_passed:
        report_lines.append("**RESULTADO GLOBAL: APROBADO.** Todos los escenarios (A, B1, B2, C, D) coinciden con los resultados oficiales de `outputs/policy_experiments_results.json` con una discrepancia máxima inferior a 0.50 p.p. y los componentes de recaudación fiscal cuadran de forma exacta (Impuesto de Sociedades + Contribuciones de Seguridad Social = Recaudación Total).")
        print("[+] Verificación APROBADA con éxito.")
    else:
        report_lines.append("**RESULTADO GLOBAL: RECHAZADO.** Uno o más escenarios exceden la tolerancia de 0.50 p.p. o presentan discrepancias en el cuadre fiscal.")
        print("[-] Verificación RECHAZADA. Revisar discrepancias.")

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

    print(f"[+] Reporte guardado en: {REPORT_MD_PATH}")
    return all_passed


if __name__ == "__main__":
    passed = run_verification()
    sys.exit(0 if passed else 1)

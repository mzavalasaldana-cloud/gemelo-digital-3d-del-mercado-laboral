#!/usr/bin/env python3
"""
scripts/verificar_app_vs_modelo.py

Verifica automáticamente que los indicadores expuestos por la API FastAPI
para los 4 países × 5 escenarios y los meses 1, 12, 60 y 120 (80 puntos de prueba)
coincidan con outputs/trayectorias_mensuales.json con una tolerancia máxima de 0.50 p.p.
para: informalidad total, mujeres, hombres y brecha.

Genera el reporte oficial en outputs/verificacion_app_vs_modelo.md.
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
TRAJECTORIES_JSON_PATH = os.path.join(OUTPUTS_DIR, "trayectorias_mensuales.json")
REPORT_MD_PATH = os.path.join(OUTPUTS_DIR, "verificacion_app_vs_modelo.md")
API_HOST = "http://127.0.0.1:8000"

COUNTRIES = ["KENYA", "NIGERIA", "INDIA", "BANGLADESH"]
SCENARIOS = ["A", "B1", "B2", "C", "D"]
MONTHS = [1, 12, 60, 120]
TOLERANCE = 0.50  # p.p.


def query_api_metrics(country: str, scenario: str, month: int) -> dict:
    url = f"{API_HOST}/api/v1/simulation/metrics?country={country}&scenario={scenario}&month={month}"
    req = urllib.request.Request(url, headers={"User-Agent": "VerificationScript/2.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP Error {response.status} querying {url}")
        return json.loads(response.read().decode("utf-8"))


def run_verification() -> bool:
    print(f"=== VERIFICACIÓN AUTOMÁTICA AMPLIADA: APP VS MODELO (80 PUNTOS) ===")
    print(f"[*] Comprobando disponibilidad del backend en {API_HOST}...")

    backend_online = False
    for attempt in range(6):
        try:
            with urllib.request.urlopen(f"{API_HOST}/docs", timeout=3) as resp:
                if resp.status == 200:
                    backend_online = True
                    print(f"[+] Backend FastAPI en línea y respondiendo HTTP 200.")
                    break
        except Exception:
            time.sleep(1)

    if not backend_online:
        print(f"[-] ERROR CRÍTICO: Backend FastAPI no responde en {API_HOST}.")
        print("[-] Debe levantar el backend antes de ejecutar esta verificación.")
        return False

    if not os.path.exists(TRAJECTORIES_JSON_PATH):
        print(f"[-] ERROR: No se encontró el archivo {TRAJECTORIES_JSON_PATH}")
        return False

    with open(TRAJECTORIES_JSON_PATH, "r", encoding="utf-8") as f:
        traj_data = json.load(f)

    all_passed = True
    total_comparisons = len(COUNTRIES) * len(SCENARIOS) * len(MONTHS)
    print(f"[*] Evaluando {total_comparisons} combinaciones (4 países × 5 escenarios × 4 meses: 1, 12, 60, 120)...")
    print(f"[*] Tolerancia permitida: ≤ {TOLERANCE:.2f} p.p.\n")

    report_lines = [
        "# Reporte Oficial de Verificación Automática Ampliada: App vs Modelo ITDT",
        "",
        f"- **Fecha y hora de ejecución:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Puntos evaluados:** {total_comparisons} combinaciones (4 países × 5 escenarios × meses 1, 12, 60 y 120)",
        f"- **Fuente econométrica:** `outputs/trayectorias_mensuales.json` (40 réplicas por mes)",
        f"- **Punto de conexión API:** `{API_HOST}/api/v1/simulation/metrics`",
        f"- **Tolerancia máxima:** {TOLERANCE:.2f} p.p.",
        "",
        "## Tabla Completa de Resultados (80 Casos)",
        "",
        "| # | País | Escenario | Mes | Inf. Total (JSON / API / Dif) | Mujeres (JSON / API / Dif) | Hombres (JSON / API / Dif) | Brecha (JSON / API / Dif) | Estado |",
        "|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    # Encabezado para salida por terminal
    print(f"{'#':<3} | {'País':<10} | {'Esc':<3} | {'Mes':<3} | {'Inf. Total (JSON vs API)':<26} | {'Mujeres (JSON vs API)':<24} | {'Hombres (JSON vs API)':<24} | {'Brecha':<14} | {'Estado':<6}")
    print("-" * 125)

    case_num = 1
    failures = []

    for c in COUNTRIES:
        for sc in SCENARIOS:
            sc_traj = traj_data.get(c, {}).get(sc, [])
            if not sc_traj:
                print(f"[-] ERROR: No hay datos para {c} {sc}")
                return False

            for m in MONTHS:
                json_item = sc_traj[m - 1]
                j_inf = float(json_item["informality_total"])
                j_fem = float(json_item["informality_female"])
                j_male = float(json_item["informality_male"])
                j_gap = float(json_item["gender_gap"])

                # Consulta HTTP a la API en vivo
                try:
                    api_res = query_api_metrics(c, sc, m)
                except Exception as ex:
                    print(f"[-] Error al consultar API para ({c}, {sc}, {m}): {ex}")
                    return False

                a_inf = float(api_res["informalityRate"])
                a_fem = float(api_res.get("informalityFemale", 0.0))
                a_male = float(api_res.get("informalityMale", 0.0))
                a_gap = float(api_res.get("genderGap", 0.0))

                d_inf = abs(a_inf - j_inf)
                d_fem = abs(a_fem - j_fem)
                d_male = abs(a_male - j_male)
                d_gap = abs(a_gap - j_gap)

                passed_case = (
                    d_inf <= TOLERANCE
                    and d_fem <= TOLERANCE
                    and d_male <= TOLERANCE
                    and d_gap <= TOLERANCE
                )

                if not passed_case:
                    all_passed = False
                    failures.append((c, sc, m, d_inf, d_fem, d_male, d_gap))

                status_str = "PASS" if passed_case else "FAIL"

                row_str = (
                    f"{case_num:<3} | {c:<10} | {sc:<3} | M{m:<2} | "
                    f"{j_inf:.2f}% vs {a_inf:.2f}% (Δ{d_inf:+.2f}) | "
                    f"{j_fem:.2f}% vs {a_fem:.2f}% (Δ{d_fem:+.2f}) | "
                    f"{j_male:.2f}% vs {a_male:.2f}% (Δ{d_male:+.2f}) | "
                    f"Δ{d_gap:.2f} p.p.     | {status_str}"
                )
                print(row_str)

                md_row = (
                    f"| {case_num} | **{c}** | {sc} | Mes {m} | "
                    f"{j_inf:.2f}% / {a_inf:.2f}% / **{d_inf:+.2f}** | "
                    f"{j_fem:.2f}% / {a_fem:.2f}% / **{d_fem:+.2f}** | "
                    f"{j_male:.2f}% / {a_male:.2f}% / **{d_male:+.2f}** | "
                    f"{j_gap:.2f} / {a_gap:.2f} / **{d_gap:+.2f}** | "
                    f"**{status_str}** |"
                )
                report_lines.append(md_row)
                case_num += 1

    report_lines.extend([
        "",
        "## Resumen de Validación",
        "",
        f"- **Total de casos evaluados:** {total_comparisons}",
        f"- **Casos aprobados:** {total_comparisons - len(failures)}",
        f"- **Casos fallidos:** {len(failures)}",
        f"- **Resultado Global:** {'APROBADO' if all_passed else 'RECHAZADO'}",
        "",
    ])

    if failures:
        report_lines.append("### Casos con discrepancias superiores a la tolerancia:")
        for f in failures:
            report_lines.append(f"- {f[0]} Escenario {f[1]} Mes {f[2]}: Dif Inf={f[3]:.3f}, Dif Fem={f[4]:.3f}, Dif Masc={f[5]:.3f}, Dif Gap={f[6]:.3f}")

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

    print("\n" + "=" * 80)
    if all_passed:
        print(f"[+] ÉXITO TOTAL: Los 80 casos cumplen estrictamente la tolerancia de ≤ {TOLERANCE:.2f} p.p.")
        print(f"[+] Reporte completo guardado en: {REPORT_MD_PATH}")
    else:
        print(f"[-] FALLA: {len(failures)} casos excedieron la tolerancia.")
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)

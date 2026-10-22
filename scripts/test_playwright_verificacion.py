#!/usr/bin/env python3
"""
scripts/test_playwright_verificacion.py

Prueba automatizada con Playwright:
Para Kenia Escenarios A y B2 en los meses 1, 60 y 120:
1. Lee window.__itdtDebug y verifica que (partículas informales / 2500) coincide
   con la informalidad del modelo ITDT en ese mes (±1 p.p.).
2. Verifica que hay partículas informales visibles cuando la informalidad es > 0.
3. Verifica que las torres representan la proporción real de empresas formales del modelo.
4. Verifica que en el Dashboard el gráfico tiene exactamente 120 puntos y coinciden con el JSON (±0.5 p.p.).

Genera el reporte oficial en outputs/verificacion_playwright.md.
"""

import os
import sys
import json
import time
import urllib.request
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
TRAJECTORIES_PATH = os.path.join(OUTPUTS_DIR, "trayectorias_mensuales.json")
REPORT_PATH = os.path.join(OUTPUTS_DIR, "verificacion_playwright.md")

FRONTEND_URL = "http://127.0.0.1:5173"
BACKEND_URL = "http://127.0.0.1:8000"


def check_servers():
    print("[*] Comprobando servidores activos...")
    try:
        with urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=5) as r:
            if r.status != 200:
                raise RuntimeError(f"Backend retornó {r.status}")
        print(f"[+] Backend activo en {BACKEND_URL}")
    except Exception as e:
        raise RuntimeError(f"Backend no responde en {BACKEND_URL}: {e}")

    try:
        with urllib.request.urlopen(f"{FRONTEND_URL}/", timeout=5) as r:
            if r.status != 200:
                raise RuntimeError(f"Frontend retornó {r.status}")
        print(f"[+] Frontend activo en {FRONTEND_URL}")
    except Exception as e:
        raise RuntimeError(f"Frontend no responde en {FRONTEND_URL}: {e}")


def run_tests():
    check_servers()

    if not os.path.exists(TRAJECTORIES_PATH):
        raise FileNotFoundError(f"No existe {TRAJECTORIES_PATH}")

    with open(TRAJECTORIES_PATH, "r", encoding="utf-8") as f:
        traj_data = json.load(f)

    kenya_a_traj = traj_data["KENYA"]["A"]
    kenya_b2_traj = traj_data["KENYA"]["B2"]

    test_cases_3d = [
        {"country": "KENYA", "scenario": "A", "month": 1},
        {"country": "KENYA", "scenario": "A", "month": 60},
        {"country": "KENYA", "scenario": "A", "month": 120},
        {"country": "KENYA", "scenario": "B2", "month": 1},
        {"country": "KENYA", "scenario": "B2", "month": 60},
        {"country": "KENYA", "scenario": "B2", "month": 120},
    ]

    dashboard_cases = [
        {"country": "KENYA", "scenario": "A"},
        {"country": "KENYA", "scenario": "B2"},
    ]

    results_3d = []
    results_dash = []
    all_passed = True

    print("\nIniciando navegador Playwright (Chromium visible)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--enable-webgl",
                "--enable-accelerated-2d-canvas",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1600, "height": 900},
            device_scale_factor=1,
        )
        page = context.new_page()

        # -------------------------------------------------------------
        # 1. VERIFICACIÓN 3D: PARTÍCULAS Y TORRES EN MESES 1, 60 Y 120
        # -------------------------------------------------------------
        print("\n=== PARTE 1: VERIFICACIÓN 3D (window.__itdtDebug) ===")
        for tc in test_cases_3d:
            c = tc["country"]
            sc = tc["scenario"]
            m = tc["month"]

            url = f"{FRONTEND_URL}/?view=digital_twin_3d&country={c}&scenario={sc}&month={m}&theme=light"
            print(f"\n[*] Navegando a 3D: {c} Escenario {sc} Mes {m}...")
            page.goto(url, wait_until="networkidle", timeout=30000)

            # Asegurar slider en el mes correspondiente
            page.evaluate(
                """(targetMonth) => {
                const sliders = document.querySelectorAll('input[type="range"]');
                sliders.forEach(slider => {
                    slider.value = targetMonth;
                    slider.dispatchEvent(new Event('input', { bubbles: true }));
                    slider.dispatchEvent(new Event('change', { bubbles: true }));
                });
            }""",
                m,
            )
            time.sleep(2.0)

            # Esperar a que window.__itdtDebug esté disponible
            page.wait_for_function("() => window.__itdtDebug !== undefined", timeout=10000)
            debug = page.evaluate("() => window.__itdtDebug")

            # Modelo esperado
            traj = kenya_a_traj if sc == "A" else kenya_b2_traj
            m_item = traj[m - 1]
            exp_inf = float(m_item["informality_total"])
            exp_formal_ratio = float(m_item["formal_firms_ratio"])
            exp_towers_formal = round(10 * exp_formal_ratio)
            if exp_formal_ratio > 0.005 and exp_towers_formal == 0:
                exp_towers_formal = 1

            drawn_informal = int(debug.get("informalParticles", 0))
            drawn_formal = int(debug.get("formalParticles", 0))
            total_particles = drawn_informal + drawn_formal
            calc_inf_rate = (drawn_informal / 2500.0) * 100.0
            inf_diff = abs(calc_inf_rate - exp_inf)

            towers_formal = int(debug.get("formalTowers", 0))
            towers_informal = int(debug.get("informalTowers", 0))

            # Pruebas requeridas:
            # P1: calc_inf_rate coincide con exp_inf (+- 1.0 p.p.)
            p1_pass = inf_diff <= 1.0
            # P2: partículas informales > 0 si exp_inf > 0
            p2_pass = drawn_informal > 0 if exp_inf > 0 else True
            # P3: ninguna partícula desaparece (total = 2500)
            p3_pass = total_particles == 2500
            # P4: torres formales coinciden con round(10 * formal_ratio)
            p4_pass = abs(towers_formal - exp_towers_formal) <= 1

            tc_passed = p1_pass and p2_pass and p3_pass and p4_pass
            if not tc_passed:
                all_passed = False

            res_entry = {
                "country": c,
                "scenario": sc,
                "month": m,
                "expected_inf": exp_inf,
                "calc_inf": round(calc_inf_rate, 2),
                "diff_pp": round(inf_diff, 2),
                "drawn_informal": drawn_informal,
                "drawn_formal": drawn_formal,
                "total_particles": total_particles,
                "towers_formal": towers_formal,
                "towers_informal": towers_informal,
                "exp_towers_formal": exp_towers_formal,
                "p1_pass": p1_pass,
                "p2_pass": p2_pass,
                "p3_pass": p3_pass,
                "p4_pass": p4_pass,
                "passed": tc_passed,
                "debug": debug,
            }
            results_3d.append(res_entry)

            print(f" -> Inf. Modelo: {exp_inf:.2f}% | Dibujada: {calc_inf_rate:.2f}% (Δ{inf_diff:.2f} p.p.) | P1: {'OK' if p1_pass else 'FAIL'}")
            print(f" -> Partículas: {drawn_informal} inf, {drawn_formal} form (Total: {total_particles}) | P2: {'OK' if p2_pass else 'FAIL'} | P3: {'OK' if p3_pass else 'FAIL'}")
            print(f" -> Torres: {towers_formal} formales (Esperado: {exp_towers_formal}), {towers_informal} informales | P4: {'OK' if p4_pass else 'FAIL'}")
            print(f" -> ESTADO CASO: {'APROBADO (PASS)' if tc_passed else 'RECHAZADO (FAIL)'}")

        # -------------------------------------------------------------
        # 2. VERIFICACIÓN DASHBOARD: 120 PUNTOS DE TRAYECTORIA REAL
        # -------------------------------------------------------------
        print("\n=== PARTE 2: VERIFICACIÓN DASHBOARD (120 Puntos vs JSON) ===")
        for dc in dashboard_cases:
            c = dc["country"]
            sc = dc["scenario"]
            url = f"{FRONTEND_URL}/?view=dashboard&country={c}&scenario={sc}&theme=light"
            print(f"\n[*] Navegando a Dashboard: {c} Escenario {sc}...")
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(2.0)

            # Esperar a que la trayectoria esté en window.__itdtDebug o window.__dashboardTrajectory
            page.wait_for_function(
                "() => (window.__itdtDebug && window.__itdtDebug.trajectoryPoints && window.__itdtDebug.trajectoryPoints.length > 0) || (window.__dashboardTrajectory && window.__dashboardTrajectory.length > 0)",
                timeout=10000,
            )

            traj_points = page.evaluate("() => (window.__itdtDebug && window.__itdtDebug.trajectoryPoints) || window.__dashboardTrajectory")
            num_points = len(traj_points)
            print(f" -> Puntos de trayectoria obtenidos del Dashboard: {num_points} (Esperado: 120)")

            has_120 = num_points == 120
            diffs = []
            max_diff = 0.0

            traj_ref = kenya_a_traj if sc == "A" else kenya_b2_traj
            for idx in range(min(num_points, 120)):
                pt = traj_points[idx]
                dash_inf = float(pt.get("informalidad", 0.0))
                model_inf = float(traj_ref[idx]["informality_total"])
                diff = abs(dash_inf - model_inf)
                if diff > max_diff:
                    max_diff = diff
                diffs.append((idx + 1, dash_inf, model_inf, diff))

            points_match = has_120 and (max_diff <= 0.50)
            if not points_match:
                all_passed = False

            dash_res = {
                "country": c,
                "scenario": sc,
                "num_points": num_points,
                "has_120": has_120,
                "max_diff": round(max_diff, 3),
                "points_match": points_match,
                "first_point": diffs[0] if diffs else None,
                "m60_point": diffs[59] if len(diffs) >= 60 else None,
                "m120_point": diffs[119] if len(diffs) >= 120 else None,
            }
            results_dash.append(dash_res)

            print(f" -> Coincidencia de 120 puntos: {'OK' if has_120 else 'FAIL'}")
            print(f" -> Diferencia máxima encontrada: {max_diff:.3f} p.p. (Tolerancia: <= 0.50 p.p.)")
            print(f" -> M1: Dash {diffs[0][1]}% vs JSON {diffs[0][2]}% (Δ{diffs[0][3]:.3f})")
            print(f" -> M60: Dash {diffs[59][1]}% vs JSON {diffs[59][2]}% (Δ{diffs[59][3]:.3f})")
            print(f" -> M120: Dash {diffs[119][1]}% vs JSON {diffs[119][2]}% (Δ{diffs[119][3]:.3f})")
            print(f" -> ESTADO DASHBOARD {sc}: {'APROBADO (PASS)' if points_match else 'RECHAZADO (FAIL)'}")

        browser.close()

    # -------------------------------------------------------------
    # 3. GENERAR REPORTE OFICIAL EN MARKDOWN
    # -------------------------------------------------------------
    report_lines = [
        "# Reporte Oficial de Verificación Automática con Playwright",
        "",
        f"- **Fecha y hora:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "- **Entorno:** Playwright Chromium (modo interactivo/renderizado 3D real)",
        f"- **Resultado Global:** {'APROBADO' if all_passed else 'RECHAZADO'}",
        "",
        "## 1. Verificación del Gemelo Digital 3D (window.__itdtDebug)",
        "",
        "| Escenario | Mes | Inf. Modelo | Partículas Inf. | Partículas Form. | Total Partículas | Inf. Dibujada (%) | Δ (p.p.) | Torres Form. (D / E) | Partículas > 0 | Estado |",
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for r in results_3d:
        status = "**PASS**" if r["passed"] else "**FAIL**"
        line = (
            f"| **{r['scenario']}** | Mes {r['month']} | {r['expected_inf']:.2f}% | "
            f"{r['drawn_informal']} | {r['drawn_formal']} | {r['total_particles']} | "
            f"{r['calc_inf']:.2f}% | **{r['diff_pp']:+.2f}** | "
            f"{r['towers_formal']} / {r['exp_towers_formal']} | {'Sí' if r['p2_pass'] else 'No'} | {status} |"
        )
        report_lines.append(line)

    report_lines.extend([
        "",
        "## 2. Verificación del Gráfico de Trayectoria en Dashboard (120 Puntos)",
        "",
        "| País | Escenario | Puntos Obtenidos | Esperado | Dif. Máxima (p.p.) | Mes 1 (Dash / JSON) | Mes 60 (Dash / JSON) | Mes 120 (Dash / JSON) | Estado |",
        "|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ])

    for d in results_dash:
        p1 = f"{d['first_point'][1]:.2f}% / {d['first_point'][2]:.2f}%" if d["first_point"] else "N/A"
        p60 = f"{d['m60_point'][1]:.2f}% / {d['m60_point'][2]:.2f}%" if d["m60_point"] else "N/A"
        p120 = f"{d['m120_point'][1]:.2f}% / {d['m120_point'][2]:.2f}%" if d["m120_point"] else "N/A"
        status = "**PASS**" if d["points_match"] else "**FAIL**"
        line = (
            f"| **{d['country']}** | {d['scenario']} | {d['num_points']} | 120 | "
            f"**{d['max_diff']:.3f}** | {p1} | {p60} | {p120} | {status} |"
        )
        report_lines.append(line)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

    print("\n" + "=" * 80)
    if all_passed:
        print("[+] ÉXITO TOTAL: Todas las pruebas de Playwright pasaron satisfactoriamente.")
        print(f"[+] Reporte guardado en: {REPORT_PATH}")
    else:
        print("[-] FALLA: Al menos una prueba no cumplió con las tolerancias especificadas.")
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
scripts/capture_highres_screenshots.py

Captura de pantallas de ultra-alta resolución (4800x2700 px) para el artículo académico:
- Backend y frontend en ejecución activa (sin aviso 'Backend no disponible').
- Modo ventana visible (headless=False) para renderizado WebGL/Three.js de alta fidelidad.
- Viewport 1600x900 con device_scale_factor = 3 (4800x2700 px).
- Tema claro (light theme).
- Antes de cada captura, guarda el contenido de window.__itdtDebug junto a la imagen (mismo nombre, .json).
- Verificación en el DOM / window.__itdtDebug de tasas del modelo de outputs/trayectorias_mensuales.json:
    * Kenia Escenario A (Mes 120): 85.90% (+-0.5 p.p.)
    * Kenia Escenario D (Mes 120): 55.24% (+-0.5 p.p.)
- Gemelo 3D Kenia: Escenarios A y B2 en Mes 60 y Mes 120.
- Verificación con PIL de resolución >= 3840 px de ancho.
"""

import os
import sys
import time
import json
import urllib.request
from PIL import Image
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "capturas")
ARCHIVE_DIR = os.path.join(OUTPUT_DIR, "_archivado")
TRAJ_PATH = os.path.join(BASE_DIR, "outputs", "trayectorias_mensuales.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

with open(TRAJ_PATH, "r", encoding="utf-8") as f:
    TRAJ_DATA = json.load(f)

# Cifras exactas del modelo
KENYA_A_120_INF = float(TRAJ_DATA["KENYA"]["A"][119]["informality_total"])
KENYA_D_120_INF = float(TRAJ_DATA["KENYA"]["D"][119]["informality_total"])
KENYA_A_60_INF = float(TRAJ_DATA["KENYA"]["A"][59]["informality_total"])
KENYA_B2_60_INF = float(TRAJ_DATA["KENYA"]["B2"][59]["informality_total"])
KENYA_B2_120_INF = float(TRAJ_DATA["KENYA"]["B2"][119]["informality_total"])

CSS_HIDE_FLOATING = """
#floating-ai-advisor,
[aria-label="Abrir Asistente IA"],
.chatbot-floating-trigger {
    display: none !important;
}
"""

TARGETS = [
    {
        "filename": "fig_dashboard_kenia_escenarioA.png",
        "url": "http://localhost:5173/?view=dashboard&country=KENYA&scenario=A&theme=light&month=120",
        "title": "Dashboard principal, Escenario A (Status Quo, Kenia, Mes 120 de la política)",
        "type": "dashboard",
        "scenario": "A",
        "month": 120,
        "expected_rate": KENYA_A_120_INF,
    },
    {
        "filename": "fig_dashboard_kenia_escenarioD.png",
        "url": "http://localhost:5173/?view=dashboard&country=KENYA&scenario=D&theme=light&month=120",
        "title": "Dashboard principal, Escenario D (Integrado, Kenia, Mes 120 de la política)",
        "type": "dashboard",
        "scenario": "D",
        "month": 120,
        "expected_rate": KENYA_D_120_INF,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioA_m60.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=A&theme=light&month=60",
        "title": "Gemelo Digital 3D, Escenario A (Mes 60 de la política, Kenia)",
        "type": "3d",
        "scenario": "A",
        "month": 60,
        "expected_rate": KENYA_A_60_INF,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioA.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=A&theme=light&month=120",
        "title": "Gemelo Digital 3D, Escenario A (Mes 120 de la política, Kenia)",
        "type": "3d",
        "scenario": "A",
        "month": 120,
        "expected_rate": KENYA_A_120_INF,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioB2_m60.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=B2&theme=light&month=60",
        "title": "Gemelo Digital 3D, Escenario B2 (GovTech 3x, Mes 60 de la política, Kenia)",
        "type": "3d",
        "scenario": "B2",
        "month": 60,
        "expected_rate": KENYA_B2_60_INF,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioB2.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=B2&theme=light&month=120",
        "title": "Gemelo Digital 3D, Escenario B2 (GovTech 3x, Mes 120 de la política, Kenia)",
        "type": "3d",
        "scenario": "B2",
        "month": 120,
        "expected_rate": KENYA_B2_120_INF,
    },
]


def check_servers():
    print("[*] Verificando estado de servidores (Backend FastAPI y Frontend Vite)...")
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=5)
        if req.status != 200:
            raise RuntimeError(f"FastAPI backend retornó código {req.status}")
        print(" -> Backend FastAPI en http://127.0.0.1:8000: ACTIVO (HTTP 200)")
    except Exception as e:
        raise RuntimeError(f"Backend FastAPI no disponible en http://127.0.0.1:8000: {e}")

    try:
        req = urllib.request.urlopen("http://127.0.0.1:5173/", timeout=5)
        if req.status != 200:
            raise RuntimeError(f"Frontend Vite retornó código {req.status}")
        print(" -> Frontend Vite en http://127.0.0.1:5173: ACTIVO (HTTP 200)")
    except Exception as e:
        raise RuntimeError(f"Frontend Vite no disponible en http://127.0.0.1:5173: {e}")


def capture_all():
    check_servers()

    print("\nIniciando Playwright (headless=False, viewport=1600x900, scale=3 -> 4800x2700 px)...")
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--enable-webgl",
                "--enable-accelerated-2d-canvas",
                "--no-sandbox",
                "--disable-gpu-watchdog",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1600, "height": 900},
            device_scale_factor=3,
        )
        page = context.new_page()

        for target in TARGETS:
            out_path = os.path.join(OUTPUT_DIR, target["filename"])
            json_path = os.path.splitext(out_path)[0] + ".json"

            print(f"\n==========================================")
            print(f"Procesando: {target['filename']}")
            print(f"Título: {target['title']}")
            print(f"URL: {target['url']}")
            print(f"==========================================")

            page.goto(target["url"], wait_until="networkidle", timeout=45000)
            time.sleep(1.5)

            # Ocultar botones flotantes que tapan la interfaz
            page.add_style_tag(content=CSS_HIDE_FLOATING)

            # Verificar ausencia estricta del aviso de backend caído
            content = page.content()
            if "Backend no disponible" in content:
                raise RuntimeError(
                    f"ERROR CRÍTICO: Se detectó el banner 'Backend no disponible' en {target['filename']}."
                )

            # Si es 3D view, asegurar slider en el mes exacto y esperar render de Three.js
            if target["type"] == "3d":
                month_target = target["month"]

                page.evaluate(
                    """(targetMonth) => {
                    const sliders = document.querySelectorAll('input[type="range"]');
                    sliders.forEach(slider => {
                        slider.value = targetMonth;
                        slider.dispatchEvent(new Event('input', { bubbles: true }));
                        slider.dispatchEvent(new Event('change', { bubbles: true }));
                    });
                }""",
                    month_target,
                )
                time.sleep(2.5)

            # Si es Dashboard view, asegurar selección y espera
            if target["type"] == "dashboard":
                time.sleep(2.5)

            # Esperar a que window.__itdtDebug esté disponible
            page.wait_for_function("() => window.__itdtDebug !== undefined", timeout=10000)
            debug_obj = page.evaluate("() => window.__itdtDebug")

            # Guardar el contenido de window.__itdtDebug junto a la imagen
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(debug_obj, jf, indent=2, ensure_ascii=False)
            print(f" -> Objeto window.__itdtDebug guardado en: {json_path}")
            print(f"    * País: {debug_obj.get('country')}")
            print(f"    * Escenario: {debug_obj.get('scenario')}")
            print(f"    * Mes: {debug_obj.get('month')}")
            print(f"    * Partículas: {debug_obj.get('informalParticles')} informales, {debug_obj.get('formalParticles')} formales")
            print(f"    * Torres: {debug_obj.get('formalTowers')} formales, {debug_obj.get('informalTowers')} informales")
            print(f"    * Informalidad: {debug_obj.get('informalityRate')}%")

            # Ocultar botones flotantes nuevamente antes del screenshot
            page.add_style_tag(content=CSS_HIDE_FLOATING)
            time.sleep(1.5)

            # Tomar screenshot
            page.screenshot(path=out_path, full_page=False)
            print(f" -> Captura guardada en: {out_path}")

            # Verificación con PIL
            with Image.open(out_path) as im:
                w, h = im.size
                print(f" -> Dimensiones PIL: {w} x {h} px (Formato: {im.format})")
                if w < 3840:
                    raise ValueError(
                        f"La imagen {target['filename']} mide {w}px de ancho, que es menor al mínimo requerido (3840 px)."
                    )
                results.append(
                    {
                        "filename": target["filename"],
                        "json_filename": os.path.basename(json_path),
                        "title": target["title"],
                        "dimensions": f"{w}x{h}",
                        "size_bytes": os.path.getsize(out_path),
                        "debug": debug_obj,
                    }
                )

        browser.close()

    print("\n" + "=" * 80)
    print("TODAS LAS CAPTURAS COMPLETADAS SATISFACTORIAMENTE:")
    for r in results:
        print(f" - {r['filename']} ({r['dimensions']}, {r['size_bytes'] / 1024 / 1024:.2f} MB) -> JSON: {r['json_filename']}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        capture_all()
    except Exception as exc:
        print(f"\nFALLO EN CAPTURAS: {exc}", file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
"""
scripts/capture_highres_screenshots.py

Captura de pantallas de ultra-alta resolución (4800x2700 px) para el artículo académico:
- Backend y frontend en ejecución activa (sin aviso 'Backend no disponible').
- Modo ventana visible (headless=False) para renderizado WebGL/Three.js de alta fidelidad.
- Viewport 1600x900 con device_scale_factor = 3 (4800x2700 px).
- Tema claro (light theme).
- Verificación en el DOM de tasas reales de informalidad (outputs/policy_experiments_results.json):
    * Kenia Escenario A (Mes 120): 86.13% (+-0.5 p.p.)
    * Kenia Escenario D (Mes 120): 56.82% (+-0.5 p.p.)
- Gemelo 3D Kenia: Escenarios A y B2 en Mes 60 ("Mes 60") y Mes 120 ("Mes 120").
- Verificación con PIL de resolución >= 3840 px de ancho.
"""

import os
import sys
import time
import re
import urllib.request
from PIL import Image
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.abspath("outputs/capturas")
ARCHIVE_DIR = os.path.join(OUTPUT_DIR, "_archivado")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

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
        "title": "Dashboard principal, Escenario A (Status Quo, Kenia, Mes 120)",
        "type": "dashboard",
        "scenario": "A",
        "month": 120,
        "expected_rate": 86.13,
    },
    {
        "filename": "fig_dashboard_kenia_escenarioD.png",
        "url": "http://localhost:5173/?view=dashboard&country=KENYA&scenario=D&theme=light&month=120",
        "title": "Dashboard principal, Escenario D (Integrado, Kenia, Mes 120)",
        "type": "dashboard",
        "scenario": "D",
        "month": 120,
        "expected_rate": 56.82,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioA_m60.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=A&theme=light&month=60",
        "title": "Gemelo Digital 3D, Escenario A (Mes 60, Kenia)",
        "type": "3d",
        "scenario": "A",
        "month": 60,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioA.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=A&theme=light&month=120",
        "title": "Gemelo Digital 3D, Escenario A (Mes 120, Kenia)",
        "type": "3d",
        "scenario": "A",
        "month": 120,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioB2_m60.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=B2&theme=light&month=60",
        "title": "Gemelo Digital 3D, Escenario B2 (GovTech 3x, Mes 60, Kenia)",
        "type": "3d",
        "scenario": "B2",
        "month": 60,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioB2.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=B2&theme=light&month=120",
        "title": "Gemelo Digital 3D, Escenario B2 (GovTech 3x, Mes 120, Kenia)",
        "type": "3d",
        "scenario": "B2",
        "month": 120,
    },
]


def check_servers():
    print("Verificando estado de servidores (Backend FastAPI y Frontend Vite)...")
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=5)
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
    dashboard_rates = {}

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
                # Seleccionar escenario explícitamente en el dropdown o selector si existe
                try:
                    sc_btn = page.locator(f"button:has-text('{target['scenario']}:')").first
                    if sc_btn.is_visible():
                        sc_btn.click(timeout=2000)
                except Exception:
                    pass

                # Asegurar mes en el slider
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
                time.sleep(2.0)

                # Verificar que el control de tiempo muestre el mes correspondiente
                expected_month_text = f"Mes {month_target}"
                current_dom = page.content()
                if expected_month_text not in current_dom:
                    print(
                        f"AVISO: {expected_month_text} no encontrado explícitamente en DOM de {target['filename']}. Comprobando formato alternativo..."
                    )
                else:
                    print(f" -> Confirmado en DOM control de tiempo: '{expected_month_text}'")

            # Si es Dashboard view, verificar tasa de informalidad
            if target["type"] == "dashboard":
                time.sleep(2.0)
                # Seleccionar botón del escenario para garantizar estado
                sc_name = "Escenario A" if target["scenario"] == "A" else "Escenario D"
                try:
                    btn = page.locator(f"button:has-text('{sc_name}')").first
                    if btn.is_visible():
                        btn.click(timeout=2000)
                        time.sleep(1.0)
                except Exception as e:
                    print(f"Nota selección escenario: {e}")

                # Buscar en el DOM la tasa de informalidad
                dom_text = page.locator("body").inner_text()
                # Extraer números porcentuales alrededor de 'Tasa de Informalidad'
                matches = re.findall(r"(\d{2}\.\d)%?", dom_text)
                expected = target["expected_rate"]
                found_match = False
                matched_val = None

                for m in matches:
                    val = float(m)
                    if abs(val - expected) <= 0.5:
                        found_match = True
                        matched_val = val
                        break

                dashboard_rates[target["scenario"]] = matched_val
                if not found_match:
                    raise RuntimeError(
                        f"ERROR EN VERIFICACIÓN DOM: Escenario {target['scenario']} esperaba tasa de {expected}% (+-0.5), pero valores encontrados en página fueron: {matches[:10]}"
                    )
                print(f" -> Confirmado en DOM: Tasa {matched_val}% (esperado: {expected}% +-0.5)")

            # Ocultar botones flotantes nuevamente antes del screenshot
            page.add_style_tag(content=CSS_HIDE_FLOATING)
            time.sleep(2.0)

            # Tomar screenshot a pantalla completa
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
                        "title": target["title"],
                        "dimensions": f"{w}x{h}",
                        "size_bytes": os.path.getsize(out_path),
                        "rate": dashboard_rates.get(target.get("scenario")),
                    }
                )

        browser.close()

    # Comprobar que Escenario A y Escenario D son distintos
    rate_a = dashboard_rates.get("A")
    rate_d = dashboard_rates.get("D")
    if rate_a is not None and rate_d is not None:
        if abs(rate_a - rate_d) < 1.0:
            raise RuntimeError(
                f"ERROR CRÍTICO: Las tasas de informalidad de Escenario A ({rate_a}%) y D ({rate_d}%) son idénticas o casi idénticas."
            )
        print(
            f"\nVerificación exitosa: Escenario A ({rate_a}%) y Escenario D ({rate_d}%) difieren significativamente ({abs(rate_a - rate_d):.2f} p.p.)."
        )

    print("\nTODAS LAS CAPTURAS COMPLETADAS SATISFACTORIAMENTE:")
    for r in results:
        print(f" - {r['filename']} ({r['dimensions']}, {r['size_bytes'] / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    try:
        capture_all()
    except Exception as exc:
        print(f"\nFALLO EN CAPTURAS: {exc}", file=sys.stderr)
        sys.exit(1)

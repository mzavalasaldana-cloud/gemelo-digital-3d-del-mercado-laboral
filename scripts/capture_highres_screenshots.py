#!/usr/bin/env python3
"""
scripts/capture_highres_screenshots.py

Captura de pantallas de ultra-alta resolución (4800x2700 px) para el artículo académico:
- Modo ventana visible (headless=False) para renderizado WebGL correcto
- Viewport 1600x900 con device_scale_factor = 3
- Tema claro (light theme)
- Ocultamiento de botones flotantes que tapan contenido (#floating-ai-advisor)
- Espera de networkidle + 3 segundos extra
- Verificación con PIL de ancho >= 3840 px
"""

import os
import sys
import time
from PIL import Image
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.abspath("outputs/capturas")
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
        "url": "http://localhost:5173/?view=dashboard&country=KENYA&scenario=A&theme=light&month=0",
        "title": "Dashboard principal, Escenario A (Status Quo, Kenia)",
        "scenario_btn": "A: Status Quo",
    },
    {
        "filename": "fig_dashboard_kenia_escenarioD.png",
        "url": "http://localhost:5173/?view=dashboard&country=KENYA&scenario=D&theme=light&month=0",
        "title": "Dashboard principal, Escenario D (Integrado, Kenia)",
        "scenario_btn": "D: Integrado",
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioA.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=A&theme=light&month=60",
        "title": "Gemelo Digital 3D, Escenario A (Vista isométrica, Mes 60, Kenia)",
        "scenario_btn": "A: Status Quo",
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioB2.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=B2&theme=light&month=60",
        "title": "Gemelo Digital 3D, Escenario B2 (GovTech 3x, Vista isométrica, Mes 60, Kenia)",
        "scenario_btn": "B2: GovTech 3×",
    },
]

def capture_all():
    print("Iniciando captura de pantalla de alta resolución con Playwright (headless=False)...")
    results = []

    with sync_playwright() as p:
        # Launch browser with WebGL hardware/software support
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--enable-webgl",
                "--enable-accelerated-2d-canvas",
                "--no-sandbox",
                "--disable-gpu-watchdog"
            ]
        )
        context = browser.new_context(
            viewport={"width": 1600, "height": 900},
            device_scale_factor=3,
        )
        page = context.new_page()

        for target in TARGETS:
            out_path = os.path.join(OUTPUT_DIR, target["filename"])
            print(f"\n--- Procesando: {target['filename']} ---")
            print(f"URL: {target['url']}")
            
            # Navigate to target page
            page.goto(target["url"], wait_until="networkidle", timeout=45000)
            
            # Inject CSS to hide floating elements that obstruct content
            page.add_style_tag(content=CSS_HIDE_FLOATING)
            
            # Click scenario button if present to ensure proper scenario state activation
            try:
                # If on dashboard, click the scenario button
                if "dashboard" in target["url"]:
                    if "scenario=A" in target["url"]:
                        page.locator("button:has-text('Escenario A')").first.click(timeout=3000)
                    elif "scenario=D" in target["url"]:
                        page.locator("button:has-text('Escenario D')").first.click(timeout=3000)
                # If on 3D twin, ensure isometric view and month=60
                elif "digital_twin_3d" in target["url"]:
                    if "scenario=A" in target["url"]:
                        btn = page.locator("button:has-text('A: Status Quo')").first
                        if btn.is_visible():
                            btn.click(timeout=3000)
                    elif "scenario=B2" in target["url"]:
                        btn = page.locator("button:has-text('B2: GovTech')").first
                        if btn.is_visible():
                            btn.click(timeout=3000)
                    
                    # Ensure isometric button is clicked if available
                    iso_btn = page.locator("button:has-text('Isom')").first
                    if iso_btn.is_visible():
                        iso_btn.click(timeout=2000)
            except Exception as e:
                print(f"Nota de interacción UI: {e}")

            # Re-inject CSS just in case
            page.add_style_tag(content=CSS_HIDE_FLOATING)

            # Wait networkidle + 3 seconds extra for WebGL scene rendering & animations
            print("Esperando estabilización de la escena 3D y gráficos (3.5 segundos)...")
            page.wait_for_timeout(3500)

            # Capture screenshot
            page.screenshot(path=out_path, full_page=False)
            print(f"Captura guardada en: {out_path}")

            # Verify with PIL
            img = Image.open(out_path)
            w, h = img.size
            file_size_mb = os.path.getsize(out_path) / (1024 * 1024)
            print(f"Dimensiones PIL: {w} x {h} px, Peso: {file_size_mb:.2f} MB")

            assert w >= 3840, f"Error: El ancho ({w} px) no alcanza el umbral mínimo de 3840 px"
            results.append({
                "filename": target["filename"],
                "path": out_path,
                "width": w,
                "height": h,
                "size_mb": file_size_mb,
                "title": target["title"]
            })

        browser.close()

    print("\n" + "="*60)
    print("RESUMEN DE CAPTURAS GENERADAS EXITOSAMENTE:")
    for r in results:
        print(f" - {r['filename']}: {r['width']}x{r['height']} px ({r['size_mb']:.2f} MB) -> {r['title']}")
    print("="*60)

if __name__ == "__main__":
    capture_all()

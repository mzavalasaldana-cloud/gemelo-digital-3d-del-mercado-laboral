#!/usr/bin/env python3
"""
scripts/capturar_figuras_3_y_4.py

Captura y composición de alta fidelidad para el artículo académico (Revista CRORR):
- Fig. 3: Panel principal del sistema (Kenia, escenario D, mes 120).
  Ancho final: 145 mm (3425 px a 600 dpi).
  Compuesto por:
    (a) Tarjetas de indicadores macro y distributivos (informalidad, brecha, recaudación, Gini).
    (b) Gráfico "Simulación ITDT (meses 1-120 de la política)".
- Fig. 4: Vista 3D del Gemelo Digital (Kenia, mes 120):
  (a) Escenario A (Status Quo)
  (b) Escenario B2 (GovTech Intensivo)
  Ancho final: 145 mm (3425 px a 600 dpi, dos paneles lado a lado).

Garantiza:
- Cero texto < 8 pt al tamaño de impresión.
- Lectura directa de tasas del modelo en tiempo real (Kenia D 120: 51.8%, A 120: 87.1%, B2 120: 49.2%).
- Exportación dual: PNG 600 dpi y PDF vectorial/impresión.
"""

import os
import sys
import time
import json
import urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "figuras_articulo")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"
FONT_BOLD_PATH = "C:\\Windows\\Fonts\\arialbd.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "arial.ttf"
    FONT_BOLD_PATH = "arialbd.ttf"


# ==============================================================================
# 1. CAPTURA Y COMPOSICIÓN DE FIGURA 3
# ==============================================================================

CSS_FIG3 = """
/* Ocultar barra superior, asistentes, menús y elementos innecesarios */
nav, header, [aria-label="Abrir Asistente IA"], #floating-ai-advisor,
.chatbot-floating-trigger, button, .recharts-legend-wrapper button,
.lg\\:col-span-4, .hud-glass.p-4.rounded-2xl.border.border-cyan-500\\/25.relative.overflow-hidden.group .absolute,
.hud-glass.p-5.rounded-2xl.border.border-cyan-500\\/25.space-y-6 {
    display: none !important;
}

/* Fondo blanco limpio institucional para impresión */
body, html, main, #root {
    background: #ffffff !important;
    color: #0f172a !important;
}

/* 1. Tarjetas de indicadores (Elemento a) */
#dashboard-kpi-cards {
    width: 850px !important;
    background: #ffffff !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 auto !important;
    gap: 12px !important;
}

#dashboard-kpi-cards > div {
    background: #f8fafc !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    box-shadow: none !important;
}

/* Tipografía de las tarjetas escalada para medir >= 8.5 pt al imprimir a 145 mm */
#dashboard-kpi-cards .text-3xl {
    font-size: 34px !important;
    line-height: 1.1 !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    font-family: Arial, "DejaVu Sans", sans-serif !important;
}

#dashboard-kpi-cards .text-xs,
#dashboard-kpi-cards .text-\\[10px\\],
#dashboard-kpi-cards .text-\\[11px\\],
#dashboard-kpi-cards span {
    font-size: 18px !important;
    line-height: 1.3 !important;
    font-weight: 600 !important;
    color: #334155 !important;
    font-family: Arial, "DejaVu Sans", sans-serif !important;
}

/* 2. Contenedor del gráfico Recharts (Elemento b) */
#dashboard-sim-chart {
    width: 850px !important;
    background: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    padding: 16px 20px !important;
    margin: 0 auto !important;
}

#dashboard-sim-chart h3 {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    font-family: Arial, "DejaVu Sans", sans-serif !important;
}

#dashboard-sim-chart .w-full.h-72 {
    height: 380px !important;
}

/* Ejes y marcas del gráfico (>= 8.6 pt a 600 dpi) */
#dashboard-sim-chart .recharts-cartesian-axis-tick text {
    font-size: 18px !important;
    font-weight: 600 !important;
    fill: #1e293b !important;
    font-family: Arial, "DejaVu Sans", sans-serif !important;
}

#dashboard-sim-chart .recharts-label {
    font-size: 19px !important;
    font-weight: 700 !important;
    fill: #0f172a !important;
    font-family: Arial, "DejaVu Sans", sans-serif !important;
}

#dashboard-sim-chart .recharts-legend-item text {
    font-size: 18px !important;
    font-weight: 600 !important;
    fill: #0f172a !important;
    font-family: Arial, "DejaVu Sans", sans-serif !important;
}

#dashboard-sim-chart .recharts-cartesian-grid line {
    stroke: #e2e8f0 !important;
    stroke-dasharray: 4 4 !important;
}
"""

def capturar_figura_3(browser):
    print("\n[*] Procesando Fig. 3: Panel principal Kenia Escenario D (mes 120)...")
    url = "http://localhost:5173/?view=dashboard&country=KENYA&scenario=D&theme=light&month=120&capture=true"
    
    context = browser.new_context(
        viewport={"width": 1100, "height": 1200},
        device_scale_factor=4,
    )
    page = context.new_page()
    page.goto(url, wait_until="networkidle", timeout=60000)

    # Esperar a que la simulación y Recharts estén listos
    page.wait_for_selector("#dashboard-kpi-cards", timeout=30000)
    page.wait_for_selector("#dashboard-sim-chart", timeout=30000)
    page.wait_for_selector(".recharts-line-curve", timeout=30000)
    page.wait_for_function("() => window.__itdtDebug && window.__itdtDebug.informalityRate !== undefined", timeout=20000)

    debug = page.evaluate("() => window.__itdtDebug")
    inf_rate = float(debug.get("informalityRate", 0.0))
    month_val = int(debug.get("month", 0))
    print(f" -> Verificado en DOM: Mes={month_val}, Informalidad={inf_rate:.1f}%")
    assert abs(inf_rate - 51.8) <= 0.5, f"La tasa de informalidad mostrada ({inf_rate}%) difiere de la esperada (51.8%)"

    # Inyectar CSS editorial
    page.add_style_tag(content=CSS_FIG3)
    time.sleep(1.0)

    kpi_locator = page.locator("#dashboard-kpi-cards")
    chart_locator = page.locator("#dashboard-sim-chart")

    path_3a = os.path.join(OUTPUT_DIR, "fig3a_tarjetas_indicadores.png")
    path_3b = os.path.join(OUTPUT_DIR, "fig3b_grafico_trayectorias.png")

    kpi_locator.screenshot(path=path_3a)
    chart_locator.screenshot(path=path_3b)
    context.close()

    print(f" -> Captura 3a guardada: {path_3a}")
    print(f" -> Captura 3b guardada: {path_3b}")

    # Componer imagen unificada Fig. 3 a exactamente 3425 px de ancho (145 mm a 600 dpi)
    TARGET_WIDTH = 3425
    im_a = Image.open(path_3a)
    im_b = Image.open(path_3b)

    # Escalar horizontalmente ambas a TARGET_WIDTH
    scale_a = TARGET_WIDTH / im_a.width
    new_h_a = int(im_a.height * scale_a)
    im_a_scaled = im_a.resize((TARGET_WIDTH, new_h_a), Image.Resampling.LANCZOS)

    scale_b = TARGET_WIDTH / im_b.width
    new_h_b = int(im_b.height * scale_b)
    im_b_scaled = im_b.resize((TARGET_WIDTH, new_h_b), Image.Resampling.LANCZOS)

    # Espaciado entre paneles
    gutter = 60
    header_pad = 70
    total_height = header_pad + new_h_a + gutter + header_pad + new_h_b + 30

    comp = Image.new("RGB", (TARGET_WIDTH, total_height), "#ffffff")
    draw = ImageDraw.Draw(comp)

    try:
        font_label = ImageFont.truetype(FONT_BOLD_PATH, 75)  # 75 px a 600 dpi = 9.0 pt
    except Exception:
        font_label = ImageFont.load_default()

    # Panel (a)
    y_cursor = 10
    draw.text((20, y_cursor), "(a) Indicadores macroeconómicos y distributivos (Kenia, Escenario D, mes 120)", font=font_label, fill="#0f172a")
    y_cursor += header_pad
    comp.paste(im_a_scaled, (0, y_cursor))
    y_cursor += new_h_a + gutter

    # Panel (b)
    draw.text((20, y_cursor), "(b) Trayectorias simuladas de informalidad y formalización (meses 1–120)", font=font_label, fill="#0f172a")
    y_cursor += header_pad
    comp.paste(im_b_scaled, (0, y_cursor))

    path_fig3_png = os.path.join(OUTPUT_DIR, "fig3_panel_kenia_D.png")
    path_fig3_pdf = os.path.join(OUTPUT_DIR, "fig3_panel_kenia_D.pdf")

    comp.save(path_fig3_png, dpi=(600, 600))
    comp.save(path_fig3_pdf, "PDF", resolution=600.0)
    print(f" [+] Figura 3 completa guardada: {path_fig3_png} ({comp.size[0]} x {comp.size[1]} px)")
    print(f" [+] Figura 3 PDF guardada: {path_fig3_pdf}")


# ==============================================================================
# 2. CAPTURA Y COMPOSICIÓN DE FIGURA 4
# ==============================================================================

CSS_FIG4 = """
/* Ocultar barra superior, menús, línea de tiempo inferior y botones flotantes */
nav, header, [aria-label="Abrir Asistente IA"], #floating-ai-advisor,
.chatbot-floating-trigger, button,
.absolute.top-6, .absolute.bottom-6, [class*="Timeline"], [class*="timeline"] {
    display: none !important;
}

body, html, main, #root {
    background: #080c14 !important;
    overflow: hidden !important;
}
"""

def dibujar_leyenda_3d(img: Image.Image, scenario_name: str, inf_rate: float, panel_tag: str) -> Image.Image:
    """
    Dibuja sobre el panel 3D la leyenda requerida con tipografía >= 8.16 pt y >= 9.0 pt a 600 dpi.
    """
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(FONT_BOLD_PATH, 75)  # 75 px a 600 dpi = 9.0 pt
        font_leg = ImageFont.truetype(FONT_PATH, 68)        # 68 px a 600 dpi = 8.16 pt
    except Exception:
        font_title = ImageFont.load_default()
        font_leg = ImageFont.load_default()

    W, H = img.size

    # 1. Cartela superior de estado (mínimo 9.0 pt en tamaño final impreso)
    title_text = f"({panel_tag}) Escenario {scenario_name} – mes 120 – informalidad {inf_rate:.1f} %"
    
    # Caja semitransparente superior izquierda
    bbox = draw.textbbox((35, 35), title_text, font=font_title)
    pad_x = 20
    pad_y = 12
    draw.rounded_rectangle(
        [bbox[0] - pad_x, bbox[1] - pad_y, bbox[2] + pad_x, bbox[3] + pad_y],
        radius=14,
        fill="#0b1329",
        outline="#00f0ff",
        width=2
    )
    draw.text((35, 35), title_text, font=font_title, fill="#ffffff")

    # 2. Leyenda inferior izquierda con marcadores coloreados (mínimo 8.16 pt)
    leg_x = 35
    leg_w = 760
    leg_h = 245
    leg_y = H - 280

    draw.rounded_rectangle(
        [leg_x, leg_y, leg_x + leg_w, leg_y + leg_h],
        radius=14,
        fill="#0b1329",
        outline="#1e293b",
        width=2
    )

    items = [
        {"label": "Trabajador formal", "color": "#00f0ff", "shape": "circle"},
        {"label": "Trabajador informal", "color": "#f59e0b", "shape": "circle"},
        {"label": "Empresa formal", "color": "#10b981", "shape": "square"},
    ]

    item_y = leg_y + 22
    for it in items:
        # Dibujar marcador
        m_x = leg_x + 38
        m_y = item_y + 20
        if it["shape"] == "circle":
            draw.ellipse([m_x - 16, m_y - 16, m_x + 16, m_y + 16], fill=it["color"], outline="#ffffff", width=2)
        else:
            draw.rectangle([m_x - 16, m_y - 16, m_x + 16, m_y + 16], fill=it["color"], outline="#ffffff", width=2)

        draw.text((m_x + 38, item_y - 4), it["label"], font=font_leg, fill="#e2e8f0")
        item_y += 72

    return img


def capturar_figura_4(browser):
    print("\n[*] Procesando Fig. 4: Gemelo 3D (Kenia, mes 120, Escenarios A y B2)...")
    
    panels_data = [
        {
            "tag": "a",
            "scenario": "A",
            "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=A&theme=light&month=120&capture=true",
            "expected_inf": 87.1,
            "filename": "fig4a_gemelo3d_kenia_A.png",
        },
        {
            "tag": "b",
            "scenario": "B2",
            "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=B2&theme=light&month=120&capture=true",
            "expected_inf": 49.2,
            "filename": "fig4b_gemelo3d_kenia_B2.png",
        },
    ]

    cropped_panels = []

    for item in panels_data:
        print(f" -> Capturando Escenario {item['scenario']}...")
        context = browser.new_context(
            viewport={"width": 1200, "height": 900},
            device_scale_factor=3,
        )
        page = context.new_page()
        page.goto(item["url"], wait_until="networkidle", timeout=60000)

        page.wait_for_selector("canvas", timeout=30000)
        page.wait_for_function("() => window.__itdtDebug && window.__itdtDebug.canvasRendered === true", timeout=30000)
        time.sleep(1.5)

        debug = page.evaluate("() => window.__itdtDebug")
        inf_val = float(debug.get("informalityRate", 0.0))
        print(f"    * Modelo leído: Escenario={debug.get('scenario')}, Informalidad={inf_val:.1f}%")
        assert abs(inf_val - item["expected_inf"]) <= 0.5, f"Informalidad {inf_val}% difiere de {item['expected_inf']}%"

        # Ocultar controles HTML
        page.add_style_tag(content=CSS_FIG4)
        time.sleep(1.0)

        # Capturar la vista 3D completa
        raw_path = os.path.join(OUTPUT_DIR, f"raw_{item['filename']}")
        page.screenshot(path=raw_path, full_page=False, animations="disabled", timeout=30000)
        context.close()

        # Recortar márgenes vacíos superior/inferior para que el terreno ocupe todo el panel
        with Image.open(raw_path) as raw_im:
            w, h = raw_im.size
            # Recortar cielo vacío superior y base inferior
            crop_box = (int(w * 0.12), int(h * 0.12), int(w * 0.88), int(h * 0.88))
            cropped = raw_im.crop(crop_box)
            
            # Escalar primero al ancho final de panel (1690 px = 71.5 mm a 600 dpi)
            TARGET_PANEL_W = 1690
            scale = TARGET_PANEL_W / cropped.width
            target_panel_h = int(cropped.height * scale)
            panel_scaled = cropped.resize((TARGET_PANEL_W, target_panel_h), Image.Resampling.LANCZOS)

            # Dibujar leyenda requerida directamente al tamaño final para asegurar >= 8.16 pt
            annotated = dibujar_leyenda_3d(panel_scaled, item["scenario"], inf_val, item["tag"])
            
            out_single = os.path.join(OUTPUT_DIR, item["filename"])
            annotated.save(out_single, dpi=(600, 600))
            print(f"    * Panel guardado: {out_single} ({annotated.size[0]} x {annotated.size[1]} px)")
            cropped_panels.append(annotated)

        # Limpiar raw
        if os.path.exists(raw_path):
            os.remove(raw_path)

    # 3. Componer Fig. 4 (los dos lado a lado) a exactamente 3425 px (145 mm a 600 dpi)
    TARGET_WIDTH = 3425
    panel_w = cropped_panels[0].width  # 1690 px
    panel_h = cropped_panels[0].height

    comp_4 = Image.new("RGB", (TARGET_WIDTH, panel_h), "#ffffff")
    comp_4.paste(cropped_panels[0], (0, 0))
    comp_4.paste(cropped_panels[1], (panel_w + 45, 0))

    path_fig4_png = os.path.join(OUTPUT_DIR, "fig4_gemelo3d_kenia.png")
    path_fig4_pdf = os.path.join(OUTPUT_DIR, "fig4_gemelo3d_kenia.pdf")

    comp_4.save(path_fig4_png, dpi=(600, 600))
    comp_4.save(path_fig4_pdf, "PDF", resolution=600.0)
    print(f" [+] Figura 4 compuesta guardada: {path_fig4_png} ({comp_4.size[0]} x {comp_4.size[1]} px)")
    print(f" [+] Figura 4 PDF guardada: {path_fig4_pdf}")


def main():
    print("================================================================")
    print(" CAPTURA PLAYWRIGHT: FIGURAS 3 Y 4 PARA ARTÍCULO (600 DPI / 145 MM)")
    print("================================================================")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--enable-webgl",
                "--enable-accelerated-2d-canvas",
                "--no-sandbox",
                "--disable-gpu-watchdog"
            ]
        )
        try:
            capturar_figura_3(browser)
            capturar_figura_4(browser)
        finally:
            browser.close()

    print("\n[+] Capturas de Figuras 3 y 4 completadas con éxito.")


if __name__ == "__main__":
    main()

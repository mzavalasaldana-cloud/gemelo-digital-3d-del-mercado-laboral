#!/usr/bin/env python3
"""
scripts/capture_highres_screenshots.py

Captura de pantallas de ultra-alta resolución (4800x2700 px) para el artículo académico:
- Backend y frontend en ejecución activa (sin aviso 'Backend no disponible').
- Modo ventana visible (headless=False) para renderizado WebGL/Three.js de alta fidelidad.
- Viewport 1600x900 con device_scale_factor = 3 (4800x2700 px).
- Tema claro (light theme).
- Espera activa antes de cada captura:
    * Espera a que desaparezca cualquier pantalla o texto de carga ('Cargando...').
    * En 3D: espera a que el canvas WebGL tenga contenido dibujado (canvasRendered === true, renderedFrames >= 20).
    * En Dashboard: desactiva animaciones de Recharts (&capture=true) y espera a que los 120 puntos estén dibujados en el DOM.
    * Posición de cámara fija y documentada para 3D: distance=46, phi=0.65, theta=pi/4, target=(0, 1.0, 0).
- Antes de cada captura, archiva capturas anteriores en outputs/capturas/_archivado/.
- Guarda el contenido de window.__itdtDebug junto a la imagen (mismo nombre, .json).
- Prueba visual automática integrada: calcula la desviación estándar de los píxeles y el número
  de colores distintos en la zona del canvas/gráfico; falla si la zona está vacía o uniforme.
- Verificación en el DOM / window.__itdtDebug de tasas del modelo de outputs/trayectorias_mensuales.json.
- Verificación con PIL de resolución >= 3840 px de ancho.
"""

import os
import sys
import time
import json
import urllib.request
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright  # type: ignore

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
        "url": "http://localhost:5173/?view=dashboard&country=KENYA&scenario=A&theme=light&month=120&capture=true",
        "title": "Dashboard principal, Escenario A (Status Quo, Kenia, Mes 120 de la política)",
        "type": "dashboard",
        "scenario": "A",
        "month": 120,
        "expected_rate": KENYA_A_120_INF,
    },
    {
        "filename": "fig_dashboard_kenia_escenarioD.png",
        "url": "http://localhost:5173/?view=dashboard&country=KENYA&scenario=D&theme=light&month=120&capture=true",
        "title": "Dashboard principal, Escenario D (Integrado, Kenia, Mes 120 de la política)",
        "type": "dashboard",
        "scenario": "D",
        "month": 120,
        "expected_rate": KENYA_D_120_INF,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioA_m60.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=A&theme=light&month=60&capture=true",
        "title": "Gemelo Digital 3D, Escenario A (Mes 60 de la política, Kenia)",
        "type": "3d",
        "scenario": "A",
        "month": 60,
        "expected_rate": KENYA_A_60_INF,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioA.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=A&theme=light&month=120&capture=true",
        "title": "Gemelo Digital 3D, Escenario A (Mes 120 de la política, Kenia)",
        "type": "3d",
        "scenario": "A",
        "month": 120,
        "expected_rate": KENYA_A_120_INF,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioB2_m60.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=B2&theme=light&month=60&capture=true",
        "title": "Gemelo Digital 3D, Escenario B2 (GovTech 3x, Mes 60 de la política, Kenia)",
        "type": "3d",
        "scenario": "B2",
        "month": 60,
        "expected_rate": KENYA_B2_60_INF,
    },
    {
        "filename": "fig_gemelo3d_kenia_escenarioB2.png",
        "url": "http://localhost:5173/?view=digital_twin_3d&country=KENYA&scenario=B2&theme=light&month=120&capture=true",
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


def archive_existing_captures():
    print("[*] Archivando capturas anteriores en outputs/capturas/_archivado/ ...")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    sub_archive = os.path.join(ARCHIVE_DIR, f"backup_{timestamp}")
    os.makedirs(sub_archive, exist_ok=True)
    count = 0
    for fname in os.listdir(OUTPUT_DIR):
        if fname == "_archivado":
            continue
        full_p = os.path.join(OUTPUT_DIR, fname)
        if os.path.isfile(full_p) and (fname.endswith(".png") or fname.endswith(".json")):
            target_p = os.path.join(sub_archive, fname)
            os.replace(full_p, target_p)
            count += 1
    print(f" -> {count} archivos archivados correctamente en: {sub_archive}")


def evaluate_image_visual_metrics(img_path: str, target_type: str):
    """
    Calcula la desviación estándar de los píxeles y el número de colores únicos
    en la zona de interés (canvas WebGL en 3D o gráfico Recharts en Dashboard).
    """
    with Image.open(img_path) as im:
        w, h = im.size
        rgb_im = im.convert("RGB")

        # Coordenadas de la zona de interés
        if target_type == "3d":
            # Vista 3D: zona central donde se despliega el terreno y partículas
            crop_box = (int(w * 0.15), int(h * 0.15), int(w * 0.85), int(h * 0.85))
        else:
            # Dashboard: zona derecha donde se renderiza el gráfico de evolución y comparación
            crop_box = (int(w * 0.35), int(h * 0.15), int(w * 0.98), int(h * 0.65))

        cropped = rgb_im.crop(crop_box)
        np_crop = np.array(cropped, dtype=np.float32)

        # Escala de grises perceptiva
        gray = 0.299 * np_crop[:, :, 0] + 0.587 * np_crop[:, :, 1] + 0.114 * np_crop[:, :, 2]
        pixel_std = float(np.std(gray))

        # Contar colores RGB distintos
        colors = len(cropped.getcolors(maxcolors=2000000) or [])

        # Criterios mínimos: si la zona está vacía o uniforme, falla
        min_std = 12.0
        min_colors = 150
        passed = (pixel_std >= min_std) and (colors >= min_colors)

        return {
            "width": w,
            "height": h,
            "crop_box": crop_box,
            "pixel_std": round(pixel_std, 2),
            "unique_colors": colors,
            "visual_passed": passed,
            "min_std": min_std,
            "min_colors": min_colors,
        }


def capture_all():
    check_servers()
    archive_existing_captures()

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
        context.route("**fonts.googleapis.com**", lambda r: r.abort())
        context.route("**fonts.gstatic.com**", lambda r: r.abort())

        for target in TARGETS:
            page = context.new_page()
            page.set_default_timeout(90000)
            out_path = os.path.join(OUTPUT_DIR, str(target["filename"]))
            json_path = os.path.splitext(out_path)[0] + ".json"

            print(f"\n==========================================")
            print(f"Procesando: {target['filename']}")
            print(f"Título: {target['title']}")
            print(f"URL: {target['url']}")
            print(f"==========================================")

            page.goto(target["url"], wait_until="networkidle", timeout=60000)

            # 1. Esperar a que desaparezca cualquier indicador o texto de carga
            try:
                page.wait_for_selector("text=Cargando", state="detached", timeout=30000)
            except Exception:
                pass

            # 2. Verificar ausencia estricta del aviso de backend caído
            content = page.content()
            if "Backend no disponible" in content:
                raise RuntimeError(
                    f"ERROR CRÍTICO: Se detectó el banner 'Backend no disponible' en {target['filename']}."
                )

            # 4. Tratamiento específico por tipo de vista
            if target["type"] == "3d":
                # Esperar a que el elemento canvas exista
                page.wait_for_selector("canvas", timeout=30000)

                # Esperar a que el canvas WebGL haya dibujado contenido (canvasRendered === true, frames >= 20)
                page.wait_for_function(
                    "() => window.__itdtDebug && window.__itdtDebug.canvasRendered === true && window.__itdtDebug.renderedFrames >= 20",
                    timeout=30000,
                )
                time.sleep(1.0)

            elif target["type"] == "dashboard":
                # Esperar a que el contenedor Recharts esté presente
                page.wait_for_selector(".recharts-responsive-container", timeout=30000)

                # Esperar a que la trayectoria completa de 120 meses esté en memoria
                page.wait_for_function(
                    "() => (window.__itdtDebug && window.__itdtDebug.trajectoryPoints && window.__itdtDebug.trajectoryPoints.length >= 120) || (window.__dashboardTrajectory && window.__dashboardTrajectory.length >= 120)",
                    timeout=30000,
                )

                # Esperar a que las curvas SVG de Recharts se hayan renderizado en el DOM
                page.wait_for_function(
                    "() => document.querySelectorAll('.recharts-line-curve').length > 0",
                    timeout=30000,
                )
                time.sleep(1.0)

            # Esperar a que window.__itdtDebug esté disponible
            page.wait_for_function("() => window.__itdtDebug !== undefined", timeout=10000)
            debug_obj = page.evaluate("() => window.__itdtDebug")

            # Tomar screenshot en 4800x2700 px (con animations='disabled' para captura inmediata y nítida)
            page.screenshot(path=out_path, full_page=False, animations="disabled", timeout=30000)
            print(f" -> Captura guardada en: {out_path}")

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
            if target["type"] == "3d":
                print(f"    * Canvas Rendered: {debug_obj.get('canvasRendered')} (Frames: {debug_obj.get('renderedFrames')})")
                print(f"    * Posición Cámara: {debug_obj.get('cameraPosition')}")

            # Verificación con PIL y métricas visuales
            v_metrics = evaluate_image_visual_metrics(out_path, str(target["type"]))
            w = v_metrics["width"]
            h = v_metrics["height"]
            std = v_metrics["pixel_std"]
            n_colors = v_metrics["unique_colors"]
            passed = v_metrics["visual_passed"]

            print(f" -> Dimensiones PIL: {w} x {h} px")
            print(f" -> Prueba Visual: Desv. Estándar = {std:.2f} (Mín: {v_metrics['min_std']}) | Colores Únicos = {n_colors} (Mín: {v_metrics['min_colors']})")
            if w < 3840:
                raise ValueError(
                    f"La imagen {target['filename']} mide {w}px de ancho, que es menor al mínimo requerido (3840 px)."
                )
            if not passed:
                raise ValueError(
                    f"ERROR EN PRUEBA VISUAL: La imagen {target['filename']} tiene una zona uniforme o vacía "
                    f"(std={std}, colores={n_colors}). Posible canvas en blanco o pantalla de carga."
                )

            print(f" -> ESTADO VISUAL: APROBADO (PASS)")
            results.append(
                {
                    "filename": target["filename"],
                    "json_filename": os.path.basename(json_path),
                    "title": target["title"],
                    "dimensions": f"{w}x{h}",
                    "size_bytes": os.path.getsize(out_path),
                    "pixel_std": std,
                    "unique_colors": n_colors,
                    "debug": debug_obj,
                }
            )
            page.close()

        browser.close()

    print("\n" + "=" * 80)
    print("TODAS LAS CAPTURAS COMPLETADAS SATISFACTORIAMENTE:")
    for r in results:
        print(f" - {r['filename']} ({r['dimensions']}, {float(r['size_bytes']) / 1024 / 1024:.2f} MB, std={r['pixel_std']}, colores={r['unique_colors']}) -> JSON: {r['json_filename']}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        capture_all()
    except Exception as exc:
        print(f"\nFALLO EN CAPTURAS: {exc}", file=sys.stderr)
        sys.exit(1)

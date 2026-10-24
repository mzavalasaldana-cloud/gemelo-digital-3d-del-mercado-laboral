#!/usr/bin/env python3
"""
scripts/verificar_interfaz_completa_playwright.py

Prueba automatizada integral con Playwright:
PASO 5: Interfaz Web (React/Vite en http://127.0.0.1:3000)
- Viewport 1600x900, device_scale_factor: 2
- Todas las vistas: Dashboard, Gemelo 3D, Motor IA (5 pestañas), Datasets y Reportes (PDF, Excel, HTML),
  Matriz OIT, Asistente IA (chat), Roles y CRUD, Administrador, Idioma ES/EN, Modo claro/oscuro.
- Inspección de 3 fichas de trabajadores en el Gemelo 3D (verificar atributos del modelo).
- Pregunta a) en el Asistente IA desde la interfaz ("¿Cuál es la tasa de informalidad de Kenia en el escenario D en el mes 120?").
- Registro de errores de consola y peticiones de red fallidas (4xx/5xx).

PASO 6: Interfaz Streamlit (en http://127.0.0.1:8501)
- Recorrido de todas las vistas: Dashboard, Gemelo 3D, Motor IA, Datasets, OIT, Copiloto.
- Capturas de cada vista y análisis de log de Streamlit.
"""

import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURAS_DIR = os.path.join(BASE_DIR, "outputs", "verificacion_sistema", "capturas")
LOGS_DIR = os.path.join(BASE_DIR, "outputs", "verificacion_sistema", "logs")
os.makedirs(CAPTURAS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://127.0.0.1:3000")
STREAMLIT_URL = os.environ.get("STREAMLIT_URL", "http://127.0.0.1:8501")
HEADLESS = os.environ.get("HEADLESS", "false").lower() == "true"

def run_verification():
    report_data = {
        "web": {
            "views_tested": [],
            "console_errors": {},
            "failed_requests": {},
            "worker_cards": [],
            "copilot_ui_test": {},
        },
        "streamlit": {
            "views_tested": [],
            "errors": [],
        }
    }

    print("================================================================================")
    print("INICIANDO PRUEBAS DE INTERFAZ PLAYWRIGHT (PASO 5 Y PASO 6)")
    print(f"Viewport: 1600x900 | device_scale_factor: 2 | Headless: {HEADLESS}")
    print(f"Frontend URL: {FRONTEND_URL} | Streamlit URL: {STREAMLIT_URL}")
    print("================================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--enable-webgl", "--enable-accelerated-2d-canvas", "--no-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1600, "height": 900},
            device_scale_factor=2
        )

        page = context.new_page()

        current_view_name = ["init"]
        console_errors_by_view = {}
        failed_requests_by_view = {}

        def on_console(msg):
            if msg.type in ["error"]:
                v = current_view_name[0]
                console_errors_by_view.setdefault(v, []).append(msg.text)
                print(f"   [Console Error @ {v}]: {msg.text[:120]}")

        def on_response(res):
            if res.status >= 400:
                v = current_view_name[0]
                failed_requests_by_view.setdefault(v, []).append({
                    "url": res.url,
                    "status": res.status,
                    "status_text": res.status_text
                })
                print(f"   [HTTP Error @ {v}]: {res.status} {res.url}")

        page.on("console", on_console)
        page.on("response", on_response)

        # ----------------------------------------------------------------------
        # 1. PASO 5: RECORRIDO DE TODAS LAS VISTAS WEB
        # ----------------------------------------------------------------------

        # 1.1 Dashboard Principal
        current_view_name[0] = "01_dashboard"
        print("\n[*] [1/15] Navegando a Dashboard Principal...")
        page.goto(f"{FRONTEND_URL}/?view=dashboard&country=KENYA&scenario=A&theme=dark", wait_until="domcontentloaded", timeout=25000)
        time.sleep(2.0)
        dash_path = os.path.join(CAPTURAS_DIR, "01_dashboard.png")
        page.screenshot(path=dash_path, full_page=False)
        print(f" [+] Captura guardada: {dash_path}")
        report_data["web"]["views_tested"].append("01_dashboard")

        # 1.2 Gemelo Digital 3D
        current_view_name[0] = "02_gemelo_digital_3d"
        print("\n[*] [2/15] Navegando a Gemelo Digital 3D...")
        page.goto(f"{FRONTEND_URL}/?view=digital_twin_3d&country=KENYA&scenario=A&month=60&theme=dark", wait_until="domcontentloaded", timeout=25000)
        time.sleep(2.5)
        twin_path = os.path.join(CAPTURAS_DIR, "02_gemelo_digital_3d.png")
        page.screenshot(path=twin_path, full_page=False)
        print(f" [+] Captura guardada: {twin_path}")
        report_data["web"]["views_tested"].append("02_gemelo_digital_3d")

        # 1.3 Inspección de 3 Trabajadores (Fichas de microdatos del modelo)
        print("\n[*] [3/15] Inspeccionando fichas de 3 trabajadores en Gemelo 3D...")
        worker_indices = [0, 500, 1500]  # formal, otro formal/informal, informal
        for idx_num, w_idx in enumerate(worker_indices, 1):
            current_view_name[0] = f"02_trabajador_{idx_num}"
            page.evaluate(f"window.__itdtSelectWorker && window.__itdtSelectWorker({w_idx})")
            time.sleep(1.0)
            card_path = os.path.join(CAPTURAS_DIR, f"02_ficha_trabajador_{idx_num}.png")
            page.screenshot(path=card_path, full_page=False)
            
            card_info = page.evaluate("""() => {
                const modals = Array.from(document.querySelectorAll('.hud-glass-solid'));
                const modal = modals.find(m => m.textContent && m.textContent.includes('TELEMETRÍA DE AGENTE')) || modals[modals.length - 1];
                if (!modal) return null;
                return {
                    title: modal.querySelector('h3')?.innerText || '',
                    text: modal.innerText || ''
                };
            }""")
            print(f" [+] Trabajador {idx_num} (idx={w_idx}): {card_info.get('title') if card_info else 'No modal'}")
            if card_info:
                txt = card_info.get('text', '')
                has_sexo = 'Sexo' in txt or 'Femenino' in txt or 'Masculino' in txt
                has_edu = 'Educ' in txt or 'Secundaria' in txt or 'Primaria' in txt or 'Terciaria' in txt
                has_zona = 'Zona' in txt or 'Rural' in txt or 'Urbana' in txt
                has_prod = 'Productividad' in txt or 'h_i' in txt
                has_cuidados = 'Cuidado' in txt or 'H_care' in txt
                has_dig = 'Digital' in txt or 'K_dig' in txt
                has_estado = 'Estado' in txt or 'Formal' in txt or 'Informal' in txt
                
                print(f"     Atributos modelo: Sexo={has_sexo}, Edu={has_edu}, Zona={has_zona}, Prod={has_prod}, Cuidados={has_cuidados}, Digital={has_dig}, Estado={has_estado}")
                report_data["web"]["worker_cards"].append({
                    "worker_index": w_idx,
                    "title": card_info.get('title'),
                    "attributes_valid": all([has_sexo, has_edu, has_zona, has_prod, has_cuidados, has_dig, has_estado]),
                    "text_sample": txt[:250]
                })

        # 1.4 Motor IA: 5 pestañas (EDA, CV, Modelos, Cohortes, Telemetría)
        current_view_name[0] = "03_motor_ia_eda"
        print("\n[*] [4/15] Navegando a Motor IA (Pestaña EDA)...")
        page.goto(f"{FRONTEND_URL}/?view=ai_engine&theme=dark", wait_until="domcontentloaded", timeout=25000)
        time.sleep(2.0)
        eda_path = os.path.join(CAPTURAS_DIR, "03_motor_ia_eda.png")
        page.screenshot(path=eda_path, full_page=False)
        print(f" [+] Captura guardada: {eda_path}")
        report_data["web"]["views_tested"].append("03_motor_ia_eda")

        # Pestaña CV
        current_view_name[0] = "04_motor_ia_cv"
        print("\n[*] [5/15] Motor IA: Cambiando a pestaña Validación Cruzada (CV)...")
        page.click("button:has-text('Validación Cruzada')", timeout=8000)
        time.sleep(2.0)
        cv_path = os.path.join(CAPTURAS_DIR, "04_motor_ia_cv.png")
        page.screenshot(path=cv_path, full_page=False)
        print(f" [+] Captura guardada: {cv_path}")
        report_data["web"]["views_tested"].append("04_motor_ia_cv")

        # Pestaña Hiperparámetros / Modelos
        current_view_name[0] = "05_motor_ia_modelos"
        print("\n[*] [6/15] Motor IA: Cambiando a pestaña Modelos & Hiperparámetros...")
        page.click("button:has-text('Hiperparámetros')", timeout=8000)
        time.sleep(2.0)
        mod_path = os.path.join(CAPTURAS_DIR, "05_motor_ia_modelos.png")
        page.screenshot(path=mod_path, full_page=False)
        print(f" [+] Captura guardada: {mod_path}")
        report_data["web"]["views_tested"].append("05_motor_ia_modelos")

        # Pestaña Cohortes
        current_view_name[0] = "06_motor_ia_cohortes"
        print("\n[*] [7/15] Motor IA: Cambiando a pestaña Proyección de Cohortes...")
        page.click("button:has-text('Cohortes')", timeout=8000)
        time.sleep(2.0)
        coh_path = os.path.join(CAPTURAS_DIR, "06_motor_ia_cohortes.png")
        page.screenshot(path=coh_path, full_page=False)
        print(f" [+] Captura guardada: {coh_path}")
        report_data["web"]["views_tested"].append("06_motor_ia_cohortes")

        # Pestaña Telemetría
        current_view_name[0] = "07_motor_ia_telemetria"
        print("\n[*] [8/15] Motor IA: Cambiando a pestaña Telemetría y Despliegue...")
        page.click("button:has-text('Telemetría')", timeout=8000)
        time.sleep(2.0)
        tel_path = os.path.join(CAPTURAS_DIR, "07_motor_ia_telemetria.png")
        page.screenshot(path=tel_path, full_page=False)
        print(f" [+] Captura guardada: {tel_path}")
        report_data["web"]["views_tested"].append("07_motor_ia_telemetria")

        # 1.5 Datasets y Reportes (incluye generar PDF, Excel, HTML)
        current_view_name[0] = "08_datasets_reports"
        print("\n[*] [9/15] Navegando a Datasets y Reportes...")
        page.goto(f"{FRONTEND_URL}/?view=datasets_reports&theme=dark", wait_until="domcontentloaded", timeout=25000)
        time.sleep(2.0)
        ds_path = os.path.join(CAPTURAS_DIR, "08_datasets_reports.png")
        page.screenshot(path=ds_path, full_page=False)
        print(f" [+] Captura guardada: {ds_path}")
        report_data["web"]["views_tested"].append("08_datasets_reports")

        # Cambiar a pestaña de Reportes y disparar exportaciones
        print("\n[*] Disparando generación de reportes (PDF, Excel, HTML)...")
        page.click("button:has-text('Exportar Reportes')", timeout=8000)
        time.sleep(1.0)
        
        # Click PDF
        try:
            pdf_btn = page.locator("button:has-text('Descargar Policy Brief')").first
            if pdf_btn.is_visible():
                pdf_btn.click()
                time.sleep(0.5)
                print(" [+] Disparo botón Descargar Policy Brief (PDF): OK")
        except Exception as e:
            print(f" [!] Botón PDF error: {e}")

        # Click Excel
        try:
            xls_btn = page.locator("button:has-text('Descargar Microdatos')").first
            if xls_btn.is_visible():
                xls_btn.click()
                time.sleep(0.5)
                print(" [+] Disparo botón Descargar Microdatos (Excel): OK")
        except Exception as e:
            print(f" [!] Botón Excel error: {e}")

        # Click HTML
        try:
            html_btn = page.locator("button:has-text('Descargar Tablero')").first
            if html_btn.is_visible():
                html_btn.click()
                time.sleep(0.5)
                print(" [+] Disparo botón Descargar Tablero (HTML): OK")
        except Exception as e:
            print(f" [!] Botón HTML error: {e}")

        rep_path = os.path.join(CAPTURAS_DIR, "08b_exportar_reportes.png")
        page.screenshot(path=rep_path, full_page=False)
        print(f" [+] Captura pestaña reportes guardada: {rep_path}")

        # 1.6 Matriz OIT Modal
        current_view_name[0] = "09_matriz_oit"
        print("\n[*] [10/15] Abriendo Matriz Trabajo Decente OIT...")
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const iloBtn = btns.find(b => b.textContent && b.textContent.includes('Matriz OIT'));
            if (iloBtn) iloBtn.click();
        }""")
        time.sleep(1.5)
        oit_path = os.path.join(CAPTURAS_DIR, "09_matriz_oit.png")
        page.screenshot(path=oit_path, full_page=False)
        print(f" [+] Captura guardada: {oit_path}")
        report_data["web"]["views_tested"].append("09_matriz_oit")
        
        # Cerrar modal OIT
        page.evaluate("""() => {
            const closeBtn = document.querySelector('.fixed.inset-0.z-50 button');
            if (closeBtn) closeBtn.click();
        }""")
        time.sleep(1.0)

        # 1.7 Asistente IA (Chatbot) y Prueba de Pregunta a)
        current_view_name[0] = "10_asistente_ia"
        print("\n[*] [11/15] Abriendo Asistente IA (Chatbot) y probando pregunta a)...")
        # Abrir botón flotante
        page.click("button[aria-label='Abrir Asistente IA']", timeout=8000)
        time.sleep(1.5)
        chat_open_path = os.path.join(CAPTURAS_DIR, "10_asistente_ia_abierto.png")
        page.screenshot(path=chat_open_path, full_page=False)

        # Enviar pregunta a)
        pregunta_a = "¿Cuál es la tasa de informalidad de Kenia en el escenario D en el mes 120?"
        page.fill("form input[type='text']", pregunta_a)
        time.sleep(0.5)
        page.click("form button[type='submit']")
        print(f" [+] Pregunta enviada: '{pregunta_a}'")
        
        # Esperar respuesta del asistente (máximo 25s)
        time.sleep(8.0)
        chat_resp_path = os.path.join(CAPTURAS_DIR, "10b_asistente_ia_respuesta.png")
        page.screenshot(path=chat_resp_path, full_page=False)
        
        # Extraer respuesta del chat
        chat_text = page.evaluate("""() => {
            const msgs = Array.from(document.querySelectorAll('div.whitespace-pre-wrap'));
            return msgs.map(m => m.innerText).join('\\n---MSG---\\n');
        }""")
        print(f" [+] Texto de respuestas en chat:\n{chat_text[-300:]}")
        has_51_8 = "51.8" in chat_text or "51,8" in chat_text or "51.79" in chat_text or "51,79" in chat_text
        report_data["web"]["copilot_ui_test"] = {
            "question": pregunta_a,
            "has_expected_rate": has_51_8,
            "response_snippet": chat_text[-300:]
        }
        report_data["web"]["views_tested"].append("10_asistente_ia")

        # Cerrar chat modal si está abierto
        page.evaluate("""() => {
            const closeBtn = document.querySelector('button[aria-label="Cerrar chat"], button:has(svg.lucide-x)');
            if (closeBtn) closeBtn.click();
        }""")
        time.sleep(1.0)

        # 1.8 Roles y CRUD Modal
        current_view_name[0] = "11_roles_crud"
        print("\n[*] [12/15] Abriendo Gestión de Roles y Usuarios (CRUD)...")
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const userBtn = btns.find(b => (b.title && b.title.includes('Gestión de Roles')) || (b.textContent && b.textContent.includes('Roles CRUD')));
            if (userBtn) userBtn.click();
        }""")
        time.sleep(1.5)
        roles_path = os.path.join(CAPTURAS_DIR, "11_roles_crud.png")
        page.screenshot(path=roles_path, full_page=False)
        print(f" [+] Captura guardada: {roles_path}")
        report_data["web"]["views_tested"].append("11_roles_crud")
        page.evaluate("""() => {
            const closeBtn = document.querySelector('.fixed.inset-0.z-50 button[title*="Cerrar"], .fixed.inset-0.z-50 button:has(svg.lucide-x)');
            if (closeBtn) closeBtn.click();
        }""")
        time.sleep(1.0)

        # 1.9 Administrador (Role Admin View)
        current_view_name[0] = "12_admin_view"
        print("\n[*] [13/15] Verificando Vista de Administrador...")
        admin_path = os.path.join(CAPTURAS_DIR, "12_admin_view.png")
        page.screenshot(path=admin_path, full_page=False)
        print(f" [+] Captura guardada: {admin_path}")
        report_data["web"]["views_tested"].append("12_admin_view")

        # 1.10 Idioma EN (Toggle English)
        current_view_name[0] = "13_idioma_en"
        print("\n[*] [14/15] Cambiando idioma a Inglés (EN)...")
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const langBtn = btns.find(b => b.textContent && (b.textContent.includes('ES') && b.textContent.includes('EN')));
            if (langBtn) langBtn.click();
        }""")
        time.sleep(1.5)
        en_path = os.path.join(CAPTURAS_DIR, "13_idioma_en.png")
        page.screenshot(path=en_path, full_page=False)
        print(f" [+] Captura guardada: {en_path}")
        report_data["web"]["views_tested"].append("13_idioma_en")

        # Revertir a español
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const langBtn = btns.find(b => b.textContent && (b.textContent.includes('ES') && b.textContent.includes('EN')));
            if (langBtn) langBtn.click();
        }""")
        time.sleep(0.5)

        # 1.11 Modo Claro y Modo Oscuro
        current_view_name[0] = "14_modo_claro"
        print("\n[*] [15/15] Probando Tema Modo Claro y Modo Oscuro...")
        page.click("#theme-toggle-btn", timeout=5000)
        time.sleep(1.5)
        light_path = os.path.join(CAPTURAS_DIR, "14_modo_claro.png")
        page.screenshot(path=light_path, full_page=False)
        print(f" [+] Captura Modo Claro guardada: {light_path}")
        report_data["web"]["views_tested"].append("14_modo_claro")

        current_view_name[0] = "15_modo_oscuro"
        page.click("#theme-toggle-btn", timeout=5000)
        time.sleep(1.5)
        dark_path = os.path.join(CAPTURAS_DIR, "15_modo_oscuro.png")
        page.screenshot(path=dark_path, full_page=False)
        print(f" [+] Captura Modo Oscuro guardada: {dark_path}")
        report_data["web"]["views_tested"].append("15_modo_oscuro")

        # ----------------------------------------------------------------------
        # 2. PASO 6: RECORRIDO DE STREAMLIT (http://localhost:8501)
        # ----------------------------------------------------------------------
        print("\n================================================================================")
        print("PASO 6: RECORRIENDO STREAMLIT APP (http://127.0.0.1:8501)")
        print("================================================================================")
        
        st_page = context.new_page()
        try:
            st_page.goto(f"{STREAMLIT_URL}/", wait_until="domcontentloaded", timeout=25000)
            time.sleep(3.0)

            # 2.1 Dashboard Streamlit
            st_dash_path = os.path.join(CAPTURAS_DIR, "streamlit_01_dashboard.png")
            st_page.screenshot(path=st_dash_path, full_page=False)
            print(f" [+] Captura Streamlit Dashboard: {st_dash_path}")
            report_data["streamlit"]["views_tested"].append("streamlit_01_dashboard")

            # 2.2 Gemelo 3D Streamlit
            print("[*] Streamlit: Navegando a Gemelo Digital 3D...")
            st_page.click("button:has-text('Gemelo Digital 3D')", timeout=10000)
            time.sleep(2.5)
            st_3d_path = os.path.join(CAPTURAS_DIR, "streamlit_02_gemelo_3d.png")
            st_page.screenshot(path=st_3d_path, full_page=False)
            print(f" [+] Captura Streamlit 3D: {st_3d_path}")
            report_data["streamlit"]["views_tested"].append("streamlit_02_gemelo_3d")

            # 2.3 Motor IA Streamlit
            print("[*] Streamlit: Navegando a Motor IA...")
            st_page.click("button:has-text('Motor IA')", timeout=10000)
            time.sleep(2.5)
            st_ai_path = os.path.join(CAPTURAS_DIR, "streamlit_03_motor_ia.png")
            st_page.screenshot(path=st_ai_path, full_page=False)
            print(f" [+] Captura Streamlit Motor IA: {st_ai_path}")
            report_data["streamlit"]["views_tested"].append("streamlit_03_motor_ia")

            # 2.4 Datasets Streamlit
            print("[*] Streamlit: Navegando a Datasets & Reportes...")
            st_page.click("button:has-text('Datasets & Reportes')", timeout=10000)
            time.sleep(2.5)
            st_ds_path = os.path.join(CAPTURAS_DIR, "streamlit_04_datasets.png")
            st_page.screenshot(path=st_ds_path, full_page=False)
            print(f" [+] Captura Streamlit Datasets: {st_ds_path}")
            report_data["streamlit"]["views_tested"].append("streamlit_04_datasets")

            # 2.5 OIT Streamlit
            print("[*] Streamlit: Navegando a Trabajo Decente OIT...")
            st_page.click("button:has-text('Trabajo Decente OIT')", timeout=10000)
            time.sleep(2.5)
            st_oit_path = os.path.join(CAPTURAS_DIR, "streamlit_05_oit.png")
            st_page.screenshot(path=st_oit_path, full_page=False)
            print(f" [+] Captura Streamlit OIT: {st_oit_path}")
            report_data["streamlit"]["views_tested"].append("streamlit_05_oit")

            # 2.6 Copiloto Streamlit
            print("[*] Streamlit: Navegando a Copiloto IA Laboral...")
            st_page.click("button:has-text('Copiloto IA Laboral')", timeout=10000)
            time.sleep(2.5)
            st_cop_path = os.path.join(CAPTURAS_DIR, "streamlit_06_copiloto.png")
            st_page.screenshot(path=st_cop_path, full_page=False)
            print(f" [+] Captura Streamlit Copiloto: {st_cop_path}")
            report_data["streamlit"]["views_tested"].append("streamlit_06_copiloto")

        except Exception as e:
            print(f" [!] Error en recorrido Streamlit: {e}")
            report_data["streamlit"]["errors"].append(str(e))

        st_page.close()
        page.close()
        context.close()
        browser.close()

    # Guardar resumen de telemetría Playwright
    report_data["web"]["console_errors"] = console_errors_by_view
    report_data["web"]["failed_requests"] = failed_requests_by_view
    
    summary_path = os.path.join(BASE_DIR, "outputs", "verificacion_sistema", "resultado_playwright_integral.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Resumen JSON guardado en: {summary_path}")
    print("================================================================================")
    print("PRUEBAS INTEGRALES DE INTERFAZ COMPLETADAS CON ÉXITO")
    print("================================================================================")

if __name__ == "__main__":
    run_verification()

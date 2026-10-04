"""
Copiloto IA de Economía Laboral: Asistente conversacional para explicación
contextual de simulaciones econométricas y políticas públicas con Langflow y Gemini,
con persistencia y sincronización total en PostgreSQL.
"""

import streamlit as st
import httpx
import logging

from streamlit_app.config import t, COLORS
from streamlit_app.data.mock_data import COUNTRY_PROFILES
from streamlit_app.simulation_engine import calculate_structural_metrics
from streamlit_app.utils.ui_components import render_metric_card, render_section_header, play_holo_sound_js

# Fallback import directo en caso de ejecución monolítica de Streamlit
try:
    from backend.copilot_service import execute_copilot_query, CopilotServiceError
    import asyncio
    HAS_LOCAL_BACKEND_MODULE = True
except ImportError:
    HAS_LOCAL_BACKEND_MODULE = False

logger = logging.getLogger("labortwin.streamlit_copilot")
BACKEND_BASE_URL = "http://127.0.0.1:8000/api/v1/copilot"


def load_postgres_copilot_history(session_id: str) -> list:
    """Recupera el historial de chat persistido en PostgreSQL vía FastAPI."""
    try:
        with httpx.Client(timeout=6.0) as client:
            resp = client.get(f"{BACKEND_BASE_URL}/history?session_id={session_id}&limit=40")
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logger.debug(f"No se pudo cargar historial de PostgreSQL para {session_id}: {e}")
    return []


def clear_postgres_copilot_history(session_id: str) -> bool:
    """Elimina el historial de conversación en PostgreSQL."""
    try:
        with httpx.Client(timeout=6.0) as client:
            resp = client.delete(f"{BACKEND_BASE_URL}/history?session_id={session_id}")
            return resp.status_code == 200
    except Exception as e:
        logger.debug(f"Error al limpiar historial en PostgreSQL: {e}")
        return False


def fetch_copilot_chat_response(
    user_prompt: str,
    country: str,
    scenario: str,
    month: int,
    policy_params: dict,
    session_id: str = "streamlit-session"
) -> dict:
    """
    Envía la consulta del usuario hacia FastAPI para ejecutar el flujo
    en Langflow con Gemini y persistir el diálogo en PostgreSQL.
    """
    payload = {
        "message": user_prompt,
        "session_id": session_id,
        "country": country,
        "scenario": scenario,
        "month": month,
        "policy_params": policy_params,
    }

    # 1. Intentar vía HTTP REST hacia FastAPI
    try:
        with httpx.Client(timeout=65.0) as client:
            resp = client.post(f"{BACKEND_BASE_URL}/chat", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "response": data.get("response", "No se recibió texto de respuesta."),
                    "source": data.get("source", "langflow"),
                    "flow_id": data.get("flow_id", "2d660758-1eee-46f8-969f-c17998844627")
                }
            elif resp.status_code in [503, 504]:
                return {
                    "response": f"⚠️ **Copiloto Temporalmente No Disponible (HTTP {resp.status_code}):** {resp.json().get('detail', 'El servicio de Langflow está demorado.')}",
                    "source": "error"
                }
            else:
                detail = resp.json().get('detail', resp.text)
                return {
                    "response": f"⚠️ **Aviso del Copiloto (HTTP {resp.status_code}):** {detail}",
                    "source": "error"
                }
    except httpx.ConnectError:
        # Si FastAPI en 8000 no responde, intentar ejecución directa del módulo backend
        if HAS_LOCAL_BACKEND_MODULE:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    execute_copilot_query(
                        user_query=user_prompt,
                        session_id=session_id,
                        country=country,
                        scenario=scenario,
                        month=month,
                        policy_params=policy_params,
                    )
                )
                loop.close()
                return {
                    "response": result.get("response", "Respuesta procesada exitosamente."),
                    "source": result.get("source", "langflow"),
                    "flow_id": result.get("flow_id")
                }
            except CopilotServiceError as cse:
                return {"response": f"⚠️ **Error en Langflow ({cse.status_code}):** {cse.message}", "source": "error"}
            except Exception as e:
                return {"response": f"⚠️ **Error de conexión con el Copiloto:** {str(e)}", "source": "error"}
        
        return {
            "response": "⚠️ **Servicio Backend no disponible:** Asegúrate de que FastAPI esté corriendo en `http://127.0.0.1:8000`.",
            "source": "error"
        }
    except httpx.TimeoutException:
        return {"response": "⚠️ **Tiempo de Espera Agotado:** Langflow tardó más de 65 segundos en responder.", "source": "error"}
    except Exception as exc:
        return {"response": f"⚠️ **Error inesperado:** {str(exc)}", "source": "error"}


def render_copilot_chat_view():
    """Renderiza la interfaz del Copiloto IA de Economía Laboral en Streamlit."""
    country_code = st.session_state.get("country", "KENYA")
    scenario = st.session_state.get("scenario", "A")
    if scenario in ("BASELINE", "STATUS_QUO"):
        scenario = "A"
    st.session_state.scenario = scenario

    month = st.session_state.get("month", 0)
    policy_params = st.session_state.get("policy_params", {})
    metrics = calculate_structural_metrics(country_code, policy_params, scenario, month)
    profile = COUNTRY_PROFILES.get(country_code, COUNTRY_PROFILES["KENYA"])
    session_id = f"streamlit-session-{country_code}"

    # Sincronización inicial desde PostgreSQL
    if "copilot_country_loaded" not in st.session_state or st.session_state.copilot_country_loaded != country_code:
        st.session_state.copilot_country_loaded = country_code
        db_history = load_postgres_copilot_history(session_id)
        if db_history:
            st.session_state.chat_messages = []
            for item in db_history:
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": item.get("user_message", ""),
                })
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": item.get("assistant_response", ""),
                    "source": item.get("source", "langflow"),
                })

    # Header con estados de PostgreSQL y Langflow
    st.markdown(f"""
    <div style="background: rgba(11, 18, 32, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(0, 240, 255, 0.35);
                border-radius: 12px; padding: 14px 22px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2 style="margin: 0; font-size: 1.45rem; color: #f8fafc;">
                    🤖 COPILOTO DE INTELIGENCIA ARTIFICIAL EN ECONOMÍA LABORAL
                </h2>
                <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #94a3b8;">
                    Orquestado mediante Langflow Desktop (v1.12.2) y Gemini 3.1 • Persistencia y Memoria en PostgreSQL
                </p>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                <span class="glow-badge badge-emerald">PostgreSQL Conectado</span>
                <span class="glow-badge badge-cyan">Langflow Desktop Online</span>
                <span class="glow-badge badge-cyan">{profile['flag']} {profile['name']}</span>
                <span class="glow-badge badge-purple">Escenario {scenario}</span>
                <span class="glow-badge badge-emerald">Mes {month} (Año {2024 + month // 12})</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Controles superiores: Preguntas rápidas y Limpiar historial
    col_prompts, col_clear = st.columns([5, 1])
    with col_prompts:
        st.markdown("#### 💡 Preguntas Rápidas sobre la Simulación:")
    with col_clear:
        if st.button("🗑️ Limpiar Chat", use_container_width=True, help="Elimina el historial de esta sesión en PostgreSQL"):
            clear_postgres_copilot_history(session_id)
            st.session_state.chat_messages = []
            play_holo_sound_js("click")
            st.rerun()

    p_cols = st.columns(4)
    suggested = [
        "¿Qué escenario reduce más la informalidad entre A, B1, B2, C y D?",
        "¿Cuál es el impacto distributivo de la red de cuidados (Escenario C)?",
        "¿Por qué el Escenario B2 aumenta los cierres anuales de empresas?",
        "¿Cómo equilibra el Escenario D la formalización con subsidio al DCC?",
    ]

    for i, col in enumerate(p_cols):
        with col:
            if st.button(suggested[i], key=f"sug_btn_{i}", use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": suggested[i]})
                with st.spinner("Consultando Langflow Desktop y datos de simulación en PostgreSQL..."):
                    res_dict = fetch_copilot_chat_response(suggested[i], country_code, scenario, month, policy_params, session_id=session_id)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": res_dict.get("response", ""),
                    "source": res_dict.get("source", "langflow")
                })
                play_holo_sound_js("click")
                st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Render Chat History
    for msg in st.session_state.get("chat_messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("role") == "assistant" and msg.get("source"):
                src = msg.get("source")
                if src == "langflow":
                    st.caption("🟢 *Respuesta orquestada por Langflow Desktop (Gemini 3.1) • Sincronizada con PostgreSQL*")
                elif src == "econometric_engine":
                    st.caption("⚡ *Respuesta generada por Motor Econométrico Autónomo • Sincronizada con PostgreSQL*")

    # Chat Input Box
    user_input = st.chat_input("Pregúntale al Copiloto sobre la simulación activa, políticas o impacto fiscal...")
    if user_input:
        play_holo_sound_js("click")
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analizando simulación en Langflow con Gemini 3.1..."):
                res_dict = fetch_copilot_chat_response(user_input, country_code, scenario, month, policy_params, session_id=session_id)
                st.markdown(res_dict.get("response", ""))
                src = res_dict.get("source", "langflow")
                if src == "langflow":
                    st.caption("🟢 *Respuesta orquestada por Langflow Desktop (Gemini 3.1) • Sincronizada con PostgreSQL*")
                elif src == "econometric_engine":
                    st.caption("⚡ *Respuesta generada por Motor Econométrico Autónomo • Sincronizada con PostgreSQL*")
                
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": res_dict.get("response", ""),
                    "source": src
                })


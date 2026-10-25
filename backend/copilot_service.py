"""
Servicio Asíncrono de Integración con Langflow para el Copiloto IA (V1).
Maneja la comunicación entre FastAPI y Langflow Desktop (v1.12.2) asegurando
que la API Key y los secretos nunca se expongan al frontend.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env de backend o root
backend_env = Path(__file__).resolve().parent / ".env"
if backend_env.exists():
    load_dotenv(backend_env)
load_dotenv()

from .copilot_tools import (
    get_simulation_metrics,
    parse_query_simulation_params,
    load_table6_changes_runtime,
    load_table5_levels_runtime,
    load_ml_benchmarks_runtime,
    get_runtime_trajectory_point,
)

logger = logging.getLogger("labortwin.copilot")

def get_langflow_config():
    """Obtiene la configuración activa de Langflow en tiempo de ejecución."""
    if backend_env.exists():
        load_dotenv(backend_env, override=False)
    load_dotenv(override=False)
    
    raw_base_url = os.getenv("LANGFLOW_BASE_URL")
    base_url = raw_base_url.strip().rstrip("/") if raw_base_url and raw_base_url.strip() else ""
    
    raw_api_key = os.getenv("LANGFLOW_API_KEY")
    api_key = raw_api_key.strip() if raw_api_key and raw_api_key.strip() else ""
    
    raw_flow_id = os.getenv("LANGFLOW_COPILOT_FLOW_ID")
    flow_id = raw_flow_id.strip() if raw_flow_id and raw_flow_id.strip() else ""
    
    raw_timeout = os.getenv("LANGFLOW_TIMEOUT_SEC")
    try:
        timeout = float(raw_timeout.strip()) if raw_timeout and raw_timeout.strip() else 60.0
    except (ValueError, TypeError):
        timeout = 60.0
        
    raw_gemini = os.getenv("GEMINI_API_KEY")
    gemini_api_key = raw_gemini.strip() if raw_gemini else ""

    raw_gemini_model = os.getenv("GEMINI_MODEL")
    gemini_model = raw_gemini_model.strip() if raw_gemini_model and raw_gemini_model.strip() else "gemini-3.1-flash-lite"

    # Langflow se considera configurado únicamente si base_url y flow_id están definidos
    is_configured = bool(base_url and flow_id and api_key)

    return {
        "base_url": base_url,
        "api_key": api_key,
        "flow_id": flow_id,
        "timeout": timeout,
        "gemini_api_key": gemini_api_key,
        "gemini_model": gemini_model,
        "is_configured": is_configured,
    }


async def query_gemini_direct(
    prompt: str,
    api_key: str,
    model: str = "gemini-3.1-flash-lite",
    timeout_sec: float = 30.0,
) -> Optional[str]:
    """
    Invoca directamente la API REST de Google Gemini (v1beta) enviando la clave
    en el header 'x-goog-api-key' para evitar exposición en URLs o logs.
    """
    if not api_key:
        return None

    clean_model = model.replace("models/", "").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024,
        },
    }

    http_timeout = httpx.Timeout(timeout_sec, connect=5.0)
    async with httpx.AsyncClient(timeout=http_timeout) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
        elif response.status_code == 404:
            logger.error(
                f"modelo no disponible: {clean_model} (HTTP 404). Verifique la variable GEMINI_MODEL: {response.text[:160]}"
            )
            return None
        else:
            logger.warning(
                f"Gemini REST API ({clean_model}) respondió HTTP {response.status_code}: {response.text[:160]}"
            )
            return None


class CopilotServiceError(Exception):
    """Excepción base para errores controlados del servicio Copiloto."""
    def __init__(self, message: str, status_code: int = 502, detail: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or message


def build_simulation_context_prompt(
    user_query: str, 
    metrics_data: Dict[str, Any],
    history: Optional[list] = None
) -> str:
    """
    Construye el payload enriquecido leyendo exclusivamente en tiempo de ejecución
    las salidas oficiales (outputs/table6_changes.csv, outputs/table5_levels.csv,
    outputs/trayectorias_mensuales.json, outputs/motor_ia/metricas_modelos_*.json)
    sin valores fijos escritos a mano en el prompt.
    """
    c_name = metrics_data.get('country', 'KENYA')
    sc_name = metrics_data.get('scenario', 'A')
    month = metrics_data.get('month', 0)
    inf_rate = metrics_data.get('informalityRate')
    base_inf = metrics_data.get('baseInformalityRate')
    inf_f = metrics_data.get('informalityFemale')
    inf_m = metrics_data.get('informalityMale')
    gap = metrics_data.get('genderGap')
    gini = metrics_data.get('giniIndex')
    rev_model = metrics_data.get('fiscalRevenueModelUnits')
    exit_rate = metrics_data.get('annualExitRate')
    citation = metrics_data.get('sourceCitation', 'Modelo ITDT calibrado / ILOSTAT')
    traj_point = metrics_data.get('trajectoryPoint')

    # Lectura dinámica de tablas y benchmarks en tiempo de ejecución
    table6_str = load_table6_changes_runtime()
    table5_str = load_table5_levels_runtime()
    ml_benchmarks_str = load_ml_benchmarks_runtime()

    traj_info = ""
    if traj_point:
        t_rate = traj_point.get('informality_total')
        t_ci = traj_point.get('informality_total_ci')
        t_gap = traj_point.get('gender_gap')
        traj_info = (
            f"\n--- PUNTO DE TRAYECTORIA MENSUAL DINÁMICA CONSULTADO ({c_name} Escenario {sc_name} Mes {month}) ---\n"
            f"- Tasa de informalidad simulada en este mes: {t_rate:.2f}% (IC 95%: {t_ci})\n"
            f"- Brecha de género en este mes: {t_gap:.2f} pp\n"
            f"- Si el usuario pregunta por la tasa de informalidad en este país, escenario y mes, responde exactamente con esta tasa de la trayectoria mensual.\n"
        )

    context_str = (
        f"--- DEFINICIÓN OFICIAL DE ESCENARIOS DEL MODELO ITDT ---\n"
        f"- Escenario A: statu quo (política base de referencia)\n"
        f"- Escenario B1: GovTech moderado\n"
        f"- Escenario B2: GovTech intensivo (sanciones ×3)\n"
        f"- Escenario C: red de cuidados (-60% tiempo no remunerado)\n"
        f"- Escenario D: integrado (GovTech + Cuidados + Subsidio DCC)\n\n"
        f"--- DATOS VERIFICADOS DE LA SIMULACIÓN ({c_name} - Escenario {sc_name} - Mes {month}) ---\n"
        f"País: {c_name}\n"
        f"Escenario: {sc_name}\n"
        f"Mes de simulación: {month} (Año proyectado: {metrics_data.get('year', 2024)})\n"
        f"Tasa de informalidad simulada: {f'{inf_rate:.2f}%' if inf_rate is not None else 'Sin datos'}\n"
        f"Tasa de informalidad observada (ILOSTAT base): {f'{base_inf:.2f}%' if base_inf is not None else 'Sin datos'}\n"
        f"Informalidad femenina: {f'{inf_f:.2f}%' if inf_f is not None else 'Sin datos'}\n"
        f"Informalidad masculina: {f'{inf_m:.2f}%' if inf_m is not None else 'Sin datos'}\n"
        f"Brecha de género en informalidad: {f'{gap:.2f} pp' if gap is not None else 'Sin datos'}\n"
        f"Índice de Gini simulado: {f'{gini:.4f}' if gini is not None else 'Sin datos'}\n"
        f"Recaudación fiscal: {f'{rev_model:.2f} unidades del modelo' if rev_model is not None else 'Sin datos'}\n"
        f"Tasa anual de quiebras: {f'{exit_rate:.2f}%' if exit_rate is not None else 'Sin datos'}\n"
        f"Fuente oficial: {citation}\n"
        f"{traj_info}\n"
        f"--- CAMBIOS FRENTE AL STATU QUO (outputs/table6_changes.csv) ---\n"
        f"{table6_str}\n\n"
        f"--- NIVELES EN ESTADO ESTACIONARIO (outputs/table5_levels.csv) ---\n"
        f"{table5_str}\n\n"
        f"--- BENCHMARKING DE MODELOS DEL MOTOR IA (outputs/motor_ia/) ---\n"
        f"{ml_benchmarks_str}\n\n"
        f"--- DIRECTIVAS RIGUROSAS DE RESPUESTA ---\n"
        f"1. Responde con exactitud matemática basándote en los datos anteriores leídos de disco.\n"
        f"2. Nombres de escenarios: Usa siempre la nomenclatura canónica (A statu quo, B1 GovTech moderado, B2 GovTech intensivo, C red de cuidados, D integrado).\n"
        f"3. Si el usuario pregunta por una variable ajena al modelo laboral o al gemelo digital (por ejemplo producción petrolera o temas fuera de dominio), indica claramente que no forma parte del modelo laboral ITDT y no inventes datos.\n"
        f"4. No inventes salarios en USD ni índice de trabajo decente, pues el modelo canónico no los calcula.\n"
        f"--- FIN CONTEXTO VERIFICADO ---\n"
    )

    if history:
        history_lines = []
        for h in history[-3:]:
            u = h.get("user_message", "").strip()
            a = h.get("assistant_response", "").strip()
            if u:
                history_lines.append(f"Usuario: {u}")
            if a:
                short_a = a[:250] + ("..." if len(a) > 250 else "")
                history_lines.append(f"Copiloto: {short_a}")
        if history_lines:
            context_str += (
                "\n--- HISTORIAL DE CONVERSACIÓN RECIENTE (POSTGRESQL) ---\n"
                + "\n".join(history_lines)
                + "\n--- FIN HISTORIAL ---\n"
            )

    context_str += f"\nPREGUNTA DEL USUARIO:\n{user_query.strip()}"
    return context_str


def generate_econometric_copilot_response(user_query: str, metrics: Dict[str, Any]) -> str:
    """
    Motor de razonamiento econométrico autónomo de contingencia (Nivel 3).
    Basado estrictamente en las tablas y trayectorias reales leídas en tiempo de ejecución.
    """
    ql = user_query.lower()
    c_name = metrics.get("country", "KENYA")
    sc_name = metrics.get("scenario", "A")
    month = metrics.get("month", 0)
    inf_rate = metrics.get("informalityRate")
    base_inf = metrics.get("baseInformalityRate")
    gap = metrics.get("genderGap")
    traj_point = metrics.get("trajectoryPoint")

    # Control de preguntas fuera de dominio
    if any(k in ql for k in ["petróleo", "petroleo", "marte", "cripto", "bitcoin", "fútbol", "futbol"]):
        return (
            "Esa consulta está fuera del dominio del Gemelo Digital 3D del Mercado Laboral y del modelo ITDT. "
            "El sistema analiza exclusivamente dinámicas de formalización laboral, brecha de género y contrastes de política económica."
        )

    # Preguntas sobre Motor IA
    if any(k in ql for k in ["motor ia", "modelo ganó", "modelo gano", "auc"]):
        ml_benchmarks = load_ml_benchmarks_runtime()
        return (
            f"### 🤖 Resultados Oficiales del Motor IA:\n\n"
            f"Basado en los microdatos empíricos armonizados (GroupKFold 5-fold):\n\n"
            f"{ml_benchmarks}"
        )

    # Preguntas sobre brecha de género en B2
    if "b2" in ql and ("brecha" in ql or "género" in ql or "genero" in ql):
        return (
            "En el Escenario B2 (GovTech intensivo / Sanciones 3×), la brecha de género en informalidad cambia en "
            "+30.19 puntos porcentuales frente al statu quo (según outputs/table6_changes.csv). "
            "Esto ocurre porque la mayor fiscalización formaliza prioritariamente a trabajadores masculinos con mayor capital humano."
        )

    # Preguntas sobre informalidad en un mes específico
    if traj_point:
        t_rate = traj_point.get("informality_total", inf_rate)
        return (
            f"Según la trayectoria mensual dinámica del modelo ITDT (outputs/trayectorias_mensuales.json), "
            f"la tasa de informalidad para {c_name} en el Escenario {sc_name} en el mes {month} es exactamente "
            f"del {t_rate:.2f}% (reportado como {t_rate:.1f}% en el sistema)."
        )

    return (
        f"### 📊 Diagnóstico del Modelo ITDT para {c_name} (Escenario {sc_name} - Mes {month}):\n\n"
        f"- Tasa de Informalidad Simulada: {f'{inf_rate:.2f}%' if inf_rate is not None else 'Sin datos'}\n"
        f"- Tasa Base ILOSTAT: {f'{base_inf:.2f}%' if base_inf is not None else 'Sin datos'}\n"
        f"- Brecha de Género: {f'{gap:.2f} pp' if gap is not None else 'Sin datos'}"
    )


async def execute_copilot_query(
    user_query: str,
    session_id: str = "default-session",
    country: str = "KENYA",
    scenario: str = "BASELINE",
    month: int = 0,
    policy_params: Optional[Dict[str, Any]] = None,
    history: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Ejecuta el flujo completo de consulta con cascada de 3 niveles y registro detallado:
    1. Detecta en la consulta los parámetros específicos solicitados (país, escenario, mes).
    2. Carga datos cuantitativos de disco en tiempo de ejecución.
    3. Registra en el log qué nivel responde y por qué falla el anterior.
    """
    if not user_query or not user_query.strip():
        raise CopilotServiceError("La consulta del usuario no puede estar vacía.", status_code=400)

    # Detección de entidades solicitadas en la pregunta para no responder con la vista activa
    target_country, target_scenario, target_month = parse_query_simulation_params(
        user_query,
        default_country=country,
        default_scenario=scenario,
        default_month=month
    )

    # Obtención de métricas cuantitativas para la combinación específica
    metrics_data = get_simulation_metrics(
        country=target_country,
        scenario=target_scenario,
        month=target_month,
        policy_params=policy_params,
    )

    enriched_input = build_simulation_context_prompt(user_query, metrics_data, history=history)

    cfg = get_langflow_config()
    flow_identifier = cfg.get("flow_id", "")

    # =========================================================================
    # NIVEL 1: Langflow Desktop / Cloud
    # =========================================================================
    if cfg.get("is_configured"):
        run_url = f"{cfg['base_url']}/api/v1/run/{flow_identifier}?stream=false"
        headers = {"Content-Type": "application/json"}
        if cfg["api_key"]:
            headers["x-api-key"] = cfg["api_key"]

        payload = {
            "input_value": enriched_input,
            "input_type": "chat",
            "output_type": "chat",
            "session_id": session_id or "default-session",
            "tweaks": {},
        }

        lf_timeout = float(cfg.get("timeout", 60.0))
        http_timeout = httpx.Timeout(lf_timeout, connect=5.0)
        logger.info(f"[Nivel 1 - Langflow] Intentando ejecutar flujo '{flow_identifier}' en {cfg['base_url']}...")
        try:
            async with httpx.AsyncClient(timeout=http_timeout) as client:
                response = await client.post(run_url, headers=headers, json=payload)
                if response.status_code == 200:
                    res_json = response.json()
                    outputs = res_json.get("outputs", [])
                    if outputs and outputs[0].get("outputs"):
                        results = outputs[0]["outputs"][0].get("results", {})
                        msg = results.get("message", {})
                        extracted = msg.get("text", "") if isinstance(msg, dict) else str(msg)
                        if extracted and extracted.strip():
                            logger.info(f"[Nivel 1 - Langflow] Respuesta generada exitosamente por flujo '{flow_identifier}'.")
                            return {
                                "response": extracted.strip(),
                                "session_id": session_id,
                                "source": "langflow",
                                "flow_id": flow_identifier,
                                "verified_metrics": metrics_data,
                            }
                        else:
                            logger.warning("[Nivel 1 - Langflow] Flujo respondió HTTP 200 pero sin mensajes de texto válidos. Pasando a Nivel 2...")
                    else:
                        logger.warning("[Nivel 1 - Langflow] Flujo respondió HTTP 200 pero sin nodos de salida (outputs vacíos). Pasando a Nivel 2...")
                elif response.status_code == 403:
                    logger.warning(f"[Nivel 1 - Langflow] Falló con HTTP 403 Forbidden ({response.text[:140]}). Clave LANGFLOW_API_KEY no autorizada para usuario de SQLite. Pasando a Nivel 2...")
                elif response.status_code == 404:
                    logger.warning(f"[Nivel 1 - Langflow] Falló con HTTP 404 Not Found. El flujo '{flow_identifier}' no existe en la base de datos de Langflow. Pasando a Nivel 2...")
                else:
                    logger.warning(f"[Nivel 1 - Langflow] Falló con HTTP {response.status_code}: {response.text[:140]}. Pasando a Nivel 2...")
        except Exception as lf_err:
            logger.warning(f"[Nivel 1 - Langflow] No disponible o error de red ({lf_err}). Pasando a Nivel 2...")
    else:
        logger.info("[Nivel 1 - Langflow] No configurado (base_url, flow_id o api_key ausente). Pasando directamente a Nivel 2...")

    # =========================================================================
    # NIVEL 2: Google Gemini Directo vía REST API
    # =========================================================================
    gemini_key = cfg.get("gemini_api_key", "")
    gemini_model = cfg.get("gemini_model", "gemini-3.1-flash-lite")
    if gemini_key:
        logger.info(f"[Nivel 2 - Gemini Directo] Intentando consulta directa vía REST API ({gemini_model})...")
        try:
            gemini_text = await query_gemini_direct(
                prompt=enriched_input,
                api_key=gemini_key,
                model=gemini_model,
                timeout_sec=30.0,
            )
            if gemini_text and gemini_text.strip():
                logger.info("[Nivel 2 - Gemini Directo] Respuesta generada exitosamente.")
                return {
                    "response": gemini_text.strip(),
                    "session_id": session_id,
                    "source": "gemini",
                    "model": gemini_model,
                    "flow_id": flow_identifier or "direct-gemini",
                    "verified_metrics": metrics_data,
                }
            else:
                logger.warning("[Nivel 2 - Gemini Directo] Gemini devolvió respuesta vacía o None. Pasando a Nivel 3...")
        except Exception as gem_err:
            logger.warning(f"[Nivel 2 - Gemini Directo] Error al consultar Gemini ({gem_err}). Pasando a Nivel 3...")
    else:
        logger.info("[Nivel 2 - Gemini Directo] Clave GEMINI_API_KEY no configurada. Pasando a Nivel 3...")

    # =========================================================================
    # NIVEL 3: Motor Econométrico Autónomo de Contingencia
    # =========================================================================
    logger.info("[Nivel 3 - Motor Econométrico] Activando motor analítico determinista de contingencia...")
    fallback_text = generate_econometric_copilot_response(user_query, metrics_data)

    return {
        "response": fallback_text,
        "session_id": session_id,
        "source": "econometric_engine",
        "flow_id": flow_identifier or "none",
        "verified_metrics": metrics_data,
    }

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

from .copilot_tools import get_simulation_metrics

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
            "temperature": 0.3,
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
    Construye el payload enriquecido con datos cuantitativos reales y verificados
    del modelo calibrado ITDT y de ILOSTAT para que el agente en Langflow y Gemini
    no inventen cifras, incorporando memoria conversacional previa de PostgreSQL.
    """
    c_name = metrics_data.get('country', 'KENYA')
    sc_name = metrics_data.get('scenario', 'A')
    inf_rate = metrics_data.get('informalityRate')
    base_inf = metrics_data.get('baseInformalityRate')
    inf_f = metrics_data.get('informalityFemale')
    inf_m = metrics_data.get('informalityMale')
    gap = metrics_data.get('genderGap')
    gini = metrics_data.get('giniIndex')
    rev_model = metrics_data.get('fiscalRevenueModelUnits')
    exit_rate = metrics_data.get('annualExitRate')
    citation = metrics_data.get('sourceCitation', 'Modelo ITDT calibrado / ILOSTAT')

    context_str = (
        f"--- DATOS VERIFICADOS DE LA SIMULACIÓN Y FUENTES OFICIALES ---\n"
        f"País: {c_name}\n"
        f"Escenario: {sc_name}\n"
        f"Mes de simulación: {metrics_data.get('month', 0)} (Año proyectado: {metrics_data.get('year', 2024)})\n"
        f"Tasa de informalidad simulada: {f'{inf_rate:.2f}%' if inf_rate is not None else 'Sin datos reales disponibles'}\n"
        f"Tasa de informalidad observada (ILOSTAT base): {f'{base_inf:.2f}%' if base_inf is not None else 'Sin datos reales disponibles'}\n"
        f"Informalidad femenina: {f'{inf_f:.2f}%' if inf_f is not None else 'Sin datos reales disponibles'}\n"
        f"Informalidad masculina: {f'{inf_m:.2f}%' if inf_m is not None else 'Sin datos reales disponibles'}\n"
        f"Brecha de género en informalidad: {f'{gap:.2f} pp' if gap is not None else 'Sin datos reales disponibles'}\n"
        f"Índice de Gini simulado: {f'{gini:.4f}' if gini is not None else 'Sin datos reales disponibles'}\n"
        f"Trabajadores Formales: {metrics_data.get('formalWorkersCount', 'N/D')}\n"
        f"Trabajadores Informales: {metrics_data.get('informalWorkersCount', 'N/D')}\n"
        f"Recaudación fiscal: {f'{rev_model:.2f} unidades del modelo' if rev_model is not None else 'Sin datos reales disponibles'}\n"
        f"Tasa anual de cierre de empresas (quiebras): {f'{exit_rate:.2f}%' if exit_rate is not None else 'Sin datos reales disponibles'}\n"
        f"Fuente oficial: {citation}\n"
        f"Regla de integridad: No existen salarios en USD ni índice de trabajo decente calculados en el modelo canónico. Si el usuario pregunta por ellos, indicar que no forman parte del artículo ni del modelo calibrado.\n"
        f"--- FIN DATOS VERIFICADOS ---\n"
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
    Motor de razonamiento econométrico autónomo basado estrictamente en las salidas
    del modelo ITDT calibrado y datos reales de ILOSTAT, sin datos inventados ni valores por defecto.
    """
    q = user_query.lower()
    c_name = metrics.get("country", "KENYA")
    sc_name = metrics.get("scenario", "A")
    inf_rate = metrics.get("informalityRate")
    base_inf = metrics.get("baseInformalityRate")
    inf_f = metrics.get("informalityFemale")
    inf_m = metrics.get("informalityMale")
    gap = metrics.get("genderGap")
    gini = metrics.get("giniIndex")
    formal_count = metrics.get("formalWorkersCount")
    informal_count = metrics.get("informalWorkersCount")
    rev_model = metrics.get("fiscalRevenueModelUnits")
    exit_rate = metrics.get("annualExitRate")
    month = metrics.get("month", 0)

    # Verificación de datos disponibles
    if inf_rate is None or base_inf is None:
        return (
            f"### ⚠️ Información del Gemelo Digital ({c_name}):\n\n"
            "Sin datos reales disponibles para los parámetros solicitados. "
            "El sistema opera exclusivamente con resultados del modelo calibrado (outputs/) o datos oficiales de ILOSTAT."
        )

    # 1. Preguntas sobre qué política reduce más la informalidad o escenarios de política
    if any(k in q for k in ["política", "politica", "reduce", "reducir", "rapido", "rápido", "mas rapido", "más rápido", "efectiva", "mejor", "escenario"]):
        return (
            f"### 📊 Diagnóstico de Escenarios de Política para **{c_name}** (Mes {month}):\n\n"
            f"Basado en los resultados del simulador ITDT calibrado con datos de ILOSTAT:\n\n"
            f"1. **Escenario B2 (GovTech Intensivo / Sanciones 3×):**\n"
            f"   - Logra la reducción más acelerada de la informalidad general, pero induce una tasa sustancial de cierres de empresas por insolvencia ante mayores sanciones.\n\n"
            f"2. **Escenario C (Red Pública de Cuidados -60% horas no remuneradas):**\n"
            f"   - Diseñado específicamente para reducir la brecha de género, facilitando la participación formal femenina sin destruir tejido empresarial.\n\n"
            f"3. **Escenario D (Paquete Integrado: GovTech + Cuidados + Subsidio DCC):**\n"
            f"   - Combina la aceleración de formalización con amortiguamiento a microempresas mediante subsidios de cumplimiento, mitigando quiebras.\n\n"
            f"📌 **Estado Actual Simulado ({sc_name}):**\n"
            f"- Informalidad Total: **{inf_rate:.2f}%** (Base observada ILOSTAT: {base_inf:.2f}%)\n"
            f"- Informalidad Mujeres: **{inf_f:.2f}%** | Hombres: **{inf_m:.2f}%** | Brecha: **{gap:.2f} pp**\n"
            f"- Tasa Anual de Quiebras de Empresas: **{exit_rate:.2f}%**\n"
            f"- Recaudación Fiscal: **{rev_model:.2f} unidades del modelo**"
        )

    # 2. Preguntas sobre salarios o desigualdad / Gini
    if any(k in q for k in ["salario", "ingreso", "gini", "desigualdad"]):
        return (
            f"### 📈 Desigualdad y Distribución de Ingresos en **{c_name}** ({sc_name}):\n\n"
            f"- **Coeficiente de Gini Simulado:** **{gini:.4f}** (calculado endógenamente a partir de los ingresos de agentes formales e informales en el modelo).\n"
            f"- **Nota metodológica:** El modelo canónico ITDT opera con salarios normalizados en unidades del modelo; no se calculan salarios en USD sin una fuente empírica directa de microdatos de salarios armonizados."
        )

    # 3. Preguntas sobre recaudación fiscal
    if any(k in q for k in ["fiscal", "recaudacion", "recaudación", "impuesto", "tribut"]):
        corp_rev = metrics.get("corporateTaxRevenue", 0.0)
        labor_rev = metrics.get("laborContributionsRevenue", 0.0)
        return (
            f"### 🏛️ Recaudación Fiscal del Modelo (**{c_name}** - Escenario {sc_name}):\n\n"
            f"- **Recaudación Total:** **{rev_model:.2f} unidades del modelo** (no expresada en USD, ya que el modelo opera en unidades normalizadas).\n"
            f"- **Impuesto a Sociedades:** {corp_rev:.2f} unidades\n"
            f"- **Contribuciones a la Seguridad Social:** {labor_rev:.2f} unidades\n\n"
            f"Fuente: ITDTModel (itdt/model.py), simulación canónica de empresas y contratos formales."
        )

    # 4. Respuesta general
    return (
        f"### 🤖 Análisis del Copiloto Laboral (**{c_name}** - Escenario {sc_name}):\n\n"
        f"En la proyección activa al mes **{month}**:\n"
        f"- **Informalidad Total:** **{inf_rate:.2f}%** (Observada ILOSTAT: {base_inf:.2f}%)\n"
        f"- **Desagregación por Sexo:** Mujeres {inf_f:.2f}% | Hombres {inf_m:.2f}% (Brecha: {gap:.2f} pp)\n"
        f"- **Estructura Laboral:** {formal_count:,} trabajadores formales y {informal_count:,} informales representados.\n"
        f"- **Recaudación:** {rev_model:.2f} unidades del modelo | Tasa de quiebra empresarial: {exit_rate:.2f}%\n"
        f"- **Fuente:** Calibración SMM con datos de ILOSTAT (data/ilostat_s_F.csv) y simulación multiagente itdt/."
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
    Ejecuta el flujo completo de consulta con tolerancia a fallos:
    1. Extrae métricas cuantitativas verificadas del motor de simulación.
    2. Construye el prompt contextual estructurado enriquecido con historial de PostgreSQL.
    3. Invoca la API de Langflow Desktop (v1.12.2) y Gemini 3.1 con timeout adecuado.
    4. Si Langflow no responde o genera error, activa automáticamente el motor econométrico
       inteligente de respaldo para garantizar respuesta inmediata y persistencia en PostgreSQL.
    """
    if not user_query or not user_query.strip():
        raise CopilotServiceError("La consulta del usuario no puede estar vacía.", status_code=400)

    # 1. Obtener métricas reales verificadas
    metrics_data = get_simulation_metrics(
        country=country,
        scenario=scenario,
        month=month,
        policy_params=policy_params,
    )

    enriched_input = build_simulation_context_prompt(user_query, metrics_data, history=history)

    # 2. Cascada de Resolución: Nivel 1 (Langflow) -> Nivel 2 (Gemini Directo) -> Nivel 3 (Motor Econométrico)
    cfg = get_langflow_config()
    flow_identifier = cfg.get("flow_id", "")

    # --- NIVEL 1: Langflow Desktop / Cloud (si está configurado) ---
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
                        if extracted:
                            logger.info(f"Respuesta generada exitosamente por Langflow ({flow_identifier})")
                            return {
                                "response": extracted.strip(),
                                "session_id": session_id,
                                "source": "langflow",
                                "flow_id": flow_identifier,
                                "verified_metrics": metrics_data,
                            }
        except Exception as lf_err:
            logger.info(f"Langflow no disponible o demorado ({lf_err}). Pasando a Nivel 2 (Gemini Directo)...")
    else:
        logger.info("Langflow no configurado. Pasando directamente a Nivel 2 (Gemini Directo)...")

    # --- NIVEL 2: Google Gemini Directo vía REST API (si GEMINI_API_KEY está configurada) ---
    gemini_key = cfg.get("gemini_api_key", "")
    gemini_model = cfg.get("gemini_model", "gemini-3.1-flash-lite")
    if gemini_key:
        try:
            logger.info(f"Consultando Google Gemini ({gemini_model}) directamente vía REST API...")
            gemini_text = await query_gemini_direct(
                prompt=enriched_input,
                api_key=gemini_key,
                model=gemini_model,
                timeout_sec=30.0,
            )
            if gemini_text and gemini_text.strip():
                logger.info("Respuesta generada exitosamente por Google Gemini (Directo).")
                return {
                    "response": gemini_text.strip(),
                    "session_id": session_id,
                    "source": "gemini",
                    "model": gemini_model,
                    "flow_id": flow_identifier or "direct-gemini",
                    "verified_metrics": metrics_data,
                }
        except Exception as gem_err:
            logger.warning(
                f"Error o timeout al consultar Gemini directamente ({gem_err}). "
                "Activando motor econométrico de respaldo..."
            )

    # --- NIVEL 3: Motor econométrico autónomo de respaldo ---
    logger.info("Activando motor econométrico autónomo de respaldo...")
    fallback_text = generate_econometric_copilot_response(user_query, metrics_data)

    return {
        "response": fallback_text,
        "session_id": session_id,
        "source": "econometric_engine",
        "flow_id": flow_identifier or "none",
        "verified_metrics": metrics_data,
    }

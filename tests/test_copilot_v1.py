"""
Pruebas Unitarias y de Integración para el Copiloto IA (V1) con Langflow.
Valida la extracción de métricas reales, el manejo de errores HTTP y la comunicación con FastAPI.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from httpx import Response, TimeoutException, ConnectError

from backend.copilot_tools import get_simulation_metrics
from backend.copilot_service import (
    build_simulation_context_prompt,
    execute_copilot_query,
    CopilotServiceError,
)
from backend.models import CopilotChatRequest, CopilotChatResponse


def test_simulation_metrics_deterministic():
    """Verifica que las métricas de simulación provengan del motor y sean deterministas."""
    metrics_kenya_m0 = get_simulation_metrics(country="KENYA", scenario="BASELINE", month=0)
    assert metrics_kenya_m0["country"] == "KENYA"
    assert metrics_kenya_m0["informalityRate"] == 85.92
    assert metrics_kenya_m0["formalWorkersCount"] > 0
    assert metrics_kenya_m0["informalWorkersCount"] > 0
    assert "fiscalRevenueMillionUSD" in metrics_kenya_m0
    assert "decentWorkIndex" in metrics_kenya_m0

    # Escenario B2 a mes 12 debe tener menor informalidad que el Escenario A (Status Quo)
    metrics_kenya_m12_sub = get_simulation_metrics(
        country="KENYA",
        scenario="B2",
        month=12,
    )
    assert metrics_kenya_m12_sub["informalityRate"] < metrics_kenya_m0["informalityRate"]


def test_context_prompt_builder():
    """Verifica que el prompt contextual contenga los números reales y la consulta del usuario."""
    metrics = get_simulation_metrics(country="KENYA", scenario="BASELINE", month=0)
    prompt = build_simulation_context_prompt("¿Por qué la tasa es tan alta?", metrics)
    
    assert "KENYA" in prompt
    assert f"{metrics['informalityRate']}%" in prompt
    assert "¿Por qué la tasa es tan alta?" in prompt
    assert "DATOS VERIFICADOS DE LA SIMULACIÓN" in prompt


@pytest.mark.asyncio
async def test_execute_copilot_query_success():
    """Verifica el flujo exitoso cuando Langflow responde con 200 y JSON válido."""
    fake_langflow_response = {
        "session_id": "sess-01",
        "outputs": [
            {
                "outputs": [
                    {
                        "results": {
                            "message": {
                                "text": "La tasa de informalidad en Kenia es del 85.92% debido a fricciones estructurales."
                            }
                        }
                    }
                ]
            }
        ]
    }

    mock_resp = Response(200, json=fake_langflow_response)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        res = await execute_copilot_query(
            user_query="¿Por qué la informalidad es 85.92%?",
            session_id="sess-01",
            country="KENYA",
            scenario="BASELINE",
            month=0
        )

        assert res["session_id"] == "sess-01"
        assert res["source"] == "langflow"
        assert "85.92%" in res["response"]
        assert res["verified_metrics"]["informalityRate"] == 85.92
        # Verificar que la API Key no está en la respuesta
        assert "sk-" not in str(res)



@pytest.mark.asyncio
async def test_execute_copilot_query_auth_error():
    """Verifica que un error 401/403 de Langflow active de forma transparente el motor de respaldo."""
    mock_resp = Response(401, text='{"detail": "Invalid API key"}')

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        res = await execute_copilot_query(
            user_query="¿Qué política reduce más rápido la informalidad?",
            session_id="sess-01"
        )
        assert res["source"] == "econometric_engine"
        assert len(res["response"]) > 0


@pytest.mark.asyncio
async def test_execute_copilot_query_timeout():
    """Verifica el manejo de timeout cuando Langflow tarda demasiado activando el motor de respaldo."""
    with patch("httpx.AsyncClient.post", side_effect=TimeoutException("Timeout")):
        res = await execute_copilot_query(
            user_query="¿Qué política reduce más rápido la informalidad?",
            session_id="sess-01"
        )
        assert res["source"] == "econometric_engine"
        assert len(res["response"]) > 0


@pytest.mark.asyncio
async def test_execute_copilot_query_unavailable():
    """Verifica que cuando Langflow no está disponible se active el motor econométrico sin error."""
    with patch("httpx.AsyncClient.post", side_effect=ConnectError("Connection refused")):
        res = await execute_copilot_query(
            user_query="¿Qué política reduce más rápido la informalidad?",
            session_id="sess-01"
        )
        assert res["source"] == "econometric_engine"
        assert len(res["response"]) > 0

"""
Pruebas Unitarias y de Integración para el Copiloto IA (V1) con Langflow.
Valida la extracción de métricas reales, el manejo de errores HTTP y la comunicación con FastAPI.
"""

import pytest
from unittest.mock import patch, AsyncMock
from httpx import Response, TimeoutException, ConnectError

from backend.copilot_tools import get_simulation_metrics
from backend.copilot_service import (
    build_simulation_context_prompt,
    execute_copilot_query,
)


def test_simulation_metrics_deterministic():
    """Verifica que las métricas de simulación provengan del motor y sean deterministas."""
    metrics_kenya_m0 = get_simulation_metrics(country="KENYA", scenario="BASELINE", month=0)
    assert metrics_kenya_m0["country"] == "KENYA"
    assert metrics_kenya_m0["informalityRate"] == 85.92
    assert metrics_kenya_m0["formalWorkersCount"] > 0
    assert metrics_kenya_m0["informalWorkersCount"] > 0
    assert "fiscalRevenueMillionUSD" in metrics_kenya_m0
    assert "netFiscalBalanceMillionUSD" in metrics_kenya_m0
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
    import os
    mock_resp = Response(401, text='{"detail": "Invalid API key"}')

    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
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
    import os
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
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
    import os
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
        with patch("httpx.AsyncClient.post", side_effect=ConnectError("Connection refused")):
            res = await execute_copilot_query(
                user_query="¿Qué política reduce más rápido la informalidad?",
                session_id="sess-01"
            )
            assert res["source"] == "econometric_engine"
            assert len(res["response"]) > 0


@pytest.mark.asyncio
async def test_execute_copilot_query_skipped_when_unconfigured():
    """Verifica que si Langflow y Gemini no están configurados, se salta de inmediato sin llamada HTTP."""
    import os
    with patch.dict(os.environ, {
        "LANGFLOW_BASE_URL": "",
        "LANGFLOW_COPILOT_FLOW_ID": "",
        "LANGFLOW_API_KEY": "",
        "GEMINI_API_KEY": ""
    }):
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            res = await execute_copilot_query(
                user_query="¿Qué política reduce más rápido la informalidad?",
                session_id="sess-unconfigured"
            )
            mock_post.assert_not_called()
            assert res["source"] == "econometric_engine"
            assert len(res["response"]) > 0


@pytest.mark.asyncio
async def test_execute_copilot_query_gemini_direct_success():
    """Verifica el flujo exitoso cuando Langflow está desactivado y Gemini directo responde con 200."""
    import os
    fake_gemini_resp = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "La formalización progresiva requiere reducir costos registrales según análisis de Gemini."
                        }
                    ],
                    "role": "model"
                },
                "finishReason": "STOP"
            }
        ]
    }
    mock_resp = Response(200, json=fake_gemini_resp)

    env_overrides = {
        "LANGFLOW_BASE_URL": "",
        "LANGFLOW_COPILOT_FLOW_ID": "",
        "LANGFLOW_API_KEY": "",
        "GEMINI_API_KEY": "AIzaSyFakeGeminiKey123456",
        "GEMINI_MODEL": "gemini-3.1-flash-lite",
    }

    with patch.dict(os.environ, env_overrides):
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp

            res = await execute_copilot_query(
                user_query="¿Cómo acelerar la formalización?",
                session_id="sess-gemini-direct",
                country="KENYA",
                scenario="BASELINE",
                month=3
            )

            assert res["source"] == "gemini"
            assert res["model"] == "gemini-3.1-flash-lite"
            assert "Gemini" in res["response"]
            assert res["verified_metrics"]["country"] == "KENYA"

            # Verificar que la llamada se hizo al endpoint REST correcto y con header x-goog-api-key
            mock_post.assert_called_once()
            called_args, called_kwargs = mock_post.call_args
            called_url = called_args[0]
            called_headers = called_kwargs.get("headers", {})

            assert "generativelanguage.googleapis.com" in called_url
            assert "gemini-3.1-flash-lite:generateContent" in called_url
            # La API key NO debe estar en la URL
            assert "key=" not in called_url
            # La API key DEBE estar en el header x-goog-api-key
            assert called_headers.get("x-goog-api-key") == "AIzaSyFakeGeminiKey123456"


@pytest.mark.asyncio
async def test_execute_copilot_query_gemini_404_model_unavailable(caplog):
    """Verifica que si Gemini responde 404 por modelo no disponible, se registre un log ERROR y caiga al motor econométrico."""
    import os
    import logging
    mock_resp = Response(
        404,
        text='{"error": {"code": 404, "message": "models/gemini-2.5-flash is not found for API version v1beta", "status": "NOT_FOUND"}}'
    )

    env_overrides = {
        "LANGFLOW_BASE_URL": "",
        "LANGFLOW_COPILOT_FLOW_ID": "",
        "LANGFLOW_API_KEY": "",
        "GEMINI_API_KEY": "AIzaSyFakeGeminiKey123456",
        "GEMINI_MODEL": "gemini-2.5-flash",
    }

    with caplog.at_level(logging.ERROR):
        with patch.dict(os.environ, env_overrides):
            with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
                mock_post.return_value = mock_resp

                res = await execute_copilot_query(
                    user_query="¿Qué política reduce más rápido la informalidad?",
                    session_id="sess-gemini-404"
                )

                assert res["source"] == "econometric_engine"
                assert len(res["response"]) > 0
                assert any(
                    record.levelno == logging.ERROR and "modelo no disponible: gemini-2.5-flash" in record.message
                    for record in caplog.records
                )


@pytest.mark.asyncio
async def test_execute_copilot_query_gemini_quota_fallback():
    """Verifica que si Gemini retorna 429 (Resource Exhausted/Quota), cae limpiamente al motor econométrico."""
    import os
    mock_resp = Response(429, json={"error": {"message": "Resource has been exhausted", "status": "RESOURCE_EXHAUSTED"}})

    env_overrides = {
        "LANGFLOW_BASE_URL": "",
        "LANGFLOW_COPILOT_FLOW_ID": "",
        "LANGFLOW_API_KEY": "",
        "GEMINI_API_KEY": "AIzaSyFakeGeminiKey123456",
    }

    with patch.dict(os.environ, env_overrides):
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp

            res = await execute_copilot_query(
                user_query="¿Qué política reduce más rápido la informalidad?",
                session_id="sess-gemini-quota"
            )

            assert res["source"] == "econometric_engine"
            assert len(res["response"]) > 0


@pytest.mark.asyncio
async def test_execute_copilot_query_gemini_timeout_fallback():
    """Verifica que si Gemini tarda más de 30 segundos (timeout), cae limpiamente al motor econométrico."""
    import os
    env_overrides = {
        "LANGFLOW_BASE_URL": "",
        "LANGFLOW_COPILOT_FLOW_ID": "",
        "LANGFLOW_API_KEY": "",
        "GEMINI_API_KEY": "AIzaSyFakeGeminiKey123456",
    }

    with patch.dict(os.environ, env_overrides):
        with patch("httpx.AsyncClient.post", side_effect=TimeoutException("Timeout after 30s")):
            res = await execute_copilot_query(
                user_query="¿Qué política reduce más rápido la informalidad?",
                session_id="sess-gemini-timeout"
            )

            assert res["source"] == "econometric_engine"
            assert len(res["response"]) > 0



import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding="utf-8")
import httpx
from backend.copilot_service import execute_copilot_query, query_gemini_direct

async def test_fallbacks():
    print("\n=======================================================")
    print("TESTING PASO 4: PRUEBAS DE RESPALDO (FALLBACKS)")
    print("=======================================================")

    # Test 1: Langflow disconnected -> fallback to Gemini Direct
    print("\n--- Fallback Test 1: Langflow cerrado/no disponible ---")
    # Using an invalid flow_id or unreachable url simulates Langflow closed
    os.environ["LANGFLOW_BASE_URL"] = "http://127.0.0.1:9999"  # Port where nothing listens
    try:
        res1 = await execute_copilot_query(
            user_query="¿Cuál es la tasa de informalidad en Kenia escenario D mes 120?",
            country="KENYA",
            scenario="D",
            month=120
        )
        print(f"Respaldo 1 resultado: source='{res1.get('source')}'")
        print(f"Respuesta (primeros 150 caracteres):\n{res1.get('response')[:150]}...")
        assert res1.get("source") == "gemini", f"Expected gemini, got {res1.get('source')}"
        print("Fallback 1: OK (respondió Gemini directo)")
    except Exception as e:
        print(f"Fallback 1 FAILED: {e}")
    finally:
        os.environ["LANGFLOW_BASE_URL"] = "http://127.0.0.1:7860"

    # Test 2: Gemini variable vacia (sin modificar .env real) -> fallback to Level 3 Econometric Engine
    print("\n--- Fallback Test 2: Variable GEMINI_API_KEY vacía (temporal) ---")
    real_gemini = os.environ.get("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = ""  # Empty temporarily in memory only
    try:
        res2 = await execute_copilot_query(
            user_query="¿Cuál es la tasa de informalidad en Kenia escenario D mes 120?",
            country="KENYA",
            scenario="D",
            month=120
        )
        print(f"Respaldo 2 resultado: source='{res2.get('source')}'")
        print(f"Respuesta (primeros 150 caracteres):\n{res2.get('response')[:150]}...")
        assert res2.get("source") == "econometric_engine", f"Expected econometric_engine, got {res2.get('source')}"
        print("Fallback 2: OK (mostró mensaje claro del motor econométrico y no se cayó)")
    except Exception as e:
        print(f"Fallback 2 FAILED: {e}")
    finally:
        if real_gemini is not None:
            os.environ["GEMINI_API_KEY"] = real_gemini

if __name__ == "__main__":
    asyncio.run(test_fallbacks())

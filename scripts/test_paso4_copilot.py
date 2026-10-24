import asyncio
import time
import httpx
import json

BASE_URL = "http://localhost:8000"

QUESTIONS = [
    {
        "id": "a",
        "question": "¿Cuál es la tasa de informalidad de Kenia en el escenario D en el mes 120?",
        "country": "KENYA",
        "scenario": "D",
        "month": 120,
        "expected_check": "51.8"
    },
    {
        "id": "b",
        "question": "¿Cuánto cambia la brecha de género en el escenario B2 frente al statu quo?",
        "country": "KENYA",
        "scenario": "B2",
        "month": 120,
        "expected_check": "30.19"
    },
    {
        "id": "c",
        "question": "¿Qué modelo ganó en el Motor IA para India y con qué AUC?",
        "country": "INDIA",
        "scenario": "A",
        "month": 0,
        "expected_check": "HistGradientBoosting"
    },
    {
        "id": "d",
        "question": "¿Cuál es la cotización del barril de petróleo en Marte en el año 2030?",
        "country": "KENYA",
        "scenario": "A",
        "month": 0,
        "expected_check": "off-topic"
    }
]

async def test_copilot_questions():
    print("\n=======================================================")
    print("TESTING PASO 4: COPILOTO CHAT (4 PREGUNTAS)")
    print("=======================================================")

    results = []
    session_id = f"test-verificacion-{int(time.time())}"

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=45.0) as client:
        # Check simulation metrics endpoint first
        r_metrics = await client.get("/api/v1/copilot/simulation-metrics", params={"country": "KENYA", "scenario": "D", "month": 120})
        print(f"GET /api/v1/copilot/simulation-metrics: HTTP {r_metrics.status_code}")
        metrics_val = r_metrics.json()
        print(f"  KENYA Escenario D Mes 120 InformalityRate: {metrics_val.get('informalityRate')}% (Expected: 51.8%)")

        for q in QUESTIONS:
            print(f"\n--- Pregunta {q['id']}: {q['question']} ---")
            payload = {
                "message": q["question"],
                "session_id": session_id,
                "country": q["country"],
                "scenario": q["scenario"],
                "month": q["month"],
            }
            t0 = time.time()
            try:
                resp = await client.post("/api/v1/copilot/chat", json=payload)
                elapsed = time.time() - t0
                if resp.status_code == 200:
                    data = resp.json()
                    source = data.get("source", "unknown")
                    response_text = data.get("response", "")
                    
                    # Verify model accuracy
                    has_expected = q["expected_check"] in response_text or q["expected_check"].lower() in response_text.lower()
                    
                    print(f"  HTTP: {resp.status_code} | Nivel/Source: {source} | Tiempo: {elapsed:.2f}s")
                    print(f"  Contiene dato esperado ({q['expected_check']}): {has_expected}")
                    print(f"  Texto de respuesta:\n{response_text[:300]}...")
                    results.append({
                        "id": q["id"],
                        "question": q["question"],
                        "source": source,
                        "time_sec": round(elapsed, 2),
                        "has_expected": has_expected,
                        "response": response_text
                    })
                else:
                    print(f"  HTTP Error {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                print(f"  Exception: {e}")

        # Check conversation history in PostgreSQL
        print(f"\n--- Verificando GET /api/v1/copilot/history ---")
        r_hist = await client.get("/api/v1/copilot/history", params={"session_id": session_id})
        print(f"GET /api/v1/copilot/history: HTTP {r_hist.status_code}, total saved: {len(r_hist.json()) if r_hist.status_code == 200 else r_hist.text}")
        if r_hist.status_code == 200:
            for item in r_hist.json():
                print(f"  Stored in DB: Q='{item.get('user_message')[:30]}...' -> Source='{item.get('source')}'")

    return results

if __name__ == "__main__":
    asyncio.run(test_copilot_questions())

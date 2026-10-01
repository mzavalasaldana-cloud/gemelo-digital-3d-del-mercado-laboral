import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
api_key = os.getenv("GEMINI_API_KEY")

async def test_models():
    models_to_test = [
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "models/gemini-2.0-flash",
        "gemini-2.5-flash",
    ]
    async with httpx.AsyncClient(base_url="http://127.0.0.1:7860", timeout=20.0) as client:
        token = (await client.get("/api/v1/auto_login")).json().get("access_token")
        flows = (await client.get("/api/v1/flows/", headers={"Authorization": f"Bearer {token}"})).json()
        target_flow = next(f for f in flows if f.get("endpoint_name") == "labortwin-copilot-v1")
        flow_id = target_flow["id"]
        
        for m in models_to_test:
            flow_data = target_flow["data"]
            for node in flow_data["nodes"]:
                if "GoogleGenerativeAI" in node.get("id", "") or node.get("data", {}).get("type") == "GoogleGenerativeAIComponent":
                    node["data"]["node"]["template"]["model_name"]["value"] = m
            
            await client.patch(
                f"/api/v1/flows/{flow_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={"data": flow_data}
            )
            
            try:
                resp = await client.post(
                    "/api/v1/run/labortwin-copilot-v1?stream=false",
                    headers={"x-api-key": "sk-TwLFZ6VRuVldtsxCB8ncpTZarkRPFuAK2HdrbZzIhYg"},
                    json={
                        "input_value": "Hola, resume en una oracion que es el empleo formal.",
                        "tweaks": {"GoogleGenerativeAI-LaborTwin": {"api_key": api_key}}
                    }
                )
                print(f"Model [{m}] -> HTTP Status: {resp.status_code}")
                if resp.status_code == 200:
                    text = resp.json()["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                    print(f"✅ EXITO con modelo [{m}]:\n{text}")
                    return m
                else:
                    print(f"❌ Error con [{m}]: {resp.text[:160]}")
            except Exception as ex:
                print(f"⚠️ Excepcion con [{m}]: {ex}")

if __name__ == "__main__":
    asyncio.run(test_models())

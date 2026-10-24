import os
import sys
import httpx
import asyncio
from dotenv import dotenv_values

sys.path.insert(0, os.path.abspath("."))

print("=== CHECKING ENVIRONMENT VARIABLES ===")
for path in [".env", "backend/.env"]:
    if os.path.exists(path):
        vals = dotenv_values(path)
        print(f"File: {path}")
        for k in sorted(vals.keys()):
            v = vals[k]
            is_set = bool(v and v.strip())
            print(f"  {k}: {'DEFINIDA' if is_set else 'NO DEFINIDA'}")
    else:
        print(f"File: {path} NOT FOUND")

print("\n=== CHECKING POSTGRESQL CONNECTION VIA backend.database ===")
async def test_db():
    try:
        from backend.database import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT version();"))
            row = res.fetchone()
            print(f"PostgreSQL connection SUCCESS: {row[0] if row else 'OK'}")
            
            # Check tables in database
            tables_res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
            tables = [r[0] for r in tables_res.fetchall()]
            print(f"Existing public tables: {tables}")
    except Exception as e:
        print(f"PostgreSQL connection FAILED: {type(e).__name__}: {e}")

async def test_langflow():
    print("\n=== CHECKING LANGFLOW SERVICE ===")
    from dotenv import load_dotenv
    load_dotenv("backend/.env")
    load_dotenv(".env")
    
    base_url = os.getenv("LANGFLOW_BASE_URL", "http://127.0.0.1:7860")
    flow_id = os.getenv("LANGFLOW_COPILOT_FLOW_ID", "")
    api_key = os.getenv("LANGFLOW_API_KEY", "")
    
    print(f"LANGFLOW_BASE_URL configured: {base_url}")
    print(f"LANGFLOW_COPILOT_FLOW_ID configured: {'DEFINIDA' if flow_id else 'NO DEFINIDA'}")
    print(f"LANGFLOW_API_KEY configured: {'DEFINIDA' if api_key else 'NO DEFINIDA'}")
    
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            resp = await client.get("/health")
            print(f"Langflow GET /health: HTTP {resp.status_code}")
            
            auto_login = await client.get("/api/v1/auto_login")
            print(f"Langflow GET /api/v1/auto_login: HTTP {auto_login.status_code}")
            if auto_login.status_code == 200:
                token = auto_login.json().get("access_token")
                flows_resp = await client.get("/api/v1/flows/", headers={"Authorization": f"Bearer {token}"})
                print(f"Langflow GET /api/v1/flows/: HTTP {flows_resp.status_code}")
                if flows_resp.status_code == 200:
                    flows = flows_resp.json()
                    print(f"Total flows in Langflow: {len(flows)}")
                    flow_matches = []
                    for f in flows:
                        f_id = f.get("id")
                        f_name = f.get("name")
                        f_ep = f.get("endpoint_name")
                        print(f"  Flow: Name='{f_name}', ID={f_id}, Endpoint='{f_ep}'")
                        if f_id == flow_id or f_ep == "labortwin-copilot-v1":
                            flow_matches.append(f)
                    if flow_matches:
                        print(f"SUCCESS: Target flow LANGFLOW_COPILOT_FLOW_ID found! Matching: {[m.get('name') for m in flow_matches]}")
                    else:
                        print(f"WARNING: Target flow ID '{flow_id}' not found in active Langflow flows.")
    except Exception as e:
        print(f"Langflow connection FAILED: {type(e).__name__}: {e}")

async def main():
    await test_db()
    await test_langflow()

if __name__ == "__main__":
    asyncio.run(main())

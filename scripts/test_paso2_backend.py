import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.abspath("."))
import httpx
import websockets
from sqlalchemy import text
from backend.database import engine

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/simulation"

COUNTRIES = ["KENYA", "NIGERIA", "INDIA", "BANGLADESH"]
SCENARIOS = ["A", "B1", "B2", "C", "D"]

async def test_simulations_endpoints(client: httpx.AsyncClient):
    print("\n--- 1. Testing Simulation Endpoints ---")
    r = await client.get("/api/v1/simulations/scenarios")
    print(f"GET /api/v1/simulations/scenarios: {r.status_code}")
    assert r.status_code == 200

    all_ok = True
    for c in COUNTRIES:
        for s in SCENARIOS:
            params = {"country": c, "scenario": s, "month": 60}
            rm = await client.get("/api/v1/simulations/metrics", params=params)
            rt = await client.get("/api/v1/simulations/trajectories", params={"country": c, "scenario": s})
            rf = await client.get("/api/v1/simulations/firms", params={"country": c, "scenario": s, "month": 60})
            rh = await client.get("/api/v1/simulations/historical", params={"country": c})
            
            codes = [rm.status_code, rt.status_code, rf.status_code, rh.status_code]
            if not all(code == 200 for code in codes):
                print(f"FAIL for {c} {s}: metrics={rm.status_code}, traj={rt.status_code}, firms={rf.status_code}, hist={rh.status_code}")
                all_ok = False
    
    print(f"All 4 countries x 5 scenarios tested on metrics, trajectories, firms, historical: {'OK (all 200)' if all_ok else 'FAIL'}")

async def test_websocket():
    print("\n--- 2. Testing WebSocket /ws/simulation ---")
    messages_received = []
    try:
        async with websockets.connect(WS_URL) as ws:
            # 1. Initial snapshot frame at month 0 sent by backend upon connection
            initial = await asyncio.wait_for(ws.recv(), timeout=5.0)
            messages_received.append(json.loads(initial))
            
            # 2. Tell engine to play at high speed to receive dynamic stream
            await ws.send(json.dumps({"action": "set_speed", "speed": 10.0}))
            await ws.send(json.dumps({"action": "play"}))
            
            for _ in range(12):
                msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(msg)
                messages_received.append(data)
                
            await ws.send(json.dumps({"action": "pause"}))

        print(f"WebSocket connected and received {len(messages_received)} messages successfully.")
        sample = messages_received[0]
        has_data = bool("month" in sample or "metrics" in sample or "informalityRate" in str(sample))
        print(f"Initial frame keys: {list(sample.keys())}")
        print(f"Frame 5 month: {messages_received[5].get('month')}, metrics informality: {messages_received[5].get('metrics', {}).get('informalityRate')}")
        print(f"WebSocket verification: {'OK' if len(messages_received) >= 10 and has_data else 'FAIL'}")
    except Exception as e:
        print(f"WebSocket test FAILED: {type(e).__name__}: {e}")

async def test_simulation_save_and_history(client: httpx.AsyncClient):
    print("\n--- 3. Testing Saved Simulations (POST save & GET history) ---")
    save_payload = {
        "country": "KENYA",
        "scenario": "D",
        "duration_sec": 4.5,
        "final_metrics": {"informalityRate": 51.8, "genderGap": 0.3},
        "policy_params": {"enforcementLevel": 1.5}
    }
    r_save = await client.post("/api/v1/simulations/save", json=save_payload)
    print(f"POST /api/v1/simulations/save: {r_save.status_code}, response={r_save.text[:120]}")
    saved_id = r_save.json().get("run", {}).get("id") if r_save.status_code in [200, 201] else None

    r_hist = await client.get("/api/v1/simulations/history")
    runs = r_hist.json().get("runs", []) if r_hist.status_code == 200 else []
    print(f"GET /api/v1/simulations/history: {r_hist.status_code}, runs count={len(runs)}")
    
    # Confirm in PostgreSQL directly
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT id, country, scenario, duration_sec FROM simulation_runs ORDER BY created_at DESC LIMIT 3;"))
        rows = res.fetchall()
        print(f"Direct PostgreSQL confirmation in simulation_runs: {rows}")

async def test_datasets_endpoints(client: httpx.AsyncClient):
    print("\n--- 4. Testing Datasets Endpoints ---")
    # /api/v1/datasets
    r1 = await client.get("/api/v1/datasets")
    print(f"GET /api/v1/datasets: {r1.status_code}, data={list(r1.json().keys()) if r1.status_code==200 else r1.text[:80]}")

    # /api/v1/datasets/list
    r2 = await client.get("/api/v1/datasets/list")
    datasets = r2.json().get("datasets", []) if r2.status_code == 200 else []
    print(f"GET /api/v1/datasets/list: {r2.status_code}, count={len(datasets)}")

    # /api/v1/datasets/select-preset
    presets = ["india", "nigeria", "kenya"]
    for p in presets:
        rp = await client.post("/api/v1/datasets/select-preset", json={"dataset_id": p})
        print(f"POST /api/v1/datasets/select-preset ({p}): {rp.status_code}, body={rp.text[:100]}")

    # /api/v1/datasets/active
    r3 = await client.get("/api/v1/datasets/active")
    print(f"GET /api/v1/datasets/active: {r3.status_code}, active_filename={r3.json().get('filename') if r3.status_code==200 else r3.text[:80]}")

    # /api/v1/datasets/preview
    r4 = await client.get("/api/v1/datasets/preview")
    print(f"GET /api/v1/datasets/preview: {r4.status_code}, sample_rows={len(r4.json().get('sample', [])) if r4.status_code==200 else r4.text[:80]}")

    # /api/v1/datasets/upload test with valid CSV
    csv_content = (
        "CAPITAL_HUMANO,ESTADO_LABORAL,INGRESO_NETO_DIA,HORAS_CUIDADO,ALFABETIZACION_DIGITAL,EDAD,SEXO,ZONA\n"
        "2.5,1,15.0,2.0,1,30,0,1\n"
        "1.2,0,8.5,5.0,0,45,1,0\n"
        "3.1,1,22.0,1.0,1,28,0,1\n"
    )
    files = {"file": ("test_real_microdatos.csv", csv_content.encode("utf-8"), "text/csv")}
    ru = await client.post("/api/v1/datasets/upload", files=files)
    print(f"POST /api/v1/datasets/upload: {ru.status_code}, response={ru.text[:120]}")

    # Verification of synthetic vs real in presets / datasets
    print("\n--- Verifying if any preset or dataset is synthetic ---")
    r_list = await client.get("/api/v1/datasets/list")
    all_ds = r_list.json().get("datasets", [])
    for d in all_ds:
        fn = d.get("filename", "")
        rec = d.get("records_count", 0)
        print(f"  Stored Dataset: {fn} (records: {rec})")

    # Check data/ folder and data_store/
    for check_dir in ["data", "data/raw", "data/microdatos_reales", "data_store"]:
        if os.path.exists(check_dir):
            files_in_dir = os.listdir(check_dir)
            print(f"  Files in {check_dir}: {[f for f in files_in_dir if os.path.isfile(os.path.join(check_dir, f))]}")

async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        await test_simulations_endpoints(client)
        await test_websocket()
        await test_simulation_save_and_history(client)
        await test_datasets_endpoints(client)

if __name__ == "__main__":
    asyncio.run(main())

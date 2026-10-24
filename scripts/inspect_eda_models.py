import asyncio
import httpx
import json

async def inspect():
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:
        for c in ["india", "nigeria"]:
            await client.post("/api/v1/datasets/select-preset", json={"dataset_id": c})
            r_eda = await client.get("/api/v1/ml/eda")
            eda = r_eda.json()
            print(f"\n--- EDA for {c.upper()} ---")
            print("KPIs:", json.dumps(eda.get("kpis", {}), indent=2))
            
            r_models = await client.get("/api/v1/ml/models")
            models = r_models.json()
            print(f"Models for {c.upper()}:")
            for m in models.get("models", []):
                print(f"  {m.get('algorithm')}: auc_cv={m.get('auc_roc_cv')} (auc_test={m.get('auc_roc_test')}, is_winner={m.get('is_winner')})")
            print("Active Model in get_ml_models:", models.get("active_model"))

if __name__ == "__main__":
    asyncio.run(inspect())

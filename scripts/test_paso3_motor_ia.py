import asyncio
import json
import httpx

BASE_URL = "http://localhost:8000"

async def test_country_ml(client: httpx.AsyncClient, country_id: str, expected_rows: int, expected_winner: str, expected_auc_cv: float):
    print(f"\n=======================================================")
    print(f"TESTING MOTOR IA FOR: {country_id.upper()}")
    print(f"=======================================================")

    # 1. Select preset to load country microdata
    r_preset = await client.post("/api/v1/datasets/select-preset", json={"dataset_id": country_id})
    print(f"1. Select preset '{country_id}': HTTP {r_preset.status_code}")
    assert r_preset.status_code == 200

    # 2. GET /api/v1/ml/eda
    r_eda = await client.get("/api/v1/ml/eda", params={"country": country_id})
    if r_eda.status_code != 200:
        # try without params
        r_eda = await client.get("/api/v1/ml/eda")
    print(f"2. GET /api/v1/ml/eda: HTTP {r_eda.status_code}")
    eda_data = r_eda.json() if r_eda.status_code == 200 else {}
    total_rows = eda_data.get("total_rows") or eda_data.get("total_records") or eda_data.get("records_count")
    print(f"   EDA total rows: {total_rows} (Expected: {expected_rows}) -> {'MATCH' if total_rows == expected_rows else 'DIFF'}")
    print(f"   EDA keys: {list(eda_data.keys())}")

    # 3. GET /api/v1/ml/models
    r_models = await client.get("/api/v1/ml/models", params={"country": country_id})
    print(f"3. GET /api/v1/ml/models: HTTP {r_models.status_code}")
    models_data = r_models.json() if r_models.status_code == 200 else []
    models_list = models_data if isinstance(models_data, list) else models_data.get("models", [])
    print(f"   Total models loaded: {len(models_list)}")
    winner_found = None
    for m in models_list:
        algo = m.get("algorithm") or m.get("name")
        is_winner = m.get("is_winner") or m.get("is_champion") or m.get("winner")
        auc_cv = m.get("auc_roc_cv") or m.get("metrics", {}).get("auc_roc_cv") or m.get("cv_metrics", {}).get("auc_roc_cv")
        if is_winner or (algo and expected_winner.lower() in algo.lower()):
            winner_found = m
            print(f"   Candidate/Winner model: {algo} | is_winner: {is_winner} | AUC CV: {auc_cv}")

    # 4. POST /api/v1/ml/cross-validation
    r_cv = await client.post("/api/v1/ml/cross-validation", json={"country": country_id, "n_splits": 5})
    print(f"4. POST /api/v1/ml/cross-validation: HTTP {r_cv.status_code}")
    cv_data = r_cv.json() if r_cv.status_code == 200 else {}
    print(f"   CV response keys: {list(cv_data.keys()) if isinstance(cv_data, dict) else len(cv_data)}")

    # 5. GET /api/v1/ml/active-model
    r_active = await client.get("/api/v1/ml/active-model", params={"country": country_id})
    print(f"5. GET /api/v1/ml/active-model: HTTP {r_active.status_code}")
    active_data = r_active.json() if r_active.status_code == 200 else {}
    active_algo = active_data.get("algorithm") or active_data.get("name")
    active_id = active_data.get("id") or active_data.get("model_id")
    print(f"   Active model: {active_algo} (id={active_id})")

    # 6. POST /api/v1/ml/deploy-model
    deploy_id = active_id or "algo-histgradientboosting"
    r_deploy = await client.post("/api/v1/ml/deploy-model", json={"model_id": deploy_id, "country": country_id})
    print(f"6. POST /api/v1/ml/deploy-model: HTTP {r_deploy.status_code}")

    # 7. POST /api/v1/ml/proyeccion-cohorte
    cohort_payload = {
        "model_id": deploy_id,
        "cohort_filters": {"gender": "F", "education_level": "SECONDARY", "age_bracket": "25-34"},
        "policy_params": {"childcareSupport": 60.0, "digitalTraining": 40.0}
    }
    r_proj = await client.post("/api/v1/ml/proyeccion-cohorte", json=cohort_payload)
    print(f"7. POST /api/v1/ml/proyeccion-cohorte: HTTP {r_proj.status_code}")
    if r_proj.status_code == 200:
        proj_data = r_proj.json()
        print(f"   Projections sample: {list(proj_data.keys()) if isinstance(proj_data, dict) else len(proj_data)}")

async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # India (PLFS 2024: 163 973 ocupados, winner HistGradientBoosting, AUC CV 93.28)
        await test_country_ml(client, "india", expected_rows=163973, expected_winner="HistGradientBoosting", expected_auc_cv=93.28)
        # Nigeria (NLFS 2023: 18 808 ocupados, winner MLP, AUC CV 89.75)
        await test_country_ml(client, "nigeria", expected_rows=18808, expected_winner="MLP", expected_auc_cv=89.75)

if __name__ == "__main__":
    asyncio.run(main())

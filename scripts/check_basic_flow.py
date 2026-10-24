import httpx
import asyncio
import json

async def check():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:7860", timeout=10.0) as client:
        token = (await client.get("/api/v1/auto_login")).json().get("access_token")
        flows = (await client.get("/api/v1/flows/", headers={"Authorization": f"Bearer {token}"})).json()
        basic = next(f for f in flows if f.get("name") == "Basic Prompting")
        print("Basic Prompting keys:", basic.keys())
        print("Nodes count:", len(basic.get("data", {}).get("nodes", [])))

if __name__ == "__main__":
    asyncio.run(check())

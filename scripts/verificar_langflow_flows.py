import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
load_dotenv(".env")

async def check():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:7860", timeout=10.0) as client:
        token = (await client.get("/api/v1/auto_login")).json().get("access_token")
        flows = (await client.get("/api/v1/flows/", headers={"Authorization": f"Bearer {token}"})).json()
        print(f"Total flows: {len(flows)}")
        for f in flows:
            print(f"- Name: {f.get('name')}, Endpoint: {f.get('endpoint_name')}, ID: {f.get('id')}")

if __name__ == "__main__":
    asyncio.run(check())

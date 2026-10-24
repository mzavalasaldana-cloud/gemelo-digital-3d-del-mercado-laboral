import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding="utf-8")
from backend.database import engine
from sqlalchemy import text

async def main():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT id, session_id, user_message, assistant_response, source FROM copilot_chat_history ORDER BY created_at DESC LIMIT 5;"))
        rows = res.fetchall()
        for r in reversed(rows):
            print(f"\n=======================================================")
            print(f"ID: {r[0]} | SESSION: {r[1]} | ORIGEN: {r[4]}")
            print(f"PREGUNTA: {r[2]}")
            print(f"RESPUESTA:\n{r[3]}")

if __name__ == "__main__":
    asyncio.run(main())

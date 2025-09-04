# app/scripts/clear_cache_all.py
import asyncio
from sqlalchemy import delete
from app.db import async_session_maker
from app.models import GPTCache

async def main():
    async with async_session_maker() as session:
        await session.execute(delete(GPTCache))
        await session.commit()
        print("✅ gpt_cache очищен полностью")

if __name__ == "__main__":
    asyncio.run(main())

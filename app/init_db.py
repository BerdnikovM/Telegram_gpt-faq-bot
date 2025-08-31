import asyncio
from app.db import init_models
import app.models



async def main():
    await init_models()
    print("✅ Таблицы успешно созданы в базе данных")


if __name__ == "__main__":
    asyncio.run(main())

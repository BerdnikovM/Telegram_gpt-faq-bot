import asyncio
from app.db import reset_db
import app.models  # обязательно импортируем, чтобы SQLModel знал про все таблицы


async def main():
    await reset_db()
    print("✅ База данных пересоздана (все таблицы удалены и созданы заново).")


if __name__ == "__main__":
    asyncio.run(main())

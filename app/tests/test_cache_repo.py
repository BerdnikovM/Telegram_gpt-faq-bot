import pytest
import pytest_asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC

from app.models import GPTCache
from app.repositories import cache_repo
from app.services.text_norm import qhash


pytestmark = pytest.mark.asyncio  # чтобы не ругался pytest на async-тесты


# Фикстура: SQLite in-memory сессия
@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session_maker() as session:
        yield session

    await engine.dispose()


# === ТЕСТЫ ===

async def test_cache_insert_and_get(session):
    q = "Привет, мир!"
    h = qhash(q)

    # В кэше ничего нет
    entry = await cache_repo.get_by_hash(session, h)
    assert entry is None

    # Записываем fresh-ответ
    entry = await cache_repo.upsert(session, h, "Ответ от GPT", fresh=True)
    assert entry.answer == "Ответ от GPT"
    assert entry.hits == 0
    assert isinstance(entry.created_at, datetime)

    # Теперь запись есть
    cached = await cache_repo.get_by_hash(session, h)
    assert cached is not None
    assert cached.answer == "Ответ от GPT"


async def test_cache_hits_increment(session):
    q = "Как сделать заказ?"
    h = qhash(q)

    # Создаем свежую запись
    entry = await cache_repo.upsert(session, h, "Ответ 1", fresh=True)
    assert entry.hits == 0

    # Обращаемся повторно (без fresh) → hits++
    entry2 = await cache_repo.upsert(session, h, "Ответ 2", fresh=False)
    assert entry2.hits == 1
    assert entry2.answer == "Ответ 1"  # старый ответ остался

    # Обновляем fresh → ответ заменится, created_at обновится
    entry3 = await cache_repo.upsert(session, h, "Новый ответ", fresh=True)
    assert entry3.answer == "Новый ответ"
    assert entry3.hits == 2

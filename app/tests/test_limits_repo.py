import pytest
import pytest_asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC, timedelta

from app.models import UsageLimit
from app.repositories import limits_repo


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session_maker() as session:
        yield session

    await engine.dispose()


# === ТЕСТЫ ===

async def test_check_and_increment_within_limit(session):
    user_id = 1
    max_per_minute = 3

    # Должно пройти три раза
    assert await limits_repo.check_and_increment(session, user_id, max_per_minute) is True
    assert await limits_repo.check_and_increment(session, user_id, max_per_minute) is True
    assert await limits_repo.check_and_increment(session, user_id, max_per_minute) is True

    # Четвёртый — лимит
    assert await limits_repo.check_and_increment(session, user_id, max_per_minute) is False


async def test_check_and_increment_new_minute(session):
    user_id = 2
    max_per_minute = 2

    # Один запрос в текущем окне
    assert await limits_repo.check_and_increment(session, user_id, max_per_minute) is True

    # Сдвигаем window_start вручную на прошлую минуту
    result = await session.execute(
        SQLModel.metadata.tables["usage_limits"].select().where(
            SQLModel.metadata.tables["usage_limits"].c.user_id == user_id
        )
    )
    row = result.first()
    await session.execute(
        UsageLimit.__table__.update().where(UsageLimit.id == row.id).values(
            window_start=datetime.now(UTC) - timedelta(minutes=1)
        )
    )
    await session.commit()

    # Новый запрос → создаст новую запись для новой минуты
    assert await limits_repo.check_and_increment(session, user_id, max_per_minute) is True


async def test_cleanup_old_limits(session):
    user_id = 3
    max_per_minute = 1

    # Добавляем запись
    assert await limits_repo.check_and_increment(session, user_id, max_per_minute) is True

    # Сдвигаем её на 10 минут назад
    await session.execute(
        UsageLimit.__table__.update().values(window_start=datetime.now(UTC) - timedelta(minutes=10))
    )
    await session.commit()

    # Чистим старые
    deleted = await limits_repo.cleanup_old_limits(session, keep_minutes=5)
    assert deleted >= 1

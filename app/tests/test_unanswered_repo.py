import pytest
import pytest_asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import UTC, datetime

from app.models import UnansweredQuestion, User
from app.repositories import unanswered_repo


pytestmark = pytest.mark.asyncio


# Фикстура для SQLite in-memory
@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session_maker() as session:
        # нужно создать пользователя, т.к. есть FK
        user = User(tg_id=999, created_at=datetime.now(UTC))
        session.add(user)
        await session.commit()
        await session.refresh(user)
        yield session

    await engine.dispose()


# === ТЕСТЫ ===

async def test_add_and_get_unanswered(session):
    # Добавляем вопрос
    entry = await unanswered_repo.add_unanswered(session, user_id=1, question_text="Как оформить заказ?", similar_score=55.5)

    assert entry.id is not None
    assert entry.question_text == "Как оформить заказ?"
    assert isinstance(entry.created_at, datetime)

    # Получаем последние вопросы
    recent = await unanswered_repo.get_recent_unanswered(session, limit=5)
    assert len(recent) == 1
    assert recent[0].question_text == "Как оформить заказ?"


async def test_delete_unanswered(session):
    # Добавляем вопрос
    entry = await unanswered_repo.add_unanswered(session, user_id=1, question_text="Как подключить подписку?", similar_score=None)

    # Удаляем его
    success = await unanswered_repo.delete_unanswered(session, entry.id)
    assert success is True

    # Повторное удаление → False
    success2 = await unanswered_repo.delete_unanswered(session, entry.id)
    assert success2 is False

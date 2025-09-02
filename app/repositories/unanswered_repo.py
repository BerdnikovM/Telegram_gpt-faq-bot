from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, UTC
from typing import List

from app.models import UnansweredQuestion


async def add_unanswered(session: AsyncSession, user_id: int, question_text: str, similar_score: float | None) -> UnansweredQuestion:
    """
    Добавляет вопрос в таблицу unanswered_questions.
    """
    entry = UnansweredQuestion(
        user_id=user_id,
        question_text=question_text,
        similar_score=similar_score,
        created_at=datetime.now(UTC),
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def get_recent_unanswered(session: AsyncSession, limit: int = 10) -> List[UnansweredQuestion]:
    """
    Возвращает последние N вопросов, которые ушли в LLM (без уверенного матча).
    """
    result = await session.execute(
        select(UnansweredQuestion)
        .order_by(UnansweredQuestion.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def delete_unanswered(session: AsyncSession, question_id: int) -> bool:
    """
    Удаляет вопрос из таблицы unanswered_questions по id.
    Возвращает True, если удалено, иначе False.
    """
    result = await session.execute(
        select(UnansweredQuestion).where(UnansweredQuestion.id == question_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        return False

    await session.delete(entry)
    await session.commit()
    return True

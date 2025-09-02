from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, UTC
from typing import Optional

from app.models import GPTCache


async def get_by_hash(session: AsyncSession, qhash: str) -> Optional[GPTCache]:
    """
    Возвращает кэшированный ответ по qhash или None.
    """
    result = await session.execute(
        select(GPTCache).where(GPTCache.qhash == qhash)
    )
    return result.scalar_one_or_none()


async def upsert(session: AsyncSession, qhash: str, answer: str, fresh: bool = False) -> GPTCache:
    """
    Обновляет или добавляет запись в кэше.
    fresh=True → сбрасывает created_at и обновляет answer (после LLM).
    fresh=False → только увеличивает hits (при попадании в кэш).
    """
    entry = await get_by_hash(session, qhash)

    if entry:
        if fresh:
            entry.answer = answer
            entry.created_at = datetime.now(UTC)
        entry.hits += 1
    else:
        entry = GPTCache(
            qhash=qhash,
            answer=answer,
            created_at=datetime.now(UTC),
            hits=0 if fresh else 1  # можно начать с 0 при свежей записи
        )
        session.add(entry)

    await session.commit()
    await session.refresh(entry)
    return entry

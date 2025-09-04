from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models import FAQEntry


# === CRUD ===
async def create_faq(session: AsyncSession, question: str, answer: str) -> FAQEntry:
    entry = FAQEntry(question=question, answer=answer)
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def get_by_id(session: AsyncSession, faq_id: int) -> FAQEntry | None:
    result = await session.execute(
        select(FAQEntry).where(FAQEntry.id == faq_id)
    )
    return result.scalar_one_or_none()


async def update_faq(session: AsyncSession, faq_id: int, question: str, answer: str) -> bool:
    entry = await get_by_id(session, faq_id)
    if not entry:
        return False
    entry.question = question
    entry.answer = answer
    await session.commit()
    return True


async def delete_faq(session: AsyncSession, faq_id: int) -> bool:
    entry = await get_by_id(session, faq_id)
    if not entry:
        return False
    await session.delete(entry)
    await session.commit()
    return True


# === Топ вопросов (по популярности) ===
async def top_faq(session: AsyncSession, limit: int, offset: int = 0) -> list[FAQEntry]:
    result = await session.execute(
        select(FAQEntry).order_by(desc(FAQEntry.popularity), FAQEntry.id).limit(limit).offset(offset)
    )
    return result.scalars().all()


# === Увеличение популярности ===
async def inc_popularity(session: AsyncSession, faq_id: int) -> None:
    entry = await get_by_id(session, faq_id)
    if entry:
        entry.popularity += 1
        await session.commit()


async def all_for_search(session: AsyncSession) -> list[FAQEntry]:
    result = await session.execute(select(FAQEntry))
    return result.scalars().all()


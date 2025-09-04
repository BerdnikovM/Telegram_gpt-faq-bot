from sqlalchemy import select, desc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, UTC
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


async def update_faq(session: AsyncSession, faq_id: int, *, answer: str) -> bool:
    res = await session.execute(select(FAQEntry).where(FAQEntry.id == faq_id))
    faq = res.scalar_one_or_none()
    if not faq:
        return False
    faq.answer = answer
    faq.updated_at = datetime.now(UTC)
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

# === Добавить FAQ ===
async def add_faq(session: AsyncSession, question: str, answer: str) -> FAQEntry:
    entry = FAQEntry(question=question, answer=answer, popularity=0)
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry

# === Удалить FAQ ===
async def delete_faq(session: AsyncSession, faq_id: int) -> bool:
    result = await session.execute(select(FAQEntry).where(FAQEntry.id == faq_id))
    entry = result.scalar_one_or_none()
    if not entry:
        return False

    await session.delete(entry)
    await session.commit()
    return True


# === Обновить ответ FAQ ===
async def update_faq_answer(session: AsyncSession, faq_id: int, new_answer: str) -> bool:
    result = await session.execute(select(FAQEntry).where(FAQEntry.id == faq_id))
    entry = result.scalar_one_or_none()
    if not entry:
        return False

    entry.answer = new_answer
    await session.commit()
    return True


# === Получить все FAQ (для списка / удаления) ===
async def all_faqs(session: AsyncSession) -> List[FAQEntry]:
    result = await session.execute(select(FAQEntry).order_by(FAQEntry.id))
    return result.scalars().all()

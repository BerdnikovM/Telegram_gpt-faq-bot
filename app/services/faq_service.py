import logging
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from rapidfuzz import fuzz

from app.models import FAQEntry
from app.repositories import faq_repo, cache_repo
from app.repositories.faq_repo import inc_popularity, all_for_search
from app.services.text_norm import normalize, qhash
from app.config import CACHE_TTL_HOURS
from typing import Optional
from app.services.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)
THRESHOLD_FAQ = 70  # порог уверенности для fuzzy-match

def _make_cache_key(text: str, context_faqs: Optional[list[FAQEntry]]) -> str:
    """
    Ключ кэша учитывает и вопрос, и ID FAQ-контекста (если он есть).
    Это предотвращает возврат старой версии без контекста.
    """
    base = normalize(text)
    if context_faqs:
        ctx_ids = ",".join(str(f.id) for f in context_faqs)
        base = f"{base}::ctx={ctx_ids}"
    return qhash(base)

async def get_answer_from_faq(
    session: AsyncSession,
    user_id: int,
    text: str
) -> tuple[str | None, list[FAQEntry], bool]:
    """
    Возвращает:
      - answer: строка (если найден exact или из GPT/cache); иначе None
      - candidates: список FAQEntry (для уточнения пользователем)
      - need_clarification: True, если нужно спросить пользователя (только fuzzy)
    """

    norm_q = normalize(text)
    candidates = await all_for_search(session)

    # === 1. Exact match ===
    for faq in candidates:
        if normalize(faq.question) == norm_q:
            await inc_popularity(session, faq.id)
            return faq.answer, [faq], False

    # === 2. Fuzzy search (только кандидаты, без автоответа) ===
    if not candidates:
        return None, [], False

    scored = [(faq, fuzz.WRatio(norm_q, normalize(faq.question))) for faq in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    top3 = [faq for faq, _ in scored[:3]]

    return None, top3, True  # пользователь должен выбрать вручную


async def get_answer_from_gpt_cache_or_llm(
    session: AsyncSession,
    user_id: int,
    text: str,
    context_faqs=None,
) -> str:
    """
    Проверка кэша → если устарело или нет → запрос в LLM с контекстом.
    """
    norm_q = normalize(text)
    h = qhash(norm_q)

    # 1. Проверка кэша
    entry = await cache_repo.get_by_hash(session, h)
    if entry:
        age = datetime.now(UTC) - entry.created_at
        if age <= timedelta(hours=CACHE_TTL_HOURS):
            entry.hits += 1
            await session.commit()
            logger.info(f"[CACHE HIT] Ответ для qhash={h} взят из кэша")
            return entry.answer  # ответ из кэша
        else:
            logger.info(f"[CACHE EXPIRED] Ответ для qhash={h} устарел")

    # 2. Формируем список контекстных блоков
    context_chunks = []
    if context_faqs:
        for faq in context_faqs:
            context_chunks.append(f"Вопрос: {faq.question}\nОтвет: {faq.answer}")

    # 3. Вызов LLM-провайдера (YandexGPT)
    provider = get_llm_provider()
    llm_answer = await provider.answer(text, context_chunks)
    logger.info(f"[LLM REQUEST] Вызван YandexGPT для qhash={h}")

    # 4. Сохраняем в кэш
    await cache_repo.upsert(session, h, llm_answer, fresh=True)
    logger.info(f"[CACHE SAVE] Ответ сохранён в кэш для qhash={h}")

    return llm_answer

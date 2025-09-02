from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from rapidfuzz import fuzz

from app.models import FAQEntry
from app.repositories import faq_repo
from app.repositories.faq_repo import inc_popularity, all_for_search
from app.services.text_norm import normalize


THRESHOLD_FAQ = 70  # порог уверенности для fuzzy-match


async def get_answer_from_faq(session: AsyncSession, user_id: int, text: str) -> tuple[str | None, list[FAQEntry]]:
    norm_q = normalize(text)

    # 1. Exact match
    candidates = await all_for_search(session)
    for faq in candidates:
        if normalize(faq.question) == norm_q:
            await inc_popularity(session, faq.id)
            return faq.answer, [faq]  # возвращаем список FAQEntry без score

    # 2. Fuzzy match
    scored = []
    for faq in candidates:
        score = fuzz.token_set_ratio(norm_q, normalize(faq.question))
        scored.append((faq, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    if not scored:
        return None, []

    best_faq, best_score = scored[0]

    if best_score >= THRESHOLD_FAQ:
        await inc_popularity(session, best_faq.id)
        # Возвращаем только FAQEntry без score
        return best_faq.answer, [faq for faq, _ in scored[:3]]

    # 3. Ничего уверенного не нашли → пусть вернётся None, но список кандидатов оставляем
    return None, [faq for faq, _ in scored[:3]]

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from app.models import FAQEntry
from app.services.faq_service import get_answer_from_faq


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with async_session() as s:
        yield s


@pytest_asyncio.fixture
async def seed_faq(session: AsyncSession):
    faqs = [
        FAQEntry(question="Как сделать заказ?", answer="Выберите товар и оформите заказ."),
        FAQEntry(question="Какие способы оплаты доступны?", answer="Можно картой или наложенным платежом."),
    ]
    session.add_all(faqs)
    await session.commit()
    return faqs


@pytest.mark.asyncio
async def test_exact_match(session, seed_faq):
    answer, ctx = await get_answer_from_faq(session, user_id=123, text="Как сделать заказ?")
    assert answer is not None
    assert "оформите заказ" in answer
    assert len(ctx) == 1

    # проверим, что популярность увеличилась
    faq = ctx[0]
    fresh = await session.get(FAQEntry, faq.id)
    assert fresh.popularity > 0


@pytest.mark.asyncio
async def test_fuzzy_match(session, seed_faq):
    answer, ctx = await get_answer_from_faq(session, user_id=123, text="Как оформить заказ?")
    assert answer is not None
    assert "оформите заказ" in answer
    assert len(ctx) >= 1

    # лучший FAQ должен быть первый
    best_faq = ctx[0]
    fresh = await session.get(FAQEntry, best_faq.id)
    assert fresh.popularity > 0


@pytest.mark.asyncio
async def test_no_match_low_score(session, seed_faq):
    answer, ctx = await get_answer_from_faq(session, user_id=123, text="Что вы думаете о космосе?")
    assert answer is None
    # кандидаты должны вернуться, но без уверенного ответа
    assert len(ctx) > 0

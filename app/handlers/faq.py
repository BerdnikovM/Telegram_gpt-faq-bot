from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, func, desc
from app.db import async_session_maker
from app.models import FAQEntry
from app.keyboards.faq_inline import faq_list_kb
from app.config import TOP_N_FAQ

router = Router()


# === Хендлер на кнопку 📋 FAQ ===
@router.message(F.text == "📋 FAQ")
async def show_faq_list(message: Message):
    async with async_session_maker() as session:
        # Считаем количество вопросов всего
        total_count = await session.scalar(select(func.count()).select_from(FAQEntry))

        # Берём первую страницу (offset=0)
        result = await session.execute(
            select(FAQEntry.id, FAQEntry.question)
            .order_by(desc(FAQEntry.popularity), FAQEntry.id)
            .limit(TOP_N_FAQ)
            .offset(0)
        )
        faq_items = result.all()

    if not faq_items:
        await message.answer("❌ В базе пока нет FAQ.")
        return

    # Если вопросов больше чем TOP_N_FAQ → добавляем кнопку «Далее»
    kb = faq_list_kb(faq_items)
    if total_count > TOP_N_FAQ:
        from aiogram.types import InlineKeyboardButton
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="➡️ Далее", callback_data="faq:page:1")
        ])

    await message.answer("📋 Часто задаваемые вопросы:", reply_markup=kb)


# === Хендлер на нажатие вопроса ===
@router.callback_query(F.data.startswith("faq:") & ~F.data.startswith("faq:page"))
async def faq_answer(callback: CallbackQuery):
    faq_id = int(callback.data.split(":")[1])

    async with async_session_maker() as session:
        result = await session.execute(
            select(FAQEntry).where(FAQEntry.id == faq_id)
        )
        faq_entry = result.scalar_one_or_none()

        if not faq_entry:
            await callback.answer("❌ Вопрос не найден", show_alert=True)
            return

        # Увеличиваем счётчик популярности
        faq_entry.popularity += 1
        await session.commit()

    await callback.message.answer(f"💡 {faq_entry.answer}")
    await callback.answer()  # убираем «часики»


# === Хендлер пагинации (следующая страница) ===
@router.callback_query(F.data.startswith("faq:page:"))
async def faq_pagination(callback: CallbackQuery):
    page = int(callback.data.split(":")[2])
    offset = page * TOP_N_FAQ

    async with async_session_maker() as session:
        total_count = await session.scalar(select(func.count()).select_from(FAQEntry))

        result = await session.execute(
            select(FAQEntry.id, FAQEntry.question)
            .order_by(desc(FAQEntry.popularity), FAQEntry.id)
            .limit(TOP_N_FAQ)
            .offset(offset)
        )
        faq_items = result.all()

    if not faq_items:
        await callback.answer("⚠️ Больше вопросов нет", show_alert=True)
        return

    kb = faq_list_kb(faq_items)

    # Если есть предыдущая страница — добавим «Назад»
    from aiogram.types import InlineKeyboardButton
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"faq:page:{page-1}"))
    if offset + TOP_N_FAQ < total_count:
        nav_row.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"faq:page:{page+1}"))
    if nav_row:
        kb.inline_keyboard.append(nav_row)

    # Редактируем предыдущее сообщение, а не отправляем новое
    await callback.message.edit_text("📋 Часто задаваемые вопросы:", reply_markup=kb)
    await callback.answer()

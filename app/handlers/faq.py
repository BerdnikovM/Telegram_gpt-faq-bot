from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.db import async_session_maker
from app.keyboards.faq_inline import faq_list_kb
from app.config import TOP_N_FAQ
from app.repositories import faq_repo

router = Router()


# === Хендлер на кнопку 📋 FAQ ===
@router.message(F.text == "📋 FAQ")
async def show_faq_list(message: Message):
    async with async_session_maker() as session:
        # Считаем общее количество FAQ
        total_count = len(await faq_repo.all_for_search(session))

        # Берём первую страницу (offset=0)
        faq_items = await faq_repo.top_faq(session, TOP_N_FAQ, offset=0)

    if not faq_items:
        await message.answer("❌ В базе пока нет FAQ.")
        return

    kb = faq_list_kb(faq_items)

    # Добавляем кнопку "Далее", если есть больше вопросов
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
        faq_entry = await faq_repo.get_by_id(session, faq_id)
        if not faq_entry:
            await callback.answer("❌ Вопрос не найден", show_alert=True)
            return

        # Увеличиваем популярность
        await faq_repo.inc_popularity(session, faq_id)

    await callback.message.answer(f"💡 {faq_entry.answer}")
    await callback.answer()


# === Хендлер пагинации (следующая/предыдущая страница) ===
@router.callback_query(F.data.startswith("faq:page:"))
async def faq_pagination(callback: CallbackQuery):
    page = int(callback.data.split(":")[2])
    offset = page * TOP_N_FAQ

    async with async_session_maker() as session:
        total_count = len(await faq_repo.all_for_search(session))
        faq_items = await faq_repo.top_faq(session, TOP_N_FAQ, offset=offset)

    if not faq_items:
        await callback.answer("⚠️ Больше вопросов нет", show_alert=True)
        return

    kb = faq_list_kb(faq_items)

    from aiogram.types import InlineKeyboardButton
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"faq:page:{page-1}"))
    if offset + TOP_N_FAQ < total_count:
        nav_row.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"faq:page:{page+1}"))
    if nav_row:
        kb.inline_keyboard.append(nav_row)

    await callback.message.edit_text("📋 Часто задаваемые вопросы:", reply_markup=kb)
    await callback.answer()

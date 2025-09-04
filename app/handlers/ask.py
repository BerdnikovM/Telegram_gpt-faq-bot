from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.db import async_session_maker
from app.services import faq_service
from app.repositories import faq_repo

router = Router()


# === FSM ===
class AskStates(StatesGroup):
    waiting_for_question = State()
    clarification = State()  # новое состояние для уточнения


# === 1. Кнопка "❓ Задать вопрос" ===
@router.message(F.text == "❓ Задать вопрос")
async def ask_question(message: Message, state: FSMContext):
    await state.set_state(AskStates.waiting_for_question)
    await message.answer(
        "✍ Напишите свой вопрос одним сообщением (до 512 символов).\n"
        "Я постараюсь найти ответ в базе знаний или спрошу у ИИ 🤖"
    )


# === 2. Кнопка "ℹ️ О сервисе" ===
@router.message(F.text == "ℹ️ О сервисе")
async def about_service(message: Message):
    text = (
        "ℹ️ <b>О сервисе</b>\n\n"
        "Этот бот помогает отвечать на часто задаваемые вопросы.\n"
        "Он ищет ответы в базе знаний, а если не находит — "
        "обращается к языковой модели (GPT).\n\n"
        "⚡ Возможности:\n"
        "• 📋 Быстрый доступ к популярным вопросам\n"
        "• 🤖 Ответы на свободные вопросы\n"
        "• 📈 Обучение на новых вопросах\n\n"
        "❗ Обратите внимание: бот может иногда ошибаться, "
        "поэтому используйте информацию с осторожностью."
    )
    await message.answer(text)


# === 3. Обработка не-текстовых сообщений в состоянии ожидания вопроса ===
@router.message(AskStates.waiting_for_question, ~F.text)
async def reject_non_text(message: Message):
    await message.answer("⚠️ Пожалуйста, отправьте именно текстовый вопрос, а не вложение.")


# === 4. Обработка текстового вопроса ===
@router.message(AskStates.waiting_for_question, F.text)
async def handle_free_text(message: Message, state: FSMContext):
    text = message.text.strip()

    if len(text) > 512:
        await message.answer("⚠️ Вопрос слишком длинный. Сократите до 512 символов.")
        return

    user_id = message.from_user.id

    async with async_session_maker() as session:
        answer, candidates, need_clarification = await faq_service.get_answer_from_faq(
            session, user_id, text
        )

    if answer:  # exact match
        await message.answer(answer)
        await state.clear()
        return

    if need_clarification and candidates:
        # сохраняем оригинальный вопрос и кандидатов
        await state.update_data(orig_question=text, candidates_ids=[c.id for c in candidates])

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"❓ {c.question}", callback_data=f"clarify:{c.id}")]
                for c in candidates
            ] + [[InlineKeyboardButton(text="❌ Другой вопрос", callback_data="clarify:none")]]
        )

        await state.set_state(AskStates.clarification)
        await message.answer("❓ Я не нашёл точный ответ. Вы имели в виду:", reply_markup=kb)
        return

    # fallback: вообще нет кандидатов → сразу GPT
    async with async_session_maker() as session:
        gpt_answer = await faq_service.get_answer_from_gpt_cache_or_llm(
            session,
            user_id=user_id,
            text=text,
            context_faqs=[],
        )
    await message.answer(gpt_answer)
    await state.clear()


# === 5. Обработка выбора пользователя при уточнении ===
@router.callback_query(F.data.startswith("clarify:"))
async def handle_clarification(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    orig_question = data.get("orig_question")
    candidates_ids = data.get("candidates_ids", [])

    choice = callback.data.split(":")[1]

    async with async_session_maker() as session:
        if choice == "none":
            # подтянем тех же кандидатов (top-3), что показывали пользователю
            context_faqs = []
            for cid in candidates_ids[:3]:
                faq = await faq_repo.get_by_id(session, cid)
                if faq:
                    context_faqs.append(faq)

            gpt_answer = await faq_service.get_answer_from_gpt_cache_or_llm(
                session,
                user_id=callback.from_user.id,
                text=orig_question,
                context_faqs=context_faqs,  # <-- передаём контекст!
            )
            await callback.message.answer(gpt_answer)
        else:
            faq_id = int(choice)
            faq_entry = await faq_service.faq_repo.get_by_id(session, faq_id)
            if faq_entry:
                await faq_service.faq_repo.inc_popularity(session, faq_id)
                await callback.message.answer(f"💡 {faq_entry.answer}")
            else:
                await callback.message.answer("❌ Этот вариант больше недоступен.")

    await state.clear()
    await callback.answer()

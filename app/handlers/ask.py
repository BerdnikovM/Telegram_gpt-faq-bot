from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.services.faq_service import get_answer_from_faq
from app.db import async_session_maker

router = Router()


# === FSM ===
class AskStates(StatesGroup):
    waiting_for_question = State()


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
        answer, ctx = await get_answer_from_faq(session, user_id, text)

    if answer:
        await message.answer(f"💡 {answer}")
    else:
        # Если уверенного совпадения нет → пока отвечаем так
        await message.answer("❓ Я не нашёл точного ответа. Скоро здесь будет GPT ✨")

    # Возвращаем пользователя в "обычный режим"
    await state.clear()


from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.keyboards.admin_inline import admin_inline_kb
from app.config import ADMINS
from app.db import async_session_maker
from app.models import Admin
from app.repositories import faq_repo, unanswered_repo

router = Router()


# === FSM для добавления FAQ ===
class AddFAQStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()


# === FSM для редактирования FAQ ===
class EditFAQStates(StatesGroup):
    waiting_for_new_answer = State()


# === Команда /admin ===
@router.message(Command("admin"))
async def admin_menu(message: Message):
    user_id = message.from_user.id

    # Проверяем доступ
    is_admin = False
    if user_id in ADMINS:
        is_admin = True
    else:
        async with async_session_maker() as session:
            admin = await session.get(Admin, user_id)
            if admin:
                is_admin = True

    if not is_admin:
        await message.answer("⛔ У вас нет доступа к админке.")
        return

    # Если админ → показываем меню
    await message.answer("⚙️ Админ-панель", reply_markup=admin_inline_kb())


# === Добавление FAQ ===
@router.callback_query(F.data == "admin:add")
async def admin_add(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("✍ Введите новый вопрос для FAQ:")
    await state.set_state(AddFAQStates.waiting_for_question)


@router.message(AddFAQStates.waiting_for_question, F.text)
async def add_faq_question(message: Message, state: FSMContext):
    await state.update_data(new_question=message.text.strip())
    await message.answer("Теперь введите ответ на этот вопрос:")
    await state.set_state(AddFAQStates.waiting_for_answer)


@router.message(AddFAQStates.waiting_for_answer, F.text)
async def add_faq_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    question = data.get("new_question")
    answer = message.text.strip()

    async with async_session_maker() as session:
        await faq_repo.add_faq(session, question, answer)

    await message.answer(f"✅ Вопрос добавлен в FAQ:\n\n❓ {question}\n💡 {answer}")
    await state.clear()


# === Удаление FAQ ===
@router.callback_query(F.data == "admin:delete")
async def admin_delete(callback: CallbackQuery):
    await callback.answer()

    async with async_session_maker() as session:
        faqs = await faq_repo.all_faqs(session)

    if not faqs:
        await callback.message.answer("📭 База FAQ пуста.")
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"❌ {f.id}. {f.question}", callback_data=f"del_faq:{f.id}")]
            for f in faqs
        ]
    )
    await callback.message.answer("Выберите вопрос для удаления:", reply_markup=kb)


@router.callback_query(F.data.startswith("del_faq:"))
async def confirm_delete(callback: CallbackQuery):
    faq_id = int(callback.data.split(":")[1])

    async with async_session_maker() as session:
        success = await faq_repo.delete_faq(session, faq_id)

    if success:
        await callback.message.answer(f"✅ Вопрос #{faq_id} удалён.")
    else:
        await callback.message.answer(f"⚠️ Вопрос #{faq_id} не найден.")

    await callback.answer()


# === Редактирование FAQ ===
@router.callback_query(F.data == "admin:edit")
async def admin_edit(callback: CallbackQuery):
    await callback.answer()

    async with async_session_maker() as session:
        faqs = await faq_repo.all_faqs(session)

    if not faqs:
        await callback.message.answer("📭 База FAQ пуста.")
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"✏ {f.id}. {f.question}", callback_data=f"edit_faq:{f.id}")]
            for f in faqs
        ]
    )
    await callback.message.answer("Выберите вопрос для редактирования:", reply_markup=kb)


@router.callback_query(F.data.startswith("edit_faq:"))
async def start_edit(callback: CallbackQuery, state: FSMContext):
    faq_id = int(callback.data.split(":")[1])
    await state.update_data(edit_faq_id=faq_id)

    await callback.message.answer("✍ Введите новый ответ для этого FAQ:")
    await state.set_state(EditFAQStates.waiting_for_new_answer)
    await callback.answer()


@router.message(EditFAQStates.waiting_for_new_answer, F.text)
async def save_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    faq_id = data.get("edit_faq_id")
    new_answer = message.text.strip()

    async with async_session_maker() as session:
        success = await faq_repo.update_faq(session, faq_id=faq_id, answer=new_answer)


    if success:
        await message.answer(f"✅ Ответ обновлён для FAQ #{faq_id}")
    else:
        await message.answer(f"⚠️ Вопрос #{faq_id} не найден.")
    await state.clear()


# === Непокрытые вопросы ===
@router.callback_query(F.data == "admin:unanswered")
async def admin_unanswered(callback: CallbackQuery):
    await callback.answer()

    async with async_session_maker() as session:
        questions = await unanswered_repo.get_recent_unanswered(session, limit=5)

    if not questions:
        await callback.message.answer("📭 Нет непросмотренных вопросов.")
        return

    text = "📝 Последние вопросы, не найденные в FAQ:\n\n"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"➕ Добавить в FAQ: {q.question_text[:30]}...", callback_data=f"add_from_unanswered:{q.id}")]
            for q in questions
        ]
    )
    for q in questions:
        text += f"❓ {q.question_text}\n"

    await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("add_from_unanswered:"))
async def add_from_unanswered(callback: CallbackQuery, state: FSMContext):
    q_id = int(callback.data.split(":")[1])

    async with async_session_maker() as session:
        questions = await unanswered_repo.get_recent_unanswered(session, limit=10)
        q = next((x for x in questions if x.id == q_id), None)

    if not q:
        await callback.message.answer("⚠️ Вопрос не найден.")
        return

    await state.update_data(new_question=q.question_text)
    await callback.message.answer(f"✍ Введите ответ для вопроса:\n\n❓ {q.question_text}")
    await state.set_state(AddFAQStates.waiting_for_answer)
    await callback.answer()

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.keyboards.admin_inline import admin_inline_kb
from app.config import ADMINS
from app.db import async_session_maker
from app.models import Admin

router = Router()


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


# === Заглушки для кнопок ===

@router.callback_query(F.data == "admin:add")
async def admin_add(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("➕ В разработке (добавление FAQ через 2 шага: вопрос → ответ).")


@router.callback_query(F.data == "admin:delete")
async def admin_delete(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🗑 В разработке (выбор FAQ для удаления).")


@router.callback_query(F.data == "admin:edit")
async def admin_edit(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("✏ В разработке (редактирование FAQ).")


@router.callback_query(F.data == "admin:unanswered")
async def admin_unanswered(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("📝 В разработке (показ последних N непросмотренных вопросов).")


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("📣 В разработке (рассылка).")

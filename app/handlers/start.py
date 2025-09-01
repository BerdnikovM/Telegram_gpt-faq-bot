from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.reply import main_menu_kb
from app.db import async_session_maker
from app.models import User
from sqlalchemy import select
from datetime import datetime, UTC

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_tg_id = message.from_user.id

    # Проверяем, есть ли пользователь в БД
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.tg_id == user_tg_id))
        user = result.scalar_one_or_none()

        if not user:
            # Если нет — создаём нового
            user = User(
                tg_id=user_tg_id,
                created_at=datetime.now(UTC)
            )
            session.add(user)
            await session.commit()

    # Отправляем приветствие
    text = (
        "👋 Привет! Я бот поддержки.\n\n"
        "Вы можете:\n"
        "📋 Посмотреть список часто задаваемых вопросов\n"
        "❓ Задать свой вопрос\n"
        "ℹ️ Узнать информацию о сервисе\n\n"
        "Выберите действие в меню 👇"
    )

    await message.answer(text, reply_markup=main_menu_kb())

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb() -> ReplyKeyboardMarkup:
    """
    Главное меню с 3 кнопками:
    📋 FAQ | ❓ Задать вопрос | ℹ️ О сервисе
    """
    keyboard = [
        [KeyboardButton(text="📋 FAQ")],
        [KeyboardButton(text="❓ Задать вопрос")],
        [KeyboardButton(text="ℹ️ О сервисе")],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,   # подгоняем под экран
        is_persistent=True      # закрепляем снизу
    )

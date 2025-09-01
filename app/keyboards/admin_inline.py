from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_inline_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="➕ Добавить FAQ", callback_data="admin:add"),
            InlineKeyboardButton(text="🗑 Удалить FAQ", callback_data="admin:delete"),
        ],
        [
            InlineKeyboardButton(text="✏ Редактировать", callback_data="admin:edit"),
            InlineKeyboardButton(text="📝 Непокрытые вопросы", callback_data="admin:unanswered"),
        ],
        [
            InlineKeyboardButton(text="📣 Рассылка", callback_data="admin:broadcast"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

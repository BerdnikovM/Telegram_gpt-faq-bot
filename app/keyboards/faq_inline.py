from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Sequence
from app.models import FAQEntry


def faq_list_kb(faq_items: Sequence[FAQEntry]) -> InlineKeyboardMarkup:
    """
    Строит inline-клавиатуру из списка FAQEntry.
    Каждая кнопка = вопрос, callback_data = faq:{id}.
    """
    keyboard = []
    for faq in faq_items:
        keyboard.append([
            InlineKeyboardButton(
                text=faq.question,
                callback_data=f"faq:{faq.id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

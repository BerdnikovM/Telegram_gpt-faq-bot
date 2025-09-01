from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Sequence


def faq_list_kb(faq_items: Sequence[tuple[int, str]]) -> InlineKeyboardMarkup:
    """
    Генерация Inline-клавиатуры для списка FAQ.
    faq_items — список кортежей (id, question).

    Пример:
    [(1, "Как сделать заказ?"), (2, "Какие способы оплаты?"), ...]
    """
    buttons = []

    # делаем по 2 кнопки в ряд (можно менять)
    row = []
    for idx, (faq_id, question) in enumerate(faq_items, start=1):
        row.append(InlineKeyboardButton(
            text=question,
            callback_data=f"faq:{faq_id}"
        ))
        if idx % 2 == 0:  # каждые 2 вопроса перенос строки
            buttons.append(row)
            row = []
    if row:  # добавляем хвост, если не делится на 2
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

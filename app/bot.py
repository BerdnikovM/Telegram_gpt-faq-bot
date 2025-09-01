import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.config import BOT_TOKEN
from app.handlers import start, faq, ask, admin

# Включаем логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    # Проверяем, что токен есть
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN не найден. Проверь .env файл")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(start.router)
    dp.include_router(faq.router)
    dp.include_router(ask.router)
    dp.include_router(admin.router)

    logger.info("🚀 Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# === Основные настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./db.sqlite3")

# === LLM провайдер ===
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")

# === Кэш и лимиты ===
CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "72"))
MAX_MSG_PER_MIN = int(os.getenv("MAX_MSG_PER_MIN", "10"))
TOP_N_FAQ = int(os.getenv("TOP_N_FAQ", "8"))

# === Админы ===
ADMINS = [int(x.strip()) for x in os.getenv("ADMINS", "").split(",") if x.strip()]

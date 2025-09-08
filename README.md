# 🤖 GPT-FAQ Bot (aiogram 3 + PostgreSQL + YandexGPT)

> **Telegram-бот для автоматических ответов на частые вопросы.**  
> Ищет ответ в базе знаний (FAQ), а если не находит — уточняет у пользователя или обращается к LLM (YandexGPT).  
> Подходит для e-commerce, сервисных компаний, онлайн-школ и техподдержки.

<p align="center">
  <img src="docs/example 1.gif" width="720">
  <img src="docs/example 2.gif" width="720">
</p>

[![Docker Pulls](https://img.shields.io/docker/pulls/mihailberd/gpt-faq-bot)](https://hub.docker.com/repository/docker/mihailberd/gpt-faq-bot/general)
[![License](https://img.shields.io/github/license/BerdnikovM/Telegram_gpt-faq-bot)](LICENSE)
---

## ✨ Ключевые фичи

| Фича | Описание |
|------|----------|
| **Асинхронный aiogram 3** | FSM, Router, CallbackQuery, Inline-кнопки |
| **Поиск по базе FAQ** | Exact-match + fuzzy-match (RapidFuzz) |
| **Уточнение вариантов** | Если есть несколько похожих вопросов — бот предлагает выбор |
| **Интеграция LLM** | Подключен **YandexGPT-Lite** с контекстом (топ-3 ближайших вопросов) |
| **Кэш ответов GPT** | SQL-таблица + TTL (72ч) для экономии запросов |
| **Лимиты запросов** | Ограничение частоты сообщений на пользователя |
| **Админ-панель** | Добавление, удаление, редактирование FAQ|
| **Тесты pytest** | Покрытие для репозиториев и поиска по FAQ |

---

## 🚀 Быстрый старт

> Требования: Python 3.12+, PostgreSQL, Telegram Bot API токен, API-ключ YandexGPT.

```bash
# 1. Клонируйте проект:
git clone https://github.com/BerdnikovM/Telegram_gpt-faq-bot.git
cd Telegram_gpt-faq-bot

# 2. Создайте виртуальное окружение и установите зависимости:
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# 3. Создайте файл .env (см. .env.example):
BOT_TOKEN=ваш_токен
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
YANDEX_API_KEY=ваш_api_ключ
YANDEX_CATALOG_ID=ваш_id_каталога
CACHE_TTL_HOURS=72
MAX_MSG_PER_MIN=10
ADMINS=123456789

# 4. Инициализируйте базу:
python -m app.init_db

# 5. Запустите бота:
python -m app.bot
```

Вариант 2: Docker-запуск

```
# 1. Склонируй репозиторий
git clone https://github.com/BerdnikovM/Telegram_gpt-faq-bot.git
cd Telegram_gpt-faq-bot

# 2. Создай .env
cp .env.example .env

# 3. Собери образ
docker build -t gpt-faq-bot:latest .

# 4. Запусти через docker-compose
docker compose up -d
```
---
## 🛠️ Стек и архитектура

| Слой            | Технологии                                 |
| --------------- | ------------------------------------------ |
| 🐍 Язык         | **Python 3.12**                            |
| 🤖 Telegram SDK | **aiogram 3** (Router, FSM, CallbackQuery) |
| 🗃️ ORM/БД      | **SQLAlchemy** + **PostgreSQL**            |
| 🔍 Поиск        | **RapidFuzz** (fuzzy-matching)             |
| 🧠 LLM          | **YandexGPT-Lite** API                     |
| 💾 Кэш          | Таблица cache с TTL                        |
| ⏰ Планировщик   | APScheduler (чистка кэша и лимитов)        |
| 🔐 Secrets      | ENV-переменные (.env: токен, база, ключи)  |
| 🧪 Тесты        | **pytest-asyncio**                         |
| ☁️ Деплой       | Docker / VPS / Timeweb Cloud               |
---
## 🤝 Связаться
|            | Контакт                                                                  |
| ---------- |--------------------------------------------------------------------------|
| ✉ Telegram | [@MihailBerd](https://t.me/MihailBerd)                                 |
| 💼 Kwork   | [https://kwork.ru/user/berdnikovmiha) |
| 📧 Email   | [MihailBerdWork@ya.ru](mailto:MihailBerdWork@ya.ru)                                |
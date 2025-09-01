from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.config import DATABASE_URL

# Создаём движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False,        # Можно включить True для логов SQL-запросов
    future=True
)

# Фабрика сессий
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Контекстный менеджер для работы с сессией
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# Функция инициализации моделей (создание таблиц)
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def reset_db():
    """Удаляет ВСЕ таблицы и создаёт заново (⚠️ все данные будут потеряны)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
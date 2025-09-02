from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, UTC, timedelta

from app.models import UsageLimit


async def check_and_increment(
    session: AsyncSession,
    user_id: int,
    max_per_minute: int
) -> bool:
    """
    Проверяет лимит запросов пользователя и увеличивает счетчик.
    Возвращает:
      True  — если лимит ещё не превышен (запрос разрешён),
      False — если лимит превышен.
    """

    now = datetime.now(UTC)
    window_start = now.replace(second=0, microsecond=0)  # начало текущей минуты

    # Ищем запись для пользователя в этом окне
    result = await session.execute(
        select(UsageLimit).where(
            UsageLimit.user_id == user_id,
            UsageLimit.window_start == window_start,
        )
    )
    record = result.scalar_one_or_none()

    if record:
        if record.count >= max_per_minute:
            return False
        record.count += 1
    else:
        # создаём новую запись для текущего окна
        record = UsageLimit(
            user_id=user_id,
            window_start=window_start,
            count=1,
        )
        session.add(record)

    await session.commit()
    return True


async def cleanup_old_limits(session: AsyncSession, keep_minutes: int = 5) -> int:
    """
    Удаляет старые записи из таблицы usage_limits (старше N минут).
    Возвращает количество удалённых записей.
    """
    cutoff = datetime.now(UTC) - timedelta(minutes=keep_minutes)
    result = await session.execute(
        delete(UsageLimit).where(UsageLimit.window_start < cutoff)
    )
    deleted = result.rowcount or 0
    await session.commit()
    return deleted

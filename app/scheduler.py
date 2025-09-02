import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

from app.db import async_session_maker
from app.repositories.limits_repo import cleanup_old_limits
from app.repositories.cache_repo import cleanup_expired_cache

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def job_cleanup_limits():
    async with async_session_maker() as session:
        deleted = await cleanup_old_limits(session, keep_minutes=5)
        if deleted:
            logger.info(f"[Scheduler] Удалено {deleted} старых записей из usage_limits в {datetime.now()}")


async def job_cleanup_cache():
    async with async_session_maker() as session:
        deleted = await cleanup_expired_cache(session)
        if deleted:
            logger.info(f"[Scheduler] Удалено {deleted} устаревших записей из gpt_cache в {datetime.now()}")


def setup_scheduler():
    # чистим лимиты каждые 30 минут
    scheduler.add_job(job_cleanup_limits, "interval", minutes=30)
    # чистим кэш раз в час
    scheduler.add_job(job_cleanup_cache, "interval", hours=1)
    scheduler.start()

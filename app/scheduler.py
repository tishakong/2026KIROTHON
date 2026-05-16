"""APScheduler — daily 18:00 notice crawl."""
from __future__ import annotations

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import settings
from .crawlers.sookmyung_notice import fetch_notices
from .routers.notices import upsert_notices

_scheduler: AsyncIOScheduler | None = None


async def _job() -> None:
    print("[scheduler] running daily notice crawl…")
    items = await fetch_notices()
    upsert_notices(items)
    print(f"[scheduler] notice crawl done — {len(items)} items")


def start() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
    _scheduler.add_job(
        _job,
        CronTrigger(
            hour=settings.NOTICE_CRAWL_HOUR,
            minute=settings.NOTICE_CRAWL_MINUTE,
        ),
        id="daily_notice_crawl",
        replace_existing=True,
    )
    _scheduler.start()
    print(
        f"[scheduler] started — notice crawl daily at "
        f"{settings.NOTICE_CRAWL_HOUR:02d}:{settings.NOTICE_CRAWL_MINUTE:02d} KST"
    )


def stop() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None

"""Crawler base interface.

Each university crawler should implement:
- async fetch_courses() -> list[dict]: catalog/curriculum scraping
- async fetch_periods() -> dict: { 'apply_start': date, 'apply_end': date,
                                    'documents': list[str], 'apply_url': str }

Until the user pastes real URLs/selectors, crawlers fall back to whatever
seed data is in db.MemoryStore.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx
from bs4 import BeautifulSoup


class BaseCrawler(ABC):
    university_id: str = ""
    name_ko: str = ""

    async def _get(self, url: str) -> BeautifulSoup:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as cx:
            r = await cx.get(url, headers={"User-Agent": "exchange-mvp/0.1"})
            r.raise_for_status()
            return BeautifulSoup(r.text, "lxml")

    @abstractmethod
    async def fetch_courses(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def fetch_periods(self) -> dict[str, Any]:
        ...

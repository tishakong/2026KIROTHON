"""Manual refresh of cached courses from each university crawler."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..crawlers.hongik import HongikCrawler
from ..crawlers.sogang import SogangCrawler
from ..crawlers.yonsei import YonseiCrawler
from ..db import get_client, memory

router = APIRouter(prefix="/api", tags=["courses"])

CRAWLERS = {
    "yonsei": YonseiCrawler(),
    "sogang": SogangCrawler(),
    "hongik": HongikCrawler(),
}


def _replace_courses(university_id: str, items: list[dict]) -> None:
    def _to_memory() -> None:
        memory.courses = [
            c for c in memory.courses if c.get("university_id") != university_id
        ]
        for it in items:
            memory.courses.append({"id": memory.next_id(), **it})

    sb = get_client()
    if sb is None:
        _to_memory()
        return
    try:
        sb.table("courses").delete().eq("university_id", university_id).execute()
        if items:
            sb.table("courses").insert(items).execute()
    except Exception as exc:
        # Fall back to memory so the app keeps working even if Supabase
        # creds are missing or the host is unreachable.
        print(
            f"[courses] supabase replace failed for {university_id}: {exc} "
            "— falling back to in-memory store"
        )
        _to_memory()


@router.post("/courses/refresh/{university_id}")
async def refresh_one(university_id: str):
    crawler = CRAWLERS.get(university_id)
    if crawler is None:
        raise HTTPException(404, f"unknown university: {university_id}")
    items = await crawler.fetch_courses()
    if items:
        _replace_courses(university_id, items)
    return {"university_id": university_id, "fetched": len(items)}


@router.post("/courses/refresh")
async def refresh_all():
    result = {}
    for uid, crawler in CRAWLERS.items():
        try:
            items = await crawler.fetch_courses()
            if items:
                _replace_courses(uid, items)
            result[uid] = len(items)
        except Exception as exc:
            print(f"[courses] {uid} crawl failed: {exc}")
            result[uid] = 0
    return result

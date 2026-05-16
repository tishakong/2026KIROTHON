from __future__ import annotations

from fastapi import APIRouter

from ..crawlers.sookmyung_notice import fetch_notices
from ..db import get_client, memory

router = APIRouter(prefix="/api", tags=["notices"])


def _from_memory(limit: int) -> list[dict]:
    return sorted(
        memory.notices,
        key=lambda x: x.get("posted_at", ""),
        reverse=True,
    )[:limit]


@router.get("/notices")
def notices(limit: int = 20):
    sb = get_client()
    if sb is None:
        return _from_memory(limit)
    try:
        res = (
            sb.table("notices")
            .select("*")
            .order("posted_at", desc=True)
            .limit(limit)
            .execute()
        )
        data = res.data or []
        if not data:
            return _from_memory(limit)
        return data
    except Exception as exc:
        print(f"[notices] supabase fetch failed: {exc} — using memory")
        return _from_memory(limit)


@router.post("/notices/refresh")
async def refresh_notices():
    """Manual trigger for the notice crawl (also runs daily at 18:00)."""
    items = await fetch_notices()
    upsert_notices(items)
    return {"fetched": len(items)}


def upsert_notices(items: list[dict]) -> None:
    if not items:
        return

    def _to_memory() -> None:
        existing = {(n["title"], n.get("url")) for n in memory.notices}
        for it in items:
            if (it["title"], it.get("url")) in existing:
                continue
            memory.notices.append({"id": memory.next_id(), **it})

    sb = get_client()
    if sb is None:
        _to_memory()
        return
    try:
        sb.table("notices").upsert(items, on_conflict="source,external_id").execute()
    except Exception as exc:
        print(f"[notices] supabase upsert failed: {exc} — using memory")
        _to_memory()

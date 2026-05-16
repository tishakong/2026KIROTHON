from __future__ import annotations

from fastapi import APIRouter

from ..db import get_client, memory

router = APIRouter(prefix="/api", tags=["history"])


def _from_memory(limit: int) -> list[dict]:
    return sorted(
        memory.search_history,
        key=lambda x: x.get("created_at", ""),
        reverse=True,
    )[:limit]


@router.get("/history")
def history(limit: int = 20):
    sb = get_client()
    if sb is None:
        return _from_memory(limit)
    try:
        res = (
            sb.table("search_history")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        data = res.data or []
        if not data:
            return _from_memory(limit)
        return data
    except Exception as exc:
        print(f"[history] supabase fetch failed: {exc} — using memory")
        return _from_memory(limit)

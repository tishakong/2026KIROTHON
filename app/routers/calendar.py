"""Calendar feed: only show universities the user can take courses at."""
from __future__ import annotations

from fastapi import APIRouter, Query

from ..db import get_client, memory
from ..services import matcher

router = APIRouter(prefix="/api", tags=["calendar"])


def _load_courses() -> list[dict]:
    sb = get_client()
    if sb is None:
        return list(memory.courses)
    try:
        data = (sb.table("courses").select("*").execute().data) or []
        if not data:
            return list(memory.courses)
        return data
    except Exception as exc:
        print(f"[calendar] supabase load failed: {exc} — using memory")
        return list(memory.courses)


def _load_universities() -> list[dict]:
    sb = get_client()
    if sb is None:
        return list(memory.universities)
    try:
        data = (sb.table("universities").select("*").execute().data) or []
        if not data:
            return list(memory.universities)
        return data
    except Exception as exc:
        print(f"[calendar] supabase load failed: {exc} — using memory")
        return list(memory.universities)


@router.get("/calendar")
def calendar(q: str | None = Query(default=None, description="강의명; 비어있으면 전체")):
    universities = _load_universities()

    if q:
        matches = matcher.rank(q, _load_courses())
        ids = {m.course.university_id for m in matches}
        universities = [u for u in universities if u["id"] in ids]

    events: list[dict] = []
    for u in universities:
        if u.get("apply_start") and u.get("apply_end"):
            events.append(
                {
                    "id": f"{u['id']}-apply",
                    "title": f"{u['name_ko']} 학점교류 신청",
                    "start": str(u["apply_start"]),
                    # FullCalendar treats `end` as exclusive, so +0 day is fine for display
                    "end": str(u["apply_end"]),
                    "url": u.get("apply_url") or "",
                    "extendedProps": {
                        "documents": u.get("documents", []),
                    },
                }
            )
    return events

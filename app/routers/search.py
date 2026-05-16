"""Search & matching API."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query

from ..db import get_client, memory
from ..schemas import SearchResult, UniversityApplyInfo
from ..services import course_lookup, matcher

router = APIRouter(prefix="/api", tags=["search"])


def _load_courses() -> list[dict]:
    sb = get_client()
    if sb is None:
        return list(memory.courses)
    try:
        res = sb.table("courses").select("*").execute()
        data = res.data or []
        if not data:
            return list(memory.courses)
        return data
    except Exception as exc:
        print(f"[search] supabase load failed: {exc} — using memory")
        return list(memory.courses)


def _load_universities() -> list[dict]:
    sb = get_client()
    if sb is None:
        return list(memory.universities)
    try:
        res = sb.table("universities").select("*").execute()
        data = res.data or []
        if not data:
            return list(memory.universities)
        return data
    except Exception as exc:
        print(f"[search] supabase load failed: {exc} — using memory")
        return list(memory.universities)


def _record_history(query: str, matched_count: int) -> None:
    payload = {"query": query, "matched_count": matched_count}

    def _to_memory() -> None:
        memory.search_history.append(
            {
                "id": memory.next_id(),
                "created_at": datetime.utcnow().isoformat(),
                **payload,
            }
        )

    sb = get_client()
    if sb is None:
        _to_memory()
        return
    try:
        sb.table("search_history").insert(payload).execute()
    except Exception as exc:
        print(f"[history] supabase insert failed: {exc} — using memory")
        _to_memory()


@router.get("/search", response_model=SearchResult)
async def search(q: str = Query(..., min_length=1, description="강의명")):
    courses = _load_courses()
    matches = matcher.rank(q, courses)

    # description 보강
    universities = {u["id"]: u for u in _load_universities()}
    for m in matches:
        if not m.course.description:
            uname = universities.get(m.course.university_id, {}).get(
                "name_ko", m.course.university_id
            )
            m.course.description = await course_lookup.search_description(
                uname, m.course.title
            )

    # 매칭된 대학들의 신청 기간/서류만 노출
    matched_univ_ids = {m.course.university_id for m in matches}
    apply_info = [
        UniversityApplyInfo(
            id=u["id"],
            name_ko=u["name_ko"],
            apply_start=u.get("apply_start"),
            apply_end=u.get("apply_end"),
            documents=u.get("documents", []) or [],
            apply_url=u.get("apply_url"),
        )
        for u in universities.values()
        if u["id"] in matched_univ_ids
    ]

    _record_history(q, len(matches))

    return SearchResult(query=q, matches=matches, apply_info=apply_info)


@router.get("/universities")
def list_universities():
    return _load_universities()

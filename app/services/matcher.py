"""Course matching: compare a target lecture name against cached courses
from other universities and return ranked candidates with reasons."""
from __future__ import annotations

from typing import Iterable

from rapidfuzz import fuzz

from ..schemas import Course, MatchedCourse


def _score(query: str, course: dict) -> float:
    title = course.get("title") or ""
    desc = course.get("description") or ""
    # Title match dominates, description nudges.
    title_score = fuzz.token_set_ratio(query, title)
    desc_score = fuzz.partial_ratio(query, desc) if desc else 0
    return round(title_score * 0.8 + desc_score * 0.2, 2)


def _reason(query: str, course: dict, score: float) -> str:
    title = course.get("title") or ""
    if score >= 85:
        return f"강의명이 '{query}'와 거의 일치 ({title})"
    if score >= 65:
        return f"강의명/설명에 '{query}' 관련 키워드가 충분히 겹침"
    return f"부분적으로 관련 (참고용)"


def rank(query: str, courses: Iterable[dict], top_k: int = 10,
         threshold: float = 50.0) -> list[MatchedCourse]:
    scored: list[tuple[float, dict]] = []
    for c in courses:
        s = _score(query, c)
        if s >= threshold:
            scored.append((s, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    out: list[MatchedCourse] = []
    for s, c in scored[:top_k]:
        out.append(
            MatchedCourse(
                course=Course(
                    university_id=c.get("university_id", ""),
                    department=c.get("department"),
                    code=c.get("code"),
                    title=c.get("title", ""),
                    description=c.get("description"),
                    credits=c.get("credits"),
                    source_url=c.get("source_url"),
                ),
                score=s,
                reason=_reason(query, c, s),
            )
        )
    return out

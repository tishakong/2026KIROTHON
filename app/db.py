"""Supabase client + in-memory fallback for local dev without credentials."""
from __future__ import annotations

from typing import Any, Optional

from .config import settings

_client = None


def get_client():
    """Return a supabase client, or None if credentials aren't set.

    Routes/services should handle the None case so the app still boots
    when Supabase isn't configured yet.
    """
    global _client
    if _client is not None:
        return _client
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None
    try:
        from supabase import create_client

        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        return _client
    except Exception as exc:  # pragma: no cover
        print(f"[db] supabase init failed: {exc}")
        return None


# ----- in-memory fallback store (used when supabase not configured) -----
class MemoryStore:
    def __init__(self) -> None:
        self.universities: list[dict[str, Any]] = []
        self.courses: list[dict[str, Any]] = []
        self.search_history: list[dict[str, Any]] = []
        self.notices: list[dict[str, Any]] = []
        self._auto = 1

    def next_id(self) -> int:
        self._auto += 1
        return self._auto


memory = MemoryStore()


def seed_if_empty() -> None:
    """Seed sample data so the UI is usable before crawlers are wired."""
    if memory.universities:
        return
    memory.universities.extend(
        [
            {
                "id": "yonsei",
                "name_ko": "연세대학교",
                "apply_url": "https://www.yonsei.ac.kr/",
                "notice_url": "",
                "documents": ["학점교류 신청서", "성적증명서", "재학증명서"],
                "apply_start": "2026-05-20",
                "apply_end": "2026-06-05",
            },
            {
                "id": "sogang",
                "name_ko": "서강대학교",
                "apply_url": "https://www.sogang.ac.kr/",
                "notice_url": "",
                "documents": ["학점교류 신청서", "지도교수 확인서"],
                "apply_start": "2026-05-25",
                "apply_end": "2026-06-10",
            },
            {
                "id": "hongik",
                "name_ko": "홍익대학교",
                "apply_url": "https://bizadmin.hongik.ac.kr/bizadmin/0301.do",
                "notice_url": "",
                "documents": ["학점교류 신청서", "성적증명서"],
                "apply_start": "2026-06-01",
                "apply_end": "2026-06-15",
            },
        ]
    )
    sample_courses = [
        ("yonsei", "컴퓨터과학과", "CSI2101", "이산수학",
         "집합, 논리, 그래프 이론 등 컴퓨터 과학을 위한 이산수학 기초", 3),
        ("yonsei", "경영학과", "BIZ2105", "마케팅원론",
         "마케팅의 기본 개념과 전략, 소비자 행동 분석", 3),
        ("sogang", "컴퓨터공학과", "CSE2030", "자료구조",
         "리스트, 트리, 그래프 등 자료구조와 알고리즘 분석", 3),
        ("sogang", "경제학과", "ECO2001", "미시경제학",
         "수요공급, 시장균형, 소비자/생산자 이론", 3),
        ("hongik", "경영학부", "033203", "기업과경영",
         "경영학 입문 강좌. 기업 이해와 경영 기본 개념 습득", 3),
        ("hongik", "경영학부", "BIZ2200", "마케팅원론",
         "마케팅 기본 개념과 전략, 시장 분석", 3),
    ]
    for uid, dept, code, title, desc, credits in sample_courses:
        memory.courses.append(
            {
                "id": memory.next_id(),
                "university_id": uid,
                "department": dept,
                "code": code,
                "title": title,
                "description": desc,
                "credits": credits,
                "source_url": "",
            }
        )

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel


class Course(BaseModel):
    university_id: str
    department: Optional[str] = None
    code: Optional[str] = None
    title: str
    description: Optional[str] = None
    credits: Optional[float] = None
    source_url: Optional[str] = None


class MatchedCourse(BaseModel):
    course: Course
    score: float
    reason: str


class UniversityApplyInfo(BaseModel):
    id: str
    name_ko: str
    apply_start: Optional[date] = None
    apply_end: Optional[date] = None
    documents: list[str] = []
    apply_url: Optional[str] = None


class SearchResult(BaseModel):
    query: str
    matches: list[MatchedCourse]
    apply_info: list[UniversityApplyInfo]


class HistoryItem(BaseModel):
    id: int
    query: str
    matched_count: int
    created_at: datetime


class Notice(BaseModel):
    id: int
    source: str
    title: str
    url: Optional[str] = None
    posted_at: Optional[date] = None
    summary: Optional[str] = None
    constraints: Optional[str] = None

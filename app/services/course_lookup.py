"""Fallback course-description lookup.

If a crawled course is missing a description, we try to fetch one here.
Right now this is a stub that returns a generic placeholder; swap in an
LLM call or a web-search call later.
"""
from __future__ import annotations


async def search_description(university: str, title: str) -> str:
    # TODO: hook up real web search / LLM here.
    return (
        f"[자동 보강] {university}의 '{title}' 강의 설명이 공식 페이지에 "
        f"없어 일반적인 강의 개요로 대체되었습니다. 강의계획서 확인 권장."
    )

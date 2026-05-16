"""Hongik University crawler.

Source page (Vue SPA):
  https://bizadmin.hongik.ac.kr/bizadmin/0301.do  (경영대학 > 경영학부 > 개설과목)

The HTML is just a shell. The page's JS (`app.dept.class.js`) calls a
JSON API that returns URL-encoded values:

  GET /sso/APICipher_temp.jsp
      ?data={"url":"/homepage/class_info.php",
              "url2":"&DEPT_CODE=",
              "url3":"<deptCd>"}

Each item has fields:
  NAME     과목명 (URL-encoded)
  HAKSU    학수번호
  GRADE    학년 (1..4)
  HAKGI    학기 (1..2)
  UNIT     학점
  SISU     시수
  ISU      이수구분 (전공선택 등, URL-encoded)
  SYLA     강의 설명 (URL-encoded HTML; '+' is used instead of spaces)
  NAME_EN/ISU_EN/SYLA_EN  English versions

Parsing follows the front-end JS exactly:
  unquote(value).replaceAll('+', ' ') and strip HTML tags from SYLA.
"""
from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import unquote

import httpx

from .base import BaseCrawler

API_URL = "https://bizadmin.hongik.ac.kr/sso/APICipher_temp.jsp"
PAGE_URL = "https://bizadmin.hongik.ac.kr/bizadmin/0301.do"
DEPT_CODE = "AAC130"  # 경영학부

_TAG_RE = re.compile(r"<\/?[^>]+(>|$)")


def _decode(value: str | None) -> str:
    if not value:
        return ""
    # Front-end does customDecodeUrl + replaceAll('+', ' ').
    # The values come from the API URL-encoded; '+' represents an actual
    # space in the original text, so substitute first then percent-decode.
    return unquote(value.replace("+", " "))


def _strip_html(value: str) -> str:
    return _TAG_RE.sub("", value).strip()


class HongikCrawler(BaseCrawler):
    university_id = "hongik"
    name_ko = "홍익대학교"

    CURRICULUM_URL = PAGE_URL
    DEPT_CODE = DEPT_CODE

    async def fetch_courses(self) -> list[dict[str, Any]]:
        params = {
            "data": json.dumps(
                {
                    "url": "/homepage/class_info.php",
                    "url2": "&DEPT_CODE=",
                    "url3": self.DEPT_CODE,
                }
            )
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (exchange-mvp/0.1)",
            "Referer": PAGE_URL,
            "Accept": "application/json,*/*;q=0.8",
        }
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as cx:
            r = await cx.get(API_URL, params=params, headers=headers)
            r.raise_for_status()
            payload = r.json()

        if payload.get("RESULT") == "ERROR":
            return []

        out: list[dict[str, Any]] = []
        for item in payload.get("DATA", []) or []:
            title = _decode(item.get("NAME"))
            if not title:
                continue
            description = _strip_html(_decode(item.get("SYLA")))
            isu = _decode(item.get("ISU"))
            grade = item.get("GRADE")
            hakgi = item.get("HAKGI")
            term = (
                f"{grade}학년/{hakgi}학기"
                if grade and hakgi
                else None
            )
            try:
                credits = float(item.get("UNIT")) if item.get("UNIT") else None
            except (TypeError, ValueError):
                credits = None

            out.append(
                {
                    "university_id": self.university_id,
                    "department": "경영학부",
                    "code": item.get("HAKSU"),
                    "title": title,
                    "description": description,
                    "credits": credits,
                    "source_url": PAGE_URL,
                    "raw": {
                        "isu": isu,
                        "term": term,
                        "sisu": item.get("SISU"),
                        "name_en": _decode(item.get("NAME_EN")),
                    },
                }
            )
        return out

    # 신청 기간/서류는 별도 페이지가 필요해 placeholder로 둠.
    PERIOD_URL = ""

    async def fetch_periods(self) -> dict[str, Any]:
        return {}

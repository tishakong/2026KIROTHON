"""Sogang University School of Business crawler.

Source page (UTF-8):
  https://sbs.sogang.ac.kr/sbs/1435/subview.do

Page structure — every course is rendered as a hidden detail layer:
  <div class="course_layer" id="course_MGT4306">
    <div class="course_layer_inner">
      <button class="course_close">×</button>
      <h3>MGT4306 금융리스크관리</h3>
      <p class="meta">(강의 3시간) 3학점</p>
      <p>선수과목 : MGT3004, MGT2002</p>   # optional
      <p>강의 설명...</p>
    </div>
  </div>

Parsing rules:
- code = id without the leading "course_"
- title = <h3> text with the leading code stripped
- credits = first integer/float before "학점" in <p class="meta">
- prerequisites = first <p> after meta if it starts with "선수과목"
- description = remaining <p> text joined together
"""
from __future__ import annotations

import re
from typing import Any

from .base import BaseCrawler

CREDIT_RE = re.compile(r"([\d.]+)\s*학점")


class SogangCrawler(BaseCrawler):
    university_id = "sogang"
    name_ko = "서강대학교"

    CURRICULUM_URL = "https://sbs.sogang.ac.kr/sbs/1435/subview.do"

    async def fetch_courses(self) -> list[dict[str, Any]]:
        soup = await self._get(self.CURRICULUM_URL)
        out: list[dict[str, Any]] = []
        for layer in soup.select("div.course_layer[id^='course_']"):
            code = layer.get("id", "")[len("course_"):].strip()
            if not code:
                continue

            inner = layer.select_one("div.course_layer_inner") or layer
            h3 = inner.find("h3")
            if not h3:
                continue
            head_text = h3.get_text(" ", strip=True)
            title = head_text
            if title.startswith(code):
                title = title[len(code):].strip()
            if not title:
                continue

            credits = None
            prereq = ""
            description_parts: list[str] = []
            for p in inner.find_all("p"):
                classes = p.get("class") or []
                text = p.get_text(" ", strip=True)
                if not text:
                    continue
                if "meta" in classes:
                    m = CREDIT_RE.search(text)
                    if m:
                        try:
                            credits = float(m.group(1))
                        except ValueError:
                            pass
                    continue
                if text.startswith("선수과목"):
                    # normalize "선수과목：..." or "선수과목 : ..."
                    prereq = re.sub(r"^선수과목\s*[:：]?\s*", "", text)
                    continue
                description_parts.append(text)

            description = " ".join(description_parts).strip()

            out.append(
                {
                    "university_id": self.university_id,
                    "department": "경영학부",
                    "code": code,
                    "title": title,
                    "description": description,
                    "credits": credits,
                    "source_url": self.CURRICULUM_URL,
                    "raw": {"prerequisites": prereq} if prereq else {},
                }
            )
        return out

    PERIOD_URL = ""

    async def fetch_periods(self) -> dict[str, Any]:
        return {}

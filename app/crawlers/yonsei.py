"""Yonsei University School of Business crawler.

Source page (EUC-KR encoded):
  https://ysb.yonsei.ac.kr/curriculum.asp?mid=m04_06

Page structure:
  <div class="icor_head"><a ...>전공명<i>...</i></a></div>
  <div class="icor_box">
    <table class="ContentsTableGray2">
      <thead><tr><th>학정번호</th><th>교과목</th>
                  <th>영문교과목</th><th>학점</th></tr></thead>
      <tbody>
        <tr>
          <td class="busnom">BIZ8043</td>
          <td class="busnom">계량마케팅세미나</td>
          <td class="busnom">QUANTITATIVE MARKETING SEMINAR</td>
          <td class="busnom">3</td>
        </tr>
        ...
      </tbody>
    </table>
  </div>

The icor_head before each icor_box gives the major (department) name.
"""
from __future__ import annotations

from typing import Any

import httpx
from bs4 import BeautifulSoup

from .base import BaseCrawler


class YonseiCrawler(BaseCrawler):
    university_id = "yonsei"
    name_ko = "연세대학교"

    CURRICULUM_URL = "https://ysb.yonsei.ac.kr/curriculum.asp?mid=m04_06"

    async def _fetch_html(self) -> str:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as cx:
            r = await cx.get(
                self.CURRICULUM_URL,
                headers={"User-Agent": "Mozilla/5.0 (exchange-mvp/0.1)"},
            )
            r.raise_for_status()
            # Page declares <meta charset="euc-kr"> but the server doesn't
            # send it in the response header, so httpx guesses utf-8 and
            # mojibakes the Korean text. Decode the raw bytes explicitly.
            return r.content.decode("euc-kr", errors="replace")

    async def fetch_courses(self) -> list[dict[str, Any]]:
        html = await self._fetch_html()
        soup = BeautifulSoup(html, "lxml")

        out: list[dict[str, Any]] = []
        for box in soup.select("div.icor_box"):
            major = self._major_for(box)
            table = box.find("table")
            if table is None:
                continue
            tbody = table.find("tbody")
            rows = tbody.find_all("tr") if tbody else []
            for tr in rows:
                cols = [
                    c.get_text(" ", strip=True)
                    for c in tr.find_all("td", class_="busnom")
                ]
                if len(cols) < 4:
                    continue
                code, title_ko, title_en, credit_str = cols[:4]
                if not (code and title_ko):
                    continue
                try:
                    credits = float(credit_str.replace(",", "."))
                except ValueError:
                    credits = None

                out.append(
                    {
                        "university_id": self.university_id,
                        "department": major or "경영대학",
                        "code": code,
                        "title": title_ko,
                        # Description isn't published on this page.
                        # course_lookup.search_description will backfill it
                        # in the search route when needed.
                        "description": "",
                        "credits": credits,
                        "source_url": self.CURRICULUM_URL,
                        "raw": {"title_en": title_en, "major": major},
                    }
                )
        return out

    @staticmethod
    def _major_for(box) -> str:
        """Find the major label in the closest preceding icor_head sibling."""
        sib = box.find_previous_sibling()
        while sib is not None:
            classes = sib.get("class") or []
            if "icor_head" in classes:
                a = sib.find("a")
                if a:
                    # Strip the trailing <i> icon text.
                    for i in a.find_all("i"):
                        i.extract()
                    return a.get_text(strip=True)
                return sib.get_text(strip=True)
            sib = sib.find_previous_sibling()
        return ""

    PERIOD_URL = ""

    async def fetch_periods(self) -> dict[str, Any]:
        return {}

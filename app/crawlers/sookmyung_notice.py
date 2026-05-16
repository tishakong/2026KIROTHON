"""Sookmyung notice crawler.

The user supplied the notice URL:
  https://www.sookmyung.ac.kr/kr/university-life/nformation07-popup.do

The exact list-page selector structure varies across Sookmyung's CMS, so
this crawler uses a defensive parse:
- Look for anchor tags inside list rows.
- Title comes from the anchor text; URL is rebuilt as absolute.
- A short summary is taken from the surrounding row text.

When the user pastes the precise table structure, swap the `_parse_list`
implementation below with targeted selectors.
"""
from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from ..config import settings


def _summarize(text: str, max_len: int = 180) -> str:
    text = " ".join(text.split())
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def _extract_constraints(text: str) -> str:
    keywords = ["제한", "불가", "마감", "기간", "필수", "유의", "주의"]
    found = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if any(k in s for k in keywords):
            found.append(s)
    return " | ".join(found[:5])


def _parse_list(html: str, base_url: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    items: list[dict[str, Any]] = []

    # Heuristic: look at every anchor that points at a board view URL.
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        title = a.get_text(strip=True)
        if not title or len(title) < 4:
            continue
        if "javascript" in href.lower() and "view" not in href.lower():
            # often Sookmyung uses fnView('123') style; keep id only
            ext_id = "".join(ch for ch in href if ch.isdigit()) or None
            url = base_url
        else:
            ext_id = None
            url = urljoin(base_url, href)

        row = a.find_parent(["tr", "li", "div"])
        row_text = row.get_text(" ", strip=True) if row else title
        items.append(
            {
                "source": "sookmyung",
                "external_id": ext_id,
                "title": title,
                "url": url,
                "summary": _summarize(row_text),
                "constraints": _extract_constraints(row_text),
                "posted_at": date.today().isoformat(),
            }
        )

    # de-dupe on (title, url)
    seen = set()
    deduped: list[dict[str, Any]] = []
    for n in items:
        key = (n["title"], n["url"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(n)
    return deduped


async def fetch_notices() -> list[dict[str, Any]]:
    url = settings.SOOKMYUNG_NOTICE_URL
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as cx:
            r = await cx.get(url, headers={"User-Agent": "exchange-mvp/0.1"})
            r.raise_for_status()
            return _parse_list(r.text, url)
    except Exception as exc:
        print(f"[notice] fetch failed: {exc}")
        return []

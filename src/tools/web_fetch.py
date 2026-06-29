"""Fetch a URL and extract clean, readable main text."""
from __future__ import annotations

import httpx

import config

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def fetch_url(url: str, max_chars: int | None = None) -> str:
    """Return cleaned main text of a page, truncated to a budget. Never raises."""
    if not url:
        return ""
    limit = max_chars or config.MAX_PAGE_CHARS
    try:
        with httpx.Client(timeout=15, follow_redirects=True, headers=_HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception:
        return ""

    text = ""
    try:
        import trafilatura

        text = trafilatura.extract(html) or ""
    except Exception:
        text = ""

    if not text:
        # Fallback: crude tag strip.
        import re

        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)

    return text[:limit].strip()

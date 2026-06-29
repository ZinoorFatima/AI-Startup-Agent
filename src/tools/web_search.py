"""Web search. Free DuckDuckGo by default; Tavily when TAVILY_API_KEY is set."""
from __future__ import annotations

from dataclasses import dataclass

import config


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str

    def as_text(self) -> str:
        return f"{self.title}\n{self.url}\n{self.snippet}"


def _search_duckduckgo(query: str, max_results: int) -> list[SearchResult]:
    from ddgs import DDGS

    out: list[SearchResult] = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            out.append(
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", "") or r.get("url", ""),
                    snippet=r.get("body", ""),
                )
            )
    return out


def _search_tavily(query: str, max_results: int) -> list[SearchResult]:
    from tavily import TavilyClient

    client = TavilyClient(api_key=config.TAVILY_API_KEY)
    resp = client.search(query, max_results=max_results)
    return [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            snippet=r.get("content", ""),
        )
        for r in resp.get("results", [])
    ]


def search(query: str, max_results: int = 6) -> list[SearchResult]:
    """Run a web search with the configured backend. Never raises — returns []."""
    try:
        if config.SEARCH_BACKEND == "tavily":
            return _search_tavily(query, max_results)
        return _search_duckduckgo(query, max_results)
    except Exception:
        return []


def search_text(query: str, max_results: int = 6) -> str:
    """Convenience: search and join results into a single text block."""
    results = search(query, max_results)
    if not results:
        return "(no search results)"
    return "\n\n".join(r.as_text() for r in results)

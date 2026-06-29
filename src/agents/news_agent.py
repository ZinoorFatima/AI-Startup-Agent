"""News monitoring agent: launches, funding, layoffs, lawsuits, controversies, M&A."""
from __future__ import annotations

from src.llm import get_llm
from src.state import DueDiligenceState, NewsFindings
from src.tools.web_search import search

SYSTEM = """You are a due-diligence news monitor. From the search results, extract
notable, recent, factual events about the startup and categorize each as one of:
launch, funding, layoffs, lawsuit, controversy, acquisition, other. Include a URL
when available. Only report items supported by the results — if there is nothing
notable, return an empty list and say so in the summary."""


def news_node(state: DueDiligenceState) -> dict:
    name = state["startup_name"]

    queries = [
        f"{name} funding round raised",
        f"{name} news launch announcement",
        f"{name} lawsuit layoffs controversy acquisition",
    ]
    results = []
    for q in queries:
        results.extend(search(q, max_results=4))
    block = "\n\n".join(r.as_text() for r in results) or "(no search results)"

    prompt = f"""Startup: {name}

--- SEARCH RESULTS ---
{block}

Extract and categorize notable news."""

    try:
        llm = get_llm().with_structured_output(NewsFindings)
        findings: NewsFindings = llm.invoke([("system", SYSTEM), ("human", prompt)])
        return {"news": findings}
    except Exception as e:  # noqa: BLE001
        return {
            "news": NewsFindings(summary=f"News monitoring failed: {e}"),
            "errors": [f"news: {e}"],
        }

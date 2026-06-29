"""Research / Website agent: builds a structured CompanyProfile from the web."""
from __future__ import annotations

from src.llm import get_llm
from src.state import CompanyProfile, DueDiligenceState
from src.tools.web_fetch import fetch_url
from src.tools.web_search import search

SYSTEM = """You are a venture-capital research analyst. From the provided web search
results and website text, extract a factual profile of the startup. Only use the
supplied material. If something is not stated, return "unknown" — never invent
founders, customers, or pricing. Keep each field concise."""


def research_node(state: DueDiligenceState) -> dict:
    name = state["startup_name"]
    industry = state.get("industry", "")
    website = state.get("website", "")

    # Gather context: website text + general + team/founder searches.
    site_text = fetch_url(website) if website else ""
    queries = [
        f"{name} {industry} startup product pricing",
        f"{name} founders team leadership",
        f"{name} customers case studies",
    ]
    results = []
    for q in queries:
        results.extend(search(q, max_results=4))
    search_block = "\n\n".join(r.as_text() for r in results) or "(no search results)"
    sources = [r.url for r in results if r.url][:8]
    if website:
        sources = [website] + sources

    prompt = f"""Startup: {name}
Stated industry: {industry or 'unknown'}
Website: {website or 'unknown'}

--- WEBSITE TEXT ---
{site_text or '(none fetched)'}

--- WEB SEARCH RESULTS ---
{search_block}

Produce the structured company profile."""

    try:
        llm = get_llm().with_structured_output(CompanyProfile)
        profile: CompanyProfile = llm.invoke(
            [("system", SYSTEM), ("human", prompt)]
        )
        if not profile.sources:
            profile.sources = sources
        return {"profile": profile}
    except Exception as e:  # noqa: BLE001
        return {
            "profile": CompanyProfile(summary=f"Research failed: {e}", sources=sources),
            "errors": [f"research: {e}"],
        }

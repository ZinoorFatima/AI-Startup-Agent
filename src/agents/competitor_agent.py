"""Competitor agent: find rivals, build a comparison, identify advantages/gaps."""
from __future__ import annotations

from src.llm import get_llm
from src.state import CompetitorAnalysis, DueDiligenceState
from src.tools.web_search import search

SYSTEM = """You are a competitive-intelligence analyst. Using the search results,
identify 2-3 real competitors of the startup. Build a comparison (pricing, feature
breadth, customer base) and list the startup's competitive advantages and gaps.
Use "unknown" where the data is not present. Do not fabricate competitor names —
only use companies that appear in the results."""


def competitor_node(state: DueDiligenceState) -> dict:
    name = state["startup_name"]
    industry = state.get("industry", "")

    queries = [
        f"{name} competitors alternatives",
        f"best {industry} companies vs {name}",
        f"{name} comparison pricing features",
    ]
    results = []
    for q in queries:
        results.extend(search(q, max_results=4))
    block = "\n\n".join(r.as_text() for r in results) or "(no search results)"

    prompt = f"""Startup: {name}
Industry: {industry or 'unknown'}

--- SEARCH RESULTS ---
{block}

Produce the competitor analysis."""

    try:
        llm = get_llm().with_structured_output(CompetitorAnalysis)
        analysis: CompetitorAnalysis = llm.invoke(
            [("system", SYSTEM), ("human", prompt)]
        )
        return {"competitors": analysis}
    except Exception as e:  # noqa: BLE001
        return {
            "competitors": CompetitorAnalysis(summary=f"Competitor analysis failed: {e}"),
            "errors": [f"competitor: {e}"],
        }

"""Financial agent: deterministic math + LLM interpretation."""
from __future__ import annotations

from src.llm import get_llm
from src.state import DueDiligenceState, FinancialAnalysis

SYSTEM = """You are a startup financial analyst. You are given pre-computed metrics
and raw inputs. Write a concise, sober interpretation: comment on runway health,
growth quality, and unit economics (LTV/CAC). Do not invent numbers that were not
provided. Flag risks plainly."""


def _compute(financials: dict) -> tuple[dict, list[str]]:
    """Return (metrics, missing_inputs). Pure Python, no LLM."""
    missing: list[str] = []
    metrics: dict = {}

    cash = financials.get("cash_on_hand")
    burn = financials.get("burn_rate")
    if cash and burn:
        metrics["runway_months"] = round(cash / burn, 1)
    else:
        if not cash:
            missing.append("cash_on_hand")
        if not burn:
            missing.append("burn_rate")

    cac = financials.get("cac")
    ltv = financials.get("ltv")
    if cac and ltv:
        metrics["ltv_cac_ratio"] = round(ltv / cac, 2)
    else:
        if not ltv:
            missing.append("ltv")
        if not cac:
            missing.append("cac")

    arr = financials.get("arr")
    if arr and burn:
        annual_burn = burn * 12
        if annual_burn:
            metrics["revenue_efficiency"] = f"{round(arr / annual_burn, 2)} ARR per $1 annual burn"
    elif not arr:
        missing.append("arr")

    return metrics, missing


def financial_node(state: DueDiligenceState) -> dict:
    financials = dict(state.get("financials") or {})
    metrics, missing = _compute(financials)

    prompt = f"""Startup: {state['startup_name']} (stage: {state.get('stage', 'unknown')})
Raw inputs provided: {financials or '(none)'}
Computed metrics: {metrics or '(none — insufficient inputs)'}
Missing inputs: {missing or '(none)'}

Write the interpretation."""

    interpretation = ""
    try:
        llm = get_llm()
        interpretation = llm.invoke([("system", SYSTEM), ("human", prompt)]).content
    except Exception as e:  # noqa: BLE001
        interpretation = f"(LLM interpretation unavailable: {e})"

    growth = financials.get("growth_rate")  # may be absent; UI doesn't collect it directly
    analysis = FinancialAnalysis(
        runway_months=metrics.get("runway_months"),
        growth_rate=growth,
        ltv_cac_ratio=metrics.get("ltv_cac_ratio"),
        revenue_efficiency=metrics.get("revenue_efficiency"),
        interpretation=interpretation,
        missing_inputs=missing,
    )
    return {"financial": analysis}

"""Risk assessment agent: synthesizes upstream findings into 4 risk dimensions."""
from __future__ import annotations

from src.llm import get_llm
from src.state import DueDiligenceState, RiskAssessment, RiskDimension
import config

SYSTEM = """You are a VC risk officer. Given research, financial, competitor, and news
findings, assess four risk dimensions — market, financial, execution, founder — each
as Low / Medium / High with a one-to-two sentence rationale grounded in the evidence.
Be balanced and specific. Where evidence is thin, say so and lean toward Medium."""


def _fallback() -> RiskAssessment:
    unknown = RiskDimension(level="Medium", rationale="Insufficient evidence to assess.")
    return RiskAssessment(
        market_risk=unknown,
        financial_risk=unknown,
        execution_risk=unknown,
        founder_risk=unknown,
        summary="Risk assessment defaulted due to limited data.",
    )


def risk_node(state: DueDiligenceState) -> dict:
    profile = state.get("profile")
    financial = state.get("financial")
    competitors = state.get("competitors")
    news = state.get("news")

    prompt = f"""Startup: {state['startup_name']} | Stage: {state.get('stage', 'unknown')} | Industry: {state.get('industry', 'unknown')}

COMPANY PROFILE:
{profile.model_dump() if profile else '(none)'}

FINANCIAL ANALYSIS:
{financial.model_dump() if financial else '(none)'}

COMPETITORS:
{competitors.model_dump() if competitors else '(none)'}

NEWS:
{news.model_dump() if news else '(none)'}

Assess the four risk dimensions."""

    try:
        llm = get_llm(config.PRO_MODEL).with_structured_output(RiskAssessment)
        assessment: RiskAssessment = llm.invoke(
            [("system", SYSTEM), ("human", prompt)]
        )
        return {"risk": assessment}
    except Exception as e:  # noqa: BLE001
        return {
            "risk": _fallback(),
            "errors": [f"risk: {e}"],
        }

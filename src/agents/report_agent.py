"""Investment report agent: final score, strengths, weaknesses, recommendation."""
from __future__ import annotations

from src.llm import get_llm
from src.state import DueDiligenceState, InvestmentReport
import config

SYSTEM = """You are a VC partner writing the final investment memo. Synthesize all
findings into: an investment score 0-100, a list of concrete strengths, a list of
concrete weaknesses, a clear recommendation (e.g. 'Proceed to partner review',
'Request more data', 'Pass'), and a short rationale. Be decisive and evidence-based.
The score should reflect the risk assessment and the stage/check size."""


def report_node(state: DueDiligenceState) -> dict:
    prompt = f"""Investment under consideration:
Startup: {state['startup_name']}
Proposed amount: ${state.get('investment_amount', 0):,.0f}
Stage: {state.get('stage', 'unknown')} | Industry: {state.get('industry', 'unknown')}

PROFILE: {state.get('profile').model_dump() if state.get('profile') else '(none)'}
FINANCIAL: {state.get('financial').model_dump() if state.get('financial') else '(none)'}
COMPETITORS: {state.get('competitors').model_dump() if state.get('competitors') else '(none)'}
NEWS: {state.get('news').model_dump() if state.get('news') else '(none)'}
RISK: {state.get('risk').model_dump() if state.get('risk') else '(none)'}

Write the final investment report."""

    try:
        llm = get_llm(config.PRO_MODEL, temperature=0.3).with_structured_output(InvestmentReport)
        report: InvestmentReport = llm.invoke([("system", SYSTEM), ("human", prompt)])
        report.score = max(0, min(100, int(report.score)))
        return {"report": report}
    except Exception as e:  # noqa: BLE001
        return {
            "report": InvestmentReport(
                score=0,
                recommendation="Inconclusive",
                rationale=f"Report generation failed: {e}",
            ),
            "errors": [f"report: {e}"],
        }

"""LangGraph coordinator: fans out 4 research agents, converges to risk, then report.

    START ─┬─> research ──┐
           ├─> financial ─┤
           ├─> competitor ┼─> risk ─> report ─> END
           └─> news ──────┘
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from src.agents.competitor_agent import competitor_node
from src.agents.financial_agent import financial_node
from src.agents.news_agent import news_node
from src.agents.report_agent import report_node
from src.agents.research_agent import research_node
from src.agents.risk_agent import risk_node
from src.state import DueDiligenceState

# Node names, also used as the labels shown in the Streamlit progress UI.
RESEARCH = "research"
FINANCIAL = "financial"
COMPETITOR = "competitor"
NEWS = "news"
RISK = "risk"
REPORT = "report"

PARALLEL_NODES = [RESEARCH, FINANCIAL, COMPETITOR, NEWS]


def build_graph():
    g = StateGraph(DueDiligenceState)

    g.add_node(RESEARCH, research_node)
    g.add_node(FINANCIAL, financial_node)
    g.add_node(COMPETITOR, competitor_node)
    g.add_node(NEWS, news_node)
    g.add_node(RISK, risk_node)
    g.add_node(REPORT, report_node)

    # Fan out: all four research agents start in parallel.
    for node in PARALLEL_NODES:
        g.add_edge(START, node)
        # Converge: each must finish before risk runs.
        g.add_edge(node, RISK)

    g.add_edge(RISK, REPORT)
    g.add_edge(REPORT, END)

    return g.compile()


# Compiled app reused by the UI and tests.
app = build_graph()

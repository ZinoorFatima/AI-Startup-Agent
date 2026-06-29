"""Streamlit UI for the AI Startup Due-Diligence Agent."""
from __future__ import annotations

import json

import streamlit as st

import config
from src.graph import app as graph_app
from src.state import DueDiligenceState

st.set_page_config(page_title="AI Due-Diligence Agent", page_icon="📊", layout="wide")

NODE_LABELS = {
    "research": "🔎 Research agent",
    "financial": "💵 Financial agent",
    "competitor": "⚔️ Competitor agent",
    "news": "📰 News agent",
    "risk": "⚠️ Risk assessment",
    "report": "📝 Investment report",
}


# --- Report rendering -------------------------------------------------------

def _score_color(score: int) -> str:
    if score >= 75:
        return "#1a7f37"
    if score >= 50:
        return "#9a6700"
    return "#cf222e"


def _risk_badge(level: str) -> str:
    colors = {"Low": "#1a7f37", "Medium": "#9a6700", "High": "#cf222e"}
    c = colors.get(level, "#57606a")
    return f"<span style='background:{c};color:white;padding:2px 10px;border-radius:12px;font-size:0.85em'>{level}</span>"


def render_report(state: dict) -> None:
    report = state.get("report")
    risk = state.get("risk")
    profile = state.get("profile")
    financial = state.get("financial")
    competitors = state.get("competitors")
    news = state.get("news")

    if report:
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(
                f"<div style='text-align:center'>"
                f"<div style='font-size:3.5em;font-weight:700;color:{_score_color(report.score)}'>{report.score}</div>"
                f"<div style='color:#57606a'>Investment Score / 100</div></div>",
                unsafe_allow_html=True,
            )
        with c2:
            st.subheader("Recommendation")
            st.success(report.recommendation)
            if report.rationale:
                st.caption(report.rationale)

        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("**Strengths**")
            for s in report.strengths:
                st.markdown(f"- {s}")
        with sc2:
            st.markdown("**Weaknesses**")
            for w in report.weaknesses:
                st.markdown(f"- {w}")

    if risk:
        st.divider()
        st.subheader("Risk Assessment")
        cols = st.columns(4)
        dims = [
            ("Market", risk.market_risk),
            ("Financial", risk.financial_risk),
            ("Execution", risk.execution_risk),
            ("Founder", risk.founder_risk),
        ]
        for col, (label, dim) in zip(cols, dims):
            with col:
                st.markdown(f"**{label}**<br>{_risk_badge(dim.level)}", unsafe_allow_html=True)
                st.caption(dim.rationale)

    if financial:
        st.divider()
        st.subheader("Financial Analysis")
        m1, m2, m3 = st.columns(3)
        m1.metric("Runway (months)", financial.runway_months if financial.runway_months is not None else "—")
        m2.metric("LTV / CAC", financial.ltv_cac_ratio if financial.ltv_cac_ratio is not None else "—")
        m3.metric("Growth", financial.growth_rate or "—")
        if financial.revenue_efficiency:
            st.caption(f"Revenue efficiency: {financial.revenue_efficiency}")
        if financial.interpretation:
            st.write(financial.interpretation)
        if financial.missing_inputs:
            st.warning("Missing inputs: " + ", ".join(financial.missing_inputs))

    if competitors and competitors.competitors:
        st.divider()
        st.subheader("Competitor Landscape")
        st.table(
            [
                {
                    "Competitor": c.name,
                    "Pricing": c.pricing,
                    "Features": c.features,
                    "Customers": c.customers,
                }
                for c in competitors.competitors
            ]
        )
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("**Advantages**")
            for a in competitors.advantages:
                st.markdown(f"- {a}")
        with cc2:
            st.markdown("**Gaps**")
            for g in competitors.gaps:
                st.markdown(f"- {g}")

    if news and news.items:
        st.divider()
        st.subheader("News Monitoring")
        for item in news.items:
            line = f"**[{item.category}]** {item.headline}"
            if item.url:
                line += f" — [link]({item.url})"
            st.markdown(line)
            if item.detail:
                st.caption(item.detail)
    elif news:
        st.caption(f"News: {news.summary or 'nothing notable found.'}")

    if profile:
        with st.expander("Company profile (raw research)"):
            st.json(profile.model_dump())

    if state.get("errors"):
        with st.expander("⚠️ Agent diagnostics"):
            for err in state["errors"]:
                st.text(err)


def report_to_markdown(state: dict) -> str:
    report = state.get("report")
    risk = state.get("risk")
    lines = [f"# Due-Diligence Report: {state.get('startup_name', '')}", ""]
    if report:
        lines += [
            f"**Investment Score:** {report.score}/100",
            f"**Recommendation:** {report.recommendation}",
            "",
            report.rationale,
            "",
            "## Strengths",
            *[f"- {s}" for s in report.strengths],
            "",
            "## Weaknesses",
            *[f"- {w}" for w in report.weaknesses],
            "",
        ]
    if risk:
        lines += [
            "## Risk Assessment",
            f"- Market: {risk.market_risk.level} — {risk.market_risk.rationale}",
            f"- Financial: {risk.financial_risk.level} — {risk.financial_risk.rationale}",
            f"- Execution: {risk.execution_risk.level} — {risk.execution_risk.rationale}",
            f"- Founder: {risk.founder_risk.level} — {risk.founder_risk.rationale}",
            "",
        ]
    return "\n".join(lines)


def state_to_json(state: dict) -> str:
    out = {}
    for k, v in state.items():
        out[k] = v.model_dump() if hasattr(v, "model_dump") else v
    return json.dumps(out, indent=2, default=str)


# --- Sidebar / inputs -------------------------------------------------------

st.title("📊 AI Startup Due-Diligence Agent")
st.caption("Multi-agent pipeline · LangGraph · Gemini · live web research")

if not config.GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is not set. Add it to your .env file and restart.")
    st.stop()

with st.form("dd"):
    c1, c2 = st.columns(2)
    with c1:
        startup_name = st.text_input("Startup name *", placeholder="AcmeAI")
        industry = st.text_input("Industry", placeholder="AI SaaS")
        website = st.text_input("Website URL", placeholder="https://acme.ai")
    with c2:
        investment_amount = st.number_input("Investment amount ($)", min_value=0, value=250_000, step=50_000)
        stage = st.selectbox("Stage", ["Pre-seed", "Seed", "Series A", "Series B", "Growth"], index=1)

    with st.expander("Optional financials (web won't have these — enter what you know)"):
        f1, f2, f3 = st.columns(3)
        with f1:
            revenue = st.number_input("Revenue ($/yr)", min_value=0, value=0, step=10_000)
            arr = st.number_input("ARR ($)", min_value=0, value=0, step=10_000)
            cash_on_hand = st.number_input("Cash on hand ($)", min_value=0, value=0, step=10_000)
        with f2:
            burn_rate = st.number_input("Monthly burn ($)", min_value=0, value=0, step=5_000)
            cac = st.number_input("CAC ($)", min_value=0, value=0, step=100)
        with f3:
            ltv = st.number_input("LTV ($)", min_value=0, value=0, step=100)
            funding_history = st.text_input("Funding history", placeholder="$1.5M pre-seed (2024)")

    submitted = st.form_submit_button("Run due diligence", type="primary")

if submitted:
    if not startup_name.strip():
        st.error("Startup name is required.")
        st.stop()

    financials = {
        k: v
        for k, v in {
            "revenue": revenue,
            "burn_rate": burn_rate,
            "arr": arr,
            "cac": cac,
            "ltv": ltv,
            "cash_on_hand": cash_on_hand,
            "funding_history": funding_history.strip(),
        }.items()
        if v
    }

    initial: DueDiligenceState = {
        "startup_name": startup_name.strip(),
        "investment_amount": float(investment_amount),
        "stage": stage,
        "industry": industry.strip(),
        "website": website.strip(),
        "financials": financials,
        "errors": [],
    }

    st.divider()
    progress_area = st.container()
    final_state: dict = dict(initial)
    done: set[str] = set()

    with progress_area:
        status = st.status("Running multi-agent pipeline…", expanded=True)
        try:
            for chunk in graph_app.stream(initial, stream_mode="updates"):
                for node, update in chunk.items():
                    if node in NODE_LABELS and node not in done:
                        done.add(node)
                        status.write(f"✅ {NODE_LABELS[node]} complete")
                    if isinstance(update, dict):
                        final_state.update(update)
            status.update(label="Pipeline complete", state="complete", expanded=False)
        except Exception as e:  # noqa: BLE001
            status.update(label=f"Pipeline error: {e}", state="error")
            st.exception(e)
            st.stop()

    st.divider()
    render_report(final_state)

    st.divider()
    d1, d2 = st.columns(2)
    d1.download_button(
        "⬇️ Download report (Markdown)",
        report_to_markdown(final_state),
        file_name=f"{startup_name.strip().replace(' ', '_')}_dd_report.md",
        mime="text/markdown",
    )
    d2.download_button(
        "⬇️ Download raw data (JSON)",
        state_to_json(final_state),
        file_name=f"{startup_name.strip().replace(' ', '_')}_dd_data.json",
        mime="application/json",
    )

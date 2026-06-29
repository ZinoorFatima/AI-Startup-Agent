"""Smoke tests that don't require network or API keys."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.financial_agent import _compute


def test_runway_and_ltv_cac():
    metrics, missing = _compute(
        {"cash_on_hand": 1_400_000, "burn_rate": 100_000, "ltv": 3000, "cac": 1000, "arr": 800_000}
    )
    assert metrics["runway_months"] == 14.0
    assert metrics["ltv_cac_ratio"] == 3.0
    assert "ARR per $1 annual burn" in metrics["revenue_efficiency"]
    assert missing == []


def test_missing_inputs_flagged():
    metrics, missing = _compute({"arr": 500_000})
    assert "cash_on_hand" in missing
    assert "burn_rate" in missing
    assert "cac" in missing and "ltv" in missing
    assert "runway_months" not in metrics


def test_graph_compiles():
    # Importing builds and compiles the StateGraph.
    from src.graph import app, PARALLEL_NODES

    assert app is not None
    assert len(PARALLEL_NODES) == 4

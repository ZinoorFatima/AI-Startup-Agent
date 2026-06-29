"""Shared graph state and structured output models."""
from __future__ import annotations

import operator
from typing import Annotated, Optional, TypedDict

from pydantic import BaseModel, Field


# --- Structured outputs produced by each agent -----------------------------

class CompanyProfile(BaseModel):
    product: str = Field("unknown", description="What the company sells / does.")
    industry: str = Field("unknown", description="Industry / category.")
    founders: str = Field("unknown", description="Founders and notable background.")
    customers: str = Field("unknown", description="Target customers / notable logos.")
    pricing: str = Field("unknown", description="Pricing model and price points.")
    market: str = Field("unknown", description="Market size / positioning.")
    summary: str = Field("", description="2-3 sentence narrative summary.")
    sources: list[str] = Field(default_factory=list, description="URLs used.")


class FinancialAnalysis(BaseModel):
    runway_months: Optional[float] = Field(None, description="Cash / monthly burn.")
    growth_rate: Optional[str] = Field(None, description="e.g. '18% MoM' or unknown.")
    ltv_cac_ratio: Optional[float] = Field(None, description="LTV / CAC.")
    revenue_efficiency: Optional[str] = Field(None, description="ARR per $ burned, etc.")
    interpretation: str = Field("", description="Narrative reading of the numbers.")
    missing_inputs: list[str] = Field(default_factory=list)


class CompetitorRow(BaseModel):
    name: str
    pricing: str = "unknown"
    features: str = "unknown"
    customers: str = "unknown"
    notes: str = ""


class CompetitorAnalysis(BaseModel):
    competitors: list[CompetitorRow] = Field(default_factory=list)
    advantages: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    summary: str = ""


class NewsItem(BaseModel):
    category: str = Field(description="launch | funding | layoffs | lawsuit | controversy | acquisition | other")
    headline: str
    detail: str = ""
    url: str = ""


class NewsFindings(BaseModel):
    items: list[NewsItem] = Field(default_factory=list)
    summary: str = ""


class RiskDimension(BaseModel):
    level: str = Field(description="Low | Medium | High")
    rationale: str = ""


class RiskAssessment(BaseModel):
    market_risk: RiskDimension
    financial_risk: RiskDimension
    execution_risk: RiskDimension
    founder_risk: RiskDimension
    summary: str = ""


class InvestmentReport(BaseModel):
    score: int = Field(description="Investment score 0-100.")
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendation: str = Field(description="e.g. 'Proceed to partner review', 'Pass'.")
    rationale: str = ""


# --- Graph state ------------------------------------------------------------

class Financials(TypedDict, total=False):
    revenue: float
    burn_rate: float          # monthly
    arr: float
    cac: float
    ltv: float
    cash_on_hand: float
    funding_history: str


class DueDiligenceState(TypedDict, total=False):
    # Inputs
    startup_name: str
    investment_amount: float
    stage: str
    industry: str
    website: str
    financials: Financials

    # Agent outputs
    profile: CompanyProfile
    financial: FinancialAnalysis
    competitors: CompetitorAnalysis
    news: NewsFindings
    risk: RiskAssessment
    report: InvestmentReport

    # Diagnostics — reducer merges concurrent updates from parallel agents.
    errors: Annotated[list[str], operator.add]

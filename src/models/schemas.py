from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class MetricAnalysisRequest(BaseModel):
    merchant_mid: str = Field(..., description="Merchant alphanumeric identifier (merchant-mid)")
    merchant_int_id: int = Field(..., description="Merchant integer identifier (merchant-int-id)")
    question: str = Field(..., description="The user's natural-language analysis question")
    analysis_today: str = Field(..., description="Reference date in YYYY-MM-DD format")
    date_range: str | None = Field(None, description="The specific time frame for analysis (e.g., 'January 2026' or 'January 2026 to February 2026')")
    grain: Literal["month"] = "month"
    group_by: Literal["risk_flag"] = "risk_flag"


class ToolResponse(BaseModel):
    tool_name: str
    payload: dict[str, Any]


class AnalysisResult(BaseModel):
    request: MetricAnalysisRequest
    tool_payload: dict[str, Any]
    answer: str


class KwikflowsAnalysisRequest(BaseModel):
    merchant_mid: str = Field(..., description="Merchant alphanumeric identifier (merchant-mid)")
    merchant_int_id: int = Field(..., description="Merchant integer identifier (merchant-int-id)")
    question: str = Field(..., description="The user's natural-language analysis question about KwikFlows")


class KwikflowsAnalysisResult(BaseModel):
    request: KwikflowsAnalysisRequest
    workflows_payload: dict[str, Any]
    answer: str


class KwikflowImpactRequest(BaseModel):
    merchant_mid: str = Field(..., description="Merchant alphanumeric identifier (merchant-mid)")
    merchant_int_id: int = Field(..., description="Merchant integer identifier (merchant-int-id)")
    rule_id: str = Field(..., description="The rule_id from the workflow rules list")
    question: str = Field(..., description="The user's question about this kwikflow's impact")


class KwikflowImpactResult(BaseModel):
    request: KwikflowImpactRequest
    impact_payload: dict[str, Any]
    answer: str

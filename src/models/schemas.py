from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class MetricAnalysisRequest(BaseModel):
    merchant_id: str = Field(..., description="Merchant identifier to scope the query")
    question: str = Field(..., description="The user's natural-language analysis question")
    input_path: str = Field(..., description="CSV or JSON file path for the mock tool")
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

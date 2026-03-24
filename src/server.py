from __future__ import annotations

import os
import sys

# Ensure the project root is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP

from src.config import Settings
from src.prompts.metric_analysis import build_prompt_template
from src.services.metric_analysis_service import MetricAnalysisService


settings = Settings.from_env()
service = MetricAnalysisService(
    api_key=settings.gemini_api_key,
    model=settings.gemini_model,
    input_path=settings.metric_analysis_input_path,
    analysis_today=settings.analysis_today,
)

mcp = FastMCP(settings.mcp_server_name)


@mcp.tool(
    name="get_metric_analysis_data",
    description="Fetch monthly metric analysis data grouped by risk flag for a merchant. Use this when the user wants raw structured data before analysis. Requires merchant_id and optional date_range (e.g., 'January 2026' or 'January 2026 to February 2026').",
)
def get_metric_analysis_data(merchant_id: str, date_range: str | None = None) -> dict:
    return service.get_metric_analysis_data(merchant_id=merchant_id, date_range=date_range)


@mcp.tool(
    name="analyze_monthly_risk_flag_metrics",
    description="Analyze monthly risk-flag performance for a merchant using the question provided by the user. Requires merchant_id, question, and optional date_range.",
)
def analyze_monthly_risk_flag_metrics(merchant_id: str, question: str, date_range: str | None = None) -> str:
    result = service.analyze(merchant_id=merchant_id, question=question, date_range=date_range)
    return result.answer


@mcp.resource("guidance://main")
def get_guidance() -> str:
    """Provides troubleshooting and domain guidance for the RTO/KwikFlows analysis tools."""
    with open("resources/guidance.md", "r") as f:
        return f.read()


@mcp.prompt(
    name="monthly_risk_flag_analysis",
    description="Collect the merchant_id and user's analysis question, then use the monthly risk-flag analysis tool.",
)
def monthly_risk_flag_analysis() -> str:
    return build_prompt_template()


if __name__ == "__main__":
    mcp.run()

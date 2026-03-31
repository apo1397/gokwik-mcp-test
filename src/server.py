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
    api_key=settings.llm_api_key,
    model=settings.llm_model,
    api_base_url=settings.api_base_url,
    api_auth_token=settings.api_auth_token,
    kwikflows_api_url=settings.kwikflows_api_url,
    kwikflows_impact_api_url=settings.kwikflows_impact_api_url,
)

mcp = FastMCP(settings.mcp_server_name)


@mcp.tool(
    name="get_metric_analysis_data",
    description="Fetch metric analysis data grouped by risk flag for a merchant. Data is aggregated to monthly by default. Requires merchant_mid, merchant_int_id. Optional: date_range (e.g., 'January 2026 to February 2026'), grain ('day', 'week', or 'month' — only override if user explicitly asks for a specific granularity).",
)
def get_metric_analysis_data(merchant_mid: str, merchant_int_id: int, date_range: str | None = None, grain: str | None = None) -> dict:
    return service.get_metric_analysis_data(merchant_mid=merchant_mid, merchant_int_id=merchant_int_id, date_range=date_range, grain=grain)


@mcp.tool(
    name="list_kwikflows_workflows",
    description="List all active and inactive KwikFlows workflows for a merchant to understand rules, conditions, and actions. Requires merchant_mid and merchant_int_id.",
)
def list_kwikflows_workflows(merchant_mid: str, merchant_int_id: int) -> list[dict]:
    return service.get_workflows(merchant_mid=merchant_mid, merchant_int_id=merchant_int_id)


@mcp.tool(
    name="analyze_kwikflows",
    description="Analyze the active KwikFlows workflow configuration for a merchant — interventions, conditions, coverage gaps, and recommendations. Requires merchant_mid, merchant_int_id, and a question.",
)
def analyze_kwikflows(merchant_mid: str, merchant_int_id: int, question: str) -> str:
    result = service.analyze_kwikflows(merchant_mid=merchant_mid, merchant_int_id=merchant_int_id, question=question)
    return result.answer


@mcp.tool(
    name="analyze_monthly_risk_flag_metrics",
    description="Analyze risk-flag performance for a merchant using the question provided by the user. Data is aggregated to monthly by default. Requires merchant_mid, merchant_int_id, question. Optional: date_range, grain ('day', 'week', or 'month').",
)
def analyze_monthly_risk_flag_metrics(merchant_mid: str, merchant_int_id: int, question: str, date_range: str | None = None, grain: str | None = None) -> str:
    result = service.analyze(merchant_mid=merchant_mid, merchant_int_id=merchant_int_id, question=question, date_range=date_range, grain=grain)
    return result.answer


@mcp.tool(
    name="analyze_kwikflow_impact",
    description="Analyze the impact of a specific KwikFlow rule for a merchant. First use list_kwikflows_workflows to get the rule_id, then call this tool. Does NOT work for AB experiment workflows. Requires merchant_mid, merchant_int_id, rule_id, and a question.",
)
def analyze_kwikflow_impact(merchant_mid: str, merchant_int_id: int, rule_id: str, question: str) -> str:
    result = service.analyze_kwikflow_impact(merchant_mid=merchant_mid, merchant_int_id=merchant_int_id, rule_id=rule_id, question=question)
    return result.answer


@mcp.resource("resource://guidance/main")
def get_guidance() -> str:
    """Provides troubleshooting and domain guidance for the RTO/KwikFlows analysis tools."""
    with open("resources/guidance.md", "r") as f:
        return f.read()


@mcp.resource("resource://business_context/main")
def get_business_context() -> str:
    """Provides business logic and benchmarks for GoKwik metrics."""
    with open("resources/business_context.md", "r") as f:
        return f.read()


@mcp.prompt(
    name="monthly_risk_flag_analysis",
    description="Collect the merchant_id and user's analysis question, then use the monthly risk-flag analysis tool.",
)
def monthly_risk_flag_analysis() -> str:
    return build_prompt_template()


if __name__ == "__main__":
    mcp.run()

from __future__ import annotations

import os
import sys

# Ensure the project root is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP

from src.config import Settings
from src.services.metric_analysis_service import MetricAnalysisService


settings = Settings.from_env()
service = MetricAnalysisService(
    api_base_url=settings.api_base_url,
    api_auth_token=settings.api_auth_token,
    kwikflows_api_url=settings.kwikflows_api_url,
    kwikflows_impact_api_url=settings.kwikflows_impact_api_url,
)

mcp = FastMCP(settings.mcp_server_name)


# ── Data tools (no LLM — MCP client does the analysis) ─────────────────────

@mcp.tool(
    name="get_metric_analysis_data",
    description="Fetch metric analysis data grouped by risk flag for a merchant. Data is aggregated to monthly by default. Read resource://domain/metric_analysis for interpretation guidance. Requires merchant_mid, merchant_int_id. Optional: date_range (e.g., 'January 2026 to February 2026'), grain ('day', 'week', or 'month' — only override if user explicitly asks for a specific granularity).",
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
    name="get_kwikflows_analysis_data",
    description="Fetch active KwikFlows workflows with simplified conditions, actions, and AB test details for analysis. Read resource://domain/kwikflows for interpretation guidance. Requires merchant_mid and merchant_int_id.",
)
def get_kwikflows_analysis_data(merchant_mid: str, merchant_int_id: int) -> dict:
    return service.get_kwikflows_analysis_data(merchant_mid=merchant_mid, merchant_int_id=merchant_int_id)


@mcp.tool(
    name="get_kwikflow_impact_data",
    description="Fetch impact metrics for a specific KwikFlow rule. First use list_kwikflows_workflows to get the rule_id. Does NOT work for AB experiment workflows. Read resource://domain/kwikflow_impact for interpretation guidance. Requires merchant_mid, merchant_int_id, and rule_id.",
)
def get_kwikflow_impact_data(merchant_mid: str, merchant_int_id: int, rule_id: str) -> dict:
    return service.get_kwikflow_impact_data(merchant_mid=merchant_mid, merchant_int_id=merchant_int_id, rule_id=rule_id)


# ── Resources (domain knowledge for the MCP client) ────────────────────────

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


@mcp.resource("resource://domain/metric_analysis")
def get_metric_analysis_domain() -> str:
    """Domain knowledge for interpreting RTO & checkout metric analysis data."""
    with open("resources/metric_analysis_domain.md", "r") as f:
        return f.read()


@mcp.resource("resource://domain/kwikflows")
def get_kwikflows_domain() -> str:
    """Domain knowledge for interpreting KwikFlows workflow configurations."""
    with open("resources/kwikflows_domain.md", "r") as f:
        return f.read()


@mcp.resource("resource://domain/kwikflow_impact")
def get_kwikflow_impact_domain() -> str:
    """Domain knowledge for interpreting KwikFlow rule impact metrics."""
    with open("resources/kwikflow_impact_domain.md", "r") as f:
        return f.read()


# ── Prompts (analysis workflow templates) ───────────────────────────────────

@mcp.prompt(
    name="monthly_risk_flag_analysis",
    description="Analyze risk-flag performance for a merchant. Collects merchant_id, date_range, and question, then fetches data and provides analysis using domain knowledge.",
)
def monthly_risk_flag_analysis() -> str:
    return """
Use this analysis flow for monthly risk-flag metric analysis.

CRITICAL: You MUST explicitly ask the user for:
1. The `merchant_mid` (alphanumeric, e.g., '12wyqc2guqmkrw6406j').
2. The `merchant_int_id` (integer, e.g., 90).
3. The specific `date_range` (e.g., 'January 2026' or 'January 2026 to February 2026').

After collecting all three:
1. Call `get_metric_analysis_data` with merchant_mid, merchant_int_id, and date_range.
2. Read `resource://domain/metric_analysis` for domain knowledge and output format guidance.
3. Read `resource://guidance/main` and `resource://business_context/main` for additional context.
4. Analyze the data and answer the user's question following the output format in the domain resource.
""".strip()


@mcp.prompt(
    name="kwikflows_analysis",
    description="Analyze KwikFlows workflow configuration for a merchant — interventions, conditions, coverage gaps, and recommendations.",
)
def kwikflows_analysis() -> str:
    return """
Use this analysis flow for KwikFlows workflow configuration analysis.

CRITICAL: You MUST explicitly ask the user for:
1. The `merchant_mid` (alphanumeric).
2. The `merchant_int_id` (integer).

After collecting both:
1. Call `get_kwikflows_analysis_data` with merchant_mid and merchant_int_id.
2. Read `resource://domain/kwikflows` for domain knowledge and output format guidance.
3. Analyze the workflow configuration and answer the user's question following the output format in the domain resource.
""".strip()


@mcp.prompt(
    name="kwikflow_impact_analysis",
    description="Analyze the impact of a specific KwikFlow rule. Requires rule_id from list_kwikflows_workflows.",
)
def kwikflow_impact_analysis() -> str:
    return """
Use this analysis flow for KwikFlow impact analysis.

CRITICAL: You MUST explicitly ask the user for:
1. The `merchant_mid` (alphanumeric).
2. The `merchant_int_id` (integer).
3. The `rule_id` (from list_kwikflows_workflows output).

After collecting all three:
1. Call `get_kwikflow_impact_data` with merchant_mid, merchant_int_id, and rule_id.
2. Read `resource://domain/kwikflow_impact` for domain knowledge and output format guidance.
3. Analyze the impact data and provide a verdict following the output format in the domain resource.

NOTE: This tool does NOT work for AB experiment workflows. If the rule belongs to an AB test, the tool will return an error.
""".strip()


# ── Commented out: LLM-backed tools (kept for reference) ───────────────────
#
# These tools called an external LLM (Gemini/DeepSeek) server-side.
# Replaced by data-returning tools above + MCP resources for domain knowledge.
# The MCP client (e.g., Claude Desktop) now does the analysis directly.
#
# from src.prompts.metric_analysis import build_prompt_template
#
# @mcp.tool(
#     name="analyze_kwikflows",
#     description="Analyze the active KwikFlows workflow configuration for a merchant.",
# )
# def analyze_kwikflows(merchant_mid: str, merchant_int_id: int, question: str) -> str:
#     result = service.analyze_kwikflows(merchant_mid=merchant_mid, merchant_int_id=merchant_int_id, question=question)
#     return result.answer
#
# @mcp.tool(
#     name="analyze_monthly_risk_flag_metrics",
#     description="Analyze risk-flag performance for a merchant using the question provided by the user.",
# )
# def analyze_monthly_risk_flag_metrics(merchant_mid: str, merchant_int_id: int, question: str, date_range: str | None = None, grain: str | None = None) -> str:
#     result = service.analyze(merchant_mid=merchant_mid, merchant_int_id=merchant_int_id, question=question, date_range=date_range, grain=grain)
#     return result.answer
#
# @mcp.tool(
#     name="analyze_kwikflow_impact",
#     description="Analyze the impact of a specific KwikFlow rule for a merchant.",
# )
# def analyze_kwikflow_impact(merchant_mid: str, merchant_int_id: int, rule_id: str, question: str) -> str:
#     result = service.analyze_kwikflow_impact(merchant_mid=merchant_mid, merchant_int_id=merchant_int_id, rule_id=rule_id, question=question)
#     return result.answer


if __name__ == "__main__":
    mcp.run()

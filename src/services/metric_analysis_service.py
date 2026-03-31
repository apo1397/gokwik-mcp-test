from __future__ import annotations

from typing import Any

from src.tools.get_metric_analysis_data import GetMetricAnalysisDataTool
from src.utils.data_transforms import (
    build_kwikflow_impact_payload,
    build_kwikflows_analysis_payload,
    fetch_workflow_data,
)


class MetricAnalysisService:
    def __init__(self, *, api_base_url: str, api_auth_token: str, kwikflows_api_url: str, kwikflows_impact_api_url: str) -> None:
        self._tool = GetMetricAnalysisDataTool()
        self._api_base_url = api_base_url
        self._api_auth_token = api_auth_token
        self._kwikflows_api_url = kwikflows_api_url
        self._kwikflows_impact_api_url = kwikflows_impact_api_url

    def get_metric_analysis_data(self, *, merchant_mid: str, merchant_int_id: int, date_range: str | None = None, grain: str | None = None) -> dict:
        from datetime import date
        analysis_today = date.today().isoformat()
        return self._tool.run(
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
            api_base_url=self._api_base_url,
            api_auth_token=self._api_auth_token,
            analysis_today=analysis_today,
            date_range=date_range,
            grain=grain,
        )

    def get_workflows(self, *, merchant_mid: str, merchant_int_id: int) -> list[dict]:
        return fetch_workflow_data(
            api_url=self._kwikflows_api_url,
            auth_token=self._api_auth_token,
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
        )

    def get_kwikflows_analysis_data(self, *, merchant_mid: str, merchant_int_id: int) -> dict[str, Any]:
        return build_kwikflows_analysis_payload(
            api_url=self._kwikflows_api_url,
            auth_token=self._api_auth_token,
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
        )

    def get_kwikflow_impact_data(self, *, merchant_mid: str, merchant_int_id: int, rule_id: str) -> dict[str, Any]:
        return build_kwikflow_impact_payload(
            workflows_api_url=self._kwikflows_api_url,
            impact_api_url=self._kwikflows_impact_api_url,
            auth_token=self._api_auth_token,
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
            rule_id=rule_id,
        )


# ── Commented out: LLM-backed methods (kept for reference) ─────────────────
#
# These methods called an external LLM (Gemini/DeepSeek) server-side.
# Replaced by data-returning methods above.
#
# from langchain_core.messages import HumanMessage, SystemMessage
# from src.clients.gemini_client import build_chat_model
# from src.models.schemas import AnalysisResult, KwikflowImpactRequest, KwikflowImpactResult, KwikflowsAnalysisRequest, KwikflowsAnalysisResult, MetricAnalysisRequest
# from src.prompts.kwikflows_analysis import build_kwikflow_impact_messages, build_kwikflows_analysis_messages
# from src.prompts.metric_analysis import build_metric_analysis_messages
#
# To restore LLM support:
# 1. Add api_key and model params to __init__
# 2. self._llm = build_chat_model(api_key=api_key, model=model)
# 3. Uncomment the methods below
#
# def analyze_kwikflows(self, *, merchant_mid, merchant_int_id, question):
#     workflows_payload = build_kwikflows_analysis_payload(...)
#     prompt_messages = build_kwikflows_analysis_messages(question, workflows_payload)
#     messages = [SystemMessage(content=prompt_messages[0][1]), HumanMessage(content=prompt_messages[1][1])]
#     response = self._llm.invoke(messages)
#     return KwikflowsAnalysisResult(request=..., workflows_payload=workflows_payload, answer=response.content)
#
# def analyze(self, *, merchant_mid, merchant_int_id, question, date_range=None, grain=None):
#     tool_payload = self.get_metric_analysis_data(...)
#     prompt_messages = build_metric_analysis_messages(question, tool_payload)
#     messages = [SystemMessage(content=prompt_messages[0][1]), HumanMessage(content=prompt_messages[1][1])]
#     response = self._llm.invoke(messages)
#     return AnalysisResult(request=..., tool_payload=tool_payload, answer=response.content)
#
# def analyze_kwikflow_impact(self, *, merchant_mid, merchant_int_id, rule_id, question):
#     impact_payload = build_kwikflow_impact_payload(...)
#     if "error" in impact_payload:
#         return KwikflowImpactResult(request=..., impact_payload=impact_payload, answer=impact_payload["error"])
#     prompt_messages = build_kwikflow_impact_messages(question, impact_payload)
#     messages = [SystemMessage(content=prompt_messages[0][1]), HumanMessage(content=prompt_messages[1][1])]
#     response = self._llm.invoke(messages)
#     return KwikflowImpactResult(request=..., impact_payload=impact_payload, answer=response.content)

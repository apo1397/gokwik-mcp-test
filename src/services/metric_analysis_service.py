from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.clients.gemini_client import build_chat_model
from src.models.schemas import AnalysisResult, KwikflowsAnalysisRequest, KwikflowsAnalysisResult, MetricAnalysisRequest
from src.prompts.kwikflows_analysis import build_kwikflows_analysis_messages
from src.prompts.metric_analysis import build_metric_analysis_messages
from src.tools.get_metric_analysis_data import GetMetricAnalysisDataTool


from src.utils.data_transforms import (
    build_kwikflows_analysis_payload,
    fetch_api_data,
    fetch_workflow_data,
    normalize_rows,
    summarize_rows,
)


class MetricAnalysisService:
    def __init__(self, *, api_key: str, model: str, api_auth_token: str, analysis_today: str) -> None:
        self._llm = build_chat_model(api_key=api_key, model=model)
        self._tool = GetMetricAnalysisDataTool()
        self._api_auth_token = api_auth_token
        self._analysis_today = analysis_today

    def get_metric_analysis_data(self, *, merchant_mid: str, merchant_int_id: int, date_range: str | None = None) -> dict:
        return self._tool.run(
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
            api_auth_token=self._api_auth_token,
            analysis_today=self._analysis_today,
            date_range=date_range,
        )

    def get_workflows(self, *, merchant_mid: str, merchant_int_id: int) -> list[dict]:
        return fetch_workflow_data(
            auth_token=self._api_auth_token,
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
        )

    def analyze_kwikflows(self, *, merchant_mid: str, merchant_int_id: int, question: str) -> KwikflowsAnalysisResult:
        request = KwikflowsAnalysisRequest(
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
            question=question,
        )

        workflows_payload = build_kwikflows_analysis_payload(
            auth_token=self._api_auth_token,
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
        )

        prompt_messages = build_kwikflows_analysis_messages(question, workflows_payload)
        messages = [
            SystemMessage(content=prompt_messages[0][1]),
            HumanMessage(content=prompt_messages[1][1]),
        ]
        response = self._llm.invoke(messages)
        answer = response.content if isinstance(response.content, str) else str(response.content)

        return KwikflowsAnalysisResult(
            request=request,
            workflows_payload=workflows_payload,
            answer=answer,
        )

    def analyze(self, *, merchant_mid: str, merchant_int_id: int, question: str, date_range: str | None = None) -> AnalysisResult:
        request = MetricAnalysisRequest(
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
            question=question,
            analysis_today=self._analysis_today,
            date_range=date_range,
        )

        tool_payload = self.get_metric_analysis_data(
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
            date_range=date_range
        )
        prompt_messages = build_metric_analysis_messages(question, tool_payload)
        messages = [
            SystemMessage(content=prompt_messages[0][1]),
            HumanMessage(content=prompt_messages[1][1]),
        ]
        response = self._llm.invoke(messages)
        answer = response.content if isinstance(response.content, str) else str(response.content)

        return AnalysisResult(
            request=request,
            tool_payload=tool_payload,
            answer=answer,
        )

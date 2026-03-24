from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.clients.gemini_client import build_chat_model
from src.models.schemas import AnalysisResult, MetricAnalysisRequest
from src.prompts.metric_analysis import build_metric_analysis_messages
from src.tools.get_metric_analysis_data import GetMetricAnalysisDataTool


class MetricAnalysisService:
    def __init__(self, *, api_key: str, model: str, input_path: str, analysis_today: str) -> None:
        self._llm = build_chat_model(api_key=api_key, model=model)
        self._tool = GetMetricAnalysisDataTool()
        self._input_path = input_path
        self._analysis_today = analysis_today

    def get_metric_analysis_data(self, *, merchant_id: str, date_range: str | None = None) -> dict:
        return self._tool.run(
            merchant_id=merchant_id,
            input_path=self._input_path,
            analysis_today=self._analysis_today,
            date_range=date_range,
        )

    def analyze(self, *, merchant_id: str, question: str, date_range: str | None = None) -> AnalysisResult:
        request = MetricAnalysisRequest(
            merchant_id=merchant_id,
            question=question,
            input_path=self._input_path,
            analysis_today=self._analysis_today,
            date_range=date_range,
        )

        tool_payload = self.get_metric_analysis_data(merchant_id=merchant_id, date_range=date_range)
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

from __future__ import annotations

from typing import Any

from src.tools.base import Tool
from src.utils.data_transforms import (
    build_maturity_metadata,
    fetch_api_data,
    normalize_rows,
    summarize_rows,
)


class GetMetricAnalysisDataTool(Tool):
    name = "get_metric_analysis_data"

    def run(
        self,
        *,
        merchant_mid: str,
        merchant_int_id: int,
        api_auth_token: str,
        analysis_today: str,
        date_range: str | None = None,
        **_: Any
    ) -> dict[str, Any]:
        from_date = "2026-01-01"
        to_date = analysis_today

        raw_rows = fetch_api_data(
            auth_token=api_auth_token,
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
            from_date=from_date,
            to_date=to_date,
        )
        rows = normalize_rows(raw_rows)

        return {
            "analysis_type": "monthly_risk_flag_summary",
            "merchant_mid": merchant_mid,
            "merchant_int_id": merchant_int_id,
            "dimension": "risk_flag",
            "grain": "day",
            "summary": summarize_rows(rows),
            "maturity": build_maturity_metadata(rows, analysis_today),
            "derived_metrics": ["cr_pct", "cod_share_pct", "rto_pct_overall"],
            "rows": rows,
        }

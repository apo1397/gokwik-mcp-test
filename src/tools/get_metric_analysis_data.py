from __future__ import annotations

from typing import Any

from src.tools.base import Tool
from src.utils.data_transforms import (
    build_maturity_metadata,
    load_input_file,
    normalize_rows,
    summarize_rows,
)


class GetMetricAnalysisDataTool(Tool):
    name = "get_metric_analysis_data"

    def run(self, *, merchant_id: str, input_path: str, analysis_today: str, date_range: str | None = None, **_: Any) -> dict[str, Any]:
        raw_rows = load_input_file(input_path, merchant_id=merchant_id, date_range=date_range)
        rows = normalize_rows(raw_rows)

        return {
            "analysis_type": "monthly_risk_flag_summary",
            "merchant_id": merchant_id,
            "dimension": "risk_flag",
            "grain": "month",
            "summary": summarize_rows(rows),
            "maturity": build_maturity_metadata(rows, analysis_today),
            "derived_metrics": ["cr_pct", "cod_share_pct"],
            "rows": rows,
        }

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.tools.base import Tool
from src.utils.data_transforms import (
    aggregate_rows,
    build_maturity_metadata,
    fetch_api_data,
    normalize_rows,
    summarize_rows,
)


def _parse_date_range(date_range: str | None, analysis_today: str) -> tuple[str, str]:
    """Parse a human-readable date range into (from_date, to_date) ISO strings.

    Supports formats like:
    - "January 2026 to March 2026"
    - "January 2026"
    - None → defaults to last 3 months
    """
    if not date_range:
        today = datetime.strptime(analysis_today, "%Y-%m-%d").date()
        # Default: 3 months back from today
        month = today.month - 3
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        from_date = f"{year}-{month:02d}-01"
        return from_date, analysis_today

    # Try "Month Year to Month Year"
    if " to " in date_range:
        parts = date_range.split(" to ", 1)
        try:
            start = datetime.strptime(parts[0].strip(), "%B %Y").date()
            end_month = datetime.strptime(parts[1].strip(), "%B %Y").date()
            # End of the end month: go to next month's 1st, subtract 1 day
            if end_month.month == 12:
                end = end_month.replace(year=end_month.year + 1, month=1)
            else:
                end = end_month.replace(month=end_month.month + 1)
            # Cap at analysis_today
            today = datetime.strptime(analysis_today, "%Y-%m-%d").date()
            end = min(end, today)
            return start.isoformat(), end.isoformat()
        except ValueError:
            pass

    # Try single "Month Year"
    try:
        start = datetime.strptime(date_range.strip(), "%B %Y").date()
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
        today = datetime.strptime(analysis_today, "%Y-%m-%d").date()
        end = min(end, today)
        return start.isoformat(), end.isoformat()
    except ValueError:
        pass

    # Fallback: last 3 months
    today = datetime.strptime(analysis_today, "%Y-%m-%d").date()
    month = today.month - 3
    year = today.year
    if month <= 0:
        month += 12
        year -= 1
    return f"{year}-{month:02d}-01", analysis_today


class GetMetricAnalysisDataTool(Tool):
    name = "get_metric_analysis_data"

    def run(
        self,
        *,
        merchant_mid: str,
        merchant_int_id: int,
        api_base_url: str,
        api_auth_token: str,
        analysis_today: str,
        date_range: str | None = None,
        grain: str | None = None,
        **_: Any
    ) -> dict[str, Any]:
        from_date, to_date = _parse_date_range(date_range, analysis_today)

        raw_rows = fetch_api_data(
            base_url=api_base_url,
            auth_token=api_auth_token,
            merchant_mid=merchant_mid,
            merchant_int_id=merchant_int_id,
            from_date=from_date,
            to_date=to_date,
        )
        rows = normalize_rows(raw_rows)

        # Compute summary and maturity from daily rows before aggregation
        summary = summarize_rows(rows)
        maturity = build_maturity_metadata(rows, analysis_today)

        # Aggregate to reduce payload size for the LLM
        rows, grain_used = aggregate_rows(rows, grain)

        return {
            "analysis_type": "risk_flag_summary",
            "merchant_mid": merchant_mid,
            "merchant_int_id": merchant_int_id,
            "dimension": "risk_flag",
            "grain": grain_used,
            "date_range": {"from": from_date, "to": to_date},
            "summary": summary,
            "maturity": maturity,
            "derived_metrics": ["cr_pct", "cod_share_pct", "rto_pct_overall"],
            "rows": rows,
        }

from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests

MONTH_FORMAT = "%B %Y"


COLUMN_MAP = {
    "date": "date",
    "risk_flag": "risk_flag",
    "total_hits": "rto_api_hits",
    "total_orders": "orders",
    "cod_orders": "cod_orders",
    "total_rto_orders": "rto_orders",
    "total_delivered_orders": "delivered_orders",
    "total_cancelled_orders": "cancelled_orders",
}


def fetch_api_data(
    base_url: str,
    auth_token: str,
    merchant_mid: str,
    merchant_int_id: int,
    from_date: str = "2026-01-01",
    to_date: str = "2026-03-24",
) -> list[dict[str, Any]]:
    headers = {
        "Authorization": auth_token,
        "merchant-mid": merchant_mid,
        "merchant-int-id": str(merchant_int_id),
        "user-type": "admin",
    }
    params = {
        "rto_segment": "all",
        "filter_type": "risk_flag",
        "from_date": from_date,
        "to_date": to_date,
    }

    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if not data or "data" not in data:
        return []

    return data["data"]


def normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        converted = {}
        for key, value in row.items():
            target_key = COLUMN_MAP.get(key, key)
            converted[target_key] = value

        hits = float(converted.get("rto_api_hits", 0))
        orders = float(converted.get("orders", 0))
        cod_orders = float(converted.get("cod_orders", 0))
        rto_orders = float(converted.get("rto_orders", 0))
        cancelled_orders = float(converted.get("cancelled_orders", 0))

        converted["cr_pct"] = round((orders / hits) * 100, 2) if hits else 0
        converted["cod_share_pct"] = round((cod_orders / orders) * 100, 2) if orders else 0

        # RTO% = RTO Orders / (Total Orders - Cancelled Orders)
        denominator = orders - cancelled_orders
        converted["rto_pct_overall"] = round((rto_orders / denominator) * 100, 2) if denominator > 0 else 0

        # Extract month label for compatibility with existing summarization
        dt = datetime.strptime(converted["date"], "%Y-%m-%d")
        converted["date_label"] = dt.strftime(MONTH_FORMAT)
        converted["period_start"] = dt.replace(day=1).date().isoformat()

        normalized.append(converted)

    normalized.sort(key=lambda x: (x["date"], x["risk_flag"]))
    return normalized


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}

    df = pd.DataFrame(rows)
    # Group by the original month label we added
    summary = df.groupby(["date_label", "risk_flag"]).agg({
        "rto_api_hits": "sum",
        "orders": "sum",
        "cod_orders": "sum",
        "rto_orders": "sum",
        "delivered_orders": "sum",
        "cancelled_orders": "sum"
    }).reset_index()

    # Recalculate percentages for the summary
    summary["cr_pct"] = (summary["orders"] / summary["rto_api_hits"] * 100).round(2).fillna(0)
    summary["cod_share_pct"] = (summary["cod_orders"] / summary["orders"] * 100).round(2).fillna(0)
    denom = summary["orders"] - summary["cancelled_orders"]
    summary["rto_pct_overall"] = (summary["rto_orders"] / denom * 100).round(2).where(denom > 0, 0)

    return summary.to_dict(orient="records")


def parse_month(label: str) -> date:
    # Handle both YYYY-MM-DD and "Month Year" formats
    try:
        return datetime.strptime(label, "%Y-%m-%d").date().replace(day=1)
    except ValueError:
        return datetime.strptime(label, MONTH_FORMAT).date().replace(day=1)


def build_maturity_metadata(rows: list[dict[str, Any]], analysis_today: str) -> dict[str, Any]:
    if not rows:
        return {"analysis_today": analysis_today}

    today = datetime.strptime(analysis_today, "%Y-%m-%d").date()
    latest_period = max(parse_month(row["date"]) for row in rows)
    latest_month_matches_today = latest_period.year == today.year and latest_period.month == today.month

    maturity_cutoff = today.replace(day=1)
    if today.day <= 15:
        if today.month == 1:
            maturity_cutoff = maturity_cutoff.replace(year=today.year - 1, month=12)
        else:
            maturity_cutoff = maturity_cutoff.replace(month=today.month - 1)

    return {
        "analysis_today": analysis_today,
        "latest_period": latest_period.isoformat(),
        "latest_period_label": latest_period.strftime(MONTH_FORMAT),
        "is_latest_period_partial": latest_month_matches_today,
        "rto_maturity_days": 15,
        "interpretation_notes": [
            "Data is fetched live from GoKwik Analytics API.",
            "RTO and COD RTO metrics mature after 15 days.",
            "Live data includes daily granularity summarized by risk flag.",
        ],
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    periods = sorted({row["date"] for row in rows}, key=parse_month)
    risk_flags = sorted({row["risk_flag"] for row in rows})
    return {
        "row_count": len(rows),
        "periods": periods,
        "risk_flags": risk_flags,
    }

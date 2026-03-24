from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

MONTH_FORMAT = "%B %Y"


COLUMN_MAP = {
    "DATE": "date",
    "RISK FLAG": "risk_flag",
    "RTO API HITS": "rto_api_hits",
    "ORDERS": "orders",
    "COD ORDERS": "cod_orders",
    "RTO COD %": "rto_cod_pct",
    "RTO % (OVERALL)": "rto_pct_overall",
    "PREPAID SHARE %": "prepaid_share_pct",
    "AWB FILL RATE %": "awb_fill_rate_pct",
    "DELIVERED ORDERS %": "delivered_orders_pct",
    "CANCELLED ORDERS %": "cancelled_orders_pct",
}


def load_input_file(path: str, merchant_id: str | None = None, date_range: str | None = None) -> list[dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(file_path)
    elif suffix == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict) and "rows" in payload:
            df = pd.DataFrame(payload["rows"])
        elif isinstance(payload, list):
            df = pd.DataFrame(payload)
        else:
            raise ValueError("JSON input must be either a list of rows or an object with a 'rows' key")
    else:
        raise ValueError("Only CSV and JSON inputs are supported")

    # Filter by merchant_id if provided
    if merchant_id:
        # Check both "Merchant ID" (CSV header) and "merchant_id" (normalized)
        id_col = next((col for col in df.columns if col.lower() in ["merchant id", "merchant_id"]), None)
        if id_col:
            df = df[df[id_col].astype(str) == str(merchant_id)]

    # Filter by date_range if provided (very basic implementation for now)
    if date_range:
        # Expected format: "January 2026" or "January 2026 to February 2026"
        date_col = next((col for col in df.columns if col.lower() in ["date", "period_start"]), None)
        if date_col:
            if " to " in date_range:
                start_label, end_label = date_range.split(" to ")
                # Simple string matching for now as the CSV uses "Month Year"
                # In a real app, we'd parse to datetime objects
                df = df[df[date_col].str.contains(start_label) | df[date_col].str.contains(end_label)]
            else:
                df = df[df[date_col].str.contains(date_range)]

    return df.to_dict(orient="records")


def normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        converted = {}
        for key, value in row.items():
            target_key = COLUMN_MAP.get(key, key)
            converted[target_key] = value

        hits = float(converted["rto_api_hits"])
        orders = float(converted["orders"])
        cod_orders = float(converted["cod_orders"])

        converted["cr_pct"] = round((orders / hits) * 100, 2) if hits else None
        converted["cod_share_pct"] = round((cod_orders / orders) * 100, 2) if orders else None
        converted["period_start"] = parse_month(converted["date"]).isoformat()
        normalized.append(converted)

    normalized.sort(key=lambda x: (x["period_start"], x["risk_flag"]))
    return normalized


def parse_month(label: str) -> date:
    return datetime.strptime(label, MONTH_FORMAT).date().replace(day=1)


def build_maturity_metadata(rows: list[dict[str, Any]], analysis_today: str) -> dict[str, Any]:
    today = datetime.strptime(analysis_today, "%Y-%m-%d").date()
    latest_period = max(parse_month(row["date"]) for row in rows)
    latest_month_matches_today = latest_period.year == today.year and latest_period.month == today.month

    maturity_cutoff = today.replace(day=1)
    if today.day <= 15:
        # If it's early in the month, even the immediately previous month can still be maturing for RTO.
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
            "Data is available till the previous day.",
            "RTO and COD RTO metrics mature after 15 days.",
            "Do not over-interpret a recent drop in RTO unless fill rate and maturity support it.",
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

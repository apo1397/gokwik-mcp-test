from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests

MONTH_FORMAT = "%B %Y"

# Count fields that should be summed during aggregation
SUM_FIELDS = [
    "rto_api_hits",
    "orders",
    "cod_orders",
    "rto_orders",
    "delivered_orders",
    "cancelled_orders",
    "total_pending_orders",
    "total_null_status_orders",
    "total_cod_rto_orders",
    "total_cod_pending_orders",
    "total_cod_delivered_orders",
]


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


def fetch_workflow_data(
    api_url: str,
    auth_token: str,
    merchant_mid: str,
    merchant_int_id: int,
) -> list[dict[str, Any]]:
    headers = {
        "Authorization": auth_token,
        "merchant-mid": merchant_mid,
        "merchant-int-id": str(merchant_int_id),
        "user-type": "admin",
    }
    params = {"merchant_id": merchant_mid}

    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if not data or "data" not in data or "workflows" not in data["data"]:
        return []

    workflows = data["data"]["workflows"]
    processed_workflows = []

    for wf in workflows:
        # Simplify structure for the agent
        processed_wf = {
            "workflow_id": wf.get("workflow_id"),
            "workflow_name": wf.get("rule_name"),
            "is_enabled": wf.get("is_enabled"),
            "rules": []
        }
        
        for rule in wf.get("rules", []):
            raw_rule = rule.get("raw_data", {})
            simplified_rule = {
                "rule_id": rule.get("rule_id"),
                "priority": raw_rule.get("priority"),
                "conditions": [],
                "actions": []
            }

            # Truncate long arrays (> 20) in conditions
            for cond in raw_rule.get("conditions", []):
                simplified_cond = cond.copy()
                if "values" in simplified_cond and isinstance(simplified_cond["values"], list):
                    if len(simplified_cond["values"]) > 20:
                        simplified_cond["values"] = simplified_cond["values"][:20] + ["... (truncated)"]
                simplified_rule["conditions"].append(simplified_cond)

            simplified_rule["actions"] = raw_rule.get("actions", [])
            processed_wf["rules"].append(simplified_rule)
            
        processed_workflows.append(processed_wf)

    return processed_workflows


def build_kwikflows_analysis_payload(
    api_url: str,
    auth_token: str,
    merchant_mid: str,
    merchant_int_id: int,
) -> dict[str, Any]:
    """Fetch workflows, filter to active only, and structure for LLM analysis."""
    headers = {
        "Authorization": auth_token,
        "merchant-mid": merchant_mid,
        "merchant-int-id": str(merchant_int_id),
        "user-type": "admin",
    }
    params = {"merchant_id": merchant_mid}

    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if not data or "data" not in data or "workflows" not in data["data"]:
        return {
            "merchant_mid": merchant_mid,
            "merchant_int_id": merchant_int_id,
            "total_workflows": 0,
            "active_workflows": 0,
            "workflows": [],
        }

    all_workflows = data["data"]["workflows"]
    active_workflows = [wf for wf in all_workflows if wf.get("is_enabled")]

    processed = []
    for wf in active_workflows:
        processed_wf = {
            "workflow_name": wf.get("rule_name"),
            "workflow_id": wf.get("workflow_id"),
            "workflow_flag": wf.get("workflow_flag"),
            "is_ab_test_enabled": wf.get("is_ab_test_enabled", False),
            "ab_control_intervention": wf.get("ab_control_intervention"),
            "created_at": wf.get("created_at"),
            "updated_at": wf.get("updated_at"),
            "rules": [],
        }

        for rule in wf.get("rules", []):
            raw = rule.get("raw_data", {})
            simplified_rule: dict[str, Any] = {
                "rule_id": rule.get("rule_id"),
                "priority": raw.get("priority"),
                "conditions": [],
                "actions": [],
            }

            for cond in raw.get("conditions", []):
                simplified_cond = _simplify_condition(cond)
                simplified_rule["conditions"].append(simplified_cond)

            for action in raw.get("actions", []):
                simplified_action = _simplify_action(action)
                simplified_rule["actions"].append(simplified_action)

            processed_wf["rules"].append(simplified_rule)

        # Include AB test arm details so the LLM can compare both sides
        if wf.get("is_ab_test_enabled"):
            processed_wf["ab_control_perc"] = wf.get("ab_control_perc")
            ab_flag = wf.get("ab_test_flag", {})
            processed_wf["ab_test_flag_name"] = ab_flag.get("flag_name")
            processed_wf["ab_control_actions"] = [
                _simplify_ab_action(a) for a in wf.get("ab_control_actions", [])
            ]

        processed.append(processed_wf)

    return {
        "merchant_mid": merchant_mid,
        "merchant_int_id": merchant_int_id,
        "total_workflows": len(all_workflows),
        "active_workflows": len(active_workflows),
        "inactive_workflows": len(all_workflows) - len(active_workflows),
        "workflows": processed,
    }


def fetch_workflow_impact_data(
    api_url: str,
    auth_token: str,
    merchant_mid: str,
    merchant_int_id: int,
    rule_id: str,
) -> dict[str, Any]:
    """Fetch impact metrics for a specific kwikflow rule.

    The impact API does NOT work for AB experiment workflows.
    Use rule_id from the workflows list (rules[].rule_id).
    """
    headers = {
        "Authorization": auth_token,
        "merchant-mid": merchant_mid,
        "merchant-int-id": str(merchant_int_id),
        "user-type": "admin",
    }
    params = {
        "rule_ids[]": rule_id,
        "merchant_id": str(merchant_int_id),
    }

    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    return data.get("data", {})


def build_kwikflow_impact_payload(
    workflows_api_url: str,
    impact_api_url: str,
    auth_token: str,
    merchant_mid: str,
    merchant_int_id: int,
    rule_id: str,
) -> dict[str, Any]:
    """Fetch a workflow's config + impact metrics and bundle for LLM analysis.

    Steps:
    1. Fetch all workflows to find the one containing this rule_id
    2. Validate it's not an AB experiment
    3. Fetch impact metrics for the rule
    4. Return combined payload
    """
    # Step 1: Find the workflow containing this rule_id
    headers = {
        "Authorization": auth_token,
        "merchant-mid": merchant_mid,
        "merchant-int-id": str(merchant_int_id),
        "user-type": "admin",
    }
    params = {"merchant_id": merchant_mid}

    wf_response = requests.get(workflows_api_url, headers=headers, params=params)
    wf_response.raise_for_status()
    wf_data = wf_response.json()

    all_workflows = wf_data.get("data", {}).get("data", {}).get("workflows", [])
    if not all_workflows:
        all_workflows = wf_data.get("data", {}).get("workflows", [])

    target_workflow = None
    target_rule = None
    for wf in all_workflows:
        for rule in wf.get("rules", []):
            if rule.get("rule_id") == rule_id:
                target_workflow = wf
                target_rule = rule
                break
        if target_workflow:
            break

    if not target_workflow:
        return {
            "error": f"No workflow found containing rule_id '{rule_id}'",
            "merchant_mid": merchant_mid,
        }

    # Step 2: Check for AB experiment
    if target_workflow.get("is_ab_test_enabled"):
        return {
            "error": f"Workflow '{target_workflow.get('rule_name')}' is an AB experiment. Impact metrics are not available for AB test workflows.",
            "workflow_name": target_workflow.get("rule_name"),
            "workflow_id": target_workflow.get("workflow_id"),
            "merchant_mid": merchant_mid,
        }

    # Step 3: Fetch impact metrics
    impact_data = fetch_workflow_impact_data(
        api_url=impact_api_url,
        auth_token=auth_token,
        merchant_mid=merchant_mid,
        merchant_int_id=merchant_int_id,
        rule_id=rule_id,
    )

    # Step 4: Build simplified workflow config
    raw = target_rule.get("raw_data", {})
    workflow_config = {
        "workflow_name": target_workflow.get("rule_name"),
        "workflow_id": target_workflow.get("workflow_id"),
        "workflow_flag": target_workflow.get("workflow_flag"),
        "is_enabled": target_workflow.get("is_enabled"),
        "rule_id": rule_id,
        "created_at": target_workflow.get("created_at"),
        "updated_at": target_workflow.get("updated_at"),
        "conditions": [_simplify_condition(c) for c in raw.get("conditions", [])],
        "actions": [_simplify_action(a) for a in raw.get("actions", [])],
    }

    return {
        "merchant_mid": merchant_mid,
        "merchant_int_id": merchant_int_id,
        "workflow": workflow_config,
        "impact_metrics": impact_data,
    }


def _simplify_condition(cond: dict[str, Any]) -> dict[str, Any]:
    """Simplify a condition for LLM consumption, truncating large arrays."""
    result: dict[str, Any] = {
        "key": cond.get("key"),
        "operator": cond.get("operator"),
        "workflow_type": cond.get("workflow_type"),
    }

    # is_not_variant=True inverts the match — must be preserved or analysis is wrong
    if cond.get("is_not_variant"):
        result["is_not_variant"] = True

    # Include scalar value if present
    if "value" in cond:
        result["value"] = cond["value"]

    # Truncate large value arrays
    if "values" in cond and isinstance(cond["values"], list):
        vals = cond["values"]
        if len(vals) > 20:
            result["values"] = vals[:20] + [f"... ({len(vals) - 20} more, {len(vals)} total)"]
        else:
            result["values"] = vals

    # Include selected_products for SKU conditions (human-readable names)
    if "selected_products" in cond and cond["selected_products"]:
        products = cond["selected_products"]
        simplified_products = []
        for p in products[:10]:  # Cap at 10 products
            simplified_products.append({
                "product_name": p.get("product_name"),
                "variants": [
                    v.get("variant_name") for v in p.get("variant_ids", [])
                ],
            })
        if len(products) > 10:
            simplified_products.append(f"... ({len(products) - 10} more products)")
        result["selected_products"] = simplified_products

    # Include file_name if present (pincode lists etc.)
    if "file_name" in cond:
        result["file_name"] = cond["file_name"]

    return result


def _simplify_action(action: dict[str, Any]) -> dict[str, Any]:
    """Simplify an action for LLM consumption, keeping key config values."""
    result: dict[str, Any] = {"action": action.get("action")}

    if "ppcod_config" in action:
        result["ppcod_config"] = action["ppcod_config"]

    if "cod_fees" in action:
        result["cod_fees"] = action["cod_fees"]

    if "cod_confirmation_prompt_configs" in action:
        cfg = action["cod_confirmation_prompt_configs"]
        result["cod_prompt_config"] = {
            "enabled": cfg.get("enable"),
            "navigates_to": cfg.get("navigateTo"),
        }

    if "upi_discount" in action:
        result["upi_discount_pct"] = action["upi_discount"]
        result["upi_discount_cap"] = action.get("discount_upto")

    if "payment_configs" in action:
        result["has_payment_ui_config"] = True

    return result


def _simplify_ab_action(action: dict[str, Any]) -> dict[str, Any]:
    """Simplify an AB control action. Configs are nested under actionConfigs (different from rule actions)."""
    result: dict[str, Any] = {"action": action.get("action")}
    configs = action.get("actionConfigs", {})

    ppcod_config = configs.get("ppcod_config")
    if ppcod_config:
        result["ppcod_config"] = ppcod_config

    if "upi_discount" in configs:
        result["upi_discount_pct"] = configs["upi_discount"]
        result["upi_discount_cap"] = configs.get("discount_upto")

    if "payment_configs" in configs:
        result["has_payment_ui_config"] = True

    return result


def _auto_grain(rows: list[dict[str, Any]]) -> str:
    """Choose aggregation grain based on date span. Default monthly; daily only for ≤7 days."""
    if not rows:
        return "month"
    dates = [datetime.strptime(r["date"], "%Y-%m-%d").date() for r in rows]
    span = (max(dates) - min(dates)).days + 1
    if span <= 7:
        return "day"
    return "month"


def _period_key(dt: date, grain: str) -> str:
    """Return a sortable key for the period a date belongs to."""
    if grain == "month":
        return dt.strftime("%Y-%m")
    if grain == "week":
        monday = dt - timedelta(days=dt.weekday())
        return monday.isoformat()
    return dt.isoformat()


def _period_label(period_key: str, grain: str, period_dates: list[date]) -> str:
    """Return a human-readable label for a period."""
    if grain == "month":
        return datetime.strptime(period_key + "-01", "%Y-%m-%d").strftime(MONTH_FORMAT)
    if grain == "week":
        week_start = datetime.strptime(period_key, "%Y-%m-%d").date()
        week_end = week_start + timedelta(days=6)
        if week_start.month == week_end.month:
            return f"{week_start.strftime('%b %d')}–{week_end.day}, {week_start.year}"
        if week_start.year == week_end.year:
            return f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d')}, {week_start.year}"
        return f"{week_start.strftime('%b %d, %Y')} – {week_end.strftime('%b %d, %Y')}"
    # day
    return datetime.strptime(period_key, "%Y-%m-%d").strftime("%b %d, %Y")


def _recalculate_derived(row: dict[str, Any]) -> None:
    """Recalculate derived percentage fields from summed counts (in-place)."""
    hits = float(row.get("rto_api_hits", 0))
    orders = float(row.get("orders", 0))
    cod_orders = float(row.get("cod_orders", 0))
    rto_orders = float(row.get("rto_orders", 0))
    cancelled = float(row.get("cancelled_orders", 0))

    row["cr_pct"] = round((orders / hits) * 100, 2) if hits else 0
    row["cod_share_pct"] = round((cod_orders / orders) * 100, 2) if orders else 0
    denom = orders - cancelled
    row["rto_pct_overall"] = round((rto_orders / denom) * 100, 2) if denom > 0 else 0


def aggregate_rows(
    rows: list[dict[str, Any]], grain: str | None = None
) -> tuple[list[dict[str, Any]], str]:
    """Aggregate daily rows to the requested grain.

    grain=None → auto (monthly unless ≤7 days span, then daily).
    grain="day"/"week"/"month" → forced.
    Returns (aggregated_rows, grain_used).
    """
    if not rows:
        return [], "day"

    grain_used = grain if grain in ("day", "week", "month") else _auto_grain(rows)

    if grain_used == "day":
        return rows, "day"

    # Phase 1: group by (risk_flag, period_key) and sum count fields
    buckets: dict[tuple[str, str], dict[str, Any]] = {}
    bucket_dates: dict[str, list[date]] = {}

    for row in rows:
        dt = datetime.strptime(row["date"], "%Y-%m-%d").date()
        pk = _period_key(dt, grain_used)
        rf = row["risk_flag"]
        key = (rf, pk)

        bucket_dates.setdefault(pk, []).append(dt)

        if key not in buckets:
            buckets[key] = {"risk_flag": rf, "_period_key": pk}
            for f in SUM_FIELDS:
                buckets[key][f] = 0

        for f in SUM_FIELDS:
            buckets[key][f] += row.get(f, 0)

    # Phase 2: compute total_rto_api_hits per period (across all risk flags)
    period_total_hits: dict[str, int] = {}
    for (rf, pk), agg in buckets.items():
        period_total_hits[pk] = period_total_hits.get(pk, 0) + agg["rto_api_hits"]

    # Phase 3: build output rows sorted chronologically
    result: list[dict[str, Any]] = []
    for (rf, pk), agg in sorted(buckets.items(), key=lambda item: (item[0][1], item[0][0])):
        agg["period_label"] = _period_label(pk, grain_used, bucket_dates[pk])
        agg["total_rto_api_hits"] = period_total_hits[pk]
        _recalculate_derived(agg)
        del agg["_period_key"]
        result.append(agg)

    return result, grain_used


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

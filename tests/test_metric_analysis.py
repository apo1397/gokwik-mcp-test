"""
Test script for the MCP server data tools.

Usage:
    python tests/test_metric_analysis.py

Requires:
    - Network access to GoKwik APIs
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date

from dotenv import load_dotenv

load_dotenv()

from src.config import Settings
from src.services.metric_analysis_service import MetricAnalysisService
from src.tools.get_metric_analysis_data import _parse_date_range


# ── Test inputs ──────────────────────────────────────────────────────────────
MERCHANT_MID = "19g6ilyznza4p"
MERCHANT_INT_ID = 5107
DATE_RANGE = "January 2026 to March 2026"


def test_date_parsing():
    print("=" * 60)
    print("1. DATE RANGE PARSING")
    print("=" * 60)

    today = date.today().isoformat()

    cases = [
        ("January 2026 to March 2026", today),
        ("March 2026", today),
        ("December 2025 to January 2026", today),
        (None, today),
    ]
    for dr, at in cases:
        fr, to = _parse_date_range(dr, at)
        print(f"  input={dr!r:>40s}  →  {fr} to {to}")

    print()


def test_metric_data_fetch(service: MetricAnalysisService):
    print("=" * 60)
    print("2. METRIC DATA FETCH + AGGREGATION")
    print("=" * 60)

    start = time.time()
    result = service.get_metric_analysis_data(
        merchant_mid=MERCHANT_MID,
        merchant_int_id=MERCHANT_INT_ID,
        date_range=DATE_RANGE,
    )
    elapsed = time.time() - start

    print(f"  Elapsed:      {elapsed:.2f}s")
    print(f"  Grain:        {result['grain']}")
    print(f"  Date range:   {result['date_range']}")
    print(f"  Row count:    {len(result['rows'])}")
    print(f"  Payload size: {len(json.dumps(result)):,} chars")
    print()

    print("  Rows:")
    for row in result["rows"]:
        print(f"    {row['period_label']:>20s} | {row['risk_flag']:>12s} | hits={row['rto_api_hits']:>8,} | orders={row['orders']:>6,} | CR={row['cr_pct']}% | COD={row['cod_share_pct']}% | RTO={row['rto_pct_overall']}%")
    print()


def test_kwikflows_analysis_data(service: MetricAnalysisService):
    print("=" * 60)
    print("3. KWIKFLOWS ANALYSIS DATA")
    print("=" * 60)

    start = time.time()
    result = service.get_kwikflows_analysis_data(
        merchant_mid=MERCHANT_MID,
        merchant_int_id=MERCHANT_INT_ID,
    )
    elapsed = time.time() - start

    print(f"  Elapsed:        {elapsed:.2f}s")
    print(f"  Total workflows: {result.get('total_workflows', 'N/A')}")
    print(f"  Active:          {result.get('active_workflows', 'N/A')}")
    print(f"  Payload size:    {len(json.dumps(result)):,} chars")
    print()

    for wf in result.get("workflows", []):
        rules_count = len(wf.get("rules", []))
        ab = " [AB TEST]" if wf.get("is_ab_test_enabled") else ""
        print(f"    {wf['workflow_name']}{ab} — {wf.get('workflow_flag', 'N/A')} ({rules_count} rules)")
    print()


def test_kwikflow_impact_data(service: MetricAnalysisService):
    print("=" * 60)
    print("4. KWIKFLOW IMPACT DATA")
    print("=" * 60)

    # First get workflows to find a rule_id
    workflows = service.get_workflows(merchant_mid=MERCHANT_MID, merchant_int_id=MERCHANT_INT_ID)
    rule_id = None
    for wf in workflows:
        for rule in wf.get("rules", []):
            if rule.get("rule_id"):
                rule_id = rule["rule_id"]
                print(f"  Using rule_id: {rule_id} from workflow: {wf.get('workflow_name')}")
                break
        if rule_id:
            break

    if not rule_id:
        print("  No rule_id found, skipping impact test")
        return

    start = time.time()
    result = service.get_kwikflow_impact_data(
        merchant_mid=MERCHANT_MID,
        merchant_int_id=MERCHANT_INT_ID,
        rule_id=rule_id,
    )
    elapsed = time.time() - start

    print(f"  Elapsed:      {elapsed:.2f}s")
    print(f"  Payload size: {len(json.dumps(result)):,} chars")

    if "error" in result:
        print(f"  Error: {result['error']}")
    else:
        print(f"  Workflow: {result.get('workflow', {}).get('workflow_name', 'N/A')}")
        impact = result.get("impact_metrics", {})
        if isinstance(impact, dict):
            print(f"  Impact keys: {list(impact.keys())}")
        elif isinstance(impact, list):
            print(f"  Impact entries: {len(impact)}")
        else:
            print(f"  Impact type: {type(impact).__name__}")
    print()


if __name__ == "__main__":
    settings = Settings.from_env()
    service = MetricAnalysisService(
        api_base_url=settings.api_base_url,
        api_auth_token=settings.api_auth_token,
        kwikflows_api_url=settings.kwikflows_api_url,
        kwikflows_impact_api_url=settings.kwikflows_impact_api_url,
    )

    test_date_parsing()
    test_metric_data_fetch(service)
    test_kwikflows_analysis_data(service)
    test_kwikflow_impact_data(service)

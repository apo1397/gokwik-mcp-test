"""
Test script for the metric analysis tool and LLM integration.

Usage:
    python tests/test_metric_analysis.py

Requires:
    - LLM_API_KEY (or GEMINI_API_KEY) in .env or environment
    - Network access to GoKwik APIs and LLM provider
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date

from dotenv import load_dotenv

load_dotenv()

from src.clients.gemini_client import build_chat_model
from src.config import Settings
from src.prompts.metric_analysis import build_metric_analysis_messages
from src.tools.get_metric_analysis_data import GetMetricAnalysisDataTool, _parse_date_range
from langchain_core.messages import HumanMessage, SystemMessage


# ── Test inputs ──────────────────────────────────────────────────────────────
MERCHANT_MID = "19g6ilyznza4p"
MERCHANT_INT_ID = 5107
DATE_RANGE = "January 2026 to March 2026"
QUESTION = "What is the hits contribution (percentage) and orders contribution (percentage) for High Risk segment across January, February, and March 2026?"


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


def test_data_fetch():
    print("=" * 60)
    print("2. API DATA FETCH + AGGREGATION")
    print("=" * 60)

    settings = Settings.from_env()
    tool = GetMetricAnalysisDataTool()
    analysis_today = date.today().isoformat()

    start = time.time()
    result = tool.run(
        merchant_mid=MERCHANT_MID,
        merchant_int_id=MERCHANT_INT_ID,
        api_base_url=settings.api_base_url,
        api_auth_token=settings.api_auth_token,
        analysis_today=analysis_today,
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

    return result


def test_prompt_build(tool_payload: dict):
    print("=" * 60)
    print("3. PROMPT CONSTRUCTION")
    print("=" * 60)

    messages = build_metric_analysis_messages(QUESTION, tool_payload)
    print(f"  System prompt: {len(messages[0][1]):,} chars")
    print(f"  Human prompt:  {len(messages[1][1]):,} chars")
    print(f"  Total:         {len(messages[0][1]) + len(messages[1][1]):,} chars")
    print()
    return messages


def test_llm_call(prompt_messages: list):
    print("=" * 60)
    print("4. LLM CALL (this may take a while)")
    print("=" * 60)

    settings = Settings.from_env()
    print(f"  Model:    {settings.llm_model}")
    print(f"  Base URL: {settings.llm_base_url}")

    llm = build_chat_model(
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
    )

    messages = [
        SystemMessage(content=prompt_messages[0][1]),
        HumanMessage(content=prompt_messages[1][1]),
    ]

    start = time.time()
    try:
        response = llm.invoke(messages)
        elapsed = time.time() - start
        answer = response.content if isinstance(response.content, str) else str(response.content)
        print(f"  Elapsed: {elapsed:.2f}s")
        print(f"  Response length: {len(answer):,} chars")
        print()
        print("  ── LLM RESPONSE ──")
        print(answer)
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ERROR after {elapsed:.2f}s: {type(e).__name__}: {e}")

    print()


if __name__ == "__main__":
    test_date_parsing()
    payload = test_data_fetch()
    prompt_msgs = test_prompt_build(payload)

    # Pass --no-llm to skip the slow LLM call
    if "--no-llm" not in sys.argv:
        test_llm_call(prompt_msgs)
    else:
        print("Skipping LLM call (--no-llm flag)")

#!/usr/bin/env python3
"""Test script to validate KwikFlows API endpoint and response mapping."""

import json
from typing import Any
import requests

# Test configuration
API_URL = "https://prod-rto-dashboard-v4.gokwik.io/v1/kwikai/workflow/rules"
AUTH_TOKEN = "rto$dash-board*prod"

# Test merchants
TEST_MERCHANTS = [
    {"mid": "19g6iluws3myg", "int_id": 3176, "name": "Rasayanam"},
]


def test_api_call(merchant_mid: str, merchant_int_id: int, merchant_name: str = "") -> dict[str, Any]:
    """Test the KwikFlows API endpoint."""
    print(f"\n{'='*70}")
    print(f"Testing {merchant_name or merchant_mid} (int_id: {merchant_int_id})")
    print(f"{'='*70}")

    headers = {
        "Authorization": AUTH_TOKEN,
        "merchant-mid": merchant_mid,
        "merchant-int-id": str(merchant_int_id),
        "user-type": "admin",
    }
    params = {"merchant_id": merchant_mid}

    try:
        print(f"\n1. API Call Details:")
        print(f"   URL: {API_URL}")
        print(f"   Method: GET")
        print(f"   Headers: {json.dumps({k: v if k != 'Authorization' else '***' for k, v in headers.items()}, indent=4)}")
        print(f"   Params: {json.dumps(params, indent=4)}")

        response = requests.get(API_URL, headers=headers, params=params, timeout=10)
        print(f"\n2. Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n3. Response Structure:")
            print(f"   Top-level keys: {list(data.keys())}")

            if "data" in data:
                data_keys = list(data["data"].keys())
                print(f"   data.* keys: {data_keys}")

                if "workflows" in data["data"]:
                    workflows = data["data"]["workflows"]
                    print(f"   Number of workflows: {len(workflows)}")

                    if workflows:
                        print(f"\n4. Sample Workflow Structure:")
                        sample_wf = workflows[0]
                        print(f"   Workflow keys: {list(sample_wf.keys())}")
                        print(f"   Sample workflow_id: {sample_wf.get('workflow_id')}")
                        print(f"   Sample rule_name: {sample_wf.get('rule_name')}")
                        print(f"   Sample is_enabled: {sample_wf.get('is_enabled')}")
                        print(f"   Number of rules: {len(sample_wf.get('rules', []))}")

                        if sample_wf.get("rules"):
                            sample_rule = sample_wf["rules"][0]
                            print(f"\n   Rule keys: {list(sample_rule.keys())}")
                            if "raw_data" in sample_rule:
                                raw_data = sample_rule["raw_data"]
                                print(f"   raw_data keys: {list(raw_data.keys())}")
                                print(f"   raw_data.priority: {raw_data.get('priority')}")
                                print(f"   raw_data.conditions length: {len(raw_data.get('conditions', []))}")
                                print(f"   raw_data.actions length: {len(raw_data.get('actions', []))}")

            print(f"\n5. Testing Response Mapping:")
            test_response_mapping(data)

            return {
                "status": "success",
                "status_code": response.status_code,
                "data": data,
            }
        else:
            print(f"   Error: {response.text[:200]}")
            return {
                "status": "error",
                "status_code": response.status_code,
                "error": response.text,
            }

    except requests.exceptions.RequestException as e:
        print(f"\n   Request Error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
        }
    except json.JSONDecodeError as e:
        print(f"\n   JSON Parse Error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
        }


def test_response_mapping(data: dict) -> None:
    """Test the mapping logic used in fetch_workflow_data."""
    if "data" not in data or "workflows" not in data["data"]:
        print("   ✗ Missing expected data structure")
        return

    workflows = data["data"]["workflows"]
    print(f"   Processing {len(workflows)} workflows...")

    processed_workflows = []
    for idx, wf in enumerate(workflows):
        try:
            processed_wf = {
                "workflow_id": wf.get("workflow_id"),
                "workflow_name": wf.get("rule_name"),
                "is_enabled": wf.get("is_enabled"),
                "rules": []
            }

            for rule in wf.get("rules", []):
                raw_rule = rule.get("raw_data", {})
                simplified_rule = {
                    "priority": raw_rule.get("priority"),
                    "conditions": [],
                    "actions": []
                }

                for cond in raw_rule.get("conditions", []):
                    simplified_cond = cond.copy()
                    if "values" in simplified_cond and isinstance(simplified_cond["values"], list):
                        if len(simplified_cond["values"]) > 20:
                            simplified_cond["values"] = simplified_cond["values"][:20] + ["... (truncated)"]
                    simplified_rule["conditions"].append(simplified_cond)

                simplified_rule["actions"] = raw_rule.get("actions", [])
                processed_wf["rules"].append(simplified_rule)

            processed_workflows.append(processed_wf)
            print(f"   ✓ Workflow {idx + 1}: {processed_wf['workflow_name']} (enabled: {processed_wf['is_enabled']}, rules: {len(processed_wf['rules'])})")

        except Exception as e:
            print(f"   ✗ Error processing workflow {idx + 1}: {str(e)}")

    print(f"\n   Summary: Successfully mapped {len(processed_workflows)} workflows")

    if processed_workflows:
        print(f"\n6. Mapped Workflow Sample (first workflow):")
        sample = processed_workflows[0]
        print(f"   {json.dumps(sample, indent=4)[:500]}...")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("KwikFlows API Test Suite")
    print("="*70)

    results = []
    for merchant in TEST_MERCHANTS:
        result = test_api_call(
            merchant_mid=merchant["mid"],
            merchant_int_id=merchant["int_id"],
            merchant_name=merchant.get("name", ""),
        )
        results.append({
            "merchant": merchant,
            "result": result,
        })

    print(f"\n\n" + "="*70)
    print("Test Summary")
    print("="*70)
    for item in results:
        status = "✓ PASS" if item["result"]["status"] == "success" else "✗ FAIL"
        merchant = item["merchant"]
        print(f"{status} - {merchant.get('name', merchant['mid'])} (int_id: {merchant['int_id']})")
        if item["result"]["status"] == "error":
            print(f"         Error: {item['result'].get('error', 'Unknown error')[:100]}")


if __name__ == "__main__":
    main()

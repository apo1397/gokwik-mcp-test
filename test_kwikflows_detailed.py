#!/usr/bin/env python3
"""Detailed inspection of KwikFlows API response."""

import json
import requests

# Test configuration
API_URL = "https://prod-rto-dashboard-v4.gokwik.io/v1/kwikai/workflow/rules"
AUTH_TOKEN = "rto$dash-board*prod"

MERCHANT_MID = "19g6iluws3myg"
MERCHANT_INT_ID = 3176


def get_detailed_response() -> dict:
    """Fetch detailed response from the API."""
    headers = {
        "Authorization": AUTH_TOKEN,
        "merchant-mid": MERCHANT_MID,
        "merchant-int-id": str(MERCHANT_INT_ID),
        "user-type": "admin",
    }
    params = {"merchant_id": MERCHANT_MID}

    response = requests.get(API_URL, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def main():
    """Display detailed response inspection."""
    print("\nFetching KwikFlows API Response...")
    data = get_detailed_response()

    print("\n" + "="*70)
    print("API Response - Top Level")
    print("="*70)
    print(f"statusCode: {data.get('statusCode')}")
    print(f"message: {data.get('message')}")
    print(f"error: {data.get('error')}")

    if "data" in data:
        print("\ndata structure:")
        print(f"  - workflows: {len(data['data']['workflows'])} workflows found")
        print(f"  - eida_reccomendations: {type(data['data']['eida_reccomendations']).__name__}")
        print(f"  - ab_control_enable: {data['data']['ab_control_enable']}")
        print(f"  - kwikflows_tier_config: {type(data['data']['kwikflows_tier_config']).__name__}")
        print(f"  - workflows_limits_config: {type(data['data']['workflows_limits_config']).__name__}")

    print("\n" + "="*70)
    print("Sample Workflow Details (First 3)")
    print("="*70)

    workflows = data["data"]["workflows"]
    for i, wf in enumerate(workflows[:3]):
        print(f"\nWorkflow {i + 1}: {wf['rule_name']}")
        print(f"  ID: {wf['workflow_id']}")
        print(f"  Enabled: {wf['is_enabled']}")
        print(f"  Type: {wf['type']}")
        print(f"  Created: {wf['created_at']}")
        print(f"  Rules: {len(wf['rules'])}")

        for j, rule in enumerate(wf["rules"]):
            raw_data = rule["raw_data"]
            print(f"\n  Rule {j + 1}:")
            print(f"    Priority: {raw_data['priority']}")
            print(f"    Conditions ({len(raw_data['conditions'])}):")
            for cond in raw_data["conditions"]:
                print(f"      - {cond['key']} {cond['operator']} {cond.get('value')}")
            print(f"    Actions ({len(raw_data['actions'])}):")
            for action in raw_data["actions"]:
                action_keys = list(action.keys())
                print(f"      - Keys: {action_keys}")

    print("\n" + "="*70)
    print("Full Response (JSON)")
    print("="*70)
    print(json.dumps(data, indent=2)[:3000] + "\n... (truncated)")


if __name__ == "__main__":
    main()

# KwikFlows API Test Report

**Date**: 2026-03-27
**Merchant**: Rasayanam (19g6iluws3myg / 3176)
**Status**: ✓ PASS

---

## Executive Summary

The KwikFlows API endpoint is functioning correctly and the response payload mapping is working as expected. All 9 workflows for Rasayanam were successfully fetched, parsed, and mapped.

---

## API Details

| Field | Value |
|-------|-------|
| **Endpoint** | https://prod-rto-dashboard-v4.gokwik.io/v1/kwikai/workflow/rules |
| **Method** | GET |
| **Auth Header** | rto$dash-board*prod |
| **Query Parameter** | merchant_id={merchant_mid} |
| **Required Headers** | Authorization, merchant-mid, merchant-int-id, user-type |

---

## Response Structure

### Top Level
- `statusCode`: 200 (Success)
- `message`: "Success"
- `error`: null
- `data`: Object containing workflows and configuration

### Data Object Keys
1. **workflows** - Array of workflow objects (9 found for Rasayanam)
2. **eida_reccomendations** - Dictionary of recommendations
3. **ab_control_enable** - Boolean flag (true)
4. **kwikflows_tier_config** - Tier configuration
5. **workflows_limits_config** - Workflow limits

---

## Workflow Structure

Each workflow contains:
```
{
  "rule_name": "string",           // Workflow name
  "workflow_id": "string",         // Unique ID
  "type": "CUSTOM",                // Workflow type
  "is_enabled": boolean,           // Active status
  "created_at": "ISO 8601",        // Creation timestamp
  "updated_at": "ISO 8601",        // Last update timestamp
  "is_ab_test_enabled": boolean,   // A/B test flag
  "workflow_flag": "string",       // Workflow classification
  "rules": [                       // Array of rules
    {
      "rule_id": "string",
      "raw_data": {
        "priority": integer,
        "conditions": [...],       // Array of conditions
        "actions": [...]           // Array of actions
      }
    }
  ]
}
```

---

## Response Mapping Test Results

### Test 1: Response Parsing ✓
- Successfully parsed JSON response
- All top-level keys accessible
- Data structure matches expected format

### Test 2: Workflow Extraction ✓
- Found 9 workflows for merchant
- All workflows have required fields
- Workflow IDs are valid

### Test 3: Rule Processing ✓
- All rules have raw_data structure
- Conditions properly nested
- Actions properly structured

### Test 4: Data Transformation ✓
Successfully mapped all workflows using current `fetch_workflow_data()` logic:
```
✓ Workflow 1: RTOScore 0.8 to 0.9 - partial cod 50 (enabled: True, rules: 1)
✓ Workflow 2: Past COD RTO (enabled: True, rules: 1)
✓ Workflow 3: COD Prompt all customers (enabled: True, rules: 1)
✓ Workflow 4: Testoboost | Pack of 1 | COD 50 Extra (enabled: False, rules: 1)
✓ Workflow 5: Testo boost Pack of 1 UPI discount (enabled: True, rules: 1)
✓ Workflow 6: Block COD (enabled: False, rules: 1)
✓ Workflow 7: RTO risk Gibberish Address (enabled: False, rules: 1)
✓ Workflow 8: Partial cod for risky pincodes >80% - 50 (enabled: False, rules: 1)
✓ Workflow 9: Cred Flow (enabled: False, rules: 1)
```

---

## Sample Workflow Analysis

### Workflow 1: RTOScore 0.8 to 0.9 - partial cod 50
- **Status**: Enabled
- **Type**: CUSTOM
- **Priority**: 1
- **Conditions**: 2
  - rto_score >= 0.8
  - rto_score <= 0.9
- **Actions**: 1 (ppcod_upi with 50 fixed deduction)

### Workflow 2: Past COD RTO
- **Status**: Enabled
- **Type**: CUSTOM
- **Priority**: 1
- **Conditions**: 1 (pincode contains)
- **Actions**: 3
  - cod_fees
  - cod_confirmation_prompt_configs
  - upi_discount

---

## Condition Structure

Sample condition from Workflow 1:
```json
{
  "key": "rto_score",
  "operator": ">=",
  "value": 0.8,
  "workflow_type": "RTO_RISK"
}
```

Observed operators:
- `>=` (greater than or equal)
- `<=` (less than or equal)
- `contains` (array contains)

---

## Action Structure

Actions have variable structure based on type:
```json
{
  "action": "ppcod_upi",           // Action type
  "ppcod_config": [                // Optional config array
    {
      "deductionType": "fixed",
      "fixedDeduction": 50
    }
  ]
}
```

Action types observed:
- `ppcod_upi` - Partial prepaid COD with UPI
- `allow_cod` - Allow COD payment
- `cod_fees` - COD fee configuration
- Others (various discount/prompt actions)

---

## Data Mapping Verification

The current `fetch_workflow_data()` function in `src/utils/data_transforms.py` correctly:
1. ✓ Handles the response structure
2. ✓ Extracts workflows array
3. ✓ Maps workflow_id and rule_name
4. ✓ Processes rules and raw_data
5. ✓ Handles conditions with value arrays
6. ✓ Truncates large condition value arrays (> 20 items)
7. ✓ Preserves all action data

---

## No Changes Required

The existing code in `fetch_workflow_data()` is working correctly with the current API endpoint and response format. No modifications needed for:
- Request headers
- Response parsing
- Data mapping
- Error handling

---

## Recommendations

1. **Test Script**: Created `test_kwikflows_api.py` for future validations
2. **Detailed Inspection**: Use `test_kwikflows_detailed.py` for debugging
3. **Error Handling**: Current code properly handles missing keys and empty arrays
4. **Response Caching**: Consider caching workflows if frequent API calls are made
5. **Monitoring**: Track API response times and status codes in production

---

## Test Environment

- Python 3.9
- requests library (HTTP client)
- Endpoint: Production (prod-rto-dashboard-v4.gokwik.io)
- Test Date: 2026-03-27

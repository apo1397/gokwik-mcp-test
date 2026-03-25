# RTO and KwikFlows Metric Analysis - Guidance v2.0

This resource provides critical context for analyzing RTO (Return to Origin) and KwikFlows metrics. Follow these requirements strictly to ensure accurate insights.

## Critical Data Maturity Guardrail

**⚠️ BEFORE ANY ANALYSIS, CHECK DATA MATURITY:**

- **RTO metrics mature after 15 days** from the order delivery attempt date
- **COD RTO metrics mature after 15 days** from the COD payment attempt date
- **Conversion Rate (CR %), Prepaid Share %, and other derived metrics** also mature on the same 15-day cycle

### Maturity Rules

| Date Range | Status | Analysis Guidance |
|---|---|---|
| 16+ days old | ✅ Mature | Full analysis allowed |
| 8-15 days old | ⚠️ Approaching Maturity | Acceptable for trends, flag as preliminary |
| 0-7 days old | ❌ Immature | Only mention if explicitly requested; mark as "preliminary" |

**User Notification Template:**
> "Note: Data from [DATE RANGE] is still maturing. Figures may shift as delivery attempts continue. Fully mature data available for [MATURE DATE RANGE]."

### What to Do with Immature Data

1. **DO NOT** draw definitive conclusions about immature periods
2. **DO NOT** compare immature data to mature data as if they're equivalent
3. **DO** prioritize analysis of mature data in your response
4. **DO** clearly label any immature data as "preliminary" or "subject to change"
5. **DO** offer to re-analyze once data matures if the user requests

---

## Core Requirements

Before calling any tools, ensure you have:

1. **Merchant MID**: Alphanumeric identifier (e.g., `12wyqc2guqmkrw6406j`). 
   - Ask if missing: "What is your Merchant MID?"

2. **Merchant Int ID**: Integer identifier (e.g., `90`). 
   - Ask if missing: "What is your Merchant Integer ID?"

3. **Date Range**: Specify month(s) for analysis (e.g., "January 2026" or "January 2026 to March 2026").
   - Prefer monthly grain for stability
   - If requesting recent data: ask "Which months would you like analyzed?" and clarify maturity expectations

4. **Analysis Scope**: Clarify what the user wants to analyze.
   - Single metric (RTO only)?
   - Multi-dimensional (RTO + Conversion + COD performance)?
   - Risk segment comparison?
   - Trend analysis across months?

---

## Multi-Dimensional Analysis Framework

Move beyond RTO-only insights. Request and analyze these dimensions:

### Primary Metrics

| Metric | Definition | Good Range | Red Flag |
|---|---|---|---|
| **RTO %** | % of orders returned to origin | <10% (Low Risk), <20% (Medium), <30% (High Risk) | >25% indicates logistics/fulfillment issues |
| **Conversion Rate (CR %)** | % of orders successfully delivered | >60% overall | <50% suggests high cancellations or null-status orders |
| **Prepaid Share %** | % of orders paid upfront (non-COD) | >40% | <30% means over-reliance on COD (high risk) |
| **COD Share %** | % of orders as Cash on Delivery | Monitor closely | >70% increases RTO risk significantly |
| **COD RTO %** | RTO specific to COD orders | <15% (Low Risk) | >30% indicates cash collection risk |

### Secondary Dimensions to Analyze

1. **Risk Segment Performance** (High, Medium, Low)
   - Compare RTO, CR%, and Prepaid Share across risk tiers
   - Identify which segment is underperforming

2. **Prepaid vs COD Comparison**
   - Prepaid orders typically have lower RTO
   - If prepaid RTO is high, investigate quality/logistics issues
   - If COD RTO is very high, consider payment/trust issues

3. **Order Status Distribution**
   - `delivered_orders`: Orders successfully completed
   - `pending_orders`: Orders still in transit (normal for recent dates)
   - `null_status_orders`: Orders with no status update (potential data quality issue)
   - `cancelled_orders`: Customer or system cancellations
   - **Red flag**: >20% null_status orders suggests tracking/data gaps

4. **Month-over-Month Trends**
   - Is RTO improving, declining, or stable?
   - Are CR% and prepaid share moving in the right direction?
   - Seasonality patterns?

5. **AWB (Air Waybill) Fill Rate** (if available)
   - Low fill rate = missing tracking data
   - May underreport true RTO
   - Always note if tracking coverage is incomplete

---

## Common Terms & Definitions

- **RTO %**: Percentage of orders returned to origin. Higher = worse fulfillment.
- **CR % (Conversion Rate)**: Percentage of orders successfully delivered and completed.
- **Prepaid Share %**: Percentage of orders paid upfront (includes cards, wallets, UPI). Lower risk than COD.
- **COD (Cash on Delivery)**: Orders collected at delivery point. Higher RTO risk.
- **COD RTO %**: Return rate specific to COD orders.
- **Risk Flags (High, Medium, Low)**: Traffic segments based on predicted RTO risk.
  - *High Risk*: Historical high RTO, low prepaid, risky customer profile
  - *Medium Risk*: Mixed signals, moderate RTO
  - *Low Risk*: Historical low RTO, high prepaid, stable customer base
- **Pending Orders**: Orders still being delivered (not yet failed or succeeded).
- **Null Status Orders**: Orders with no delivery update (data quality concern or stuck shipments).
- **API Hits**: Number of status check API calls made for orders in this segment.

---

## Multi-Metric Analysis Workflow

### Step 1: Data Collection
```
Call get_metric_analysis_data with:
- merchant_mid
- merchant_int_id
- date_range (only mature months, or specify if including preliminary data)
```

### Step 2: Data Maturity Check
- For each month in the result, verify it's 16+ days old
- Flag immature periods clearly
- Prioritize mature data in findings

### Step 3: Risk Segment Breakdown
Analyze each risk segment (High, Medium, Low):
- What is the RTO trend?
- What is the CR% and prepaid share?
- Is this segment performing better/worse than others?
- What's the ratio of null_status to pending orders?

### Step 4: Trend Analysis
- Compare month-over-month changes in:
  - Overall RTO
  - Risk segment distribution
  - Prepaid vs COD balance
  - CR% and delivery success
- Identify patterns: improving, declining, seasonal, cyclic?

### Step 5: Root Cause Insights
- High RTO in Low-Risk segment? → Logistics quality issue
- High RTO in High-Risk segment only? → Risk segmentation working correctly
- High null_status orders? → Tracking data gap or fulfillment bottleneck
- Declining CR% with rising pending orders? → System processing delay or backlog

---

## When to Use Each Tool

### `get_metric_analysis_data`
- User asks for raw data or dashboards
- You need structured numbers before analysis
- User wants to explore multiple metrics themselves
- Large date ranges requiring trend analysis

### `analyze_monthly_risk_flag_metrics`
- User asks a specific question ("Why is my RTO high?" "Which segment is underperforming?")
- You need AI-assisted analysis of trends and patterns
- User wants actionable insights with context
- Complex multi-month comparisons

---

## Handling Missing Information

### Scenario 1: Missing Merchant IDs
**User:** "How is my business doing?"

**Response:** 
> "I'd be happy to analyze your RTO and KwikFlows metrics! To get started, I need:
> 1. Your **Merchant MID** (alphanumeric ID like `12wyqc2guqmkrw6406j`)
> 2. Your **Merchant Integer ID** (numeric ID like `90`)
> 3. Which month(s) would you like analyzed? (e.g., January 2026, or January-March 2026?)
> 
> Once you provide these, I can analyze RTO, conversion rates, prepaid vs COD performance, and identify trends."

### Scenario 2: Requesting Current Month Data
**User:** "What's my RTO for March 2026?" (asked on March 25)

**Response:** 
> "I can pull March data, but keep in mind:
> - Only data from **March 1-10** is mature (16+ days old)
> - Data from **March 11 onwards** is still settling (less than 15 days)
> 
> I recommend focusing on **February 2026** (fully mature) for reliable insights. If you'd like, I can show preliminary March trends alongside February for context."

### Scenario 3: Immature Data Explicitly Requested
**User:** "I need yesterday's numbers for an urgent review."

**Response:** 
> "Yesterday's data is immature and highly volatile. However, here's what I can show:
> 
> **[PRELIMINARY - Subject to Change]**
> - Current snapshot: [brief preliminary metrics]
> - **Caveat**: These numbers will likely shift significantly over the next 10-14 days as delivery attempts complete
> 
> **Recommendation**: For actionable decisions, use data that's 16+ days old ([mature date range]). I can re-analyze this with final numbers once it matures."

---

## KwikFlows Workflow Analysis

KwikFlows allows merchants to set up automated rules for order validation.
- **Structure**: Workflows are made of rules. Each rule has **Conditions** (segment) and **Actions** (outcome).
- **Priority**: Rules within a workflow are sorted by priority. The first rule whose conditions are met is executed.
- **Serialization**: Requests pass through workflows in a serial priority. Only the action of the first breached condition is implemented.
- **Array Truncation**: When listing workflows, arrays (like lists of pincodes) longer than 20 items are truncated to keep the context clean.

## Troubleshooting

| Issue | Cause | Resolution |
|---|---|---|
| Empty results from tool | Invalid merchant IDs or date range with no data | Verify merchant_mid and merchant_int_id; try different date range |
| Very low conversion rates (<30%) | High pending or null_status orders | Check order fulfillment status; investigate logistics delays |
| Null_status orders >20% | Tracking data not syncing or fulfillment stuck | Contact logistics partner; check data pipeline health |
| RTO immature but user insists on analysis | User under time pressure | Clearly label as "preliminary"; offer to re-analyze with mature data; suggest using recent but mature months instead |
| Huge variance between High/Medium/Low risk | Risk segmentation working as designed | This is expected; focus on improving High-Risk segment |
| AWB fill rate low (if visible) | Tracking not integrated or partners not reporting | Note in findings: "True RTO may be higher due to incomplete tracking coverage" |

---

## Analysis Output Template

### Structure for Reports
1. **Data Maturity Notice** (if applicable)
   - Which periods are mature? Which are preliminary?

2. **Executive Summary**
   - Overall RTO trend (improving/declining/stable)
   - Key metric snapshot (CR%, Prepaid Share, COD RTO)

3. **Risk Segment Breakdown**
   - High Risk: [RTO, CR%, Prepaid Share]
   - Medium Risk: [RTO, CR%, Prepaid Share]
   - Low Risk: [RTO, CR%, Prepaid Share]
   - Comparison: Which segment is dragging down overall metrics?

4. **Trends & Patterns**
   - Month-over-month changes
   - Notable anomalies or turning points
   - Data quality flags (null_status spikes, etc.)

5. **Root Cause Hypotheses**
   - Why is metric X moving that way?
   - What operational factors could explain the trend?

6. **Recommendations**
   - Which segment needs intervention?
   - Specific actions (reduce COD, improve logistics, adjust pricing)?
   - Metrics to monitor going forward

---

## Key Reminders

✅ **DO:**
- Always check data maturity before drawing conclusions
- Analyze across multiple metrics (not just RTO)
- Break down findings by risk segment
- Compare prepaid vs COD performance
- Flag data quality issues (null_status, low AWB fill)
- Recommend re-analysis once immature data matures

❌ **DON'T:**
- Draw definitive conclusions from <8 day old data
- Compare mature and immature data as if equivalent
- Analyze RTO in isolation (needs context of CR%, Prepaid Share, COD RTO)
- Guess missing merchant IDs
- Proceed without knowing which months user wants analyzed
- Ignore null_status spikes or data quality warnings
# GoKwik RTO & KwikFlows - Business Context & Logic v2.0

This document provides internal business rules and logic for interpreting RTO (Return to Origin) and KwikFlows metrics. Use this to deliver insightful, context-aware analysis with proper risk acknowledgment.

---

## Risk Segment Behavior & Expectations

The RTO risk flags (High, Medium, Low) are predictive based on historical patterns. Actual performance should follow these directional patterns:

### Expected Metric Ranges by Risk Segment

| Metric | High Risk | Medium Risk | Low Risk | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **RTO %** | 25% - 40%+ | 10% - 20% | < 8% | Represents failed delivery + customer returns |
| **Prepaid Share %** | < 20% | 30% - 50% | > 60% | Higher prepaid = lower RTO risk |
| **COD Share %** | 60% - 90%+ | 40% - 60% | 20% - 40% | Inverse of prepaid; higher COD = higher RTO |
| **Conversion Rate (CR %)** | 30% - 50% | 50% - 65% | 65% - 80%+ | Delivery success rate |
| **COD RTO %** | 30% - 50%+ | 15% - 25% | < 10% | Critical metric; COD-specific returns |

---

## Critical Validation Rules (Red Flags)

These indicate data quality issues, model degradation, or operational problems. Always investigate and report.

### 1. **Low Risk RTO > 10%** ⚠️
**What it means:** Low Risk segment is under-performing expectations.

**Likely causes:**
- Logistics partner quality degradation
- NDR (Non-Delivery Report) management breakdown
- Model drift (segment classification may be stale)
- Address quality issues in Low Risk customer base
- Data tracking gap (AWB not being captured)

**Action:**
- Investigate logistics partner performance for this segment
- Check AWB fill rate for Low Risk orders
- Audit recent customer base shifts in Low Risk segment
- If systemic: may indicate model needs retraining

---

### 2. **High Risk Segment with >80% COD Share** ⚠️
**What it means:** Dangerous concentration of risky payment behavior.

**Impact:** Overall merchant RTO will spike significantly, regardless of other improvements.

**Why this happens:**
- Risk model predicted high RTO → merchant forced to use COD for payment guarantee
- OR merchant deliberately targeting high-COD segments (risky strategy)
- Creates feedback loop: High COD → Higher RTO → Less prepaid adoption

**Action:**
- Consider disabling/limiting COD for High Risk segment
- Implement stricter COD verification (OTP, address verification)
- Offer incentives to shift High Risk segment toward prepaid
- Monitor if High Risk grows as percentage of overall traffic

---

### 3. **Prepaid RTO > 3%** 🚨
**What it means:** CRITICAL data quality or fraud issue.

**Why this is wrong:** Prepaid orders should have near-zero RTO (customer already paid, low incentive to return).

**Likely causes:**
- Data tracking error (prepaid orders misclassified as COD returns)
- Refund/chargeback fraud detection (prepaid customers disputing charges)
- System error in payment status classification
- Partner integration issue (payment status not syncing)

**Action:**
- STOP analysis immediately and escalate to data team
- Do NOT make business decisions based on these metrics
- Verify merchant_mid and date range are correct
- Check if prepaid definition has changed
- Request data quality audit before proceeding

---

### 4. **Order Status Distribution Anomaly** ⚠️

| Status | Normal Range | Red Flag Range | Investigation |
| :--- | :--- | :--- | :--- |
| **Pending Orders** | 5% - 15% of total | > 30% | Fulfillment backlog or system delay |
| **Null Status Orders** | < 5% of total | > 15% | Tracking data not syncing, partner integration issue |
| **Cancelled Orders** | 2% - 8% of total | > 15% | Customer churn, payment failures, or system issue |
| **Delivered Orders** | 70% - 90% of total | < 60% | Combined effect of pending/null/cancelled spike |

**Action:** High null_status orders invalidate RTO analysis; request data refresh or note caveat in findings.

---

### 5. **CR % Declining While RTO Climbing** ⚠️
**What it means:** Possible negative feedback loop or operational breakdown.

**Pattern:** 
- CR% down (fewer successful deliveries)
- RTO% up (more returns)
- Pending orders increasing

**Likely causes:**
- Logistics partner struggling with volume
- Address quality degradation
- Fulfillment bottleneck or inventory issues
- System performance issues (slow API, tracking delays)

**Action:**
- Identify if trend started after a specific event (sale, partner change, system update)
- Check if correlated with traffic growth or geographic expansion
- Assess logistics partner capacity
- May indicate need for fulfillment partner change

---

### 6. **AWB Fill Rate < 95%** ⚠️
**What it means:** Tracking data is incomplete; RTO figures are likely under-reported.

**Why it matters:** If 10% of orders aren't tracked, actual RTO could be 10-15% higher than reported.

**Action:**
- Always flag in analysis: "True RTO may be [X% higher] due to incomplete tracking coverage"
- Request missing AWB data from logistics partner
- Do not make aggressive business decisions without tracking coverage
- Prioritize fixing data pipeline over analyzing incomplete data

---

## Metric Interpretation Nuances

### CR % vs. RTO % Relationship
**Rule:** An increase in CR% often correlates with an increase in RTO%

**Why:** As conversion improves, merchant captures "lower quality" traffic segments (geographic expansion, age group changes, price point changes). This new cohort may have higher RTO even though overall CR improved.

**Example:**
- Month 1: CR 60%, RTO 12%, focused on metros
- Month 2: CR 65%, RTO 15%, expanded to Tier 2 cities
- Appears bad (RTO up), but actually acceptable—quality-adjusted

**Interpretation:** When analyzing, separate organic improvement (operational) from cohort shift (natural expansion effect).

---

### Prepaid vs. COD Dynamics
**Core Rule:** Prepaid orders have near-zero RTO (0-2%). Any deviation indicates data/fraud issues.

**Healthier Pattern:** Increasing prepaid share while maintaining/reducing overall RTO

| Scenario | Interpretation | Action |
| :--- | :--- | :--- |
| Prepaid ↑, Overall RTO ↓ | Excellent; risk reduction through payment method shift | Sustain strategy |
| Prepaid ↓, Overall RTO ↑ | Concerning; forced back to riskier COD | Investigate why prepaid declining |
| Prepaid flat, COD RTO ↑ | Logistics/operations issue, not payment-related | Fix fulfillment, not payment terms |
| Prepaid RTO ↑ | DATA ERROR or fraud—investigate immediately | Escalate to data team |

---

### Seasonality & Event Impact

**Expected RTO Movement During High-Traffic Events:**

| Event | Expected RTO Impact | Duration | Why | Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| **Diwali, Holi, Festival** | +3-8% | 5-10 days post-event | Impulse purchases, lower quality customers | Tighten verification; reduce COD limits |
| **Big Billion Days (BBD)** | +5-10% | Event week + 2 weeks settlement | High volume stress, logistics bottleneck | Pre-arrange logistics capacity; QA increase |
| **New Product Launch** | +2-5% | 10-20 days | Uncertain demand, new customer cohort | Monitor cohort separately; lower COD% |
| **Logistics Partner Change** | +5-15% | 5-20 days | Integration issues, training period | Parallel run with old partner; monitor closely |
| **Geographic Expansion** | +2-6% | Ongoing | New region may have different logistics, payment preferences | Separate analysis by region; adjust expectations |

**Analysis Note:** When reporting RTO during/after events, always contextualize:
> "RTO is X% during BBD (expected +5-10% above baseline). Baseline performance would be ~Y%. Improvement plan: [...]"

---

## What "Good" Looks Like

### Benchmark Targets (by Merchant Maturity)

| Metric | Early Stage | Growth | Mature | Excellent |
| :--- | :--- | :--- | :--- | :--- |
| **Overall RTO %** | < 25% | < 20% | < 15% | < 10% |
| **COD RTO %** | < 35% | < 28% | < 20% | < 12% |
| **CR % (Conversion)** | > 50% | > 60% | > 70% | > 80% |
| **Prepaid Share %** | 30%+ | 40%+ | 50%+ | 60%+ |
| **Low Risk RTO %** | < 10% | < 8% | < 6% | < 4% |
| **AWB Fill Rate %** | > 90% | > 95% | > 98% | > 99% |

**Note:** Targets vary by product category (apparel RTO different from electronics). Use industry benchmarks for context.

---

## Segment-Specific Analysis Patterns

### High Risk Segment Strategy

**Expected state:** High RTO (25-40%), but should decrease over time with interventions.

**Healthy trajectory:**
```
Month 1: High Risk RTO 35%, COD 85%, Prepaid 15%
Month 2: High Risk RTO 33%, COD 80%, Prepaid 20%
Month 3: High Risk RTO 30%, COD 75%, Prepaid 25%
→ Trend: Successful de-risking through prepaid incentives
```

**Red flags in High Risk:**
- RTO increasing instead of decreasing (losing control)
- COD share growing (opposite of strategy)
- Prepaid incentives not working (stuck at <20%)
- Segment size growing too fast (volume outpacing quality improvements)

---

### Low Risk Segment Health

**Expected state:** Low RTO (<8%), high prepaid (>60%), stable.

**When Low Risk RTO increases:**

| RTO Increase | Likely Cause | Evidence to Look For | Fix |
| :--- | :--- | :--- | :--- |
| 8-10% | Model staleness | Low Risk cohort composition shifted | Retrain risk model |
| 10-15% | Logistics issue | AWB fill ↓, null_status ↑ | Partner quality audit |
| 15%+ | Structural problem | Sustained over 2+ months | Operational review needed |

---

### Medium Risk as Bellwether

**Role:** Medium Risk often indicates broader trends before they show in High/Low.

**Use Medium Risk to detect:**
- Emerging logistics issues (Medium RTO increasing first)
- Seasonal sensitivity (Medium RTO more volatile than others)
- Cohort quality shifts (Medium prepaid share movements)
- Model performance (Medium is least stable, most sensitive to changes)

---

## Root Cause Framework

Use this decision tree when RTO/metrics are abnormal:

### Step 1: Isolate the problem
```
Is RTO increasing?
├─ YES → Step 2a (Segment-specific or overall?)
└─ NO → Check CR%, Prepaid Share (different issue)

Is problem in specific segment only?
├─ High Risk only → Step 3a (Model or operational?)
├─ Low Risk only → Step 3b (Logistics or tracking?)
├─ COD-specific → Step 3c (Payment or verification?)
└─ All segments → Step 3d (Systemic issue)
```

### Step 2a: Is it segment-specific or overall RTO rising?
```
Segment-Specific (one risk tier):
├─ Likely: Operational issue in that cohort
├─ Check: Prepaid/COD mix, geography, product category
└─ Action: Targeted intervention for that segment

Overall RTO Rising:
├─ Likely: Logistics partner degradation OR traffic composition shift
├─ Check: AWB fill rate, logistics partner metrics, new geographies
└─ Action: Partner audit or traffic composition analysis
```

### Step 3a: High Risk RTO up (Segment-specific analysis)
```
Is COD RTO increasing?
├─ YES → Payment verification/fraud issue
│   └─ Action: Tighten OTP, address checks, ID verification
├─ NO but prepaid declining → Forced back to COD
│   └─ Action: Increase prepaid incentives, simplify checkout
└─ Model issue → High Risk segment changed composition
    └─ Action: Retrain risk model with latest data
```

### Step 3b: Low Risk RTO up (Logistics red flag)
```
Check AWB fill rate and null_status:
├─ AWB fill < 95% → Tracking data gap
│   └─ Action: Fix data pipeline with partner
├─ Null_status > 15% → Orders stuck in system
│   └─ Action: Investigate fulfillment bottleneck
├─ Both normal → Actual logistics degradation
│   └─ Action: Logistics partner audit and capacity planning
└─ NDR increasing → Non-delivery management failure
    └─ Action: Partner retry policy review
```

### Step 3c: COD RTO up (Payment/verification)
```
Check if correlated with:
├─ New geographic expansion → Adjust for region
├─ Increased volume → May need stricter verification
├─ Prepaid decline → Forced composition shift to COD
└─ Amount limit changes → Verification rules may be loose
    └─ Action: Tighten verification for higher COD amounts
```

### Step 3d: All segments RTO up (Systemic issue)
```
Diagnosis:
├─ Logistics partner change/degradation → Get capacity report
├─ Seasonal event impact → Check event calendar, expect normalization
├─ Data quality degradation → Check AWB fill, null_status
├─ Traffic surge without capacity → Discuss volume limits with partner
└─ System integration issue → Check API logs, webhook failures
    └─ Action: Data pipeline audit
```

---

## Actionable Recommendations Framework

### If RTO is HIGH in High Risk Segment
**Diagnosis:** Expected behavior, but should be actively managed down.

**Options (in priority order):**
1. **Tighten COD verification** (most cost-effective)
   - Require OTP confirmation before delivery
   - Add address verification (pincode match, phone call)
   - Blacklist serial returners or high-risk locations

2. **Shift payment method mix toward prepaid**
   - Offer 5-10% prepaid discount
   - Make prepaid default, COD optional
   - Remove COD for specific address patterns

3. **Reduce High Risk segment traffic** (if unwilling to manage)
   - Disable COD for zip codes with >40% RTO
   - Increase minimum order value for High Risk
   - Geographic restrictions

4. **Partner with alternate logistics** (if partner-specific issue)
   - Test parallel partner for High Risk segment
   - Get separate SLA for this cohort
   - Performance-based incentives

**When to escalate:** If High Risk RTO > 45% and not improving after 30 days of intervention.

---

### If RTO is HIGH in Low Risk Segment
**Diagnosis:** DATA ISSUE or LOGISTICS FAILURE—not expected, urgent investigation required.

**First: Validate data integrity**
- Confirm AWB fill rate > 95%
- Check null_status orders < 5%
- Verify prepaid RTO is near-zero (should be)

**If data is clean:**
1. **Logistics partner quality audit** (most likely cause)
   - Request performance metrics by geography
   - Check RTOs by delivery partner within network
   - Identify underperforming zones/partners

2. **Customer segmentation analysis**
   - Did Low Risk cohort composition change?
   - New geographic expansion affecting Low Risk?
   - Age/category shift in Low Risk?
   - May need to retrain risk model

3. **NDR (Non-Delivery Report) management**
   - Are failed deliveries being retried?
   - Return window management
   - Pickup point effectiveness

**When to escalate:** If Low Risk RTO exceeds 10% for 2+ consecutive weeks.

---

### If CR % is DECLINING while RTO is INCREASING
**Diagnosis:** Operational breakdown or system stress.

**Investigation priority:**
1. Check fulfillment status distribution
   - Are pending orders accumulating? → Volume/capacity issue
   - Are null_status orders spiking? → Data pipeline problem
   - Are cancelled orders rising? → Customer churn or payment failures

2. Correlate with external events
   - Did this coincide with sales event? → Expected, should normalize
   - Partner change or maintenance? → Integration issue
   - Traffic surge without capacity? → Discuss limits with logistics partner

3. Geographic analysis
   - Is problem in specific region? → Regional partner issue
   - Widespread? → Systemic operational issue

**Recommendation:** This pattern often precedes customer complaints and churn. High priority to resolve within 7 days.

---

### If Prepaid Share is DECLINING
**Diagnosis:** Customers gravitating back to COD; may indicate trust/UX issue.

**Investigation:**
1. **Is it voluntary or forced?**
   - Check payment failure rates (declined transactions)
   - Check checkout abandonment rate for prepaid
   - Are prepaid incentives still active?

2. **Payment method quality:**
   - Did prepaid options reduce? (e.g., wallet down)
   - Are payment flows working? (test personally)
   - Is there a new competitor offering better prepaid terms?

3. **Cohort shift:**
   - Did traffic mix change to more rural/unbanked areas?
   - New product categories with different payment preferences?
   - Geographic expansion to regions with lower digital adoption?

**Action:** Declining prepaid share is concerning because overall RTO will increase. Prioritize fixing this.

---

## Analysis Quality Checklist

Before delivering findings, verify:

- [ ] **Data maturity checked** (all periods 16+ days old, or marked preliminary?)
- [ ] **No red flag metrics ignored** (prepaid RTO, null_status spike, AWB fill <95%?)
- [ ] **Segment breakdown included** (High/Medium/Low analysis, not just overall?)
- [ ] **Prepaid vs. COD comparison made** (payment method impact analyzed?)
- [ ] **Seasonality/events considered** (is this during a known event?)
- [ ] **Trend direction identified** (improving, declining, stable?)
- [ ] **Root cause hypothesized** (operational, logistics, payment, or model issue?)
- [ ] **Contextual benchmarks provided** (is this normal for their stage/category?)
- [ ] **Recommendations prioritized** (by impact and cost to implement?)
- [ ] **Data quality caveats noted** (AWB fill, null_status, tracking gaps?)
- [ ] **Month-over-month comparison included** (not just absolute numbers?)
- [ ] **Action items are specific** (not "improve RTO" but "tighten OTP verification")

---

## When to Recommend Re-Analysis

**Suggest re-analysis after:**
- Data matures (immature periods now become mature)
- Intervention implemented (want to measure impact)
- External event resolves (sales event ends, partner integrated)
- Seasonal baseline shift (e.g., post-festival normalization)
- Risk model retraining (segment definitions may change)

**Always offer:** "Once [condition] settles, I can re-analyze with updated data."
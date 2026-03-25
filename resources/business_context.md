# GoKwik RTO & KwikFlows - Business Context & Logic

This document provides the internal business rules and logic for interpreting RTO (Return to Origin) and KwikFlows metrics. Use this to provide more insightful analysis.

## Risk Segment Behavior

The RTO risk flags (High, Medium, Low) are predictive. Actual performance should follow these directional patterns:

| Metric | High Risk | Medium Risk | Low Risk |
| :--- | :--- | :--- | :--- |
| **RTO %** | 25% - 40%+ | 10% - 20% | < 8% |
| **Prepaid Share %** | < 20% | 30% - 50% | > 60% |
| **Conversion (CR %)** | Low | Moderate | High |
| **COD RTO %** | Very High | Moderate | Low |

### Key Observations
-   **Low Risk RTO**: If Low Risk RTO is > 10%, it indicates either a data tracking issue or a breakdown in the predictive model for that specific merchant.
-   **High Risk COD Exposure**: If High Risk traffic has > 80% COD share, the overall RTO for the merchant will likely spike regardless of other factors.

## Metric Interpretation Nuances

-   **CR % vs. RTO %**: A sudden increase in Conversion Rate (CR%) often comes with an increase in RTO%, as the merchant might be capturing "lower quality" traffic.
-   **Prepaid vs. COD**: Prepaid orders have near-zero RTO. Any significant RTO in prepaid segments should be flagged as a critical data error.
-   **Seasonality**: RTO typically increases during major sale events (e.g., Diwali, BBD) due to higher impulse purchases and logistical delays.

## What "Good" Looks Like
-   **Overall RTO**: For a healthy D2C brand, overall RTO should ideally be below **15-18%**.
-   **COD RTO**: Below **20-25%** is considered excellent for COD segments.
-   **AWB Fill Rate**: Should always be > **95%**. Anything lower means the RTO numbers are likely under-reported because delivery outcomes aren't being tracked properly.

## Actionable Recommendations
-   If RTO is high in **High Risk**: Recommend tightening COD verification or disabling COD for that segment.
-   If RTO is high in **Low Risk**: Investigate NDR (Non-Delivery Report) management and logistical partner performance.

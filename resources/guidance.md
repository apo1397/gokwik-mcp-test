# RTO and KwikFlows Metric Analysis - Guidance

This resource provides additional context for the RTO (Return to Origin) and KwikFlows analysis tools. Use this if you are unable to proceed with a user's request.

## Core Requirements

Before calling any tools, ensure you have:
1.  **Merchant MID**: This is an alphanumeric identifier (e.g., `12wyqc2guqmkrw6406j`). If missing, ask the user.
2.  **Merchant Int ID**: This is an integer identifier (e.g., `90`). If missing, ask the user.
3.  **Date Range**: The analysis works best on a monthly grain. Ask for specific months like "January 2026".

## Handling Missing Information

If a user asks a general question like "How is my business doing?" without providing both merchant IDs and a date range:
-   **DO NOT** guess the merchant IDs.
-   **DO NOT** proceed with only one ID.
-   **DO** ask the user: "Could you please provide your Merchant MID, Merchant Integer ID, and the month(s) you'd like me to analyze?"

## Common Terms & Definitions

-   **RTO %**: The percentage of orders that were returned to the origin. High RTO is generally bad.
-   **Prepaid Share %**: The percentage of orders paid upfront. Higher prepaid share usually leads to lower RTO.
-   **COD (Cash on Delivery)**: Orders paid at the door. These have a much higher risk of RTO.
-   **Risk Flags (High, Medium, Low)**: Segments of traffic based on predicted RTO risk. 
    -   *High Risk*: Expect high RTO, low prepaid share.
    -   *Low Risk*: Expect low RTO, high prepaid share.

## Troubleshooting

-   **Empty Results**: If a tool returns no data, check if the `merchant_id` exists in the `sample_data/risk_flag_summary.csv` file.
-   **Data Maturity**: RTO metrics take about 15 days to "mature". If analyzing the current month, warn the user that the numbers might change as more delivery attempts are made.
-   **AWB Fill Rate**: If this is low, it means tracking data is missing, and the reported RTO might be lower than reality.

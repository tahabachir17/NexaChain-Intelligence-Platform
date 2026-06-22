# Business Questions and Hypotheses

## High-Priority Business Questions

1. Which vendors represent the highest operational and financial risk?
   - Hypothesis: vendors with low on-time delivery, high disruption counts, and poor financial stability contribute disproportionately to delays and margin erosion.

2. Which products and warehouses experience recurring stockouts?
   - Hypothesis: stockouts are concentrated in a subset of high-demand SKUs with long vendor lead times and weak reorder settings.

3. Which factors are associated with delivery delays?
   - Hypothesis: fulfillment channel, vendor, region, warehouse availability, and product category influence delay risk.

4. Which business segments contribute most to profitability?
   - Hypothesis: a small number of product categories, regions, or customer segments drive most gross margin and EBITDA contribution.

5. How does vendor performance affect inventory health?
   - Hypothesis: vendors with longer and more volatile lead times are linked to lower days of supply and more stockout events.

6. Which operational conditions are associated with negative order values or weak margins?
   - Hypothesis: returns, pricing issues, discounting, and certain categories or regions explain many low-quality financial outcomes.

7. Which vendors should be prioritized for remediation or replacement?
   - Hypothesis: vendors with high `vris_score`, active disputes, high concentration risk, and poor delivery quality should be escalated first.

8. Where are the biggest working capital risks?
   - Hypothesis: high inventory value, long cash conversion cycles, and weak vendor/customer payment timing drive elevated risk scores.

## Suggested Analytical Themes

- Vendor scorecards and risk segmentation
- Delay root-cause analysis
- Inventory exception analysis
- Profitability decomposition by region, segment, and category
- Financial risk and working capital monitoring

## Priority Hypothesis Tests

1. Compare delay rates by vendor, region, and fulfillment channel.
2. Compare stockout frequency by vendor lead time band and reorder policy quality.
3. Compare margins across customer segments and product categories.
4. Test whether vendor risk signals predict operational issues downstream.

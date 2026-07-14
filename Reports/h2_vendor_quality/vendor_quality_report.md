# Vendor Quality Report: Hypothesis H2

## Executive summary
Tier-1 vendors have the lowest average defect rates and the differences are statistically significant.

## Key statistics
- Tier-1 mean defect rate: 0.0450
- Tier-2 mean defect rate: 0.1182
- Tier-3 mean defect rate: 0.2002
- One-Way ANOVA F-statistic: 872.0792
- One-Way ANOVA p-value: 9.8862e-157
- Effect size (eta-squared): 0.7924
- Decision: Reject H0 in favor of H1

## Assumption check summary
- Independence was improved by aggregating monthly records to one record per vendor.
- Shapiro-Wilk p-values by tier: Tier-1=0.3940, Tier-2=0.0324, Tier-3=0.0575
- Levene test p-value: 2.0016e-13
- Variance equality is not supported, so the ANOVA result should be interpreted with that caveat.

## Procurement recommendations
- Favor Tier-1 vendors for quality-sensitive categories and warranty-sensitive products.
- Launch corrective action plans for Tier-2 and Tier-3 vendors with the highest average defect rates.
- Add defect-rate thresholds and review checkpoints to supplier scorecards and renewal decisions.
- Use this result together with spend, lead time, and concentration risk before changing sourcing allocations.
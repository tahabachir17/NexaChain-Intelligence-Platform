# Pricing Recommendation Report: Hypothesis H3

## Executive summary
The >30% discount hypothesis cannot be directly tested because the cleaned dataset contains no orders above 30% discount.

## Data coverage check
- Total analyzable orders: 122,731
- Orders above 30% discount: 0
- Maximum observed discount: 25.00%

## Correlation findings
- Primary method used: Spearman
- Pearson correlation: 0.4701 (p-value=0.0000e+00)
- Spearman correlation: 0.4467 (p-value=0.0000e+00)

## Statistical interpretation
- The normality diagnostics are not supportive of a purely parametric assumption, so Spearman is treated as the primary relationship measure.
- In this dataset, discount percentage and profit margin move in the same direction, which is the opposite of the original hypothesis.
- Because the thresholded >30% group does not exist in the data, any threshold-specific conclusion would require additional records.

## Pricing recommendation
- Do not assume larger discounts automatically erode margin in this dataset. Review pricing rules, product mix, and margin calculation logic before tightening discount policies.
- Confirm whether `profit_margin_pct` is defined after discounts and rebates, not before them.
- If management wants a true >30% discount test, extend the dataset or source historical campaigns where such discounts actually occurred.
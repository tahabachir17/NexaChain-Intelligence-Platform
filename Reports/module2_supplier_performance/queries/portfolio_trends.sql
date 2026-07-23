SELECT snapshot_month, 'Spend-weighted' AS series,
       spend_weighted_supplier_score AS score
FROM portfolio_monthly_trends
UNION ALL
SELECT snapshot_month, 'Unweighted' AS series,
       unweighted_supplier_score AS score
FROM portfolio_monthly_trends;

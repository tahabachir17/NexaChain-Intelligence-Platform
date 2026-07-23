SELECT supplier_rank, vendor_name, vendor_category, dynamic_supplier_score,
       score_change_3m, supplier_risk_class, procurement_spend_12m_usd
FROM supplier_ranking
WHERE trend_class = 'Deteriorating'
ORDER BY procurement_spend_12m_usd DESC
LIMIT 10;

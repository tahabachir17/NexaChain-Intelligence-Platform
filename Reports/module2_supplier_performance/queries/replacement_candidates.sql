SELECT supplier_rank, vendor_name, vendor_category, dynamic_supplier_score,
       score_change_3m, supplier_risk_class, procurement_spend_12m_usd
FROM supplier_ranking
WHERE replacement_candidate = 1
ORDER BY procurement_spend_12m_usd DESC;

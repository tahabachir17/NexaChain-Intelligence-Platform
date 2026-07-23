SELECT supplier_risk_class,
       COUNT(DISTINCT vendor_id) AS supplier_count,
       SUM(procurement_spend_12m_usd) AS spend_usd,
       100.0 * SUM(procurement_spend_12m_usd)
         / SUM(SUM(procurement_spend_12m_usd)) OVER () AS spend_share_pct
FROM supplier_ranking
GROUP BY supplier_risk_class;

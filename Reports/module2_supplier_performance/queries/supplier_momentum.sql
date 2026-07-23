SELECT trend_class, COUNT(*) AS supplier_count
FROM supplier_ranking
GROUP BY trend_class;

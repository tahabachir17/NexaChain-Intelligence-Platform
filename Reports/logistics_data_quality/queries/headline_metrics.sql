SELECT
    (SELECT COUNT(*) FROM cleaned_logistics) AS clean_rows,
    (SELECT rows_affected FROM repair_summary WHERE repair = 'duplicate_rows_removed') AS duplicate_rows_removed,
    (SELECT SUM(CASE WHEN passed IN (1, 'True', 'true') THEN 1 ELSE 0 END) FROM validation_results) AS checks_passed;


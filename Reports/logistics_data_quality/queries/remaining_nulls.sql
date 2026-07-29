WITH null_counts AS (
    SELECT 'weather_severity' AS column_name, SUM(CASE WHEN weather_severity IS NULL THEN 1 ELSE 0 END) AS remaining_nulls FROM cleaned_logistics
    UNION ALL SELECT 'delay_reason', SUM(CASE WHEN delay_reason IS NULL THEN 1 ELSE 0 END) FROM cleaned_logistics
    UNION ALL SELECT 'port_of_loading', SUM(CASE WHEN port_of_loading IS NULL THEN 1 ELSE 0 END) FROM cleaned_logistics
    UNION ALL SELECT 'port_of_discharge', SUM(CASE WHEN port_of_discharge IS NULL THEN 1 ELSE 0 END) FROM cleaned_logistics
    UNION ALL SELECT 'actual_arrival_date', SUM(CASE WHEN actual_arrival_date IS NULL THEN 1 ELSE 0 END) FROM cleaned_logistics
    UNION ALL SELECT 'transit_days_actual', SUM(CASE WHEN transit_days_actual IS NULL THEN 1 ELSE 0 END) FROM cleaned_logistics
    UNION ALL SELECT 'delay_days', SUM(CASE WHEN delay_days IS NULL THEN 1 ELSE 0 END) FROM cleaned_logistics
    UNION ALL SELECT 'delay_flag', SUM(CASE WHEN delay_flag IS NULL THEN 1 ELSE 0 END) FROM cleaned_logistics
)
SELECT
    column_name AS column,
    remaining_nulls,
    ROUND(100.0 * remaining_nulls / (SELECT COUNT(*) FROM cleaned_logistics), 2) AS null_rate_pct,
    CASE column_name
        WHEN 'weather_severity' THEN 'Expected when weather impact is 0'
        WHEN 'delay_reason' THEN 'Expected without a completed positive delay'
        WHEN 'port_of_loading' THEN 'Not applicable to non-ocean modes'
        WHEN 'port_of_discharge' THEN 'Not applicable to non-ocean modes'
        WHEN 'actual_arrival_date' THEN 'No completed arrival for active/failed records'
        WHEN 'transit_days_actual' THEN 'No completed arrival for active/failed records'
        WHEN 'delay_days' THEN 'Outcome is not yet observable'
        WHEN 'delay_flag' THEN 'Outcome is not yet observable'
    END AS interpretation
FROM null_counts
ORDER BY remaining_nulls DESC, column_name;

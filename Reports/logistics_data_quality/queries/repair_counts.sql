SELECT
    CASE repair
        WHEN 'delay_days_recalculated' THEN 'Delay days recalculated'
        WHEN 'late_shipments_assigned_unknown_delay_reason' THEN 'Late reasons set to Unknown'
        WHEN 'duplicate_rows_removed' THEN 'Duplicate rows removed'
        WHEN 'eightfold_fuel_surcharge_corruptions_corrected' THEN '8x fuel corruption corrected'
        WHEN 'delivered_actual_arrival_dates_recovered' THEN 'Delivered dates recovered'
        WHEN 'shipment_weights_recovered_from_total_divided_by_cost_per_kg' THEN 'Missing weights recovered'
        WHEN 'transport_mode_values_normalized' THEN 'Transport modes normalized'
        WHEN 'negative_freight_signs_corrected' THEN 'Negative freight signs fixed'
    END AS repair_label,
    rows_affected,
    CASE repair
        WHEN 'delay_days_recalculated' THEN 'Actual transit days minus planned transit days'
        WHEN 'late_shipments_assigned_unknown_delay_reason' THEN 'PDF-allowed fallback for completed late shipments'
        WHEN 'duplicate_rows_removed' THEN 'One row retained per shipment ID'
        WHEN 'eightfold_fuel_surcharge_corruptions_corrected' THEN 'Total-cost residual proved the true surcharge'
        WHEN 'delivered_actual_arrival_dates_recovered' THEN 'Dispatch date plus actual transit days'
        WHEN 'shipment_weights_recovered_from_total_divided_by_cost_per_kg' THEN 'Total logistics cost divided by cost per kg'
        WHEN 'transport_mode_values_normalized' THEN 'Case normalization to the supplied allowed set'
        WHEN 'negative_freight_signs_corrected' THEN 'Absolute value reconciled exactly to trusted total'
    END AS basis
FROM repair_summary
WHERE repair IN (
    'delay_days_recalculated',
    'late_shipments_assigned_unknown_delay_reason',
    'duplicate_rows_removed',
    'eightfold_fuel_surcharge_corruptions_corrected',
    'delivered_actual_arrival_dates_recovered',
    'shipment_weights_recovered_from_total_divided_by_cost_per_kg',
    'transport_mode_values_normalized',
    'negative_freight_signs_corrected'
)
ORDER BY rows_affected DESC, repair_label;


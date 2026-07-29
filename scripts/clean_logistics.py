"""Clean and validate the logistics dataset using the supplied metadata rules.

The raw file is never modified. Repairs are limited to deterministic corrections
supported by another field, a documented business rule, or a higher-quality copy
of a duplicated shipment record.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


DATE_COLUMNS = [
    "shipment_dispatch_date",
    "estimated_arrival_date",
    "actual_arrival_date",
]

COST_COMPONENTS = [
    "freight_cost_usd",
    "fuel_surcharge_usd",
    "customs_duty_usd",
    "port_handling_usd",
    "insurance_cost_usd",
    "last_mile_cost_usd",
]

CANONICAL_TRANSPORT_MODES = {
    "air freight": "Air Freight",
    "ocean freight": "Ocean Freight",
    "road freight": "Road Freight",
    "rail freight": "Rail Freight",
    "multimodal": "Multimodal",
}


def _json_ready(value):
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) else float(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def _duplicate_quality_score(frame: pd.DataFrame) -> pd.Series:
    """Prefer the valid copy when duplicate IDs disagree in one known field."""
    canonical_mode = frame["transport_mode"].isin(CANONICAL_TRANSPORT_MODES.values())
    score = pd.Series(0, index=frame.index, dtype="int64")
    score += frame["shipment_weight_kg"].notna().astype("int64") * 4
    score += frame["shipment_weight_kg"].gt(0).fillna(False).astype("int64") * 4
    score += frame["freight_cost_usd"].gt(0).fillna(False).astype("int64") * 4
    score += canonical_mode.astype("int64") * 2
    score += frame["actual_arrival_date"].notna().astype("int64")
    return score


def _resolve_duplicate_shipments(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    working = frame.copy()
    working["_source_row"] = np.arange(2, len(working) + 2)
    working["_quality_score"] = _duplicate_quality_score(working)

    duplicate_mask = working.duplicated("shipment_id", keep=False)
    duplicate_rows = working.loc[duplicate_mask].copy()
    selected_index = (
        working.sort_values(
            ["shipment_id", "_quality_score", "_source_row"],
            ascending=[True, False, True],
            kind="stable",
        )
        .drop_duplicates("shipment_id", keep="first")
        .index
    )

    audit_records = []
    for shipment_id, group in duplicate_rows.groupby("shipment_id", sort=False):
        comparison = group.drop(columns=["_source_row", "_quality_score"])
        conflict_columns = [
            column
            for column in comparison.columns
            if column != "shipment_id" and comparison[column].nunique(dropna=False) > 1
        ]
        resolution = "exact duplicate; retained first source row"
        if conflict_columns:
            resolution = "retained highest-quality copy; conflict in " + ", ".join(conflict_columns)
        for index, row in group.iterrows():
            audit_records.append(
                {
                    "shipment_id": shipment_id,
                    "source_row": int(row["_source_row"]),
                    "quality_score": int(row["_quality_score"]),
                    "selected": bool(index in selected_index),
                    "conflict_columns": ", ".join(conflict_columns),
                    "resolution": resolution,
                }
            )

    cleaned = working.loc[working.index.isin(selected_index)].copy()
    cleaned = cleaned.sort_values("_source_row", kind="stable").drop(
        columns=["_source_row", "_quality_score"]
    )
    duplicate_audit = pd.DataFrame(audit_records)
    return cleaned.reset_index(drop=True), duplicate_audit


def _validation_row(check: str, passed: bool, observed, expected: str, severity: str) -> dict:
    return {
        "check": check,
        "passed": bool(passed),
        "observed": observed,
        "expected": expected,
        "severity_if_failed": severity,
    }


def validate_cleaned_data(frame: pd.DataFrame, order_ids: set[str], expected_rows: int) -> pd.DataFrame:
    dispatch = pd.to_datetime(frame["shipment_dispatch_date"], errors="coerce")
    estimated = pd.to_datetime(frame["estimated_arrival_date"], errors="coerce")
    actual = pd.to_datetime(frame["actual_arrival_date"], errors="coerce")
    component_total = frame[COST_COMPONENTS].sum(axis=1).round(2)
    calculated_cost_per_kg = (frame["total_logistics_cost_usd"] / frame["shipment_weight_kg"]).round(4)
    calculated_actual_days = (actual - dispatch).dt.days
    calculated_delay_days = frame["transit_days_actual"] - frame["transit_days_planned"]
    calculated_delay_flag = (calculated_delay_days > 0).astype("Int64").where(calculated_delay_days.notna())

    tests = []
    tests.append(_validation_row("row_count_matches_unique_raw_shipments", len(frame) == expected_rows, len(frame), str(expected_rows), "Critical"))
    tests.append(_validation_row("shipment_id_is_unique", frame["shipment_id"].is_unique, int(frame["shipment_id"].duplicated().sum()), "0 duplicate keys", "Critical"))
    tests.append(_validation_row("no_exact_duplicate_rows", not frame.duplicated().any(), int(frame.duplicated().sum()), "0 duplicate rows", "Critical"))
    tests.append(_validation_row("shipment_id_format", frame["shipment_id"].str.fullmatch(r"SHP-\d{8}").all(), int((~frame["shipment_id"].str.fullmatch(r"SHP-\d{8}")).sum()), "0 invalid", "High"))
    tests.append(_validation_row("order_id_format", frame["order_id"].str.fullmatch(r"ORD-\d{8}").all(), int((~frame["order_id"].str.fullmatch(r"ORD-\d{8}")).sum()), "0 invalid", "High"))
    tests.append(_validation_row("order_foreign_key_coverage", frame["order_id"].isin(order_ids).all(), int((~frame["order_id"].isin(order_ids)).sum()), "0 orphan rows", "Critical"))
    tests.append(_validation_row("carrier_id_format", frame["carrier_id"].str.fullmatch(r"CAR-\d{6}").all(), int((~frame["carrier_id"].str.fullmatch(r"CAR-\d{6}")).sum()), "0 invalid", "High"))
    tests.append(_validation_row("route_id_format_supplied_schema", frame["route_id"].str.fullmatch(r"RTE-\d{5}").all(), int((~frame["route_id"].str.fullmatch(r"RTE-\d{5}")).sum()), "0 invalid", "High"))
    tests.append(_validation_row("transport_mode_allowed_values", frame["transport_mode"].isin(CANONICAL_TRANSPORT_MODES.values()).all(), int((~frame["transport_mode"].isin(CANONICAL_TRANSPORT_MODES.values())).sum()), "0 invalid", "High"))
    tests.append(_validation_row("required_dates_parse", dispatch.notna().all() and estimated.notna().all(), int(dispatch.isna().sum() + estimated.isna().sum()), "0 invalid required dates", "High"))
    tests.append(_validation_row("estimated_not_before_dispatch", (estimated >= dispatch).all(), int((estimated < dispatch).sum()), "0 invalid rows", "High"))
    tests.append(_validation_row("delivered_has_actual_arrival", frame.loc[frame["delivery_status"].eq("Delivered"), "actual_arrival_date"].notna().all(), int((frame["delivery_status"].eq("Delivered") & frame["actual_arrival_date"].isna()).sum()), "0 missing", "High"))
    actual_day_mismatch = frame["transit_days_actual"].notna() & frame["transit_days_actual"].ne(calculated_actual_days)
    tests.append(_validation_row("actual_transit_days_match_dates", not actual_day_mismatch.any(), int(actual_day_mismatch.sum()), "0 mismatches", "High"))
    delay_day_mismatch = frame["delay_days"].notna() & frame["delay_days"].ne(calculated_delay_days)
    tests.append(_validation_row("delay_days_match_actual_minus_planned", not delay_day_mismatch.any(), int(delay_day_mismatch.sum()), "0 mismatches", "High"))
    delay_flag_mismatch = frame["delay_flag"].notna() & frame["delay_flag"].ne(calculated_delay_flag)
    tests.append(_validation_row("delay_flag_matches_positive_delay_days", not delay_flag_mismatch.any(), int(delay_flag_mismatch.sum()), "0 mismatches", "High"))
    missing_delay_reason = frame["delay_flag"].eq(1) & frame["delay_reason"].isna()
    tests.append(_validation_row("completed_late_shipments_have_reason", not missing_delay_reason.any(), int(missing_delay_reason.sum()), "0 missing", "Medium"))
    nonpositive_weight = frame["shipment_weight_kg"].isna() | frame["shipment_weight_kg"].le(0)
    tests.append(_validation_row("shipment_weight_positive_and_complete", not nonpositive_weight.any(), int(nonpositive_weight.sum()), "0 missing or nonpositive", "High"))
    negative_cost_components = frame[COST_COMPONENTS].lt(0).any(axis=1)
    tests.append(_validation_row("cost_components_nonnegative", not negative_cost_components.any(), int(negative_cost_components.sum()), "0 rows", "High"))
    excessive_fuel = frame["fuel_surcharge_usd"].gt(3 * frame["freight_cost_usd"])
    tests.append(_validation_row("fuel_surcharge_not_over_3x_freight", not excessive_fuel.any(), int(excessive_fuel.sum()), "0 rows", "High"))
    total_mismatch = frame["total_logistics_cost_usd"].sub(component_total).abs().gt(0.011)
    tests.append(_validation_row("total_cost_equals_component_sum", not total_mismatch.any(), int(total_mismatch.sum()), "0 mismatches over $0.01", "High"))
    cost_per_kg_mismatch = frame["cost_per_kg_usd"].sub(calculated_cost_per_kg).abs().gt(0.00011)
    tests.append(_validation_row("cost_per_kg_is_reconciled", not cost_per_kg_mismatch.any(), int(cost_per_kg_mismatch.sum()), "0 mismatches over 0.0001", "High"))
    tests.append(_validation_row("weather_flag_binary", frame["weather_impact_flag"].isin([0, 1]).all(), int((~frame["weather_impact_flag"].isin([0, 1])).sum()), "0 invalid", "Medium"))
    tests.append(_validation_row("weather_severity_consistent", not (frame["weather_impact_flag"].eq(1) & frame["weather_severity"].isna()).any(), int((frame["weather_impact_flag"].eq(1) & frame["weather_severity"].isna()).sum()), "0 impacted rows without severity", "Medium"))
    tests.append(_validation_row("domestic_customs_days_zero", not (frame["is_cross_border"].eq(0) & frame["customs_clearance_days"].ne(0)).any(), int((frame["is_cross_border"].eq(0) & frame["customs_clearance_days"].ne(0)).sum()), "0 rows", "Medium"))
    tests.append(_validation_row("domestic_customs_duty_zero", not (frame["is_cross_border"].eq(0) & frame["customs_duty_usd"].ne(0)).any(), int((frame["is_cross_border"].eq(0) & frame["customs_duty_usd"].ne(0)).sum()), "0 rows", "Medium"))
    return pd.DataFrame(tests)


def clean_logistics(
    raw_path: Path,
    orders_path: Path,
    cleaned_path: Path,
    report_dir: Path,
) -> dict:
    raw = pd.read_csv(raw_path, low_memory=False)
    orders = pd.read_csv(orders_path, usecols=["order_id"])
    order_ids = set(orders["order_id"].dropna().astype(str))
    expected_unique_shipments = int(raw["shipment_id"].nunique())

    raw_profile = {
        "rows": len(raw),
        "columns": len(raw.columns),
        "unique_shipments": expected_unique_shipments,
        "exact_duplicate_rows": int(raw.duplicated().sum()),
        "duplicate_shipment_id_rows_to_remove": int(raw["shipment_id"].duplicated().sum()),
        "duplicate_shipment_id_groups": int(raw.loc[raw.duplicated("shipment_id", keep=False), "shipment_id"].nunique()),
        "order_fk_orphan_rows": int((~raw["order_id"].isin(order_ids)).sum()),
        "dispatch_date_min": str(raw["shipment_dispatch_date"].min()),
        "dispatch_date_max": str(raw["shipment_dispatch_date"].max()),
        "missing_values": {key: int(value) for key, value in raw.isna().sum().items() if value},
    }

    cleaned, duplicate_audit = _resolve_duplicate_shipments(raw)
    repair_counts = {
        "duplicate_rows_removed": int(len(raw) - len(cleaned)),
    }

    for column in cleaned.select_dtypes(include="object").columns:
        cleaned[column] = cleaned[column].str.strip()

    normalized_modes = cleaned["transport_mode"].str.casefold().map(CANONICAL_TRANSPORT_MODES)
    mode_change = cleaned["transport_mode"].ne(normalized_modes) & normalized_modes.notna()
    repair_counts["transport_mode_values_normalized"] = int(mode_change.sum())
    cleaned.loc[normalized_modes.notna(), "transport_mode"] = normalized_modes[normalized_modes.notna()]

    for column in DATE_COLUMNS:
        cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")

    missing_weight = cleaned["shipment_weight_kg"].isna()
    inferred_weight = (cleaned["total_logistics_cost_usd"] / cleaned["cost_per_kg_usd"]).round(2)
    valid_inferred_weight = missing_weight & inferred_weight.gt(0)
    cleaned.loc[valid_inferred_weight, "shipment_weight_kg"] = inferred_weight[valid_inferred_weight]
    repair_counts["shipment_weights_recovered_from_total_divided_by_cost_per_kg"] = int(valid_inferred_weight.sum())

    delivered_missing_actual = (
        cleaned["delivery_status"].eq("Delivered")
        & cleaned["actual_arrival_date"].isna()
        & cleaned["transit_days_actual"].notna()
    )
    cleaned.loc[delivered_missing_actual, "actual_arrival_date"] = (
        cleaned.loc[delivered_missing_actual, "shipment_dispatch_date"]
        + pd.to_timedelta(cleaned.loc[delivered_missing_actual, "transit_days_actual"], unit="D")
    )
    repair_counts["delivered_actual_arrival_dates_recovered"] = int(delivered_missing_actual.sum())

    rows_with_actual = cleaned["actual_arrival_date"].notna()
    calculated_actual_days = (
        cleaned["actual_arrival_date"] - cleaned["shipment_dispatch_date"]
    ).dt.days.astype("Int64")
    transit_days_changed = rows_with_actual & cleaned["transit_days_actual"].ne(calculated_actual_days).fillna(True)
    cleaned.loc[rows_with_actual, "transit_days_actual"] = calculated_actual_days[rows_with_actual]
    repair_counts["transit_days_actual_recalculated"] = int(transit_days_changed.sum())

    calculated_delay_days = (
        cleaned["transit_days_actual"].astype("Float64") - cleaned["transit_days_planned"]
    ).astype("Int64")
    delay_days_changed = calculated_delay_days.notna() & cleaned["delay_days"].ne(calculated_delay_days).fillna(True)
    cleaned.loc[calculated_delay_days.notna(), "delay_days"] = calculated_delay_days[calculated_delay_days.notna()]
    repair_counts["delay_days_recalculated"] = int(delay_days_changed.sum())

    calculated_delay_flag = (calculated_delay_days > 0).astype("Int64").where(calculated_delay_days.notna())
    delay_flag_changed = calculated_delay_flag.notna() & cleaned["delay_flag"].ne(calculated_delay_flag).fillna(True)
    cleaned.loc[calculated_delay_flag.notna(), "delay_flag"] = calculated_delay_flag[calculated_delay_flag.notna()]
    repair_counts["delay_flags_recalculated"] = int(delay_flag_changed.sum())

    missing_reason = cleaned["delay_flag"].eq(1) & cleaned["delay_reason"].isna()
    cleaned.loc[missing_reason, "delay_reason"] = "Unknown"
    repair_counts["late_shipments_assigned_unknown_delay_reason"] = int(missing_reason.sum())

    negative_freight = cleaned["freight_cost_usd"].lt(0)
    cleaned.loc[negative_freight, "freight_cost_usd"] = cleaned.loc[negative_freight, "freight_cost_usd"].abs()
    repair_counts["negative_freight_signs_corrected"] = int(negative_freight.sum())

    other_costs = cleaned[[
        "customs_duty_usd",
        "port_handling_usd",
        "insurance_cost_usd",
        "last_mile_cost_usd",
    ]].sum(axis=1)
    residual_fuel = (
        cleaned["total_logistics_cost_usd"]
        - cleaned["freight_cost_usd"]
        - other_costs
    ).round(2)
    inflated_fuel = residual_fuel.gt(0) & np.isclose(
        cleaned["fuel_surcharge_usd"], residual_fuel * 8, atol=0.011
    )
    cleaned.loc[inflated_fuel, "fuel_surcharge_usd"] = residual_fuel[inflated_fuel]
    repair_counts["eightfold_fuel_surcharge_corruptions_corrected"] = int(inflated_fuel.sum())

    recalculated_total = cleaned[COST_COMPONENTS].sum(axis=1).round(2)
    total_changed = cleaned["total_logistics_cost_usd"].sub(recalculated_total).abs().gt(0.011)
    cleaned["total_logistics_cost_usd"] = recalculated_total
    repair_counts["total_logistics_cost_values_recalculated"] = int(total_changed.sum())

    recalculated_cost_per_kg = (
        cleaned["total_logistics_cost_usd"] / cleaned["shipment_weight_kg"]
    ).round(4)
    cost_per_kg_changed = (
        cleaned["cost_per_kg_usd"].isna()
        | cleaned["cost_per_kg_usd"].sub(recalculated_cost_per_kg).abs().gt(0.00011)
    )
    cleaned.loc[cost_per_kg_changed, "cost_per_kg_usd"] = recalculated_cost_per_kg[cost_per_kg_changed]
    repair_counts["cost_per_kg_values_recalculated"] = int(cost_per_kg_changed.sum())

    integer_nullable_columns = ["transit_days_actual", "delay_days", "delay_flag"]
    for column in integer_nullable_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce").astype("Int64")

    validation = validate_cleaned_data(cleaned, order_ids, expected_unique_shipments)

    report_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    output_frame = cleaned.copy()
    for column in DATE_COLUMNS:
        output_frame[column] = output_frame[column].dt.strftime("%Y-%m-%d")
    output_frame.to_csv(cleaned_path, index=False, encoding="utf-8-sig")
    duplicate_audit.to_csv(report_dir / "duplicate_resolution_log.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [{"repair": key, "rows_affected": value} for key, value in repair_counts.items()]
    ).to_csv(report_dir / "repair_summary.csv", index=False, encoding="utf-8-sig")
    validation.to_csv(report_dir / "validation_results.csv", index=False, encoding="utf-8-sig")

    remaining_nulls = {
        key: int(value) for key, value in cleaned.isna().sum().items() if value
    }
    summary = {
        "source_metadata": {
            "raw_csv": str(raw_path.as_posix()),
            "orders_reference": str(orders_path.as_posix()),
            "metadata_pdf": "C:/Users/hp/OneDrive/Documents/logistics data.pdf",
            "cleaned_csv": str(cleaned_path.as_posix()),
        },
        "schema_mapping": {
            "shipment_date": "shipment_dispatch_date",
            "promised_delivery_date": "estimated_arrival_date",
            "actual_delivery_date": "actual_arrival_date",
            "carrier_type": "transport_mode",
            "last_port_scan": "last_checkpoint",
            "unavailable_pdf_fields": [
                "origin_country",
                "destination_country",
                "carrier_rating_score",
                "shipment_notes",
                "warehouse_id",
            ],
            "supplied_schema_note": "The CSV has 47 columns; the PDF describes an older selected 32-column schema.",
        },
        "raw_profile": raw_profile,
        "repair_counts": repair_counts,
        "clean_profile": {
            "rows": len(cleaned),
            "columns": len(cleaned.columns),
            "unique_shipments": int(cleaned["shipment_id"].nunique()),
            "dispatch_date_min": cleaned["shipment_dispatch_date"].min(),
            "dispatch_date_max": cleaned["shipment_dispatch_date"].max(),
            "validation_checks_passed": int(validation["passed"].sum()),
            "validation_checks_total": len(validation),
        },
        "remaining_nulls": remaining_nulls,
        "remaining_null_interpretation": {
            "actual_arrival_date_transit_days_actual_delay_flag_delay_days": "Expected for active Delayed, In-Transit, and Failed Delivery records without a completed arrival.",
            "port_of_loading_port_of_discharge": "Expected for non-ocean modes where the source uses N/A.",
            "weather_severity": "Expected when weather_impact_flag is 0.",
            "delay_reason": "Expected where no completed positive delay is recorded; active Delayed records may retain a known operational reason.",
        },
        "outlier_treatment": {
            "policy": "Retain plausible long-tail operational values; correct only deterministic corruption.",
            "reason": "Shipment weights, distances, package counts, and costs vary structurally by transport mode and shipment type, so global IQR clipping would remove valid records.",
        },
        "validation": validation.to_dict(orient="records"),
        "caveats": [
            "Carrier and route master files were not supplied, so only identifier format was validated for those keys.",
            "The PDF expects six digits after RTE-, while every supplied route_id consistently uses five digits; the supplied schema was preserved and documented.",
            "The source contains statuses Failed Delivery and Returned to Sender rather than the PDF's shorter Failed and Returned labels; meaningful source labels were retained.",
            "No values were imputed from medians or clipped solely because they were statistical outliers.",
        ],
    }
    with (report_dir / "cleaning_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(_json_ready(summary), handle, indent=2, ensure_ascii=False)
    return _json_ready(summary)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=Path("data/logistics.csv"))
    parser.add_argument("--orders", type=Path, default=Path("data/orders.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/cleaned/logistics_clean.csv"))
    parser.add_argument("--report-dir", type=Path, default=Path("Reports/logistics_data_quality"))
    args = parser.parse_args()
    summary = clean_logistics(args.raw, args.orders, args.output, args.report_dir)
    print(json.dumps(summary["clean_profile"], indent=2))
    failed = [item for item in summary["validation"] if not item["passed"]]
    if failed:
        raise SystemExit(f"Validation failed: {failed}")


if __name__ == "__main__":
    main()

"""Dynamic multi-factor supplier performance scoring for Module 2 / Model 10.

The module is intentionally importable from the companion notebook and executable
as a script.  It uses only the cleaned monthly vendor snapshot as the governed
source plus product-level order costs, writes decision-ready CSV/JSON outputs, and keeps every business rule in
one place for auditability.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "cleaned" / "vendors_clean.csv"
ORDERS_PATH = ROOT / "data" / "cleaned" / "orders_clean.csv"
OUTPUT_DIR = ROOT / "Reports" / "module2_supplier_performance"

WEIGHTS = {
    "otd_score": 0.30,
    "quality_score": 0.20,
    "risk_performance_score": 0.20,
    "cost_efficiency_score": 0.15,
    "lead_time_score": 0.15,
}


def weighted_average(values: pd.Series, weights: pd.Series) -> float:
    mask = values.notna() & weights.notna()
    if not mask.any():
        return np.nan
    return float(np.average(values[mask], weights=weights[mask]))


def load_and_validate(path: Path = INPUT_PATH) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(path)
    required = {
        "vendor_record_id", "vendor_id", "vendor_name", "vendor_region",
        "vendor_category", "snapshot_month", "on_time_delivery_rate",
        "quality_acceptance_rate", "defect_rate_pct", "lead_time_avg_days",
        "lead_time_variance_days", "contract_lead_time_days",
        "procurement_spend_usd", "purchase_order_count",
        "invoice_accuracy_rate", "financial_stability_score",
        "past_disruption_count", "active_dispute_flag", "vris_score",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["snapshot_month"] = pd.to_datetime(df["snapshot_month"], errors="raise")
    duplicate_keys = int(df.duplicated(["vendor_id", "snapshot_month"]).sum())
    null_required = int(df[list(required)].isna().sum().sum())

    bounded_columns = [
        "on_time_delivery_rate", "quality_acceptance_rate",
        "invoice_accuracy_rate", "vris_score", "financial_stability_score",
    ]
    out_of_range = int(
        sum((~df[col].between(0, 100)).sum() for col in bounded_columns)
    )
    invalid_lead_time = int(
        ((df["lead_time_avg_days"] <= 0) | (df["contract_lead_time_days"] <= 0)).sum()
    )
    negative_spend = int((df["procurement_spend_usd"] < 0).sum())

    checks = pd.DataFrame(
        [
            ("Required columns present", len(missing) == 0, len(missing), "Critical"),
            ("Unique vendor-month grain", duplicate_keys == 0, duplicate_keys, "Critical"),
            ("Required fields complete", null_required == 0, null_required, "High"),
            ("Core scores within 0-100", out_of_range == 0, out_of_range, "High"),
            ("Lead-time denominators positive", invalid_lead_time == 0, invalid_lead_time, "High"),
            ("Procurement spend non-negative", negative_spend == 0, negative_spend, "High"),
        ],
        columns=["check", "passed", "exceptions", "severity_if_failed"],
    )
    if not checks["passed"].all():
        failed = checks.loc[~checks["passed"], "check"].tolist()
        raise ValueError(f"Input validation failed: {failed}")
    return df, checks


def build_cost_competitiveness(order_path: Path = ORDERS_PATH) -> pd.DataFrame:
    """Benchmark supplier unit COGS against the same product in the same year."""
    orders = pd.read_csv(
        order_path,
        usecols=[
            "order_date", "vendor_id", "product_id", "order_quantity",
            "cost_of_goods_usd",
        ],
    )
    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="raise")
    orders["year"] = orders["order_date"].dt.year
    valid = (
        orders["vendor_id"].notna()
        & orders["product_id"].notna()
        & orders["order_quantity"].gt(0)
        & orders["cost_of_goods_usd"].gt(0)
    )
    orders = orders.loc[valid].copy()
    orders["unit_cogs_usd"] = orders["cost_of_goods_usd"] / orders["order_quantity"]
    orders["product_year_median_unit_cogs"] = orders.groupby(
        ["product_id", "year"]
    )["unit_cogs_usd"].transform("median")
    orders["order_cost_competitiveness_score"] = (
        100 * orders["product_year_median_unit_cogs"] / orders["unit_cogs_usd"]
    ).clip(0, 100)

    records = []
    for (vendor_id, year), group in orders.groupby(["vendor_id", "year"], sort=False):
        records.append(
            {
                "vendor_id": vendor_id,
                "year": int(year),
                "product_cost_competitiveness_score": weighted_average(
                    group["order_cost_competitiveness_score"],
                    group["cost_of_goods_usd"],
                ),
                "cost_benchmark_order_count": int(len(group)),
            }
        )
    return pd.DataFrame(records)


def add_monthly_scores(
    df: pd.DataFrame,
    cost_competitiveness: pd.DataFrame,
) -> pd.DataFrame:
    scored = df.copy()
    scored["year"] = scored["snapshot_month"].dt.year
    scored = scored.merge(
        cost_competitiveness,
        on=["vendor_id", "year"],
        how="left",
        validate="many_to_one",
    )
    if scored["product_cost_competitiveness_score"].isna().any():
        missing = int(scored["product_cost_competitiveness_score"].isna().sum())
        raise ValueError(f"Missing product cost benchmarks for {missing} vendor-month rows")
    scored["otd_score"] = scored["on_time_delivery_rate"].clip(0, 100)
    scored["quality_score"] = scored["quality_acceptance_rate"].clip(0, 100)

    # VRIS is an adverse risk measure: lower is better.  Inverting it ensures
    # every score component has the same direction before weighting.
    scored["risk_performance_score"] = (100 - scored["vris_score"]).clip(0, 100)

    # Cost efficiency combines like-for-like product cost competitiveness with
    # invoice accuracy. Spend is retained as exposure, not rewarded as performance.
    scored["cost_efficiency_score"] = (
        0.70 * scored["product_cost_competitiveness_score"].clip(0, 100)
        + 0.30 * scored["invoice_accuracy_rate"].clip(0, 100)
    )

    lead_adherence = np.minimum(
        1.0,
        scored["contract_lead_time_days"] / scored["lead_time_avg_days"],
    ) * 100
    lead_consistency = (
        1 - np.minimum(
            1.0,
            scored["lead_time_variance_days"] / scored["contract_lead_time_days"],
        )
    ) * 100
    scored["lead_time_score"] = 0.80 * lead_adherence + 0.20 * lead_consistency
    scored["lead_time_score"] = scored["lead_time_score"].clip(0, 100)

    scored["supplier_score"] = sum(
        scored[component] * weight for component, weight in WEIGHTS.items()
    ).round(2)
    return scored


def classify_risk(row: pd.Series) -> str:
    if row["dynamic_supplier_score"] < 45 or (
        row["active_dispute_flag"] == 1 and row["vris_score"] >= 70
    ):
        return "Critical"
    if (
        row["dynamic_supplier_score"] < 60
        or row["vris_score"] >= 70
        or row["active_dispute_flag"] == 1
        or row["past_disruption_count"] >= 4
    ):
        return "High"
    if (
        row["dynamic_supplier_score"] < 75
        or row["vris_score"] >= 45
        or row["past_disruption_count"] >= 2
    ):
        return "Medium"
    return "Low"


def recommend_tier(row: pd.Series) -> str:
    if row["replacement_candidate"]:
        return "Replace"
    if (
        row["dynamic_supplier_score"] >= 75
        and row["supplier_risk_class"] in {"Low", "Medium"}
        and row["trend_class"] != "Deteriorating"
        and row["spend_percentile"] >= 0.60
    ):
        return "Strategic Partner"
    if (
        row["dynamic_supplier_score"] >= 68
        and row["supplier_risk_class"] in {"Low", "Medium"}
        and row["trend_class"] != "Deteriorating"
    ):
        return "Preferred"
    if row["dynamic_supplier_score"] >= 58 and row["supplier_risk_class"] != "Critical":
        return "Approved"
    return "Conditional"


def build_supplier_ranking(scored: pd.DataFrame) -> pd.DataFrame:
    as_of = scored["snapshot_month"].max()
    history_start = as_of - pd.DateOffset(months=5)
    spend_start = as_of - pd.DateOffset(months=11)
    history = scored.loc[scored["snapshot_month"].between(history_start, as_of)].copy()
    history["month_age"] = (
        (as_of.year - history["snapshot_month"].dt.year) * 12
        + as_of.month - history["snapshot_month"].dt.month
    )
    history["recency_weight"] = 0.5 ** (history["month_age"] / 3.0)

    score_columns = list(WEIGHTS) + ["supplier_score"]
    records: list[dict] = []
    for vendor_id, group in history.groupby("vendor_id", sort=False):
        latest = group.sort_values("snapshot_month").iloc[-1]
        record = {
            "vendor_id": vendor_id,
            "vendor_name": latest["vendor_name"],
            "vendor_region": latest["vendor_region"],
            "vendor_category": latest["vendor_category"],
            "as_of_month": as_of.date().isoformat(),
            "months_in_dynamic_window": int(group["snapshot_month"].nunique()),
        }
        for col in score_columns:
            target = "dynamic_supplier_score" if col == "supplier_score" else col
            record[target] = weighted_average(group[col], group["recency_weight"])
        for col in [
            "vris_score", "defect_rate_pct", "lead_time_avg_days",
            "contract_lead_time_days", "financial_stability_score",
            "past_disruption_count", "active_dispute_flag", "preferred_vendor_flag",
        ]:
            record[col] = latest[col]
        records.append(record)

    ranking = pd.DataFrame(records)
    trend_frame = scored.loc[scored["snapshot_month"].between(history_start, as_of)].copy()
    recent_cutoff = as_of - pd.DateOffset(months=2)
    prior_start = as_of - pd.DateOffset(months=5)
    prior_end = as_of - pd.DateOffset(months=3)
    recent = (
        trend_frame.loc[trend_frame["snapshot_month"].between(recent_cutoff, as_of)]
        .groupby("vendor_id")["supplier_score"].mean().rename("recent_3m_score")
    )
    prior = (
        trend_frame.loc[trend_frame["snapshot_month"].between(prior_start, prior_end)]
        .groupby("vendor_id")["supplier_score"].mean().rename("prior_3m_score")
    )
    ranking = ranking.join(pd.concat([recent, prior], axis=1), on="vendor_id")
    ranking["score_change_3m"] = ranking["recent_3m_score"] - ranking["prior_3m_score"]
    ranking["trend_class"] = np.select(
        [ranking["score_change_3m"] >= 2, ranking["score_change_3m"] <= -2],
        ["Improving", "Deteriorating"],
        default="Stable",
    )

    annual_spend = (
        scored.loc[scored["snapshot_month"].between(spend_start, as_of)]
        .groupby("vendor_id")["procurement_spend_usd"].sum()
        .rename("procurement_spend_12m_usd")
    )
    ranking = ranking.join(annual_spend, on="vendor_id")
    ranking["spend_percentile"] = ranking["procurement_spend_12m_usd"].rank(pct=True)
    ranking["supplier_risk_class"] = ranking.apply(classify_risk, axis=1)
    ranking["replacement_candidate"] = (
        ((ranking["dynamic_supplier_score"] < 55) & ranking["supplier_risk_class"].isin(["High", "Critical"]))
        | ((ranking["supplier_risk_class"] == "Critical") & (ranking["trend_class"] == "Deteriorating"))
    )
    ranking["recommended_tier"] = ranking.apply(recommend_tier, axis=1)
    ranking = ranking.sort_values(
        ["dynamic_supplier_score", "procurement_spend_12m_usd"], ascending=[False, False]
    ).reset_index(drop=True)
    ranking.insert(0, "supplier_rank", np.arange(1, len(ranking) + 1))
    ranking["category_rank"] = (
        ranking.groupby("vendor_category")["dynamic_supplier_score"]
        .rank(method="min", ascending=False).astype(int)
    )
    numeric_round = [
        *score_columns[:-1], "dynamic_supplier_score", "recent_3m_score",
        "prior_3m_score", "score_change_3m", "procurement_spend_12m_usd",
        "spend_percentile",
    ]
    ranking[numeric_round] = ranking[numeric_round].round(2)
    return ranking


def build_monthly_trends(scored: pd.DataFrame) -> pd.DataFrame:
    trends = (
        scored.groupby("snapshot_month")
        .apply(
            lambda g: pd.Series(
                {
                    "supplier_count": g["vendor_id"].nunique(),
                    "spend_weighted_supplier_score": np.average(
                        g["supplier_score"], weights=g["procurement_spend_usd"]
                    ),
                    "unweighted_supplier_score": g["supplier_score"].mean(),
                    "procurement_spend_usd": g["procurement_spend_usd"].sum(),
                }
            ),
            include_groups=False,
        )
        .reset_index()
    )
    numeric_columns = trends.select_dtypes(include="number").columns
    trends[numeric_columns] = trends[numeric_columns].round(2)
    return trends


def build_summary(ranking: pd.DataFrame, trends: pd.DataFrame, checks: pd.DataFrame) -> dict:
    total_spend = ranking["procurement_spend_12m_usd"].sum()
    replacements = ranking[ranking["replacement_candidate"]]
    partners = ranking[ranking["recommended_tier"] == "Strategic Partner"]
    deteriorating = ranking[ranking["trend_class"] == "Deteriorating"]
    improving = ranking[ranking["trend_class"] == "Improving"]
    critical_high = ranking[ranking["supplier_risk_class"].isin(["Critical", "High"])]
    return {
        "as_of_month": ranking["as_of_month"].iloc[0],
        "supplier_count": int(len(ranking)),
        "dynamic_score_mean": round(float(ranking["dynamic_supplier_score"].mean()), 2),
        "dynamic_score_median": round(float(ranking["dynamic_supplier_score"].median()), 2),
        "improving_count": int(len(improving)),
        "deteriorating_count": int(len(deteriorating)),
        "replacement_candidate_count": int(len(replacements)),
        "replacement_spend_usd": round(float(replacements["procurement_spend_12m_usd"].sum()), 2),
        "replacement_spend_share": round(float(replacements["procurement_spend_12m_usd"].sum() / total_spend), 4),
        "strategic_partner_count": int(len(partners)),
        "strategic_partner_spend_usd": round(float(partners["procurement_spend_12m_usd"].sum()), 2),
        "strategic_partner_spend_share": round(float(partners["procurement_spend_12m_usd"].sum() / total_spend), 4),
        "high_or_critical_risk_count": int(len(critical_high)),
        "high_or_critical_spend_share": round(float(critical_high["procurement_spend_12m_usd"].sum() / total_spend), 4),
        "latest_portfolio_score": round(float(trends.iloc[-1]["spend_weighted_supplier_score"]), 2),
        "portfolio_score_change_6m": round(float(trends.iloc[-1]["spend_weighted_supplier_score"] - trends.iloc[-7]["spend_weighted_supplier_score"]), 2),
        "validation_checks_passed": int(checks["passed"].sum()),
        "validation_checks_total": int(len(checks)),
        "score_weights": WEIGHTS,
        "trend_definition": "Improving >= +2 points; Deteriorating <= -2 points; recent 3 months versus prior 3 months.",
        "dynamic_definition": "Six-month exponentially weighted average with a three-month half-life.",
    }


def run_pipeline(input_path: Path = INPUT_PATH, output_dir: Path = OUTPUT_DIR) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw, checks = load_and_validate(input_path)
    cost_competitiveness = build_cost_competitiveness()
    expected_vendor_years = raw.assign(year=raw["snapshot_month"].dt.year)[
        ["vendor_id", "year"]
    ].drop_duplicates()
    cost_coverage = expected_vendor_years.merge(
        cost_competitiveness[["vendor_id", "year"]],
        on=["vendor_id", "year"],
        how="left",
        indicator=True,
        validate="one_to_one",
    )
    missing_cost_years = int(cost_coverage["_merge"].ne("both").sum())
    checks = pd.concat(
        [
            checks,
            pd.DataFrame(
                [{
                    "check": "Product-year cost benchmark coverage",
                    "passed": missing_cost_years == 0,
                    "exceptions": missing_cost_years,
                    "severity_if_failed": "High",
                }]
            ),
        ],
        ignore_index=True,
    )
    if missing_cost_years:
        raise ValueError(f"Missing cost benchmarks for {missing_cost_years} vendor-years")
    scored = add_monthly_scores(raw, cost_competitiveness)
    ranking = build_supplier_ranking(scored)
    trends = build_monthly_trends(scored)
    summary = build_summary(ranking, trends, checks)

    ranking.to_csv(output_dir / "supplier_ranking.csv", index=False)
    scored.to_csv(output_dir / "supplier_monthly_scores.csv", index=False)
    trends.to_csv(output_dir / "portfolio_monthly_trends.csv", index=False)
    checks.to_csv(output_dir / "data_quality_checks.csv", index=False)
    ranking.loc[ranking["trend_class"] == "Improving"].to_csv(output_dir / "improving_suppliers.csv", index=False)
    ranking.loc[ranking["trend_class"] == "Deteriorating"].to_csv(output_dir / "deteriorating_suppliers.csv", index=False)
    ranking.loc[ranking["replacement_candidate"]].to_csv(output_dir / "replacement_candidates.csv", index=False)
    ranking.loc[ranking["recommended_tier"] == "Strategic Partner"].to_csv(output_dir / "strategic_partnership_candidates.csv", index=False)
    (output_dir / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return {"raw": raw, "scored": scored, "ranking": ranking, "trends": trends, "checks": checks, "summary": summary}


if __name__ == "__main__":
    result = run_pipeline()
    print(json.dumps(result["summary"], indent=2))

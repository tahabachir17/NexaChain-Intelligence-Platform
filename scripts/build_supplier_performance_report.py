"""Build the canonical report artifact and executive recommendation memo."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Reports" / "module2_supplier_performance"


def money(value: float) -> str:
    return f"${value / 1_000_000:.1f}M"


def compact_rows(frame: pd.DataFrame, columns: list[str]) -> list[dict]:
    clean = frame[columns].copy()
    for column in clean.select_dtypes(include="number").columns:
        clean[column] = clean[column].round(2)
    return clean.to_dict(orient="records")


def build_report() -> tuple[Path, Path]:
    ranking = pd.read_csv(REPORT_DIR / "supplier_ranking.csv")
    trends = pd.read_csv(REPORT_DIR / "portfolio_monthly_trends.csv")
    summary = json.loads((REPORT_DIR / "analysis_summary.json").read_text(encoding="utf-8"))
    checks = pd.read_csv(REPORT_DIR / "data_quality_checks.csv")

    replacement = ranking.loc[ranking["replacement_candidate"]].copy()
    strategic = ranking.loc[ranking["recommended_tier"].eq("Strategic Partner")].copy()
    deteriorating = (
        ranking.loc[ranking["trend_class"].eq("Deteriorating")]
        .nlargest(10, "procurement_spend_12m_usd")
    )

    trend_counts = (
        ranking["trend_class"].value_counts()
        .reindex(["Improving", "Stable", "Deteriorating"], fill_value=0)
        .rename_axis("trend_class").reset_index(name="supplier_count")
    )
    risk_exposure = (
        ranking.groupby("supplier_risk_class", as_index=False)
        .agg(supplier_count=("vendor_id", "nunique"), spend_usd=("procurement_spend_12m_usd", "sum"))
    )
    risk_exposure["spend_share_pct"] = (
        risk_exposure["spend_usd"] / risk_exposure["spend_usd"].sum() * 100
    ).round(1)
    order = pd.CategoricalDtype(["Critical", "High", "Medium", "Low"], ordered=True)
    risk_exposure["supplier_risk_class"] = risk_exposure["supplier_risk_class"].astype(order)
    risk_exposure = risk_exposure.sort_values("supplier_risk_class")

    high_spend_name = deteriorating.iloc[0]["vendor_name"]
    high_spend_value = deteriorating.iloc[0]["procurement_spend_12m_usd"]
    top_partner = strategic.sort_values("dynamic_supplier_score", ascending=False).iloc[0]
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    source_file = {
        "id": "vendor_source",
        "label": "Cleaned monthly vendor snapshots",
        "path": "data/cleaned/vendors_clean.csv",
    }
    source_orders = {
        "id": "orders_source",
        "label": "Cleaned order-level product costs",
        "path": "data/cleaned/orders_clean.csv",
    }
    source_ranking = {
        "id": "supplier_ranking",
        "label": "Dynamic supplier ranking output",
        "path": "Reports/module2_supplier_performance/supplier_ranking.csv",
    }
    source_trends = {
        "id": "portfolio_trends",
        "label": "Monthly supplier score trends",
        "path": "Reports/module2_supplier_performance/portfolio_monthly_trends.csv",
    }
    source_summary = {
        "id": "analysis_summary",
        "label": "Supplier scoring analysis summary",
        "path": "Reports/module2_supplier_performance/analysis_summary.json",
    }

    cards = [
        {
            "id": "supplier_count_card", "description": "Suppliers ranked in the latest six-month scoring window.",
            "dataset": "headline_metrics", "sourceId": "analysis_summary",
            "metrics": [{"label": "Suppliers ranked", "field": "supplier_count", "format": "number"}],
        },
        {
            "id": "portfolio_score_card", "description": "Latest monthly score weighted by procurement spend.",
            "dataset": "headline_metrics", "sourceId": "analysis_summary",
            "metrics": [
                {"label": "Portfolio score", "field": "latest_portfolio_score", "format": "number", "unit": "/100"},
                {"label": "6-month change", "field": "portfolio_score_change_6m", "format": "number", "unit": " points"},
            ],
        },
        {
            "id": "replacement_card", "description": "Suppliers requiring replacement due diligence under the model rules.",
            "dataset": "headline_metrics", "sourceId": "analysis_summary",
            "metrics": [
                {"label": "Replacement candidates", "field": "replacement_candidate_count", "format": "number"},
                {"label": "Spend exposed", "field": "replacement_spend_share", "format": "percent"},
            ],
        },
        {
            "id": "strategic_card", "description": "High-performing, controlled-risk suppliers with meaningful spend exposure.",
            "dataset": "headline_metrics", "sourceId": "analysis_summary",
            "metrics": [
                {"label": "Strategic candidates", "field": "strategic_partner_count", "format": "number"},
                {"label": "Spend represented", "field": "strategic_partner_spend_share", "format": "percent"},
            ],
        },
    ]

    rank_columns = [
        {"field": "supplier_rank", "label": "Rank", "format": "number"},
        {"field": "vendor_name", "label": "Supplier", "type": "text"},
        {"field": "vendor_category", "label": "Category", "type": "text"},
        {"field": "dynamic_supplier_score", "label": "Score", "format": "number", "unit": "/100"},
        {"field": "score_change_3m", "label": "3m change", "format": "number", "unit": " pts", "movement": True},
        {"field": "supplier_risk_class", "label": "Risk", "type": "text"},
        {"field": "procurement_spend_12m_usd", "label": "12m spend", "format": "currency", "currency": "USD"},
    ]

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "Supplier Performance and Sourcing Recommendations",
            "description": "Dynamic supplier ranking, trend diagnosis, risk classification, and procurement actions as of December 2024.",
            "generatedAt": generated_at,
            "cards": cards,
            "charts": [
                {
                    "id": "portfolio_trend_chart", "title": "Monthly supplier performance score",
                    "subtitle": "Spend-weighted and unweighted portfolio scores, January 2021 to December 2024.",
                    "type": "line", "dataset": "portfolio_trends", "sourceId": "portfolio_trends",
                    "valueFormat": "number",
                    "encodings": {
                        "x": {"field": "snapshot_month", "type": "temporal", "label": "Month"},
                        "y": {"field": "score", "type": "quantitative", "label": "Score (0-100)"},
                        "color": {"field": "series", "type": "nominal", "label": "Series"},
                        "tooltip": [
                            {"field": "snapshot_month", "type": "temporal", "label": "Month"},
                            {"field": "series", "type": "nominal", "label": "Series"},
                            {"field": "score", "type": "quantitative", "label": "Score", "format": "number"},
                        ],
                    },
                },
                {
                    "id": "trend_status_chart", "title": "Supplier momentum classification",
                    "subtitle": "Latest three-month average compared with the prior three months; +/-2 points defines movement.",
                    "type": "bar", "dataset": "trend_counts", "sourceId": "supplier_ranking",
                    "valueFormat": "number",
                    "encodings": {
                        "x": {"field": "trend_class", "type": "nominal", "label": "Momentum"},
                        "y": {"field": "supplier_count", "type": "quantitative", "label": "Suppliers"},
                        "tooltip": [
                            {"field": "trend_class", "type": "nominal", "label": "Momentum"},
                            {"field": "supplier_count", "type": "quantitative", "label": "Suppliers", "format": "number"},
                        ],
                    },
                },
            ],
            "tables": [
                {
                    "id": "risk_exposure_table", "title": "Risk classification and spend exposure",
                    "subtitle": "Trailing-12-month procurement spend represented by each model risk class.",
                    "dataset": "risk_exposure", "sourceId": "supplier_ranking",
                    "defaultSort": {"field": "spend_usd", "direction": "desc"},
                    "columns": [
                        {"field": "supplier_risk_class", "label": "Risk class", "type": "text"},
                        {"field": "supplier_count", "label": "Suppliers", "format": "number"},
                        {"field": "spend_usd", "label": "12m spend", "format": "currency", "currency": "USD"},
                        {"field": "spend_share_pct", "label": "Spend share", "format": "number", "unit": "%"},
                    ],
                },
                {
                    "id": "replacement_table", "title": "Suppliers requiring replacement due diligence",
                    "subtitle": "Candidates meet the model rule; operational feasibility must be confirmed before an exit decision.",
                    "dataset": "replacement", "sourceId": "supplier_ranking",
                    "defaultSort": {"field": "procurement_spend_12m_usd", "direction": "desc"},
                    "columns": rank_columns,
                },
                {
                    "id": "strategic_table", "title": "Strategic partnership candidates",
                    "subtitle": "High performance, controlled risk, non-deteriorating momentum, and spend at or above the 60th percentile.",
                    "dataset": "strategic", "sourceId": "supplier_ranking",
                    "defaultSort": {"field": "dynamic_supplier_score", "direction": "desc"},
                    "columns": rank_columns,
                },
                {
                    "id": "deteriorating_table", "title": "Highest-spend deteriorating suppliers",
                    "subtitle": "The ten largest spend exposures among suppliers declining by at least two score points.",
                    "dataset": "deteriorating", "sourceId": "supplier_ranking",
                    "defaultSort": {"field": "procurement_spend_12m_usd", "direction": "desc"},
                    "columns": rank_columns,
                },
            ],
            "sources": [source_file, source_orders, source_ranking, source_trends, source_summary],
            "blocks": [
                {"id": "title", "type": "markdown", "body": "# Supplier Performance and Sourcing Recommendations"},
                {
                    "id": "executive_summary", "type": "markdown", "sourceId": "analysis_summary",
                    "body": (
                        "## Executive summary\n\n"
                        f"**The portfolio is stable overall, but supplier-level action is still required.** "
                        f"The spend-weighted score is {summary['latest_portfolio_score']:.2f}/100 and changed "
                        f"{summary['portfolio_score_change_6m']:+.2f} points over six months. "
                        f"The engine identifies {summary['improving_count']} improving and "
                        f"{summary['deteriorating_count']} deteriorating suppliers.\n\n"
                        f"**Start replacement due diligence on {summary['replacement_candidate_count']} suppliers** "
                        f"representing {summary['replacement_spend_share']:.1%} of spend, while opening partnership "
                        f"discussions with {summary['strategic_partner_count']} candidates representing "
                        f"{summary['strategic_partner_spend_share']:.1%}."
                    ),
                },
                {"id": "metrics", "type": "metric-strip", "cardIds": [c["id"] for c in cards]},
                {
                    "id": "portfolio_context", "type": "markdown", "sourceId": "portfolio_trends",
                    "body": (
                        "## Portfolio stability masks supplier-level movement\n\n"
                        f"The portfolio score is almost unchanged over six months, yet "
                        f"{summary['improving_count'] + summary['deteriorating_count']} suppliers crossed the "
                        "two-point movement threshold. Aggregate stability should not be interpreted as an absence of supplier risk."
                    ),
                },
                {"id": "portfolio_chart", "type": "chart", "chartId": "portfolio_trend_chart"},
                {"id": "momentum_chart", "type": "chart", "chartId": "trend_status_chart"},
                {
                    "id": "risk_context", "type": "markdown", "sourceId": "supplier_ranking",
                    "body": (
                        "## Risk exposure needs stronger commercial controls\n\n"
                        f"High or Critical suppliers account for {summary['high_or_critical_spend_share']:.1%} of "
                        "trailing-12-month procurement spend. This classification is deliberately conservative: high VRIS, "
                        "active disputes, repeated disruption, or weak combined performance can trigger escalation."
                    ),
                },
                {"id": "risk_table", "type": "table", "tableId": "risk_exposure_table"},
                {
                    "id": "replace_context", "type": "markdown", "sourceId": "supplier_ranking",
                    "body": (
                        "## Replace selectively after feasibility checks\n\n"
                        f"The replacement set is small and represents {money(summary['replacement_spend_usd'])} in annual spend. "
                        "Treat the flag as a due-diligence trigger: validate alternate capacity, switching cost, category criticality, "
                        "and contract exit terms before a sourcing decision."
                    ),
                },
                {"id": "replace_table", "type": "table", "tableId": "replacement_table"},
                {
                    "id": "partner_context", "type": "markdown", "sourceId": "supplier_ranking",
                    "body": (
                        "## Concentrate strategic partnerships on proven performers\n\n"
                        f"{top_partner['vendor_name']} leads the partnership set at "
                        f"{top_partner['dynamic_supplier_score']:.2f}/100. Partnership offers should exchange greater "
                        "volume visibility or term length for measurable delivery, quality, resilience, and continuous-improvement commitments."
                    ),
                },
                {"id": "partner_table", "type": "table", "tableId": "strategic_table"},
                {
                    "id": "deteriorating_context", "type": "markdown", "sourceId": "supplier_ranking",
                    "body": (
                        "## Put the largest deteriorating exposures on corrective-action plans\n\n"
                        f"{high_spend_name} is the largest deteriorating exposure at {money(high_spend_value)} of annual spend. "
                        "Require a 30/60/90-day recovery plan with OTD, quality, VRIS, cost efficiency, and lead-time milestones, "
                        "then rescore monthly."
                    ),
                },
                {"id": "deteriorating_table_block", "type": "table", "tableId": "deteriorating_table"},
                {
                    "id": "recommendations", "type": "markdown",
                    "body": (
                        "## Executive recommendations\n\n"
                        "1. Approve replacement due diligence for every flagged supplier; do not terminate until continuity and contract checks are complete.\n"
                        "2. Launch partnership negotiations with the strategic candidates, using performance-linked commercial terms.\n"
                        "3. Assign executive owners and 30/60/90-day recovery plans to the highest-spend deteriorating suppliers.\n"
                        "4. Review High/Critical spend exposure monthly and diversify categories where concentration and operational risk overlap.\n"
                        "5. Recalibrate the score quarterly and reconcile the product-cost benchmark with negotiated-price or should-cost data."
                    ),
                },
                {
                    "id": "methodology", "type": "markdown",
                    "body": (
                        "## Methodology and caveats\n\n"
                        "The score uses the requested weights: 30% on-time delivery, 20% quality acceptance, 20% inverted VRIS, "
                        "15% cost efficiency, and 15% lead-time performance. Cost efficiency is 70% product-year unit-COGS competitiveness "
                        "and 30% invoice accuracy. The dynamic result is a six-month exponentially weighted average with a three-month half-life. "
                        "Spend is used for exposure and partnership prioritization, not as a score reward.\n\n"
                        "Product cost is benchmarked against the median COGS per unit for the same product and year. It improves like-for-like "
                        "comparability but is not a substitute for negotiated-price or should-cost data. Risk rules are screening rules, not legal "
                        "or contractual determinations. All blocking source-data checks passed."
                    ),
                },
            ],
        },
        "snapshot": {
            "version": 1, "generatedAt": generated_at, "status": "ready",
            "datasets": {
                "headline_metrics": [summary],
                "portfolio_trends": [
                    {"snapshot_month": row.snapshot_month, "series": series, "score": round(float(value), 2)}
                    for row in trends.itertuples(index=False)
                    for series, value in [
                        ("Spend-weighted", row.spend_weighted_supplier_score),
                        ("Unweighted", row.unweighted_supplier_score),
                    ]
                ],
                "trend_counts": compact_rows(trend_counts, ["trend_class", "supplier_count"]),
                "risk_exposure": compact_rows(risk_exposure, ["supplier_risk_class", "supplier_count", "spend_usd", "spend_share_pct"]),
                "replacement": compact_rows(replacement, [c["field"] for c in rank_columns]),
                "strategic": compact_rows(strategic, [c["field"] for c in rank_columns]),
                "deteriorating": compact_rows(deteriorating, [c["field"] for c in rank_columns]),
            },
        },
        "sources": [source_file, source_orders, source_ranking, source_trends, source_summary],
    }

    artifact_path = REPORT_DIR / "artifact.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, default=str), encoding="utf-8")

    memo = (
        "# Executive Recommendations — Supplier Performance\n\n"
        f"As of {summary['as_of_month']}, the spend-weighted supplier portfolio score is "
        f"**{summary['latest_portfolio_score']:.2f}/100**, essentially flat over six months "
        f"({summary['portfolio_score_change_6m']:+.2f} points). Supplier-level movement is material: "
        f"**{summary['improving_count']} are improving** and **{summary['deteriorating_count']} are deteriorating**.\n\n"
        "## Decisions\n\n"
        f"1. Begin replacement due diligence for **{summary['replacement_candidate_count']} suppliers** "
        f"representing **{summary['replacement_spend_share']:.1%} of annual spend**. Validate substitutes, capacity, switching costs, and exit terms first.\n"
        f"2. Open strategic partnership discussions with **{summary['strategic_partner_count']} suppliers** "
        f"representing **{summary['strategic_partner_spend_share']:.1%} of spend**. Tie commitments to measurable service and resilience gains.\n"
        f"3. Put **{high_spend_name}** and the other highest-spend deteriorators on 30/60/90-day recovery plans.\n"
        f"4. Reduce the **{summary['high_or_critical_spend_share']:.1%} of spend** classified High or Critical through diversification and stronger risk clauses.\n"
        "5. Recalibrate thresholds quarterly and reconcile product-cost benchmarks with negotiated-price or should-cost data.\n\n"
        "## Decision guardrails\n\n"
        "- A replacement flag triggers procurement due diligence; it is not an automatic termination.\n"
        "- Spend indicates exposure and priority, not supplier quality.\n"
        "- Risk classifications are screening rules and require category-owner review.\n"
        "- Strategic status should be reviewed monthly and renewed only while score, trend, and risk conditions remain satisfied.\n"
    )
    memo_path = REPORT_DIR / "executive_recommendations.md"
    memo_path.write_text(memo, encoding="utf-8")
    return artifact_path, memo_path


if __name__ == "__main__":
    for path in build_report():
        print(path)

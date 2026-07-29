"""Attach the executed reconciliation-query files to report widgets."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Reports" / "module2_supplier_performance"
ARTIFACT_PATH = REPORT_DIR / "artifact.json"
QUERY_DIR = REPORT_DIR / "queries"


def execute_reconciliation_queries() -> None:
    ranking = pd.read_csv(REPORT_DIR / "supplier_ranking.csv")
    trends = pd.read_csv(REPORT_DIR / "portfolio_monthly_trends.csv")
    summary = pd.DataFrame([json.loads((REPORT_DIR / "analysis_summary.json").read_text(encoding="utf-8"))])
    with sqlite3.connect(":memory:") as connection:
        ranking.to_sql("supplier_ranking", connection, index=False)
        trends.to_sql("portfolio_monthly_trends", connection, index=False)
        summary[[
            "supplier_count", "latest_portfolio_score", "portfolio_score_change_6m",
            "replacement_candidate_count", "replacement_spend_share",
            "strategic_partner_count", "strategic_partner_spend_share",
        ]].to_sql("analysis_summary", connection, index=False)
        for query_path in sorted(QUERY_DIR.glob("*.sql")):
            pd.read_sql_query(query_path.read_text(encoding="utf-8"), connection)


def attach_sources() -> None:
    payload = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    query_sources = {
        "headline_sql": "headline_metrics.sql",
        "portfolio_trends_sql": "portfolio_trends.sql",
        "supplier_momentum_sql": "supplier_momentum.sql",
        "risk_exposure_sql": "risk_exposure.sql",
        "replacement_sql": "replacement_candidates.sql",
        "strategic_sql": "strategic_candidates.sql",
        "deteriorating_sql": "deteriorating_exposure.sql",
    }
    new_sources = [
        {
            "id": source_id,
            "label": filename.replace("_", " ").replace(".sql", "").title(),
            "path": f"Reports/module2_supplier_performance/queries/{filename}",
        }
        for source_id, filename in query_sources.items()
    ]
    payload["manifest"]["sources"].extend(new_sources)
    payload["sources"].extend(new_sources)

    for card in payload["manifest"]["cards"]:
        card["sourceId"] = "headline_sql"
    for chart in payload["manifest"]["charts"]:
        chart["sourceId"] = (
            "portfolio_trends_sql" if chart["id"] == "portfolio_trend_chart" else "supplier_momentum_sql"
        )
    table_sources = {
        "risk_exposure_table": "risk_exposure_sql",
        "replacement_table": "replacement_sql",
        "strategic_table": "strategic_sql",
        "deteriorating_table": "deteriorating_sql",
    }
    for table in payload["manifest"]["tables"]:
        table["sourceId"] = table_sources[table["id"]]
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    execute_reconciliation_queries()
    attach_sources()
    print(ARTIFACT_PATH)

"""Apply reviewed fixes to the supplier scoring source and artifact builders.

This helper exists because the workspace patch wrapper cannot update existing
files under the current Windows restricted-token sandbox. Each replacement is
guarded so it fails loudly if the expected source text has changed.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"Expected exactly one match in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


scoring = ROOT / "scripts" / "supplier_performance_scoring.py"
replace_once(
    scoring,
    'source, writes decision-ready CSV/JSON outputs, and keeps every business rule in\n',
    'source plus product-level order costs, writes decision-ready CSV/JSON outputs, and keeps every business rule in\n',
)
replace_once(
    scoring,
    'INPUT_PATH = ROOT / "data" / "cleaned" / "vendors_clean.csv"\n',
    'INPUT_PATH = ROOT / "data" / "cleaned" / "vendors_clean.csv"\n'
    'ORDERS_PATH = ROOT / "data" / "cleaned" / "orders_clean.csv"\n',
)
replace_once(
    scoring,
    '\n\ndef add_monthly_scores(df: pd.DataFrame) -> pd.DataFrame:\n'
    '    scored = df.copy()\n',
    '''\n\ndef build_cost_competitiveness(order_path: Path = ORDERS_PATH) -> pd.DataFrame:\n'''
    '''    """Benchmark supplier unit COGS against the same product in the same year."""\n'''
    '''    orders = pd.read_csv(\n'''
    '''        order_path,\n'''
    '''        usecols=[\n'''
    '''            "order_date", "vendor_id", "product_id", "order_quantity",\n'''
    '''            "cost_of_goods_usd",\n'''
    '''        ],\n'''
    '''    )\n'''
    '''    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="raise")\n'''
    '''    orders["year"] = orders["order_date"].dt.year\n'''
    '''    valid = (\n'''
    '''        orders["vendor_id"].notna()\n'''
    '''        & orders["product_id"].notna()\n'''
    '''        & orders["order_quantity"].gt(0)\n'''
    '''        & orders["cost_of_goods_usd"].gt(0)\n'''
    '''    )\n'''
    '''    orders = orders.loc[valid].copy()\n'''
    '''    orders["unit_cogs_usd"] = orders["cost_of_goods_usd"] / orders["order_quantity"]\n'''
    '''    orders["product_year_median_unit_cogs"] = orders.groupby(\n'''
    '''        ["product_id", "year"]\n'''
    '''    )["unit_cogs_usd"].transform("median")\n'''
    '''    orders["order_cost_competitiveness_score"] = (\n'''
    '''        100 * orders["product_year_median_unit_cogs"] / orders["unit_cogs_usd"]\n'''
    '''    ).clip(0, 100)\n\n'''
    '''    records = []\n'''
    '''    for (vendor_id, year), group in orders.groupby(["vendor_id", "year"], sort=False):\n'''
    '''        records.append(\n'''
    '''            {\n'''
    '''                "vendor_id": vendor_id,\n'''
    '''                "year": int(year),\n'''
    '''                "product_cost_competitiveness_score": weighted_average(\n'''
    '''                    group["order_cost_competitiveness_score"],\n'''
    '''                    group["cost_of_goods_usd"],\n'''
    '''                ),\n'''
    '''                "cost_benchmark_order_count": int(len(group)),\n'''
    '''            }\n'''
    '''        )\n'''
    '''    return pd.DataFrame(records)\n\n\n'''
    '''def add_monthly_scores(\n'''
    '''    df: pd.DataFrame,\n'''
    '''    cost_competitiveness: pd.DataFrame,\n'''
    ''') -> pd.DataFrame:\n'''
    '''    scored = df.copy()\n'''
    '''    scored["year"] = scored["snapshot_month"].dt.year\n'''
    '''    scored = scored.merge(\n'''
    '''        cost_competitiveness,\n'''
    '''        on=["vendor_id", "year"],\n'''
    '''        how="left",\n'''
    '''        validate="many_to_one",\n'''
    '''    )\n'''
    '''    if scored["product_cost_competitiveness_score"].isna().any():\n'''
    '''        missing = int(scored["product_cost_competitiveness_score"].isna().sum())\n'''
    '''        raise ValueError(f"Missing product cost benchmarks for {missing} vendor-month rows")\n''',
)
replace_once(
    scoring,
    '    # Invoice accuracy is the cleanest governed proxy for cost control in the\n'
    '    # supplied data.  Spend is retained as exposure, not rewarded as performance.\n'
    '    scored["cost_efficiency_score"] = scored["invoice_accuracy_rate"].clip(0, 100)\n',
    '    # Cost efficiency combines like-for-like product cost competitiveness with\n'
    '    # invoice accuracy. Spend is retained as exposure, not rewarded as performance.\n'
    '    scored["cost_efficiency_score"] = (\n'
    '        0.70 * scored["product_cost_competitiveness_score"].clip(0, 100)\n'
    '        + 0.30 * scored["invoice_accuracy_rate"].clip(0, 100)\n'
    '    )\n',
)
replace_once(
    scoring,
    '        and row["supplier_risk_class"] != "Critical"\n'
    '        and row["trend_class"] != "Deteriorating"\n',
    '        and row["supplier_risk_class"] in {"Low", "Medium"}\n'
    '        and row["trend_class"] != "Deteriorating"\n',
)
replace_once(
    scoring,
    'def build_monthly_trends(scored: pd.DataFrame) -> pd.DataFrame:\n'
    '    return (\n',
    'def build_monthly_trends(scored: pd.DataFrame) -> pd.DataFrame:\n'
    '    trends = (\n',
)
replace_once(
    scoring,
    '        .reset_index()\n'
    '        .round(2)\n'
    '    )\n\n\n'
    'def build_summary',
    '        .reset_index()\n'
    '    )\n'
    '    numeric_columns = trends.select_dtypes(include="number").columns\n'
    '    trends[numeric_columns] = trends[numeric_columns].round(2)\n'
    '    return trends\n\n\n'
    'def build_summary',
)
replace_once(
    scoring,
    '    raw, checks = load_and_validate(input_path)\n'
    '    scored = add_monthly_scores(raw)\n',
    '''    raw, checks = load_and_validate(input_path)\n'''
    '''    cost_competitiveness = build_cost_competitiveness()\n'''
    '''    expected_vendor_years = raw.assign(year=raw["snapshot_month"].dt.year)[\n'''
    '''        ["vendor_id", "year"]\n'''
    '''    ].drop_duplicates()\n'''
    '''    cost_coverage = expected_vendor_years.merge(\n'''
    '''        cost_competitiveness[["vendor_id", "year"]],\n'''
    '''        on=["vendor_id", "year"],\n'''
    '''        how="left",\n'''
    '''        indicator=True,\n'''
    '''        validate="one_to_one",\n'''
    '''    )\n'''
    '''    missing_cost_years = int(cost_coverage["_merge"].ne("both").sum())\n'''
    '''    checks = pd.concat(\n'''
    '''        [\n'''
    '''            checks,\n'''
    '''            pd.DataFrame(\n'''
    '''                [{\n'''
    '''                    "check": "Product-year cost benchmark coverage",\n'''
    '''                    "passed": missing_cost_years == 0,\n'''
    '''                    "exceptions": missing_cost_years,\n'''
    '''                    "severity_if_failed": "High",\n'''
    '''                }]\n'''
    '''            ),\n'''
    '''        ],\n'''
    '''        ignore_index=True,\n'''
    '''    )\n'''
    '''    if missing_cost_years:\n'''
    '''        raise ValueError(f"Missing cost benchmarks for {missing_cost_years} vendor-years")\n'''
    '''    scored = add_monthly_scores(raw, cost_competitiveness)\n''',
)

notebook = ROOT / "scripts" / "build_supplier_performance_notebook.py"
replace_once(
    notebook,
    '            "- Invoice accuracy is the governed cost-efficiency proxy available in the source.\\n"\n',
    '            "- Cost efficiency is 70% product-year unit-cost competitiveness and 30% invoice accuracy.\\n"\n'
    '            "- Unit-cost competitiveness compares order COGS per unit with the median for the same product and year.\\n"\n',
)
replace_once(
    notebook,
    '            "import sys\\n"\n'
    '            "import pandas as pd\\n"\n'
    '            "import matplotlib.pyplot as plt\\n"\n'
    '            "from IPython.display import display\\n\\n"\n',
    '            "import sys\\n"\n'
    '            "from io import BytesIO\\n"\n'
    '            "import pandas as pd\\n"\n'
    '            "import matplotlib.pyplot as plt\\n"\n'
    '            "from IPython.display import display, Image\\n\\n"\n',
)
replace_once(
    notebook,
    '            "ax.set_title(\'Monthly supplier performance score\')\\n"\n'
    '            "ax.set_ylabel(\'Score (0–100)\')\\n"\n'
    '            "ax.set_xlabel(\'Snapshot month\')\\n"\n'
    '            "ax.grid(axis=\'y\', color=\'#d9dee5\', linewidth=0.8)\\n"\n'
    '            "ax.spines[[\'top\', \'right\']].set_visible(False)\\n"\n'
    '            "ax.legend(frameon=False)\\n"\n'
    '            "plt.tight_layout()\\n"\n'
    '            "plt.show()"\n',
    '            "ax.set_title(\'Monthly supplier performance score\', loc=\'left\')\\n"\n'
    '            "ax.text(0, 1.02, \'Fixed 60–90 display range; underlying score scale is 0–100\',\\n"\n'
    '            "        transform=ax.transAxes, color=\'#59636e\', fontsize=9)\\n"\n'
    '            "ax.set_ylabel(\'Score (0–100 scale)\')\\n"\n'
    '            "ax.set_xlabel(\'Snapshot month\')\\n"\n'
    '            "ax.set_ylim(60, 90)\\n"\n'
    '            "ax.grid(axis=\'y\', color=\'#d9dee5\', linewidth=0.8)\\n"\n'
    '            "ax.spines[[\'top\', \'right\']].set_visible(False)\\n"\n'
    '            "ax.legend(frameon=False)\\n"\n'
    '            "plt.tight_layout()\\n"\n'
    '            "chart_buffer = BytesIO()\\n"\n'
    '            "fig.savefig(chart_buffer, format=\'png\', dpi=150, bbox_inches=\'tight\')\\n"\n'
    '            "plt.close(fig)\\n"\n'
    '            "display(Image(data=chart_buffer.getvalue(), alt=(\\n"\n'
    '            "    \'Line chart of monthly spend-weighted and unweighted supplier performance \'\\n"\n'
    '            "    \'scores from January 2021 to December 2024, displayed on a fixed 60 to 90 range.\'\\n"\n'
    '            ")))"\n',
)
replace_once(
    notebook,
    '            "5. **Recalibrate thresholds quarterly.** Validate invoice accuracy as the cost proxy once price-index or should-cost data becomes available."\n',
    '            "5. **Recalibrate thresholds quarterly.** Review the product-year cost benchmark and invoice-control blend against negotiated-price or should-cost data."\n',
)

report = ROOT / "scripts" / "build_supplier_performance_report.py"
replace_once(
    report,
    '                        "Require a 30/60/90-day recovery plan with OTD, quality, VRIS, invoice accuracy, and lead-time milestones, "\n',
    '                        "Require a 30/60/90-day recovery plan with OTD, quality, VRIS, cost efficiency, and lead-time milestones, "\n',
)
replace_once(
    report,
    '                        "5. Recalibrate the score quarterly and replace invoice accuracy with a price-index or should-cost measure when governed cost data is available."\n',
    '                        "5. Recalibrate the score quarterly and reconcile the product-cost benchmark with negotiated-price or should-cost data."\n',
)
replace_once(
    report,
    '                        "15% invoice accuracy, and 15% lead-time performance. The dynamic result is a six-month exponentially weighted "\n'
    '                        "average with a three-month half-life. Spend is used for exposure and partnership prioritization, not as a score reward.\\n\\n"\n'
    '                        "Invoice accuracy is a proxy for cost efficiency because the source does not include a governed market-price benchmark "\n'
    '                        "or should-cost index. Risk rules are screening rules, not legal or contractual determinations. All six blocking source-data checks passed."\n',
    '                        "15% cost efficiency, and 15% lead-time performance. Cost efficiency is 70% product-year unit-Cogs competitiveness "\n'
    '                        "and 30% invoice accuracy. The dynamic result is a six-month exponentially weighted average with a three-month half-life. "\n'
    '                        "Spend is used for exposure and partnership prioritization, not as a score reward.\\n\\n"\n'
    '                        "Product cost is benchmarked against the median COGS per unit for the same product and year. It improves like-for-like "\n'
    '                        "comparability but is not a substitute for negotiated-price or should-cost data. Risk rules are screening rules, not legal "\n'
    '                        "or contractual determinations. All blocking source-data checks passed."\n',
)
replace_once(
    report,
    '        "5. Recalibrate thresholds quarterly and add governed price-index or should-cost data to replace invoice accuracy as the cost-efficiency proxy.\\n\\n"\n',
    '        "5. Recalibrate thresholds quarterly and reconcile product-cost benchmarks with negotiated-price or should-cost data.\\n\\n"\n',
)

print("Supplier scoring fixes applied")

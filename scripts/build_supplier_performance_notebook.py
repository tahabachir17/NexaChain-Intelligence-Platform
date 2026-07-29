"""Generate the reader-facing Supplier Performance notebook with nbformat."""

from __future__ import annotations

import json
from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "Reports" / "module2_supplier_performance" / "analysis_summary.json"
NOTEBOOK_PATH = ROOT / "Notebooks" / "week_2" / "supplier_performance_scoring.ipynb"


def build_notebook() -> Path:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    }

    notebook["cells"] = [
        nbf.v4.new_markdown_cell(
            "# Supplier Performance Scoring\n\n"
            "## tl;dr\n\n"
            f"- **{summary['supplier_count']} suppliers** are ranked as of "
            f"**{summary['as_of_month']}** using a six-month recency-weighted score.\n"
            f"- The average dynamic score is **{summary['dynamic_score_mean']:.2f}/100**; "
            f"the latest spend-weighted portfolio score is **{summary['latest_portfolio_score']:.2f}/100**.\n"
            f"- **{summary['improving_count']} suppliers are improving** and "
            f"**{summary['deteriorating_count']} are deteriorating**.\n"
            f"- **{summary['replacement_candidate_count']} suppliers** meet the replacement rule; "
            f"they represent **{summary['replacement_spend_share']:.1%}** of trailing-12-month spend.\n"
            f"- **{summary['strategic_partner_count']} suppliers** qualify for strategic partnership; "
            f"they represent **{summary['strategic_partner_spend_share']:.1%}** of spend."
        ),
        nbf.v4.new_markdown_cell(
            "## Context & Methods\n\n"
            "The procurement team needs one directionally consistent 0–100 score that can be "
            "ranked, trended, and converted into action. The supplied weights are used exactly: "
            "30% on-time delivery, 20% quality, 20% risk performance, 15% cost efficiency, "
            "and 15% lead time.\n\n"
            "Sources: `data/cleaned/vendors_clean.csv` and `data/cleaned/orders_clean.csv`.\n\n"
            "### Key Assumptions\n\n"
            "- VRIS is an adverse risk measure, so the scored component is `100 - VRIS`.\n"
            "- Cost efficiency is 70% product-year unit-cost competitiveness and 30% invoice accuracy.\n"
            "- Unit-cost competitiveness compares order COGS per unit with the median for the same product and year.\n"
            "- Procurement spend measures exposure and strategic importance; it does not boost performance.\n"
            "- Lead-time performance combines 80% contract adherence and 20% consistency.\n"
            "- The dynamic score is a six-month exponentially weighted average with a three-month half-life.\n"
            "- Improving/deteriorating means a change of at least +/-2 points between the latest and prior three-month averages."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import sys\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "from IPython.display import display\n\n"
            "ROOT = Path.cwd()\n"
            "if not (ROOT / 'data').exists():\n"
            "    ROOT = ROOT.parents[1]\n"
            "sys.path.insert(0, str(ROOT))\n"
            "from scripts.supplier_performance_scoring import run_pipeline, WEIGHTS\n"
            "pd.set_option('display.max_columns', 30)\n"
            "pd.set_option('display.float_format', lambda x: f'{x:,.2f}')"
        ),
        nbf.v4.new_markdown_cell("## Data\n\n### 1. Load, validate, and score vendor snapshots with product-level order costs"),
        nbf.v4.new_code_cell(
            "result = run_pipeline()\n"
            "raw = result['raw']\n"
            "scored = result['scored']\n"
            "ranking = result['ranking']\n"
            "trends = result['trends']\n"
            "checks = result['checks']\n"
            "summary = result['summary']\n\n"
            "display(checks)\n"
            "print(f\"Rows: {len(raw):,} | Suppliers: {raw.vendor_id.nunique():,} | \"\n"
            "      f\"Window: {raw.snapshot_month.min().date()} to {raw.snapshot_month.max().date()}\")"
        ),
        nbf.v4.new_markdown_cell("### 2. Confirm the score calculation and coverage"),
        nbf.v4.new_code_cell(
            "print('Weights:', WEIGHTS, '| Sum:', sum(WEIGHTS.values()))\n"
            "assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-12\n"
            "assert scored['supplier_score'].between(0, 100).all()\n"
            "assert ranking['dynamic_supplier_score'].between(0, 100).all()\n"
            "display(ranking[['months_in_dynamic_window']].describe().T)"
        ),
        nbf.v4.new_markdown_cell("## Results\n\n### 3. Review the supplier ranking"),
        nbf.v4.new_code_cell(
            "ranking_columns = ['supplier_rank', 'vendor_id', 'vendor_name', 'vendor_category',\n"
            "                   'dynamic_supplier_score', 'score_change_3m', 'trend_class',\n"
            "                   'supplier_risk_class', 'recommended_tier',\n"
            "                   'procurement_spend_12m_usd']\n"
            "display(ranking[ranking_columns].head(20))"
        ),
        nbf.v4.new_markdown_cell("### 4. Compare score momentum across the portfolio"),
        nbf.v4.new_code_cell(
            "fig, ax = plt.subplots(figsize=(11, 5.5))\n"
            "ax.plot(trends['snapshot_month'], trends['spend_weighted_supplier_score'],\n"
            "        color='#2f6b9a', linewidth=2.2, label='Spend-weighted')\n"
            "ax.plot(trends['snapshot_month'], trends['unweighted_supplier_score'],\n"
            "        color='#c58b2a', linewidth=1.8, linestyle='--', label='Unweighted')\n"
            "ax.set_title('Monthly supplier performance score', loc='left')\n"
            "ax.text(0, 1.02, 'Fixed 60–90 display range; underlying score scale is 0–100',\n"
            "        transform=ax.transAxes, color='#59636e', fontsize=9)\n"
            "ax.set_ylabel('Score (0–100 scale)')\n"
            "ax.set_xlabel('Snapshot month')\n"
            "ax.set_ylim(60, 90)\n"
            "ax.grid(axis='y', color='#d9dee5', linewidth=0.8)\n"
            "ax.spines[['top', 'right']].set_visible(False)\n"
            "ax.legend(frameon=False)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        nbf.v4.new_markdown_cell("### 5. Identify improving and deteriorating suppliers"),
        nbf.v4.new_code_cell(
            "display(ranking.nlargest(10, 'score_change_3m')[ranking_columns])\n"
            "display(ranking.nsmallest(10, 'score_change_3m')[ranking_columns])"
        ),
        nbf.v4.new_markdown_cell("### 6. Prioritize replacement and strategic partnership decisions"),
        nbf.v4.new_code_cell(
            "replacement = ranking.loc[ranking['replacement_candidate'], ranking_columns]\n"
            "strategic = ranking.loc[ranking['recommended_tier'].eq('Strategic Partner'), ranking_columns]\n"
            "print('Replacement candidates')\n"
            "display(replacement)\n"
            "print('Strategic partnership candidates')\n"
            "display(strategic)"
        ),
        nbf.v4.new_markdown_cell(
            "## Takeaways\n\n"
            "1. **Use the ranking for performance decisions, and spend for sequencing.** Spend is exposure, not a performance reward.\n"
            "2. **Start replacement due diligence with the flagged candidates.** Confirm category substitutability, contractual constraints, and capacity before exiting.\n"
            "3. **Offer partnership plans to the strategic candidates.** Tie longer commitments to service-level, quality, and risk-monitoring clauses.\n"
            "4. **Place high-spend deteriorators on 30/60/90-day corrective-action plans.** Trend and exposure together determine urgency.\n"
            "5. **Recalibrate thresholds quarterly.** Review the product-year cost benchmark and invoice-control blend against negotiated-price or should-cost data."
        ),
    ]
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, NOTEBOOK_PATH)
    return NOTEBOOK_PATH


if __name__ == "__main__":
    print(build_notebook())

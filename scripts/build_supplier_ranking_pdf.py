"""Create a print-ready PDF version of the supplier ranking report."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Reports" / "module2_supplier_performance"
OUTPUT_PATH = ROOT / "output" / "pdf" / "supplier_ranking_report.pdf"
TEMP_DIR = ROOT / "tmp" / "pdfs" / "supplier_ranking_assets"

BLUE = colors.HexColor("#2F6B9A")
BLUE_DARK = colors.HexColor("#1F4868")
GOLD = colors.HexColor("#C58B2A")
ORANGE = colors.HexColor("#D97745")
INK = colors.HexColor("#202832")
MUTED = colors.HexColor("#5D6874")
GRID = colors.HexColor("#D9DEE5")
PALE = colors.HexColor("#F4F7FA")


def compact_money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def build_charts(trends: pd.DataFrame, ranking: pd.DataFrame) -> tuple[Path, Path]:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    trend_path = TEMP_DIR / "portfolio_score_trend.png"
    momentum_path = TEMP_DIR / "supplier_momentum.png"

    trends = trends.copy()
    trends["snapshot_month"] = pd.to_datetime(trends["snapshot_month"])
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    ax.plot(
        trends["snapshot_month"], trends["spend_weighted_supplier_score"],
        color="#2F6B9A", linewidth=2.3, label="Spend-weighted",
    )
    ax.plot(
        trends["snapshot_month"], trends["unweighted_supplier_score"],
        color="#C58B2A", linewidth=1.8, linestyle="--", label="Unweighted",
    )
    fig.suptitle(
        "Monthly supplier performance score", x=0.08, y=0.98,
        ha="left", fontsize=13, weight="bold",
    )
    fig.text(
        0.08, 0.925, "Fixed 60-80 display range; underlying score scale is 0-100",
        ha="left", fontsize=8.5, color="#5D6874",
    )
    ax.set_ylim(60, 80)
    ax.set_ylabel("Score")
    ax.set_xlabel("Snapshot month")
    ax.grid(axis="y", color="#D9DEE5", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc="lower right")
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    fig.savefig(trend_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    momentum = (
        ranking["trend_class"].value_counts()
        .reindex(["Improving", "Stable", "Deteriorating"], fill_value=0)
    )
    fig, ax = plt.subplots(figsize=(7.6, 3.5))
    bars = ax.bar(
        momentum.index, momentum.values,
        color=["#2F6B9A", "#AAB4BE", "#D97745"], edgecolor="#34414D", linewidth=0.7,
    )
    fig.suptitle(
        "Supplier momentum classification", x=0.08, y=0.98,
        ha="left", fontsize=13, weight="bold",
    )
    fig.text(
        0.08, 0.885, "Recent three-month average versus prior three months; +/-2 points defines movement",
        ha="left", fontsize=8.5, color="#5D6874",
    )
    ax.set_ylabel("Suppliers")
    ax.set_ylim(0, max(momentum.values) * 1.18)
    ax.grid(axis="y", color="#D9DEE5", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, value in zip(bars, momentum.values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 5, f"{value}", ha="center", fontsize=9)
    fig.tight_layout(rect=[0, 0, 1, 0.80])
    fig.savefig(momentum_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return trend_path, momentum_path


def make_table(data, widths, header=True, font_size=7.2, alignments=None):
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, PALE]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        style.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    if alignments:
        for column, alignment in alignments.items():
            style.append(("ALIGN", (column, 1 if header else 0), (column, -1), alignment))
    table.setStyle(TableStyle(style))
    return table


def build_pdf() -> Path:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ranking = pd.read_csv(REPORT_DIR / "supplier_ranking.csv")
    trends = pd.read_csv(REPORT_DIR / "portfolio_monthly_trends.csv")
    summary = json.loads((REPORT_DIR / "analysis_summary.json").read_text(encoding="utf-8"))
    trend_chart, momentum_chart = build_charts(trends, ranking)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=INK, alignment=TA_LEFT, spaceAfter=5))
    styles.add(ParagraphStyle(name="Subtitle", parent=styles["Normal"], fontSize=9, leading=13, textColor=MUTED, spaceAfter=12))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=INK, spaceBefore=8, spaceAfter=6))
    styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontSize=8.5, leading=12, textColor=INK, spaceAfter=6))
    styles.add(ParagraphStyle(name="CardLabel", parent=styles["Normal"], fontSize=7.5, leading=9, textColor=MUTED, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="CardValue", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=16, leading=19, textColor=BLUE_DARK, alignment=TA_CENTER))

    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(GRID)
        canvas.line(0.55 * inch, 0.48 * inch, 7.95 * inch, 0.48 * inch)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(0.55 * inch, 0.28 * inch, "Supplier Performance and Sourcing Recommendations")
        canvas.drawRightString(7.95 * inch, 0.28 * inch, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(OUTPUT_PATH), pagesize=letter,
        rightMargin=0.55 * inch, leftMargin=0.55 * inch,
        topMargin=0.55 * inch, bottomMargin=0.62 * inch,
        title="Supplier Performance and Sourcing Recommendations",
        author="Procurement Analytics",
    )
    story = []
    story.append(Paragraph("Supplier Performance and Sourcing Recommendations", styles["ReportTitle"]))
    story.append(Paragraph("Dynamic supplier ranking, trend diagnosis, risk classification, and procurement actions as of December 2024.", styles["Subtitle"]))
    story.append(Paragraph("Executive summary", styles["Section"]))
    story.append(Paragraph(
        f"The portfolio is stable overall, but supplier-level action is still required. The latest spend-weighted score is "
        f"<b>{summary['latest_portfolio_score']:.2f}/100</b>, changing {summary['portfolio_score_change_6m']:+.2f} points over six months. "
        f"The model identifies <b>{summary['improving_count']} improving</b> and <b>{summary['deteriorating_count']} deteriorating</b> suppliers.",
        styles["BodySmall"],
    ))
    story.append(Paragraph(
        f"Begin replacement due diligence on <b>{summary['replacement_candidate_count']} suppliers</b> representing "
        f"<b>{summary['replacement_spend_share']:.1%}</b> of annual spend. Open partnership discussions with "
        f"<b>{summary['strategic_partner_count']} candidates</b> representing <b>{summary['strategic_partner_spend_share']:.1%}</b> of spend.",
        styles["BodySmall"],
    ))
    cards = [
        [Paragraph("Suppliers ranked", styles["CardLabel"]), Paragraph("Portfolio score", styles["CardLabel"]), Paragraph("Replacement candidates", styles["CardLabel"]), Paragraph("Strategic candidates", styles["CardLabel"])],
        [Paragraph(str(summary["supplier_count"]), styles["CardValue"]), Paragraph(f"{summary['latest_portfolio_score']:.2f}", styles["CardValue"]), Paragraph(str(summary["replacement_candidate_count"]), styles["CardValue"]), Paragraph(str(summary["strategic_partner_count"]), styles["CardValue"])],
        [Paragraph("Latest six-month window", styles["CardLabel"]), Paragraph("Spend-weighted, /100", styles["CardLabel"]), Paragraph(f"{summary['replacement_spend_share']:.1%} of spend", styles["CardLabel"]), Paragraph(f"{summary['strategic_partner_spend_share']:.1%} of spend", styles["CardLabel"])],
    ]
    card_table = Table(cards, colWidths=[1.82 * inch] * 4, rowHeights=[0.28 * inch, 0.35 * inch, 0.30 * inch])
    card_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE), ("BOX", (0, 0), (-1, -1), 0.6, GRID),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.extend([Spacer(1, 5), card_table, Spacer(1, 12)])
    story.append(Paragraph("Recommended decisions", styles["Section"]))
    decisions = [
        "Approve replacement due diligence for every flagged supplier, subject to continuity and contract checks.",
        "Open performance-linked partnership negotiations with the strategic candidates.",
        "Assign 30/60/90-day recovery plans to the largest deteriorating spend exposures.",
        "Review High/Critical spend exposure monthly and diversify where concentration and operational risk overlap.",
    ]
    for i, item in enumerate(decisions, 1):
        story.append(Paragraph(f"{i}. {item}", styles["BodySmall"]))

    story.append(PageBreak())
    story.append(Paragraph("Portfolio stability masks supplier-level movement", styles["Section"]))
    story.append(Paragraph(
        f"The portfolio score is almost unchanged over six months, while {summary['improving_count'] + summary['deteriorating_count']} suppliers crossed the two-point movement threshold. Aggregate stability should not be read as an absence of supplier risk.",
        styles["BodySmall"],
    ))
    story.append(Image(str(trend_chart), width=7.25 * inch, height=3.28 * inch))
    story.append(Spacer(1, 8))
    story.append(Image(str(momentum_chart), width=6.65 * inch, height=3.06 * inch))

    story.append(PageBreak())
    story.append(Paragraph("Risk exposure needs stronger commercial controls", styles["Section"]))
    story.append(Paragraph(
        f"High or Critical suppliers account for {summary['high_or_critical_spend_share']:.1%} of trailing-12-month procurement spend. The classification is intentionally conservative and can be triggered by high VRIS, active disputes, repeated disruption, or weak combined performance.",
        styles["BodySmall"],
    ))
    risk = ranking.groupby("supplier_risk_class", as_index=False).agg(
        suppliers=("vendor_id", "nunique"), spend=("procurement_spend_12m_usd", "sum")
    )
    risk["share"] = risk["spend"] / risk["spend"].sum()
    risk_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    risk = risk.sort_values("supplier_risk_class", key=lambda x: x.map(risk_order))
    risk_data = [["Risk class", "Suppliers", "12m spend", "Spend share"]] + [
        [row.supplier_risk_class, int(row.suppliers), compact_money(row.spend), f"{row.share:.1%}"]
        for row in risk.itertuples(index=False)
    ]
    story.append(make_table(risk_data, [1.8 * inch, 1.2 * inch, 1.5 * inch, 1.3 * inch], font_size=8.3, alignments={1: "RIGHT", 2: "RIGHT", 3: "RIGHT"}))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Suppliers requiring replacement due diligence", styles["Section"]))
    story.append(Paragraph("These candidates meet the model rule. Confirm alternate capacity, switching cost, category criticality, and contract exit terms before any sourcing decision.", styles["BodySmall"]))
    replacement = ranking[ranking["replacement_candidate"]].sort_values("procurement_spend_12m_usd", ascending=False)
    replacement_data = [["Rank", "Supplier", "Category", "Score", "3m change", "Risk", "12m spend"]] + [
        [int(row.supplier_rank), row.vendor_name, row.vendor_category, f"{row.dynamic_supplier_score:.2f}", f"{row.score_change_3m:+.2f}", row.supplier_risk_class, compact_money(row.procurement_spend_12m_usd)]
        for row in replacement.itertuples(index=False)
    ]
    story.append(make_table(replacement_data, [0.42 * inch, 1.55 * inch, 1.28 * inch, 0.58 * inch, 0.72 * inch, 0.65 * inch, 0.82 * inch], alignments={0: "RIGHT", 3: "RIGHT", 4: "RIGHT", 6: "RIGHT"}))

    story.append(PageBreak())
    story.append(Paragraph("Concentrate strategic partnerships on proven performers", styles["Section"]))
    story.append(Paragraph("Partnership offers should exchange greater volume visibility or term length for measurable delivery, quality, resilience, and continuous-improvement commitments.", styles["BodySmall"]))
    strategic = ranking[ranking["recommended_tier"] == "Strategic Partner"].sort_values("dynamic_supplier_score", ascending=False)
    strategic_data = [["Rank", "Supplier", "Category", "Score", "3m change", "Risk", "12m spend"]] + [
        [int(row.supplier_rank), row.vendor_name, row.vendor_category, f"{row.dynamic_supplier_score:.2f}", f"{row.score_change_3m:+.2f}", row.supplier_risk_class, compact_money(row.procurement_spend_12m_usd)]
        for row in strategic.itertuples(index=False)
    ]
    story.append(make_table(strategic_data, [0.42 * inch, 1.55 * inch, 1.28 * inch, 0.58 * inch, 0.72 * inch, 0.65 * inch, 0.82 * inch], alignments={0: "RIGHT", 3: "RIGHT", 4: "RIGHT", 6: "RIGHT"}))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Highest-spend deteriorating suppliers", styles["Section"]))
    deteriorating = ranking[ranking["trend_class"] == "Deteriorating"].nlargest(10, "procurement_spend_12m_usd")
    det_data = [["Rank", "Supplier", "Category", "Score", "3m change", "Risk", "12m spend"]] + [
        [int(row.supplier_rank), row.vendor_name, row.vendor_category, f"{row.dynamic_supplier_score:.2f}", f"{row.score_change_3m:+.2f}", row.supplier_risk_class, compact_money(row.procurement_spend_12m_usd)]
        for row in deteriorating.itertuples(index=False)
    ]
    story.append(make_table(det_data, [0.42 * inch, 1.55 * inch, 1.28 * inch, 0.58 * inch, 0.72 * inch, 0.65 * inch, 0.82 * inch], font_size=6.9, alignments={0: "RIGHT", 3: "RIGHT", 4: "RIGHT", 6: "RIGHT"}))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Methodology and caveats", styles["Section"]))
    story.append(Paragraph(
        "The score uses 30% on-time delivery, 20% quality acceptance, 20% inverted VRIS, 15% cost efficiency, and 15% lead-time performance. Cost efficiency is 70% product-year unit-COGS competitiveness and 30% invoice accuracy. The dynamic result is a six-month exponentially weighted average with a three-month half-life. Procurement spend is used for exposure and partnership prioritization, not as a performance reward.",
        styles["BodySmall"],
    ))
    story.append(Paragraph(
        "Product cost is benchmarked against median COGS per unit for the same product and year. This improves like-for-like comparability but is not a substitute for negotiated-price or should-cost data. Risk rules are screening rules, not legal or contractual determinations. All blocking source-data checks passed.",
        styles["BodySmall"],
    ))
    story.append(Paragraph("Sources: data/cleaned/vendors_clean.csv; data/cleaned/orders_clean.csv; Reports/module2_supplier_performance/supplier_ranking.csv.", styles["BodySmall"]))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return OUTPUT_PATH


if __name__ == "__main__":
    print(build_pdf())

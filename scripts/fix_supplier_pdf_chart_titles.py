"""Correct chart title/subtitle spacing in the supplier PDF builder."""

from pathlib import Path


path = Path(__file__).resolve().parents[1] / "scripts" / "build_supplier_ranking_pdf.py"
text = path.read_text(encoding="utf-8")

old_trend = '''    ax.set_title("Monthly supplier performance score", loc="left", fontsize=13, weight="bold")
    ax.text(
        0, 1.02, "Fixed 60-80 display range; underlying score scale is 0-100",
        transform=ax.transAxes, fontsize=8.5, color="#5D6874",
    )
'''
new_trend = '''    fig.suptitle(
        "Monthly supplier performance score", x=0.08, y=0.98,
        ha="left", fontsize=13, weight="bold",
    )
    fig.text(
        0.08, 0.925, "Fixed 60-80 display range; underlying score scale is 0-100",
        ha="left", fontsize=8.5, color="#5D6874",
    )
'''
if text.count(old_trend) != 1:
    raise RuntimeError("Trend title block not found")
text = text.replace(old_trend, new_trend, 1)
text = text.replace("    fig.tight_layout()\n    fig.savefig(trend_path", "    fig.tight_layout(rect=[0, 0, 1, 0.88])\n    fig.savefig(trend_path", 1)

old_momentum = '''    ax.set_title("Supplier momentum classification", loc="left", fontsize=13, weight="bold")
    ax.text(
        0, 1.02, "Recent three-month average versus prior three months; +/-2 points defines movement",
        transform=ax.transAxes, fontsize=8.5, color="#5D6874",
    )
'''
new_momentum = '''    fig.suptitle(
        "Supplier momentum classification", x=0.08, y=0.98,
        ha="left", fontsize=13, weight="bold",
    )
    fig.text(
        0.08, 0.925, "Recent three-month average versus prior three months; +/-2 points defines movement",
        ha="left", fontsize=8.5, color="#5D6874",
    )
'''
if text.count(old_momentum) != 1:
    raise RuntimeError("Momentum title block not found")
text = text.replace(old_momentum, new_momentum, 1)
text = text.replace("    fig.tight_layout()\n    fig.savefig(momentum_path", "    fig.tight_layout(rect=[0, 0, 1, 0.88])\n    fig.savefig(momentum_path", 1)

path.write_text(text, encoding="utf-8")
print(path)

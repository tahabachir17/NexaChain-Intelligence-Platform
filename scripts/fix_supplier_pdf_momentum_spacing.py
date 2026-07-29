from pathlib import Path


path = Path(__file__).with_name("build_supplier_ranking_pdf.py")
text = path.read_text(encoding="utf-8")
old = '''    fig.text(
        0.08, 0.925, "Recent three-month average versus prior three months; +/-2 points defines movement",
        ha="left", fontsize=8.5, color="#5D6874",
    )'''
new = '''    fig.text(
        0.08, 0.885, "Recent three-month average versus prior three months; +/-2 points defines movement",
        ha="left", fontsize=8.5, color="#5D6874",
    )'''
if old not in text:
    raise SystemExit("Momentum subtitle block was not found")
text = text.replace(old, new, 1)

marker = '"Supplier momentum classification"'
before, after = text.split(marker, 1)
old_layout = "    fig.tight_layout(rect=[0, 0, 1, 0.88])"
new_layout = "    fig.tight_layout(rect=[0, 0, 1, 0.80])"
if old_layout not in after:
    raise SystemExit("Momentum layout block was not found")
after = after.replace(old_layout, new_layout, 1)
path.write_text(before + marker + after, encoding="utf-8")

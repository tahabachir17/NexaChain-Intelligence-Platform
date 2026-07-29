"""Add the order-cost source to notebook and report provenance."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"Expected one match in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


notebook = ROOT / "scripts" / "build_supplier_performance_notebook.py"
replace_once(
    notebook,
    '            "and 15% lead time.\\n\\n"\n',
    '            "and 15% lead time.\\n\\n"\n'
    '            "Sources: `data/cleaned/vendors_clean.csv` and `data/cleaned/orders_clean.csv`.\\n\\n"\n',
)
replace_once(
    notebook,
    'nbf.v4.new_markdown_cell("## Data\\n\\n### 1. Load, validate, and score the monthly vendor snapshots"),',
    'nbf.v4.new_markdown_cell("## Data\\n\\n### 1. Load, validate, and score vendor snapshots with product-level order costs"),',
)

report = ROOT / "scripts" / "build_supplier_performance_report.py"
replace_once(
    report,
    '    source_ranking = {\n',
    '    source_orders = {\n'
    '        "id": "orders_source",\n'
    '        "label": "Cleaned order-level product costs",\n'
    '        "path": "data/cleaned/orders_clean.csv",\n'
    '    }\n'
    '    source_ranking = {\n',
)
replace_once(
    report,
    '            "sources": [source_file, source_ranking, source_trends, source_summary],\n',
    '            "sources": [source_file, source_orders, source_ranking, source_trends, source_summary],\n',
)
replace_once(
    report,
    '                    "id": "methodology", "type": "markdown", "sourceId": "vendor_source",\n',
    '                    "id": "methodology", "type": "markdown",\n',
)
replace_once(
    report,
    '        "sources": [source_file, source_ranking, source_trends, source_summary],\n',
    '        "sources": [source_file, source_orders, source_ranking, source_trends, source_summary],\n',
)

print("Supplier provenance fixes applied")

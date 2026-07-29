"""Finalize accessibility and reviewed wording after notebook export."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

report_builder = ROOT / "scripts" / "build_supplier_performance_report.py"
report_text = report_builder.read_text(encoding="utf-8")
if "unit-Cogs" in report_text:
    report_builder.write_text(report_text.replace("unit-Cogs", "unit-COGS"), encoding="utf-8")

html_path = ROOT / "Notebooks" / "week_2" / "supplier_performance_scoring.html"
html = html_path.read_text(encoding="utf-8")
generic_alt = 'alt="No description has been provided for this image"'
descriptive_alt = (
    'alt="Line chart of monthly spend-weighted and unweighted supplier performance '
    'scores from January 2021 to December 2024, displayed on a fixed 60 to 90 range."'
)
if html.count(generic_alt) != 1:
    raise RuntimeError("Expected exactly one generic notebook image alt attribute")
html_path.write_text(html.replace(generic_alt, descriptive_alt, 1), encoding="utf-8")
print(html_path)

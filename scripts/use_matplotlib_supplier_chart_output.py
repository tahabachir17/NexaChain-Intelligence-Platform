"""Use Matplotlib's native notebook renderer; HTML alt text is finalized after export."""

from pathlib import Path


path = Path(__file__).resolve().parents[1] / "scripts" / "build_supplier_performance_notebook.py"
text = path.read_text(encoding="utf-8")

old_imports = (
    '            "import sys\\n"\n'
    '            "from io import BytesIO\\n"\n'
    '            "import pandas as pd\\n"\n'
    '            "import matplotlib.pyplot as plt\\n"\n'
    '            "from IPython.display import display, Image\\n\\n"\n'
)
new_imports = (
    '            "import sys\\n"\n'
    '            "import pandas as pd\\n"\n'
    '            "import matplotlib.pyplot as plt\\n"\n'
    '            "from IPython.display import display\\n\\n"\n'
)
if text.count(old_imports) != 1:
    raise RuntimeError("Expected notebook import block was not found")
text = text.replace(old_imports, new_imports, 1)

old_tail = (
    '            "plt.tight_layout()\\n"\n'
    '            "chart_buffer = BytesIO()\\n"\n'
    '            "fig.savefig(chart_buffer, format=\'png\', dpi=150, bbox_inches=\'tight\')\\n"\n'
    '            "plt.close(fig)\\n"\n'
    '            "display(Image(data=chart_buffer.getvalue(), alt=(\\n"\n'
    '            "    \'Line chart of monthly spend-weighted and unweighted supplier performance \'\\n"\n'
    '            "    \'scores from January 2021 to December 2024, displayed on a fixed 60 to 90 range.\'\\n"\n'
    '            ")))"\n'
)
new_tail = (
    '            "plt.tight_layout()\\n"\n'
    '            "plt.show()"\n'
)
if text.count(old_tail) != 1:
    raise RuntimeError("Expected notebook chart-rendering block was not found")
path.write_text(text.replace(old_tail, new_tail, 1), encoding="utf-8")
print(path)

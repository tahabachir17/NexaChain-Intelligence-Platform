"""Normalize generated supplier artifact cells to the portable scalar contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "Reports" / "module2_supplier_performance" / "artifact.json"


payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
headline = payload["snapshot"]["datasets"]["headline_metrics"][0]
payload["snapshot"]["datasets"]["headline_metrics"] = [
    {key: value for key, value in headline.items() if isinstance(value, (str, int, float, bool)) or value is None}
]
ARTIFACT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(ARTIFACT)

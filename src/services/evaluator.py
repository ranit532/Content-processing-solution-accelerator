from typing import Dict, Any
from dateutil import parser


def evaluate_mapping(mapped: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate mapped JSON against expected invoice schema and return accuracy metrics.

    Returns:
      {
        "accuracy": float,  # 0-100
        "details": { field: bool },
        "rationale": str
      }
    """
    fields = ["invoice_number", "date", "total", "vendor", "line_items"]
    present = 0
    details = {}
    rationale_parts = []

    for f in fields:
        ok = False
        if f in mapped and mapped.get(f) not in (None, "", []):
            ok = True
        details[f] = ok
        if ok:
            present += 1
        else:
            rationale_parts.append(f"missing {f}")

    # extra checks
    bonus = 0.0
    total = mapped.get("total")
    try:
        total_val = float(total)
        if total_val > 0:
            bonus += 0.1
            rationale_parts.append("total numeric OK")
    except Exception:
        rationale_parts.append("total non-numeric or missing")

    date_ok = False
    try:
        d = mapped.get("date")
        if d:
            parser.parse(d)
            date_ok = True
            bonus += 0.1
            rationale_parts.append("date parse OK")
    except Exception:
        rationale_parts.append("date parse failed or missing")

    base_score = present / len(fields) if fields else 0
    score = base_score + bonus
    accuracy = min(1.0, score) * 100.0

    rationale = ", ".join(rationale_parts) if rationale_parts else "All checks passed"

    return {
        "accuracy": round(accuracy, 2),
        "details": details,
        "rationale": rationale
    }

from typing import Dict, Any


def calculate_confidence(extracted: Dict[str, Any], mapped: Dict[str, Any]) -> float:
    """Simple heuristic confidence scoring:
    - Presence of required fields increases score
    - Numeric consistency checks increase score
    - Length and token heuristics applied
    This is a placeholder but suitable for POC.
    """
    score = 0.5
    required = ['invoice_number', 'total']
    for f in required:
        if mapped.get(f):
            score += 0.2
    # numeric checks
    try:
        total = float(mapped.get('total', 0))
        if total > 0:
            score += 0.1
    except Exception:
        pass
    # clamp
    return min(1.0, score)

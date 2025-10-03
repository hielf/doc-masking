from __future__ import annotations

from typing import Dict, List, Any


def _overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> int:
    return max(0, min(a_end, b_end) - max(a_start, b_start))


def evaluate_entities(true_entities: List[Dict[str, Any]], pred_entities: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Compute counters-only precision/recall metrics. No content logging.

    A prediction is correct if it overlaps any true span of the same type.
    """
    # Index true by type for quick lookup
    type_to_true: Dict[str, List[Dict[str, Any]]] = {}
    for t in true_entities:
        et = str(t.get("type", ""))
        type_to_true.setdefault(et, []).append(t)

    tp = 0
    fp = 0
    fn = 0

    matched_true_ids = set()

    for p in pred_entities:
        et = str(p.get("type", ""))
        s = int(p.get("start", 0))
        e = int(p.get("end", 0))
        candidates = type_to_true.get(et, [])
        found = False
        for idx, t in enumerate(candidates):
            ts = int(t.get("start", 0))
            te = int(t.get("end", 0))
            if _overlap(s, e, ts, te) > 0 and (et, idx, ts, te) not in matched_true_ids:
                tp += 1
                matched_true_ids.add((et, idx, ts, te))
                found = True
                break
        if not found:
            fp += 1

    # Count unmatched true as FN
    total_true = sum(len(v) for v in type_to_true.values())
    fn = total_true - len(matched_true_ids)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "true": float(total_true),
        "pred": float(tp + fp),
        "tp": float(tp),
        "fp": float(fp),
        "fn": float(fn),
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }



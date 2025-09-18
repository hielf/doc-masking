from typing import List, Dict, Any


def merge_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not entities:
        return []
    entities_sorted = sorted(entities, key=lambda e: (e["start"], -e["end"]))
    merged: List[Dict[str, Any]] = []
    current = entities_sorted[0].copy()
    for e in entities_sorted[1:]:
        if e["start"] <= current["end"] and e["type"] == current["type"]:
            # overlap: extend and keep higher score
            current["end"] = max(current["end"], e["end"])
            current["score"] = max(float(current.get("score", 0.0)), float(e.get("score", 0.0)))
        else:
            merged.append(current)
            current = e.copy()
    merged.append(current)
    return merged


def filter_by_policy(entities: List[Dict[str, Any]], policy: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(policy, dict):
        return entities
    selected = set(policy.get("entities", []))
    if not selected:
        return []
    thresholds = policy.get("thresholds", {}) or {}
    filtered: List[Dict[str, Any]] = []
    for e in entities:
        et = e.get("type")
        if et not in selected:
            continue
        thr = float(thresholds.get(et, 0.0))
        if float(e.get("score", 1.0)) >= thr:
            filtered.append(e)
    return filtered



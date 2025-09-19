from typing import List, Dict, Any


COMMON_STREET_SUFFIXES = {
    "st", "street", "ave", "avenue", "rd", "road", "blvd", "lane", "ln", "dr", "drive",
    "ct", "court", "pl", "place", "trl", "trail", "pkwy", "parkway", "sq", "square",
    "hwy", "highway", "cir", "circle", "way"
}

UNIT_KEYWORDS = {"apt", "unit", "suite", "ste", "#"}

CITY_LABELS = {"city", "town", "village"}
STATE_LABELS = {"state", "province", "region"}
POSTAL_LABELS = {"zip", "postal", "postcode"}
ADDRESS_LABELS = {"address", "addr"}


def _looks_like_street_line(line: str) -> bool:
    text = line.strip()
    if not text:
        return False
    low = text.lower()
    # Heuristic checks: starts with number, contains a street suffix
    tokens = [t.strip(",. ") for t in low.split()]
    if not tokens:
        return False
    starts_with_number = tokens[0].isdigit()
    has_suffix = any(t in COMMON_STREET_SUFFIXES for t in tokens)
    has_unit = any(t in UNIT_KEYWORDS for t in tokens)
    # Allow cases without initial number if there is a clear suffix and unit
    return (starts_with_number and has_suffix) or (has_suffix and has_unit)


def _has_postal_cues(line: str) -> bool:
    low = line.lower()
    return any(lbl in low for lbl in ("zip", "postal", "postcode"))


def detect_addresses(text: str, requested: List[str]) -> List[Dict[str, Any]]:
    if "address" not in requested:
        return []
    results: List[Dict[str, Any]] = []
    start = 0
    lines = text.splitlines(keepends=True)
    for idx, line in enumerate(lines):
        end = start + len(line)
        stripped = line.strip()
        if not stripped:
            start = end
            continue
        # Direct label signal
        has_label = any(lbl in stripped.lower() for lbl in ADDRESS_LABELS)
        # Street-like line
        street_like = _looks_like_street_line(stripped)
        # Context look-ahead to see if next line contains city/state/zip cues
        context_cue = False
        if idx + 1 < len(lines):
            next_line = lines[idx + 1].strip().lower()
            if any(lbl in next_line for lbl in CITY_LABELS | STATE_LABELS | POSTAL_LABELS):
                context_cue = True
        if has_label or street_like or (street_like and context_cue):
            results.append({
                "type": "address",
                "start": start + line.find(stripped),
                "end": start + line.find(stripped) + len(stripped),
                "text": stripped,
                "score": 0.7 if street_like else 0.6,
                "source": "heuristics"
            })
        start = end
    return results



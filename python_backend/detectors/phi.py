import re
from typing import List, Dict, Any


Entity = Dict[str, Any]


# ICD-10: Letter + 2 digits, optional . and up to 4 alphanumerics (simplified)
ICD10_RE = re.compile(r"\b[A-TV-Z][0-9]{2}(?:\.[A-Z0-9]{1,4})?\b")

# CPT: 5 digits, sometimes with modifiers; restrict to common range
CPT_RE = re.compile(r"\b[0-9]{5}\b")

# MRN/insurer IDs via context + alphanum token (6–12)
MRN_LABEL = re.compile(r"(?i)\b(MRN|Med\.? Rec\.? No\.?|Medical Record Number|Member ID|Policy #|Insurance ID)\b")
ALNUM_6_12 = re.compile(r"\b[A-Z0-9]{6,12}\b")


def detect_phi(text: str, requested: List[str]) -> List[Entity]:
    if "health" not in requested:
        return []
    results: List[Entity] = []

    def add(s: int, e: int, value: str, label: str, score: float):
        results.append({
            "type": "health",
            "start": s,
            "end": e,
            "text": value,
            "score": score,
            "source": label
        })

    for m in ICD10_RE.finditer(text):
        add(m.start(), m.end(), m.group(0), "icd10", 0.85)

    for m in CPT_RE.finditer(text):
        add(m.start(), m.end(), m.group(0), "cpt", 0.8)

    # MRN/Insurer IDs: look for label and next token
    for lbl in MRN_LABEL.finditer(text):
        s = lbl.end()
        right = text[s:s+64]
        m = ALNUM_6_12.search(right)
        if m:
            token = m.group(0)
            start = s + m.start()
            end = s + m.end()
            add(start, end, token, "mrn_or_insurance", 0.9)

    return results



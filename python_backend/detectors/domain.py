import re
from typing import List, Dict, Any


Entity = Dict[str, Any]


# Transportation
VIN_RE = re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
PLATE_LABEL = re.compile(r"(?i)(plate|license plate)")
PLATE_TOKEN = re.compile(r"\b[A-Z0-9\-]{5,8}\b")

# Legal/privileged
CASE_RE = re.compile(r"(?i)(Case\s*(No\.|#)?\s*[:#]?\s*[A-Za-z0-9\-:]+)")
DOCKET_RE = re.compile(r"(?i)(Dkt\.|Docket)\s*[:#]?\s*[A-Za-z0-9\-:]+")
PRIV_RE = re.compile(r"(?i)(Attorney\s*-?\s*Client|Privileged|Confidential)\b.*")
SETTLE_RE = re.compile(r"(?i)(Settlement\s+Agreement|Settlement\s+Terms)")

# Commercial/trade secrets
COMM_LABEL = re.compile(r"(?i)(pricing|price|margin|discount|msrp|cogs|roadmap|confidential|nda|customer list|supplier list)")
CURRENCY_RE = re.compile(r"\$\d[\d,]*(?:\.\d{2})?\b")

# Calendar/communications headers
HDR_RE = re.compile(r"(?m)^(From|To|Subject|Date|Message-ID|Received):\s+.+$")
MEETING_RE = re.compile(r"(?i)(meeting|attendees|agenda)")

# Employment/Education
EMP_EDU_LABEL = re.compile(r"(?i)(Employee ID|EmpID|Student ID|Transcript|GPA|Performance Review)")
ALNUM_5_12 = re.compile(r"\b[A-Z0-9\-]{5,12}\b")

# Special-category (GDPR)
SPECIAL_WORDS = re.compile(r"(?i)(race|ethnicity|religion|religious|political|union|sexual orientation|biometric|genetic)")

# Children's data
CHILDREN_WORDS = re.compile(r"(?i)(minor|under\s*18|child|children|guardian)")


def detect_domain_sensitive(text: str, requested: List[str]) -> List[Entity]:
    # Map all to 'metadata' for policy selection
    if "metadata" not in requested:
        return []
    results: List[Entity] = []

    def add_span(s: int, e: int, label: str, score: float = 0.8):
        results.append({
            "type": "metadata",
            "start": s,
            "end": e,
            "text": text[s:e],
            "score": score,
            "source": label
        })

    # VIN
    for m in VIN_RE.finditer(text):
        add_span(m.start(), m.end(), "vin", 0.9)

    # License plates (label + token nearby)
    for lbl in PLATE_LABEL.finditer(text):
        s = lbl.end()
        right = text[s:s+32]
        tok = PLATE_TOKEN.search(right)
        if tok:
            add_span(s + tok.start(), s + tok.end(), "license_plate", 0.85)

    # Legal/privileged
    for m in CASE_RE.finditer(text):
        add_span(m.start(), m.end(), "legal_case", 0.85)
    for m in DOCKET_RE.finditer(text):
        add_span(m.start(), m.end(), "docket", 0.85)
    for m in PRIV_RE.finditer(text):
        add_span(m.start(), m.end(), "privileged", 0.9)
    for m in SETTLE_RE.finditer(text):
        add_span(m.start(), m.end(), "settlement", 0.8)

    # Commercial via label or dictionary
    for m in COMM_LABEL.finditer(text):
        s, e = m.span()
        left = max(0, s - 32)
        right = min(len(text), e + 32)
        score = 0.8 + (0.1 if CURRENCY_RE.search(text[left:right]) else 0)
        add_span(s, e, "commercial", min(score, 0.9))

    # Calendar/communications
    for m in HDR_RE.finditer(text):
        add_span(m.start(), m.end(), "email_header", 0.9)
    for m in MEETING_RE.finditer(text):
        add_span(m.start(), m.end(), "meeting", 0.8)

    # Employment/Education
    for lbl in EMP_EDU_LABEL.finditer(text):
        s = lbl.end()
        right = text[s:s+48]
        tok = ALNUM_5_12.search(right)
        if tok:
            add_span(s + tok.start(), s + tok.end(), "employment_education", 0.85)

    # Special-category and children (dictionary-backed)
    try:
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent / 'dictionaries'
        def load_terms(name: str) -> List[str]:
            try:
                with open(base / name, 'r', encoding='utf-8') as f:
                    return [ln.strip().lower() for ln in f if ln.strip()]
            except Exception:
                return []
        gdpr_terms = load_terms('gdpr_special.txt')
        child_terms = load_terms('children.txt')
    except Exception:
        gdpr_terms = []
        child_terms = []

    text_low = text.lower()
    for term in gdpr_terms:
        for m in re.finditer(r"\b" + re.escape(term) + r"\b", text_low):
            add_span(m.start(), m.end(), "special_gdpr", 0.8)
    for term in child_terms:
        for m in re.finditer(r"\b" + re.escape(term) + r"\b", text_low):
            add_span(m.start(), m.end(), "children", 0.85)

    return results



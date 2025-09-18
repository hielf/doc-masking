import re
from typing import List, Dict, Any, Tuple


Entity = Dict[str, Any]


EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?:(?<!\d)(\+?\d[\d\s().-]{7,}\d))")
US_ZIP_RE = re.compile(r"\b\d{5}(?:-\d{4})?\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
AKIA_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
JWT_RE = re.compile(r"eyJ[\w-]+\.[\w-]+\.[\w-]+")
PEM_RE = re.compile(r"-----BEGIN [^-]+-----[\s\S]*?-----END [^-]+-----")
CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")


def detect_entities_rules(text: str, selected: List[str]) -> List[Entity]:
    results: List[Entity] = []
    add = results.append

    def find_all(pattern: re.Pattern, label: str, confidence: float = 0.85):
        for m in pattern.finditer(text):
            add({
                "type": label,
                "start": m.start(),
                "end": m.end(),
                "text": m.group(0),
                "score": confidence,
                "source": "rules"
            })

    if "email" in selected:
        find_all(EMAIL_RE, "email")
    if "phone" in selected:
        find_all(PHONE_RE, "phone", 0.8)
    if "postal_code" in selected:
        find_all(US_ZIP_RE, "postal_code", 0.8)
    if "government_id" in selected:
        find_all(SSN_RE, "government_id", 0.8)
    if "credentials" in selected:
        find_all(JWT_RE, "credentials", 0.9)
        find_all(PEM_RE, "credentials", 0.95)
        find_all(AKIA_RE, "credentials", 0.95)
    if "financial" in selected:
        find_all(CARD_RE, "financial", 0.7)
        find_all(IBAN_RE, "financial", 0.7)

    return results



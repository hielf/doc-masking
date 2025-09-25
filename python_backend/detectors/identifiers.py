import re
from typing import List, Dict, Any


Entity = Dict[str, Any]


IPV4_RE = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
)
IPV6_RE = re.compile(
    r"\b(?:(?:[A-Fa-f0-9]{1,4}:){2,7}[A-Fa-f0-9]{1,4})\b"
)
MAC_RE = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}\b")

COOKIE_RE = re.compile(
    r"(?i)\b(sessionid|jsessionid|csrftoken|auth_token|sid)=([A-Za-z0-9\-_.]{8,})"
)

HOST_CTXT = re.compile(r"(?i)(host|hostname|domain)")
HOSTNAME_RE = re.compile(r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[A-Za-z]{2,}\b")

IMEI_MEID_CTXT = re.compile(r"(?i)(imei|meid)")
FIFTEEN_DIGITS_RE = re.compile(r"\b\d{15}\b")
MEID_HEX_RE = re.compile(r"\b[0-9A-Fa-f]{14}\b")

# GPS coordinates: lat,lon decimal degrees with optional spaces and N/S/E/W
GPS_RE = re.compile(
    r"\b([+-]?([1-8]?\d(?:\.\d+)?|90(?:\.0+)?))\s*,\s*([+-]?(?:1[0-7]\d(?:\.\d+)?|\d?\d(?:\.\d+)?|180(?:\.0+)?))\b"
)
GPS_LABEL = re.compile(r"(?i)(gps|coord|latitude|longitude|lat|lon)")

# Geohash: base32 (excluding a,i,l,o) length 5–9 for precision
GEOHASH_RE = re.compile(r"\b[0123456789bcdefghjkmnpqrstuvwxyz]{5,9}\b")
GEOHASH_LABEL = re.compile(r"(?i)(geohash)")

# Itinerary cues: date + location keyword in proximity
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})\b")
TRAVEL_LABEL = re.compile(r"(?i)(flight|itinerary|arrival|departure|gate|terminal|boarding)")


def detect_identifiers(text: str, requested: List[str]) -> List[Entity]:
    # Map device/network/location to 'metadata' entity for policy selection
    if "metadata" not in requested:
        return []
    results: List[Entity] = []

    def add(m, label: str, score: float = 0.85):
        s, e = m.span()
        results.append({
            "type": "metadata",
            "start": s,
            "end": e,
            "text": m.group(0),
            "score": score,
            "source": label
        })

    for m in IPV4_RE.finditer(text):
        add(m, "ipv4", 0.9)
    for m in IPV6_RE.finditer(text):
        add(m, "ipv6", 0.85)
    for m in MAC_RE.finditer(text):
        add(m, "mac", 0.9)
    for m in COOKIE_RE.finditer(text):
        add(m, "cookie", 0.95)

    # Hostnames only when context suggests hostname/domain
    for m in HOSTNAME_RE.finditer(text):
        s, e = m.span()
        left = max(0, s - 32)
        right = min(len(text), e + 32)
        if HOST_CTXT.search(text[left:right]):
            add(m, "hostname", 0.85)

    # IMEI: 15 digits with nearby context
    for m in FIFTEEN_DIGITS_RE.finditer(text):
        s, e = m.span()
        left = max(0, s - 24)
        right = min(len(text), e + 24)
        if IMEI_MEID_CTXT.search(text[left:right]):
            add(m, "imei", 0.9)

    # MEID: 14 hex with context
    for m in MEID_HEX_RE.finditer(text):
        s, e = m.span()
        left = max(0, s - 24)
        right = min(len(text), e + 24)
        if IMEI_MEID_CTXT.search(text[left:right]):
            add(m, "meid", 0.9)

    # GPS coordinates, boost if label nearby
    for m in GPS_RE.finditer(text):
        s, e = m.span()
        left = max(0, s - 32)
        right = min(len(text), e + 32)
        score = 0.85 + (0.1 if GPS_LABEL.search(text[left:right]) else 0)
        add(m, "gps", min(score, 0.95))

    # Geohash with label
    for m in GEOHASH_RE.finditer(text):
        s, e = m.span()
        left = max(0, s - 16)
        right = min(len(text), e + 16)
        if GEOHASH_LABEL.search(text[left:right]):
            add(m, "geohash", 0.9)

    # Itinerary heuristic: date near travel terms
    for m in DATE_RE.finditer(text):
        s, e = m.span()
        left = max(0, s - 40)
        right = min(len(text), e + 40)
        if TRAVEL_LABEL.search(text[left:right]):
            add(m, "itinerary", 0.8)

    return results



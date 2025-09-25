import re
from typing import List, Dict, Any


Entity = Dict[str, Any]


PATTERNS = [
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b"), "credentials"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "credentials"),
    (re.compile(r"\bxox[abops]-[A-Za-z0-9-]{10,}\b"), "credentials"),
    (re.compile(r"\bsk_(live|test)_[A-Za-z0-9]{20,}\b"), "credentials"),
    (re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"), "credentials"),
    (re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"), "credentials"),  # OpenAI
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "credentials"),  # AWS Access Key ID
    (re.compile(r"\bASIA[0-9A-Z]{16}\b"), "credentials"),
    (re.compile(r"\bSK[0-9a-f]{32}\b"), "credentials"),  # Twilio SID
    (re.compile(r"(?i)Authorization:\s*Bearer\s+([A-Za-z0-9\-_.~+/=]{20,})"), "credentials"),
    # Crypto wallets
    (re.compile(r"\b5[HJK][1-9A-HJ-NP-Za-km-z]{49}\b"), "credentials"),  # BTC WIF (legacy)
    (re.compile(r"\b[KL][1-9A-HJ-NP-Za-km-z]{51}\b"), "credentials"),     # BTC WIF compressed
    (re.compile(r"\b0x?[0-9a-fA-F]{64}\b"), "credentials"),              # ETH private key
]


def detect_secrets(text: str, requested: List[str]) -> List[Entity]:
    if "credentials" not in requested:
        return []
    results: List[Entity] = []
    for pattern, label in PATTERNS:
        for m in pattern.finditer(text):
            start, end = m.span()
            results.append({
                "type": label,
                "start": start,
                "end": end,
                "text": m.group(0),
                "score": 0.95,
                "source": "secrets"
            })
    # Entropy-based generic detector (base64/base64url-ish or opaque tokens)
    # Only for long strings and boosted by context keywords nearby
    ctx_keywords = re.compile(r"(?i)(key|token|secret|password|bearer|auth|api[_-]?key|mnemonic|seed|recovery)")
    for m in re.finditer(r"[A-Za-z0-9_\-]{24,}", text):
        s, e = m.span()
        token = m.group(0)
        # Skip already matched vendor patterns (rough overlap check)
        if any((s < r["end"] and e > r["start"]) for r in results):
            continue
        # entropy estimate
        import math
        def shannon_entropy(sv: str) -> float:
            if not sv:
                return 0.0
            freq = {}
            for ch in sv:
                freq[ch] = freq.get(ch, 0) + 1
            l = len(sv)
            return -sum((c/l) * math.log2(c/l) for c in freq.values())
        ent = shannon_entropy(token)
        # context window around token
        left = max(0, s - 64)
        right = min(len(text), e + 64)
        has_context = bool(ctx_keywords.search(text[left:right]))
        if ent >= 3.5 and has_context:
            results.append({
                "type": "credentials",
                "start": s,
                "end": e,
                "text": token,
                "score": 0.9,
                "source": "secrets_entropy"
            })
    # BIP-39 mnemonic heuristic: presence of >=12 dictionary-like lowercase words
    # We avoid bundling the full 2048-word list; use a light heuristic with context labels
    words = re.findall(r"\b[a-z]{3,}\b", text)
    if len(words) >= 12 and ctx_keywords.search(text):
        # find the first 12-word window and report its span
        idx = 0
        count = 0
        start_pos = None
        for m in re.finditer(r"\b[a-z]{3,}\b", text):
            if start_pos is None:
                start_pos = m.start()
            count += 1
            if count == 12:
                end_pos = m.end()
                results.append({
                    "type": "credentials",
                    "start": start_pos,
                    "end": end_pos,
                    "text": text[start_pos:end_pos],
                    "score": 0.8,
                    "source": "secrets_mnemonic"
                })
                break
    return results



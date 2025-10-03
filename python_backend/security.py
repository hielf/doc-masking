from __future__ import annotations

import hashlib
from typing import Optional


def derive_document_key(input_filepath: str, content_bytes: Optional[bytes] = None) -> bytes:
    """
    Derive a document-scoped key using SHA-256 over file path and content length/bytes.

    Returns 32-byte digest; callers may truncate if needed. Pure ASCII-safe logic.
    """
    h = hashlib.sha256()
    h.update(input_filepath.encode("utf-8", errors="ignore"))
    if content_bytes is not None:
        h.update(b"|")
        h.update(content_bytes)
    return h.digest()



from __future__ import annotations

import hmac
import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional, Any
import re


def _to_bytes(value: Optional[str | bytes]) -> bytes:
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    return value.encode("utf-8")


def _token_shape(value: str) -> str:
    mapping = []
    for ch in value:
        if ch.isdigit():
            mapping.append("9")
        elif ch.isalpha():
            mapping.append("A" if ch.isupper() else "a")
        elif ch.isspace():
            mapping.append(" ")
        else:
            mapping.append(ch)
    return "".join(mapping)


_HASH_PLACEHOLDER_RE = re.compile(r"\{hash(\d+)\}")
_DATE_PLACEHOLDER_RE = re.compile(r"\{date:([^}]+)\}")
_ORIG_LAST_RE = re.compile(r"\{orig_last:(\d+)\}")


@dataclass
class PseudonymizerConfig:
    env_key: bytes
    doc_key: bytes = b""
    algo: str = "sha256"


class Pseudonymizer:
    """
    HMAC-based pseudonymizer with environment- and document-scoped keys.

    Deterministic given the same keys and inputs; unlinkable across different keys.
    Supports template expansion tokens: {hashN}, {index}, {date:%Y%m%d}, {shape}.
    Also supports {orig_last:N} to retain trailing characters from the source token.
    """

    def __init__(self, env_key: str | bytes, doc_key: Optional[str | bytes] = None, algo: str = "sha256") -> None:
        self._config = PseudonymizerConfig(env_key=_to_bytes(env_key), doc_key=_to_bytes(doc_key), algo=algo)
        self._counters: Dict[str, int] = {}

    @staticmethod
    def from_environment(algo: str = "sha256") -> "Pseudonymizer":
        env_k = os.getenv("DOC_MASKING_ENV_KEY", "").encode("utf-8")
        doc_k = os.getenv("DOC_MASKING_DOC_KEY", "").encode("utf-8")
        return Pseudonymizer(env_k, doc_k, algo=algo)

    def set_document_key(self, doc_key: str | bytes) -> None:
        self._config.doc_key = _to_bytes(doc_key)
        self._counters.clear()

    def _scoped_key(self) -> bytes:
        # Derive a scoped key: HMAC(env_key, doc_key) if doc_key present; else env_key
        if self._config.doc_key:
            return hmac.new(self._config.env_key, self._config.doc_key, getattr(hashlib, self._config.algo)).digest()
        return self._config.env_key

    def _digest_hex(self, message: str) -> str:
        scoped = self._scoped_key()
        return hmac.new(scoped, message.encode("utf-8"), getattr(hashlib, self._config.algo)).hexdigest()

    def next_index(self, entity_type: str) -> int:
        current = self._counters.get(entity_type, 0) + 1
        self._counters[entity_type] = current
        return current

    def pseudonymize(
        self,
        original_value: str,
        *,
        entity_type: str = "entity",
        template: str = "{hash8}",
        index: Optional[int] = None,
        date: Optional[datetime] = None,
        keep_parts: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render a pseudonym string according to the template and options.

        - entity_type is included in the HMAC message to reduce cross-entity collisions
        - index defaults to per-entity-type counter if not provided
        - date defaults to current UTC time if not provided
        - keep_parts supports {"last": N} to preserve last N characters via {orig_last:N}
        """
        normalized = original_value.strip()
        if index is None:
            index = self.next_index(entity_type)
        if date is None:
            date = datetime.now(timezone.utc)

        # Compute digest once per token+entity
        digest = self._digest_hex(f"{entity_type}\u241F{normalized}")  # use unit separator-like char to reduce ambiguity

        def _expand_hash(match: re.Match[str]) -> str:
            n = int(match.group(1))
            return digest[:n]

        def _expand_date(match: re.Match[str]) -> str:
            fmt = match.group(1)
            return date.strftime(fmt)

        def _expand_orig_last(match: re.Match[str]) -> str:
            n = int(match.group(1))
            return normalized[-n:] if n > 0 else ""

        result = template
        # Primitive replacement for simple placeholders
        result = result.replace("{index}", str(index))
        if "{shape}" in result:
            result = result.replace("{shape}", _token_shape(normalized))
        result = _HASH_PLACEHOLDER_RE.sub(_expand_hash, result)
        result = _DATE_PLACEHOLDER_RE.sub(_expand_date, result)
        result = _ORIG_LAST_RE.sub(_expand_orig_last, result)

        # If keep_parts is provided and template didn't use {orig_last:N}, append kept part at end
        if keep_parts and isinstance(keep_parts.get("last", None), int):
            n = int(keep_parts["last"])  # type: ignore[index]
            if n > 0 and "{orig_last:" not in template:
                result = f"{result}{normalized[-n:]}"

        return result



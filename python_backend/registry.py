from __future__ import annotations

from typing import Callable, Dict, List, Any


DetectorFn = Callable[[str, List[str]], List[Dict[str, Any]]]


class DetectorRegistry:
    def __init__(self) -> None:
        self._detectors: Dict[str, DetectorFn] = {}

    def register(self, name: str, fn: DetectorFn) -> None:
        self._detectors[name] = fn

    def list(self) -> List[str]:
        return sorted(self._detectors.keys())

    def run_selected(self, text: str, selected: List[str]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for name, fn in self._detectors.items():
            try:
                results.extend(fn(text, selected))
            except Exception:
                continue
        return results


def build_default_registry() -> DetectorRegistry:
    from python_backend.detectors.rules import detect_entities_rules
    from python_backend.detectors.ner import detect_entities_ner
    from python_backend.detectors.address import detect_addresses
    from python_backend.detectors.secrets import detect_secrets
    from python_backend.detectors.identifiers import detect_identifiers
    from python_backend.detectors.phi import detect_phi
    from python_backend.detectors.domain import detect_domain_sensitive

    reg = DetectorRegistry()
    reg.register("rules", detect_entities_rules)
    reg.register("ner", _safe_wrap(detect_entities_ner))
    reg.register("address", _safe_wrap(detect_addresses))
    reg.register("secrets", _safe_wrap(detect_secrets))
    reg.register("identifiers", _safe_wrap(detect_identifiers))
    reg.register("phi", _safe_wrap(detect_phi))
    reg.register("domain", _safe_wrap(detect_domain_sensitive))
    return reg


def _safe_wrap(fn: DetectorFn) -> DetectorFn:
    def wrapper(text: str, selected: List[str]) -> List[Dict[str, Any]]:
        try:
            return fn(text, selected)
        except Exception:
            return []
    return wrapper



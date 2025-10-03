from __future__ import annotations

from typing import Any, Dict, Optional, Callable


ALLOWED_ACTIONS = {"remove", "pseudonymize", "format", "placeholder"}


def validate_and_normalize_policy(policy: Any) -> Dict[str, Any]:
    if not isinstance(policy, dict):
        return {"mask_all": False, "entities": [], "actions": {}, "thresholds": {}}
    out: Dict[str, Any] = {}
    out["mask_all"] = bool(policy.get("mask_all", False))
    entities = policy.get("entities", [])
    if not isinstance(entities, list):
        entities = []
    out["entities"] = [str(e) for e in entities]
    thresholds = policy.get("thresholds", {}) or {}
    out["thresholds"] = {str(k): float(v) for k, v in thresholds.items() if _is_number(v)}
    actions = policy.get("actions", {}) or {}
    if not isinstance(actions, dict):
        actions = {}
    normalized_actions: Dict[str, Dict[str, Any]] = {}
    for et, cfg in actions.items():
        if not isinstance(cfg, dict):
            continue
        action = str(cfg.get("action", "remove")).lower()
        if action not in ALLOWED_ACTIONS:
            action = "remove"
        entry: Dict[str, Any] = {"action": action}
        if action in {"pseudonymize", "placeholder", "format"}:
            tmpl = cfg.get("template")
            if isinstance(tmpl, str):
                entry["template"] = tmpl
        kp = cfg.get("keep_parts", None)
        if isinstance(kp, dict):
            last = kp.get("last")
            if isinstance(last, int) and last >= 0:
                entry["keep_parts"] = {"last": int(last)}
        normalized_actions[str(et)] = entry
    out["actions"] = normalized_actions
    # Template validation: forbid obvious original-echoing templates
    for et, cfg in list(out["actions"].items()):
        tmpl = cfg.get("template")
        if isinstance(tmpl, str) and ("{orig}" in tmpl or "{text}" in tmpl):
            # Remove unsafe template
            del out["actions"][et]["template"]
    # Optional global preserve_length hint for text; default False when using actions
    if "preserve_length" in policy:
        out["preserve_length"] = bool(policy.get("preserve_length"))
    return out


def _is_number(v: Any) -> bool:
    try:
        float(v)
        return True
    except Exception:
        return False


def build_text_pseudonymize_fn(policy: Dict[str, Any], pseudonymizer: Any) -> Callable[[Dict[str, Any], str], str]:
    actions: Dict[str, Dict[str, Any]] = policy.get("actions", {})

    def _map_default_template(entity_type: str) -> str:
        if entity_type == "person_name":
            return "NAME_{hash8}"
        if entity_type == "address":
            return "ADDRESS_{hash6}"
        if entity_type == "email":
            return "EMAIL_{hash6}@mask.local"
        if entity_type == "phone":
            return "PHONE_{hash6}_{orig_last:4}"
        if entity_type == "postal_code":
            return "ZIP_{hash4}"
        return f"{entity_type.upper()}_{{hash6}}"

    def _fn(entity: Dict[str, Any], original: str) -> str:
        et = str(entity.get("type", "entity"))
        cfg = actions.get(et, {})
        action = cfg.get("action", None)
        if action == "remove":
            return ""
        if action == "placeholder":
            tmpl = cfg.get("template") or f"[{et}]"
            return tmpl
        if action == "pseudonymize":
            tmpl = cfg.get("template") or _map_default_template(et)
            return pseudonymizer.pseudonymize(original, entity_type=et, template=tmpl, keep_parts=cfg.get("keep_parts"))
        if action == "format":
            # Basic format-preserving approach: keep last N if provided, otherwise use shape
            kp = cfg.get("keep_parts")
            if isinstance(kp, dict) and isinstance(kp.get("last"), int):
                n = int(kp["last"])  # type: ignore[index]
                return f"{pseudonymizer.pseudonymize(original, entity_type=et, template='{shape}', keep_parts={'last': n})}"
            return pseudonymizer.pseudonymize(original, entity_type=et, template="{shape}")
        # Default fallback: default template
        return pseudonymizer.pseudonymize(original, entity_type=et, template=_map_default_template(et))

    return _fn


def resolve_pdf_mask_text(policy: Dict[str, Any], pseudonymizer: Optional[Any], entity_type: str, original_text: str) -> Optional[str]:
    actions: Dict[str, Dict[str, Any]] = policy.get("actions", {})
    cfg = actions.get(entity_type, {})
    action = cfg.get("action", None)
    if action == "remove":
        return None
    if action == "placeholder":
        return cfg.get("template") or f"[{entity_type}]"
    if action == "pseudonymize":
        tmpl = cfg.get("template")
        if not tmpl:
            # Defaults
            if entity_type == "email":
                tmpl = "EMAIL_{hash6}@mask.local"
            elif entity_type == "phone":
                tmpl = "PHONE_{hash6}_{orig_last:4}"
            elif entity_type == "postal_code":
                tmpl = "ZIP_{hash4}"
            else:
                tmpl = f"{entity_type.upper()}_{{hash6}}"
        if pseudonymizer is None:
            return None
        return pseudonymizer.pseudonymize(original_text, entity_type=entity_type, template=tmpl, keep_parts=cfg.get("keep_parts"))
    if action == "format":
        # Default to shape mapping
        if pseudonymizer is None:
            return None
        kp = cfg.get("keep_parts")
        if isinstance(kp, dict) and isinstance(kp.get("last"), int):
            n = int(kp["last"])  # type: ignore[index]
            return pseudonymizer.pseudonymize(original_text, entity_type=entity_type, template="{shape}", keep_parts={"last": n})
        return pseudonymizer.pseudonymize(original_text, entity_type=entity_type, template="{shape}")
    # No explicit action: if pseudonymizer provided and defaults desired, caller may decide; else return None (pure redaction)
    return None



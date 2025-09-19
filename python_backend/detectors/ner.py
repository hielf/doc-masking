from typing import List, Dict, Any, Optional


_NLP = None


def _load_spacy() -> Optional[object]:
    global _NLP
    if _NLP is not None:
        return _NLP
    try:
        import spacy  # type: ignore
    except Exception:
        return None
    # Try transformer, then large, then small
    for model in ("en_core_web_trf", "en_core_web_lg", "en_core_web_sm"):
        try:
            _NLP = spacy.load(model)  # type: ignore
            return _NLP
        except Exception:
            continue
    # Fallback: blank English with no NER
    return None


def detect_entities_ner(text: str, requested: List[str]) -> List[Dict[str, Any]]:
    """Detect entities using spaCy NER if available.

    Maps spaCy labels to our policy types where possible.
    Currently supports mapping PERSON -> person_name.
    """
    nlp = _load_spacy()
    if nlp is None:
        return []
    doc = nlp(text)
    results: List[Dict[str, Any]] = []
    want_person = "person_name" in requested

    if want_person:
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                results.append({
                    "type": "person_name",
                    "start": int(ent.start_char),
                    "end": int(ent.end_char),
                    "text": ent.text,
                    "score": float(getattr(ent, "_.confidence", 0.85) if hasattr(ent, "_.confidence") else 0.85),
                    "source": "ner"
                })
    return results



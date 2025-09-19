import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def test_ner_detector_optional():
    try:
        from python_backend.detectors.ner import detect_entities_ner  # type: ignore
    except Exception:
        return
    text = "Name: John Doe meets Alice Johnson."
    ents = detect_entities_ner(text, ["person_name"]) or []
    # Optional: if spacy not installed, ents == [] is acceptable
    assert isinstance(ents, list)


def test_libpostal_detector_optional():
    try:
        from python_backend.detectors.address import detect_addresses  # type: ignore
    except Exception:
        return
    text = "123 Market St, San Francisco, CA 94103\nRandom line"
    ents = detect_addresses(text, ["address"]) or []
    # If libpostal missing, ents == [] is acceptable
    assert isinstance(ents, list)



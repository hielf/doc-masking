import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from python_backend.redaction import mask_text_spans  # type: ignore


def test_mask_text_spans_preserve_length():
    text = "Email alice@example.com and phone 415-555-1234"
    ents = [
        {"type": "email", "start": 6, "end": 23},  # alice@example.com
        {"type": "phone", "start": 34, "end": 46},  # 415-555-1234
    ]
    out = mask_text_spans(text, ents)
    assert out[:6] == "Email "
    assert out[6:23] == "x" * (23 - 6)
    assert out[23:34] == " and phone "
    assert out[34:46] == "x" * (46 - 34)


def test_mask_text_spans_placeholder():
    text = "Name: Alice"
    ents = [{"type": "person_name", "start": 6, "end": 11}]
    out = mask_text_spans(text, ents, preserve_length=False)
    assert out.startswith("Name: ") and "[person_name]" in out



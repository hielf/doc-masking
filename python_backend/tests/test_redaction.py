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


def test_mask_text_spans_with_pseudonymize_hook():
    from python_backend.redaction import mask_text_spans

    text = "Email: alice@example.com"
    entities = [{"start": 7, "end": 24, "type": "email"}]

    def pseudo(e, original):
        return "EMAIL_abcdef"  # deterministic stub

    out = mask_text_spans(text, entities, preserve_length=False, pseudonymize_fn=pseudo)
    assert out.endswith("EMAIL_abcdef")


def test_mask_text_spans_with_pseudonymize_hook_exception_fallback_preserve_length():
    text = "Email: alice@example.com"
    entities = [{"start": 7, "end": 24, "type": "email"}]

    def pseudo_raises(e, original):  # noqa: ARG001
        raise RuntimeError("boom")

    out = mask_text_spans(text, entities, preserve_length=True, pseudonymize_fn=pseudo_raises)
    # Fallback should be length-preserving mask of entity span
    masked_segment = out[7:24]
    assert masked_segment == "x" * (24 - 7)


def test_mask_pdf_spans_invokes_redact_annot_with_and_without_text():
    class DummyPage:
        def __init__(self):
            self.calls = []

        def add_redact_annot(self, rect, text=None, fill=None, text_color=None):  # noqa: D401, ARG002
            # Simulate TypeError only when text is not None to exercise fallback path
            self.calls.append((rect, text))
            if text is not None:
                raise TypeError("no text variant")

        def apply_redactions(self):  # noqa: D401
            pass

    from python_backend.redaction import mask_pdf_spans

    page = DummyPage()
    items = [
        {"rect": (0, 0, 10, 10), "masked_text": "MASKED"},
        {"rect": (10, 10, 20, 20)},
    ]
    mask_pdf_spans(page, items)
    # 1) attempt with text (fails)  2) fallback without text  3) second annot without text
    assert len(page.calls) == 3



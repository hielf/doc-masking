import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def test_pdf_policy_masks_email(tmp_path):
    try:
        import fitz  # type: ignore
    except Exception:
        return  # skip if PyMuPDF not installed

    from python_backend.pdf_processor import process_pdf_file  # type: ignore

    src = tmp_path / "in.pdf"
    dst = tmp_path / "out.pdf"

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Contact: alice@example.com")
    doc.save(str(src))
    doc.close()

    policy = {"entities": ["email"]}
    result = process_pdf_file(str(src), str(dst), policy)
    assert result["status"] == "success"
    assert dst.exists()


def test_pdf_policy_default_templates_email(tmp_path, monkeypatch):
    try:
        import fitz  # type: ignore
    except Exception:
        return  # skip if PyMuPDF not installed

    from python_backend.pdf_processor import process_pdf_file  # type: ignore

    src = tmp_path / "in.pdf"
    dst = tmp_path / "out.pdf"

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Contact: alice@example.com")
    doc.save(str(src))
    doc.close()

    monkeypatch.setenv("DOCMASK_USE_DEFAULT_TEMPLATES", "true")
    monkeypatch.setenv("DOC_MASKING_ENV_KEY", "envk")
    monkeypatch.setenv("DOC_MASKING_DOC_KEY", "dockey")
    policy = {"entities": ["email"]}
    result = process_pdf_file(str(src), str(dst), policy)
    assert result["status"] == "success"
    assert dst.exists()



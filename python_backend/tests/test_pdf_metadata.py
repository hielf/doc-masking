from pathlib import Path


def test_pdf_metadata_cleared(tmp_path):
    try:
        import fitz  # type: ignore
    except Exception:
        return

    src = tmp_path / "in.pdf"
    out = tmp_path / "out.pdf"

    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "hello")
    doc.set_metadata({"author": "Alice", "title": "Secret"})
    doc.save(str(src))
    doc.close()

    # Call processor directly
    from python_backend.pdf_processor import process_pdf_file
    res = process_pdf_file(str(src), str(out))
    assert res["status"] == "success"

    out_doc = fitz.open(str(out))
    md = out_doc.metadata or {}
    assert md.get("author") in (None, "") and md.get("title") in (None, "")
    out_doc.close()


import json
import subprocess
import sys
from pathlib import Path

def test_cli_success(tmp_path):
    repo = Path(__file__).resolve().parents[2]
    proc = repo / "python_backend" / "processor.py"
    src = tmp_path / "in.txt"
    dst = tmp_path / "out.txt"
    src.write_text("abc", encoding="utf-8")

    cp = subprocess.run([sys.executable, str(proc), str(src), str(dst)], capture_output=True, text=True)

    assert cp.returncode == 0
    data = json.loads(cp.stdout.strip())
    assert data["status"] == "success"
    assert dst.read_text(encoding="utf-8") == "ABC"


def test_cli_pdf_success(tmp_path):
    pytest = None
    try:
        import fitz  # noqa: F401
        pytest = __import__("pytest")
    except Exception:
        # Skip test when PyMuPDF not available
        return

    repo = Path(__file__).resolve().parents[2]
    proc = repo / "python_backend" / "processor.py"
    src = tmp_path / "in.pdf"
    dst = tmp_path / "out.pdf"

    # Create a simple PDF with some text
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "your name: abc")
    doc.save(str(src))
    doc.close()

    cp = subprocess.run([sys.executable, str(proc), str(src), str(dst)], capture_output=True, text=True)
    assert cp.returncode == 0
    data = json.loads(cp.stdout.strip())
    assert data["status"] == "success"
    assert Path(dst).exists()


def test_cli_invalid_args(tmp_path):
    repo = Path(__file__).resolve().parents[2]
    proc = repo / "python_backend" / "processor.py"

    cp = subprocess.run([sys.executable, str(proc)], capture_output=True, text=True)

    assert cp.returncode == 1
    data = json.loads(cp.stdout.strip())
    assert data["status"] == "error"
    assert data["error"] == "InvalidArguments"

import sys
from pathlib import Path

# Ensure repository root is on sys.path so `python_backend` is importable
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from python_backend.processor import process_text_file
from python_backend.pdf_processor import mask_text_value


def test_process_text_file_policy_mask_email(tmp_path, monkeypatch):
    src = tmp_path / "in.txt"
    dst = tmp_path / "out.txt"
    src.write_text("Hello alice@example.com!\n", encoding="utf-8")
    monkeypatch.setenv("DOCMASK_ENTITY_POLICY", "{\"entities\": [\"email\"]}")

    result = process_text_file(str(src), str(dst))

    assert result["status"] == "success"
    out = dst.read_text(encoding="utf-8")
    assert "alice@example.com" not in out


def test_process_text_file_missing_input(tmp_path):
    src = tmp_path / "missing.txt"
    dst = tmp_path / "out.txt"

    result = process_text_file(str(src), str(dst))

    assert result["status"] == "error"
    assert result["error"] == "FileNotFoundError"


def test_mask_text_value_basic():
    assert mask_text_value("your name: abc") == "xxxx xxxx: xxx"
    assert mask_text_value("Email: John.Doe99@example.com") == "xxxxx: xxxx.xxxxx@xxxxxxx.xxx"

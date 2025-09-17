from python_backend.processor import process_text_file

def test_process_text_file_uppercases(tmp_path):
    src = tmp_path / "in.txt"
    dst = tmp_path / "out.txt"
    src.write_text("Hello, World!\n", encoding="utf-8")

    result = process_text_file(str(src), str(dst))

    assert result["status"] == "success"
    assert dst.read_text(encoding="utf-8") == "HELLO, WORLD!\n"


def test_process_text_file_missing_input(tmp_path):
    src = tmp_path / "missing.txt"
    dst = tmp_path / "out.txt"

    result = process_text_file(str(src), str(dst))

    assert result["status"] == "error"
    assert result["error"] == "FileNotFoundError"

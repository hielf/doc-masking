import os
import re


def mask_text_value(value: str) -> str:
    """Replace all ASCII letters and digits with 'x', preserve whitespace and punctuation."""
    return re.sub(r"[A-Za-z0-9]", "x", value)


def process_pdf_file(input_filepath: str, output_filepath: str):
    """
    Process a PDF by replacing all alphanumeric characters with 'x' while preserving
    layout as best as possible. Outputs a new PDF.

    Uses PyMuPDF redactions where possible; falls back to overlaying masked text.
    """
    try:
        if not os.path.exists(input_filepath):
            return {
                "status": "error",
                "message": f"Input file does not exist: {input_filepath}",
                "error": "FileNotFoundError",
            }

        try:
            import fitz  # type: ignore  # PyMuPDF
        except Exception as e:  # ImportError or others
            return {
                "status": "error",
                "message": f"PyMuPDF (pymupdf) is required to process PDFs: {str(e)}",
                "error": "MissingDependency",
            }

        doc = fitz.open(input_filepath)
        total_chars = 0

        for page in doc:
            page_dict = page.get_text("dict")
            for block in page_dict.get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if not text:
                            continue
                        masked = mask_text_value(text)
                        total_chars += len(text)
                        bbox = span.get("bbox", None)
                        if not bbox:
                            continue
                        rect = fitz.Rect(bbox)
                        try:
                            page.add_redact_annot(
                                rect, text=masked, fill=(1, 1, 1), text_color=(0, 0, 0)
                            )
                        except TypeError:
                            page.add_redact_annot(rect, fill=(1, 1, 1))
                            page.apply_redactions()
                            page.insert_textbox(
                                rect,
                                masked,
                                fontname="helv",
                                fontsize=span.get("size", 11),
                                color=(0, 0, 0),
                                align=0,
                                overlay=True,
                            )
            try:
                page.apply_redactions()
            except Exception:
                pass

        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        doc.save(output_filepath)
        doc.close()

        return {
            "status": "success",
            "message": "PDF processed successfully!",
            "output": output_filepath,
            "input_file": input_filepath,
            "characters_processed": total_chars,
        }

    except PermissionError as e:
        return {
            "status": "error",
            "message": f"Permission denied: {str(e)}",
            "error": "PermissionError",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "error": type(e).__name__,
        }



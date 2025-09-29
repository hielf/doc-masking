import os
import re


def mask_text_value(value: str) -> str:
    """Replace all ASCII letters and digits with 'x', preserve whitespace and punctuation."""
    return re.sub(r"[A-Za-z0-9]", "x", value)


def process_pdf_file(input_filepath: str, output_filepath: str, policy=None):
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
        # Strip document metadata (author/title/etc.) and XMP
        try:
            doc.set_metadata({})
        except Exception:
            pass
        total_chars = 0

        from python_backend.detectors.rules import EMAIL_RE, PHONE_RE, US_ZIP_RE  # type: ignore
        from python_backend.redaction import mask_pdf_spans  # type: ignore
        from python_backend.pseudonymizer import Pseudonymizer  # type: ignore

        for page in doc:
            page_dict = page.get_text("dict")
            mask_all = bool(policy.get("mask_all")) if isinstance(policy, dict) else True
            # If mask_all: mask all spans as before
            if mask_all:
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
            else:
                # Entity-based masking: emails, phones, US ZIP as baseline
                selected = set(policy.get("entities", [])) if isinstance(policy, dict) else set()
                email_re = EMAIL_RE if "email" in selected else None
                phone_re = PHONE_RE if "phone" in selected else None
                zip_re = US_ZIP_RE if "postal_code" in selected else None

                use_defaults = os.environ.get("DOCMASK_USE_DEFAULT_TEMPLATES", "false").lower() in {"1", "true", "yes"}
                pseudo = Pseudonymizer.from_environment() if use_defaults else None

                def _map_template(entity_type: str) -> str:
                    if entity_type == "email":
                        return "EMAIL_{hash6}@mask.local"
                    if entity_type == "phone":
                        return "PHONE_{hash6}_{orig_last:4}"
                    if entity_type == "postal_code":
                        return "ZIP_{hash4}"
                    return f"{entity_type.upper()}_{{hash6}}"

                rects_to_mask = []
                for block in page_dict.get("blocks", []):
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            if not text:
                                continue
                            bbox = span.get("bbox", None)
                            if not bbox:
                                continue
                            rect = fitz.Rect(bbox)
                            total_chars += len(text)
                            # Determine if this span contains any selected entity
                            matched_type = None
                            if email_re and email_re.search(text):
                                matched_type = "email"
                            elif phone_re and phone_re.search(text):
                                matched_type = "phone"
                            elif zip_re and zip_re.search(text):
                                matched_type = "postal_code"
                            if matched_type:
                                if pseudo is not None:
                                    tmpl = _map_template(matched_type)
                                    masked = pseudo.pseudonymize(text, entity_type=matched_type, template=tmpl)
                                else:
                                    masked = mask_text_value(text)
                                rects_to_mask.append({"rect": rect, "masked_text": masked})
                if rects_to_mask:
                    mask_pdf_spans(page, rects_to_mask)
            try:
                page.apply_redactions()
            except Exception:
                pass
        # Optional QR/barcode redaction using pyzbar if available
        try:
            import numpy as _np  # type: ignore
            import PIL.Image as _Image  # type: ignore
            from pyzbar.pyzbar import decode as _decode  # type: ignore

            for p in range(len(doc)):
                page = doc[p]
                pix = page.get_pixmap(alpha=False)
                img = _Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                codes = _decode(img)
                for code in codes:
                    # code.rect gives left, top, width, height in pixels
                    left, top, width, height = code.rect.left, code.rect.top, code.rect.width, code.rect.height
                    # Map pixel rect to PDF user space
                    # Compute scale factors from image pixels to page rect
                    page_rect = page.rect
                    scale_x = page_rect.width / pix.width
                    scale_y = page_rect.height / pix.height
                    rect = fitz.Rect(
                        left * scale_x,
                        top * scale_y,
                        (left + width) * scale_x,
                        (top + height) * scale_y,
                    )
                    try:
                        page.add_redact_annot(rect, fill=(0, 0, 0))
                    except Exception:
                        pass
                try:
                    page.apply_redactions()
                except Exception:
                    pass
        except Exception:
            # pyzbar or pillow not installed; skip barcode redaction silently
            pass

        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Ensure no incremental save (flatten metadata removal), garbage collect objects
        doc.save(output_filepath, deflate=True, garbage=4, clean=True)
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



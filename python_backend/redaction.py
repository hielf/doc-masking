from typing import List, Dict, Any


def mask_text_spans(text: str, entities: List[Dict[str, Any]], masking_char: str = 'x', preserve_length: bool = True) -> str:
    if not entities:
        return text
    entities_sorted = sorted(entities, key=lambda e: e["start"])
    pieces = []
    last = 0
    for e in entities_sorted:
        s = int(e["start"])
        e_end = int(e["end"])
        if s < last:
            s = last
        if e_end <= s:
            continue
        pieces.append(text[last:s])
        length = e_end - s
        if preserve_length:
            pieces.append(masking_char * length)
        else:
            pieces.append(f"[{e.get('type','MASK')}]")
        last = e_end
    pieces.append(text[last:])
    return ''.join(pieces)


def mask_pdf_spans(page, spans_with_rects: List[Dict[str, Any]], masking_char: str = 'x') -> None:
    for item in spans_with_rects:
        rect = item["rect"]
        masked_text = item.get("masked_text", None)
        try:
            if masked_text:
                page.add_redact_annot(rect, text=masked_text, fill=(1, 1, 1), text_color=(0, 0, 0))
            else:
                page.add_redact_annot(rect, fill=(1, 1, 1))
        except TypeError:
            page.add_redact_annot(rect, fill=(1, 1, 1))
            try:
                page.apply_redactions()
            except Exception:
                pass


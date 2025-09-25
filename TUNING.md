## Tuning Guide

How to adjust thresholds, reduce false positives, and balance precision/recall.

### Thresholds
- Set per-entity thresholds in policy: lower for high-recall, higher for precision.
- Start: email=0.85, phone=0.80, postal=0.80, gov_id=0.80, credentials=0.90+, financial=0.70, person_name=0.85, address=0.70.

### Context boosting
- Boost detections near labels: Name:, Address:, Email:, Phone:, Zip:, SSN:, Bearer, Key.
- Penalize matches in headers/footers/boilerplate; downweight all-caps section titles.

### Heuristics
- Collapse hyphenation/line breaks before detection.
- Require mixed letters+digits for addresses or presence of street suffix.
- Validate phones via last-4 keep + shape; emails with non-routable domain when masked.

### Policy actions
- High risk: remove (credentials/secrets).
- Medium: pseudonymize (names, addresses, emails).
- Low/format-sensitive: format-preserving (phones, some postals).

### Evaluation
- Build a small gold set; compute precision/recall per entity.
- Iterate thresholds and heuristics; log counts only (no content).

### Performance
- Reuse NLP pipeline; batch pages; prefer text layer over OCR.
- Consider ONNX NER for CPU speed if needed.



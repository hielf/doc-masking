## Roadmap

Short- and mid-term plan to evolve detection quality, redaction fidelity, platform coverage, and UX while keeping the app fully local and performant.

### Detection quality
- NER upgrade toggle: spaCy transformer or ONNX-exported model for higher recall.
- Multilingual NER; auto-language detection or user-selected language.
- Address heuristics: enrich with country postal-code regexes, street suffix dictionaries, city/state/country lexicons.
- Structured IDs: integrate validators (python-stdnum) for VAT, IBAN, national IDs, company reg numbers.
- Context boosting: label-aware scoring (e.g., "Address:", "SSN", "Bearer") with per-entity thresholds.

### PDF redaction enhancements
- Character/word-level bbox masking to redact only matched substrings (not entire spans).
- Layout awareness for forms/tables; evaluate layoutparser for complex docs.
- OCR fallback using Tesseract with preprocessing (deskew, denoise); map word boxes back to spans.

### Policy and actions
- Per-entity actions: mask, hash, remove, placeholder.
- Per-entity thresholds and masking styles (preserve length, fixed token).
- Entity groups/presets (Personal, Financial, Credentials) for quick policy switching.

### Performance and scalability
- Batch/stream processing for large docs; parallelize per page where safe.
- Reuse a single NER pipeline instance; optional warm worker pool.
- ONNX/quantized NER for faster CPU inference and smaller memory footprint.

### Platform support
- macOS/Linux: default rules + NER; keep libpostal optional behind a feature flag.
- Windows: rules + NER by default; evaluate native deps later.
- Mobile (iOS/Android, future): rules + small NER only; avoid heavy native libs.

### User experience (UX)
- Detection preview: highlight entities per page before committing redaction.
- Confidence/threshold sliders; per-entity toggles (current) and presets.
- Dry-run report export (JSON/CSV) of detected entities for audit.

### Security and privacy
- Deterministic masking (e.g., salted hash) option.
- Zero-retention: in-memory only; scrub temp files on crash.
- PII-safe logging; redact sensitive content from logs.

### Testing and quality
- Gold corpus with labeled PII; track precision/recall per entity.
- Synthetic PDF generation for bbox accuracy and regression tests.
- Fuzz tests for regex overmatch/undermatch resilience.

### Packaging and developer experience
- Makefile/scripts to set up venv, download models, and run tests.
- Prebuilt app bundles for macOS/Windows; signing/notarization where applicable.
- Optional model cache management via UI.

### Documentation
- Expand RULES.md with country-specific patterns and examples.
- Tuning guide for thresholds, context boosting, and false-positive handling.
- Platform setup docs (Python 3.12, optional native deps on macOS/Linux).

### Telemetry (local-only, optional)
- Aggregate counters for which detectors fired and timings (no content stored).
- Optional anonymized summary export for tuning (explicit user opt-in).

### Milestones
- M1: Character-level PDF redaction; per-entity thresholds/actions; dry-run reports.
- M2: OCR fallback with word-level mapping and preprocessing pipeline.
- M3: Enhanced address heuristics (country patterns, suffix dictionaries).
- M4: NER toggle (transformer/ONNX), multilingual support.
- M5: UI detection preview; exportable detection reports.
- M6: Platform hardening (Windows packaging), extended validators (stdnum), documentation and tuning guide.

### Risks and mitigations
- Model size/performance trade-offs: provide small (default) and upgraded model paths.
- False positives: thresholds, context boosting, validators; preview before redact.
- Native deps (optional): keep optional, feature-flagged; portable path remains rules + NER.



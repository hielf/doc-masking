## Roadmap

Short- and mid-term plan to evolve detection quality, redaction fidelity, platform coverage, and UX while keeping the app fully local and performant.

### Detection quality
- NER upgrade toggle: spaCy transformer or ONNX-exported model for higher recall.
- Multilingual NER; auto-language detection or user-selected language.
- Address heuristics: enrich with country postal-code regexes, street suffix dictionaries, city/state/country lexicons.
- Structured IDs: integrate validators (python-stdnum) for VAT, IBAN, national IDs, company reg numbers.
- Context boosting: label-aware scoring (e.g., "Address:", "SSN", "Bearer") with per-entity thresholds.
 - Sensitive categories expansion (plan):
   - Credentials/secrets: vendor prefixes (GitHub/Slack/Stripe/OpenAI/AWS/Twilio), OAuth/Bearer, entropy-based unknown tokens.
   - Passwords/keys in configs: .env/JSON/YAML sensitive keys; deny-list trivial values.
   - Crypto wallets: BIP-39 mnemonics (12–24 words, wordlist check), BTC WIF, ETH private keys.
   - Device/network: IP/MAC/IMEI/MEID, serials, hostnames, SSIDs, cookies/session IDs.
  - Contact/location: GPS coordinates, geohashes, precise address+timestamp pairs, travel itineraries.
   - Health (PHI): MRN/insurer IDs; ICD/CPT code lists in context; provider names + condition context.
   - Special-category (GDPR): race/ethnicity, religion, politics, union, orientation, biometric/genetic (context-only).
   - Employment/education: employee/student IDs, reviews, grades.
   - Commercial/trade secrets: code blocks, internal roadmaps, pricing/margins, customer/supplier lists, contracts/NDAs.
   - Legal/privileged: case/docket numbers; attorney–client phrases; settlement terms.
  - Transportation/vehicle: VINs, license plates, toll/transponder IDs.
  - Calendar/communications: meeting invites, attendee lists, chat logs, email headers with routing.
  - Children’s data: minors’ PII indicators (COPPA/FERPA context and policy route).
  - Metadata/media: EXIF GPS/device, document properties, tracked changes/comments; barcodes/QRs.

### PDF redaction enhancements
- Character/word-level bbox masking to redact only matched substrings (not entire spans).
- Layout awareness for forms/tables; evaluate layoutparser for complex docs.
- OCR fallback using Tesseract with preprocessing (deskew, denoise); map word boxes back to spans.
 - Overlay pseudonyms/placeholders with matching font/spacing; ensure true redaction removes original text layer.
 - Support format-preserving overlays (e.g., phone masks) and non-routable domains for masked emails.

### Media and metadata redaction
- Strip image EXIF (GPS, device model) on import/output; remove PDF/Office author/company and tracked changes/comments.
- Detect and redact faces, signatures, and ID card regions in images/PDF scans (classical CV or lightweight CNNs).
- Decode and redact barcodes/QRs (e.g., using zxing/pyzbar) when they encode IDs/URLs/tokens.

### Policy and actions
- Per-entity actions: remove | pseudonymize | format-preserving | placeholder.
- Per-entity thresholds and masking styles (preserve length, fixed token).
- Entity groups/presets (Personal, Financial, Credentials) for quick policy switching.
- Recommended default masking:
  - Names/Addresses: deterministic pseudonyms using HMAC(key, normalized_value) → NAME_{hash8}, ADDRESS_{hash6}
  - Emails: EMAIL_{hash6}@mask.local (pseudonymized, non-routable domain)
  - Phones: format-preserving mask, keep last 4 digits (e.g., +1 (xxx) xxx-1234)
  - Postal codes: country-shaped mask (e.g., 98xxx or A1A xA1); high-risk → ZIP_{hash4}
  - Credentials/Secrets (API keys, JWTs, PEM): remove (true redaction), no placeholders
  - Allow policy templates: {hashN}, {index}, {date:%Y%m%d}, {shape}, keep_parts=head/tail counts

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
- Use Tailwind CSS to re-write the UI for modern, responsive design.
 - Per-entity action selector (remove | pseudonymize | format-preserving | placeholder) and template editor in UI.
 - Preview shows final masked token/pseudonym (not only redaction boxes) for verification.
 - Optional export of per-document mapping (encrypted) for audit/reversibility when enabled.
 - Regulatory presets (GDPR/HIPAA/COPPA) toggle policy groups; warn when children’s data likely present.

### Security and privacy
 - HMAC-based pseudonymization with key scoping (document-level vs environment-level) and rotation plan.
- Zero-retention: in-memory only; scrub temp files on crash.
- PII-safe logging; redact sensitive content from logs.
 - Enforce non-routable domains for masked emails; forbid templates embedding original substrings.
 - Note on format-preserving masking: potential re-identification risk; prefer pseudonymization for high-risk data.
 - Region-aware policy presets and documentation for GDPR/HIPAA/COPPA applicability (non-legal guidance).

### Testing and quality
- Gold corpus with labeled PII; track precision/recall per entity.
- Synthetic PDF generation for bbox accuracy and regression tests.
- Fuzz tests for regex overmatch/undermatch resilience.
 - Determinism tests (same key → same token) and unlinkability tests (different keys → different tokens).
 - Collision checks for truncated hashes; template expansion validation.
 - PDF overlay checks (length, clipping) and format validators for phones/emails after masking.

### Packaging and developer experience
- Makefile/scripts to set up venv, download models, and run tests.
- Prebuilt app bundles for macOS/Windows; signing/notarization where applicable.
- Optional model cache management via UI.
 - Key management: env/secure store integration; default document-scoped key; optional persistent key.
 - Policy file schema supports per-entity actions/templates; CLI flags to override policy at runtime.

### Documentation
- Expand RULES.md with country-specific patterns and examples.
- Tuning guide for thresholds, context boosting, and false-positive handling.
- Platform setup docs (Python 3.12, optional native deps on macOS/Linux).

### Telemetry (local-only, optional)
- Aggregate counters for which detectors fired and timings (no content stored).
- Optional anonymized summary export for tuning (explicit user opt-in).
 - Counters by entity and action type (remove/pseudonym/format/placeholder) for tuning; never log content.

### Milestones
- M1: Detection platform & policy foundation (priority)
  - Expand detectors: credentials/secrets (vendor prefixes + entropy), crypto wallets (BIP‑39/WIF/ETH), device/network IDs, contact/location, PHI, legal/trade secrets, transportation, calendar/communications, children’s data.
  - Media/metadata: EXIF/PDF/Office metadata scrubbing; barcode/QR decode & redact; plan for faces/signatures/ID-region detection.
  - Pseudonymization + template engine integrated; per‑entity actions in policy; determinism/unlinkability tests; dry‑run reports.
  - Modular, easily extensible detector API; unit tests and gold corpus for all categories.
- M2: PDF redaction fidelity & OCR
  - Character/word‑level bbox masking; overlays for pseudonyms/placeholders; format‑preserving masks; non‑routable email handling.
  - OCR fallback with preprocessing and word‑level mapping.
- M3: UX & policy tooling
  - UI action/template editor; detection preview with masked tokens; regulatory presets (GDPR/HIPAA/COPPA); encrypted per‑document mapping export.
- M4: Security & key management
  - Key scoping (document vs environment), rotation; optional reversible mode (encrypted vault) if required.
- M5: Platform hardening & multilingual
  - Multilingual NER, extended validators (stdnum), layout‑aware PDFs; macOS/Windows packaging and performance tuning.

### Risks and mitigations
- Model size/performance trade-offs: provide small (default) and upgraded model paths.
- False positives: thresholds, context boosting, validators; preview before redact.
- Native deps (optional): keep optional, feature-flagged; portable path remains rules + NER.



## Development Plan – Milestone M1

Scope (from ROADMAP): Pseudonymization + template engine; per-entity actions in policy; determinism/unlinkability tests; dry-run reports.

### Finished (with timestamp)
- 2025-09-25: Modular pipeline scaffolding (`detectors/`, `aggregator.py`, `redaction.py`).
- 2025-09-25: Rule-based detectors (email, phone, ZIP, SSN, credentials, financial).
- 2025-09-25: NER + heuristics address detector; integrated into `processor.py`.
- 2025-09-25: UI entity policy flow wired (`index.html` → `main.js` → backend env).
- 2025-09-25: PDF masking honors policy for email/phone/ZIP; text masking via spans.
- 2025-09-25: Tests added/updated (rules, aggregator, redaction, CLI/unit); 17 passing.
- 2025-09-25: Documentation: `RULES.md`, `ROADMAP.md`; `.gitignore` updated.
- 2025-09-25: Python 3.12 dev environment set up via pyenv/venv.
- 2025-09-27: Unicode character policy implemented; all emoji and special characters replaced with ASCII alternatives for cross-platform compatibility; Windows CI encoding issues resolved.
- 2025-09-30: Enforced ASCII-only delimiter in pseudonymizer; full test suite passed (45).
  - 2025-09-30: Policy module added with per-entity actions/templates; validated at startup; applied to text and PDF processing; tests passing (45).
  - 2025-09-30: Text/PDF application enhanced: format-preserving phones; PDF fallback overlays draw pseudonyms with font size; tests passing (45).
 - 2025-09-30: Testing & quality suite expanded: eval metrics, determinism/unlinkability, collision checks, template validation, PDF shape assertions; suite passing (59).
 - 2025-09-30: Security & registry: document-scoped key derivation integrated; safe template validation; detector registry added; suite passing (61).
  - 2025-09-29: Test document generation system implemented with realistic test data covering all entity types; TXT and PDF document generation; output estimation and validation; masked document inspection tools; CI pipeline updated with new dependencies; comprehensive test coverage with 100% success rate.
- 2025-01-27: Reports and preview functionality implemented; dry-run JSON/CSV reports with entity details, actions, and tokens; UI preview with entity counts and type breakdowns; command-line dry-run interface; comprehensive unit tests; documentation updated.

### TODO (M1)
1) Detector expansion (priority)
- [x] Credentials/secrets: vendor prefixes (GitHub/Slack/Stripe/OpenAI/AWS/Twilio), Authorization Bearer, OAuth tokens
- [x] Entropy-based generic token detector with context boosting (key/token/secret labels)
- [x] Crypto wallets: BIP-39 mnemonic wordlist (12-24 words), BTC WIF (base58), ETH private keys (64 hex)
- [x] Device/network: IP (v4/v6), MAC, IMEI/MEID, serials, hostnames, SSIDs, cookies/session IDs
- [x] Contact/location: GPS coords/geohash, precise address+timestamp pairs, travel itineraries
- [x] Health (PHI): MRN/insurer IDs; ICD/CPT presence in medical context; provider names + condition cues
- [x] Special-category (GDPR): race/ethnicity, religion, politics, union, orientation, biometric/genetic (context rules)
- [x] Employment/education: employee/student IDs, reviews, grades/transcripts
- [x] Commercial/trade secrets: code blocks, internal roadmaps, pricing/margins, customer/supplier lists, contracts/NDAs
- [x] Legal/privileged: case/docket numbers, attorney-client phrases, settlement/privileged terms
- [x] Transportation/vehicle: VINs, license plates, toll/transponder IDs
- [x] Calendar/communications: meeting invites, attendee lists, chat logs, email headers/routing
- [x] Children’s data: minors’ PII indicators and COPPA/FERPA policy routing

2) Media & metadata redaction
- [x] Strip EXIF (GPS/device) on image import/output; remove PDF/Office author/company and tracked changes/comments
- [x] Decode and redact barcodes/QR codes (IDs/URLs/tokens) using zxing/pyzbar
- [ ] Draft plan/backlog for faces, signatures, and ID-region detection (later milestone)

3) Pseudonymization engine
- [x] Implement HMAC-based pseudonymizer (document- and environment-scoped keys)
- [x] Add template expansion: `{hashN}`, `{index}`, `{date:%Y%m%d}`, `{shape}`, `keep_parts`
- [x] Wire per-entity default templates:
  - Names -> `NAME_{hash8}`
  - Addresses -> `ADDRESS_{hash6}`
  - Emails -> `EMAIL_{hash6}@mask.local`
  - Phones -> format-preserving; last 4 kept
  - Postal codes -> country-shaped or `ZIP_{hash4}` (policy-controlled)
  - Credentials/Secrets -> remove (true redaction)
  
  Status: Implemented defaults behind env flag `DOCMASK_USE_DEFAULT_TEMPLATES`; text + PDF overlays wired.

4) Policy and actions
- [x] Extend policy schema: `action` per entity (`remove|pseudonymize|format|placeholder`), `template`, `keep_parts`
- [ ] CLI overrides and environment variables for policy options
- [x] Validate policy at startup; fallback to safe defaults

5) Text and PDF application
- [x] Apply pseudonyms/placeholders in text masking (`mask_text_spans`)
- [x] PDF overlays: draw pseudonym/placeholder text with matching font/spacing; keep true redaction
- [x] Format-preserving overlays for phones/emails in PDFs; enforce non-routable masked email domains

6) Reports and preview
- [x] Dry-run JSON/CSV report (entities, pages, spans, actions, tokens)
- [x] UI preview (minimal): show masked token in result summary (phase 1)

7) Testing and quality
- [x] Build gold corpus; precision/recall per entity; counters only (no content logging)
- [x] Determinism tests (same key -> same token) and unlinkability tests (different keys -> different tokens)
- [x] Collision checks for truncated hashes; template validation tests
- [x] PDF overlay assertions (length, clipping) and shape validators for phone/email after masking

8) Security and key management
- [x] Key sourcing: document-level default; optional environment-level key; rotation plan documented
- [x] Forbid templates embedding original substrings; use non-routable domains for masked emails

9) Architecture & extensibility
- [x] Detector registry with category tags and confidence; simple plugin interface for adding detectors
- [x] Central aggregator with context boosting and policy filtering; shared utilities (entropy, validators)
- [ ] Documentation for contributing new detectors and policies

### Acceptance Criteria
- Expanded detector coverage across listed categories with unit tests and measurable precision/recall on a small corpus
- Media/metadata scrubbing implemented; barcode/QR decoding & redaction supported
- Policy supports per-entity actions/templates and is validated at runtime
- Text and PDF outputs reflect chosen actions; credentials are removed, not masked
- Pseudonymization is deterministic (given key) and unlinkable across keys
- Dry-run report available via CLI; determinism/unlinkability tests pass

### Timeline (target)
- Weeks 1-2: Detector expansion & media/metadata scrubbing; gold corpus; initial tests
- Week 3: Pseudonymizer + policy + text/PDF application; reports; determinism tests
- Week 4: PDF overlays refinements; format-preserving masks; preview; polish and QA

### Risks / Mitigations
- PDF overlay fidelity -> test on varied fonts/sizes; fallback to placeholder-only when metrics fail
- Hash collisions when truncating -> choose adequate length (>=8 hex) and guard with tests
- Policy complexity -> defaults + validation with clear errors

### Code Standards
- **Unicode Character Policy**: All code must use ASCII characters only. No Unicode emoji (❌, ✅, →, etc.) or special characters are allowed to ensure cross-platform compatibility, especially for Windows CI/CD environments. Use ASCII alternatives like `[ERROR]`, `[SUCCESS]`, `->` instead.
 - **Unit Test Coverage for New Functions**: Every new function must include unit tests.
 - **Tests for Modified Functions**: Review and update unit tests for any modified functions.
 - **CI Pipeline Currency**: Check the CI pipeline and update to the latest stable versions when necessary.
 - **Build Script Currency**: Check build scripts and update them when necessary.
 - **Completion Tracking**: When an item is finished, check it off and add a dated entry to the "Finished (with timestamp)" section of `DEVELOPMENT_PLAN.md`.
 - **Documentation Updates**: Update README.md after functions are completed or updated to reflect new features and capabilities.
 - **Test Document Generation**: All new test functionality must include realistic test document generation with both TXT and PDF formats for comprehensive testing.
 - **Masked Document Inspection**: Provide easy access to masked document outputs for validation and debugging purposes.



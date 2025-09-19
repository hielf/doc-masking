## Rule-based PII Detectors

This document defines the current rule-based detectors used by the backend. Rules are applied to plain text inputs directly, and to PDFs per text span extracted from the PDF text layer.

Notes
- Matching is case-sensitive where applicable. Most patterns are case-insensitive by nature (digits/symbols).
- Masking preserves original length by default (replaces each matched character with `x`).
- Overlaps are merged; higher-confidence match wins.
- Names and Addresses are NOT covered by rules; those are handled by optional NER/libpostal detectors.

### Entities and Patterns

- email
  - Description: RFC-like email addresses
  - Pattern:
    ```
    \b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b
    ```
  - Scope: text, pdf
  - Caveats: May match unusual but syntactically valid addresses; does not validate domain existence.

- phone
  - Description: International phone numbers, flexible separators
  - Pattern:
    ```
    (?:(?<!\d)(\+?\d[\d\s().-]{7,}\d))
    ```
  - Scope: text, pdf
  - Caveats: Broad; can match long digit sequences. A stricter validator (e.g., phonenumbers) can be added later.

- postal_code
  - Description: US ZIP or ZIP+4
  - Pattern:
    ```
    \b\d{5}(?:-\d{4})?\b
    ```
  - Scope: text, pdf
  - Caveats: US-only. Add per-country patterns as needed.

- government_id
  - Description: US Social Security Number
  - Pattern:
    ```
    \b\d{3}-\d{2}-\d{4}\b
    ```
  - Scope: text
  - Caveats: Format-only; does not validate disallowed ranges.

- credentials
  - Subtypes and Patterns:
    - JWT (JSON Web Token-like)
      ```
      eyJ[\w-]+\.[\w-]+\.[\w-]+
      ```
    - PEM blocks (keys/certs)
      ```
      -----BEGIN [^-]+-----[\s\S]*?-----END [^-]+-----
      ```
    - AWS Access Key ID (AKIA)
      ```
      \bAKIA[0-9A-Z]{16}\b
      ```
  - Scope: text
  - Caveats: JWT regex is shape-based; PEM is greedy across newlines.

- financial
  - Subtypes and Patterns:
    - Credit/debit number (generic length/shape)
      ```
      \b(?:\d[ -]*?){13,19}\b
      ```
      Caveat: Format-only; add Luhn validation to reduce false positives.
    - IBAN (generic)
      ```
      \b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b
      ```
      Caveat: Country-specific checks not included.
  - Scope: text

### Confidence Defaults

- email: 0.85
- phone: 0.80
- postal_code: 0.80
- government_id: 0.80
- credentials: 0.90–0.95 depending on subtype
- financial: 0.70

These scores are used for threshold filtering when a policy defines per-entity thresholds.

### Policy Mapping

Supported policy entity keys that map to the above rules:
- `email`, `phone`, `postal_code`, `government_id`, `credentials`, `financial`

The following entity keys are not rule-based and rely on ML/heuristics:
- `person_name` (NER), `address` (NER + heuristics; libpostal optional, currently disabled)

### PDF Specifics

- Detection is applied per extracted span. If a pattern matches anywhere within a span, the entire span is masked in the current implementation.
- Future enhancement: character-level bbox mapping to mask only the matched substring within a span.



import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from python_backend.detectors.rules import detect_entities_rules, EMAIL_RE, PHONE_RE, US_ZIP_RE, SSN_RE, AKIA_RE, JWT_RE, PEM_RE, CARD_RE, IBAN_RE  # type: ignore


def test_email_detection():
    text = "Contact me at alice.smith+dev@sub.example.co.uk and bob@test.io"
    ents = detect_entities_rules(text, ["email"]) 
    emails = [e["text"] for e in ents if e["type"] == "email"]
    assert "alice.smith+dev@sub.example.co.uk" in emails
    assert "bob@test.io" in emails


def test_phone_detection():
    text = "Call +1 (415) 555-1234 or 020 7946 0958"
    ents = detect_entities_rules(text, ["phone"]) 
    assert any(e for e in ents if e["type"] == "phone")


def test_zip_and_ssn_detection():
    text = "ZIP 94103, SSN 123-45-6789"
    ents = detect_entities_rules(text, ["postal_code", "government_id"]) 
    types = [e["type"] for e in ents]
    assert "postal_code" in types
    assert "government_id" in types


def test_credentials_and_financial_detection():
    text = (
        "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc.def "
        "KEY AKIAABCDEFGHIJKLMNOP "
        "PEM -----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----\n "
        "CARD 4111 1111 1111 1111 IBAN GB33BUKB20201555555555"
    )
    ents = detect_entities_rules(text, ["credentials", "financial"]) 
    tset = set(e["type"] for e in ents)
    assert "credentials" in tset and "financial" in tset



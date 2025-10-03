from python_backend.policy import validate_and_normalize_policy, build_text_pseudonymize_fn, resolve_pdf_mask_text


def test_validate_and_normalize_basic():
    raw = {
        "mask_all": False,
        "entities": ["email", "phone"],
        "thresholds": {"email": 0.8, "phone": 0.7},
        "actions": {
            "email": {"action": "pseudonymize", "template": "EMAIL_{hash8}@mask.local"},
            "phone": {"action": "format", "keep_parts": {"last": 4}},
            "credentials": {"action": "remove"},
        },
    }
    p = validate_and_normalize_policy(raw)
    assert p["entities"] == ["email", "phone"]
    assert p["actions"]["email"]["action"] == "pseudonymize"
    assert p["actions"]["phone"]["action"] == "format"
    assert p["actions"]["credentials"]["action"] == "remove"


def test_template_forbid_original_echo():
    raw = {
        "entities": ["email"],
        "actions": {
            "email": {"action": "pseudonymize", "template": "{orig}"},
        },
    }
    p = validate_and_normalize_policy(raw)
    assert "template" not in p["actions"]["email"]


def test_build_text_pseudonymize_fn_and_resolve_pdf_masks(monkeypatch):
    raw = {
        "entities": ["email", "phone", "credentials"],
        "actions": {
            "email": {"action": "pseudonymize", "template": "EMAIL_{hash6}@mask.local"},
            "phone": {"action": "pseudonymize", "template": "PHONE_{hash6}_{orig_last:4}"},
            "credentials": {"action": "remove"},
        },
    }
    policy = validate_and_normalize_policy(raw)

    from python_backend.pseudonymizer import Pseudonymizer

    pseudo = Pseudonymizer(env_key=b"e", doc_key=b"d")
    fn = build_text_pseudonymize_fn(policy, pseudo)

    # Text
    email_out = fn({"type": "email"}, "alice@example.com")
    phone_out = fn({"type": "phone"}, "415-555-1234")
    cred_out = fn({"type": "credentials"}, "eyJabc.123.456")
    assert email_out.endswith("@mask.local") and len(email_out) > len("@mask.local")
    assert phone_out.endswith("1234")
    assert cred_out == ""

    # PDF resolve
    email_pdf = resolve_pdf_mask_text(policy, pseudo, "email", "alice@example.com")
    phone_pdf = resolve_pdf_mask_text(policy, pseudo, "phone", "415-555-1234")
    cred_pdf = resolve_pdf_mask_text(policy, pseudo, "credentials", "eyJabc.123.456")
    assert email_pdf and email_pdf.endswith("@mask.local")
    assert phone_pdf and phone_pdf.endswith("1234")
    assert cred_pdf is None



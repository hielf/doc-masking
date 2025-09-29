from datetime import datetime, timezone

from python_backend.pseudonymizer import Pseudonymizer


def test_determinism_same_keys_same_output():
    p1 = Pseudonymizer(env_key=b"env", doc_key=b"doc")
    p2 = Pseudonymizer(env_key=b"env", doc_key=b"doc")
    a = p1.pseudonymize("Alice Smith", entity_type="person_name", template="NAME_{hash8}")
    b = p2.pseudonymize("Alice Smith", entity_type="person_name", template="NAME_{hash8}")
    assert a == b


def test_unlinkability_different_keys_different_output():
    p1 = Pseudonymizer(env_key=b"envA", doc_key=b"doc")
    p2 = Pseudonymizer(env_key=b"envB", doc_key=b"doc")
    a = p1.pseudonymize("alice@example.com", entity_type="email", template="EMAIL_{hash8}")
    b = p2.pseudonymize("alice@example.com", entity_type="email", template="EMAIL_{hash8}")
    assert a != b


def test_template_tokens_hash_index_date_shape_keep_last():
    fixed_date = datetime(2025, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    p = Pseudonymizer(env_key=b"k", doc_key=b"d")
    out = p.pseudonymize(
        "(415) 555-1212",
        entity_type="phone",
        template="PHONE_{hash6}_{index}_{date:%Y%m%d}_{shape}_{orig_last:4}",
        index=42,
        date=fixed_date,
    )
    # Shape should retain punctuation and map digits to 9
    assert "PHONE_" in out and "_42_20250102_" in out
    assert out.endswith("_1212")


def test_from_environment_factory_works(monkeypatch):
    monkeypatch.setenv("DOC_MASKING_ENV_KEY", "envkey")
    monkeypatch.setenv("DOC_MASKING_DOC_KEY", "dockey")
    p = Pseudonymizer.from_environment()
    a = p.pseudonymize("bob@example.com", entity_type="email", template="EMAIL_{hash8}")
    assert a.startswith("EMAIL_") and len(a) == len("EMAIL_") + 8


def test_keep_parts_appended_when_not_using_orig_last():
    p = Pseudonymizer(env_key=b"k", doc_key=b"d")
    out = p.pseudonymize("secret-token-XYZ", entity_type="credential", template="TOKEN_{hash6}", keep_parts={"last": 3})
    assert out.endswith("XYZ") and out.startswith("TOKEN_")


def test_keep_parts_ignored_when_using_orig_last():
    p = Pseudonymizer(env_key=b"k", doc_key=b"d")
    out = p.pseudonymize("secret-token-XYZ", entity_type="credential", template="TOKEN_{hash6}_{orig_last:2}", keep_parts={"last": 3})
    assert out.endswith("_YZ") and "XYZ" not in out


def test_index_auto_increments_per_entity_type():
    p = Pseudonymizer(env_key=b"k", doc_key=b"d")
    a = p.pseudonymize("alice", entity_type="person_name", template="N{index}")
    b = p.pseudonymize("bob", entity_type="person_name", template="N{index}")
    c = p.pseudonymize("corp", entity_type="organization", template="O{index}")
    assert a == "N1" and b == "N2" and c == "O1"


def test_set_document_key_changes_digest_and_resets_index():
    p = Pseudonymizer(env_key=b"env", doc_key=b"doc1")
    x1 = p.pseudonymize("alice@example.com", entity_type="email", template="{hash8}_{index}")
    p.set_document_key(b"doc2")
    x2 = p.pseudonymize("alice@example.com", entity_type="email", template="{hash8}_{index}")
    # Digest must change; index restarts at 1
    assert x1 != x2 and x2.endswith("_1")


def test_hash_length_with_sha1_algo():
    p = Pseudonymizer(env_key=b"env", doc_key=b"doc", algo="sha1")
    out = p.pseudonymize("alice@example.com", entity_type="email", template="{hash40}")
    assert len(out) == 40


def test_unicode_shape_mapping():
    p = Pseudonymizer(env_key=b"e", doc_key=b"d")
    token = "Aesshanzi123-abc XYZ"
    out = p.pseudonymize(token, entity_type="misc", template="{shape}")
    # Check length preserved and punctuation retained (dash and spaces)
    assert len(out) == len(token)
    assert "-" in out and out.count(" ") == token.count(" ")



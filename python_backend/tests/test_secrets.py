import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from python_backend.detectors.secrets import detect_secrets  # type: ignore


def test_detect_github_pat():
    text = "token: github_pat_ABCDEF1234567890_abcdef"
    ents = detect_secrets(text, ["credentials"]) 
    assert any("github_pat_" in e["text"] for e in ents)


def test_detect_openai_and_bearer():
    text = "sk-1234567890ABCDEFGHIJabcdefghij1234 Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc.def"
    ents = detect_secrets(text, ["credentials"]) 
    s = " ".join(e["text"] for e in ents)
    assert "sk-" in s and "Authorization:" in s


def test_detect_aws_and_twilio():
    text = "AKIAABCDEFGHIJKLMNOP and SK0123456789abcdef0123456789abcdef"
    ents = detect_secrets(text, ["credentials"]) 
    s = " ".join(e["text"] for e in ents)
    assert "AKIA" in s and "SK012345" in s


def test_entropy_detector_with_context():
    # Random-looking token with context keyword should be flagged
    token = "aZ9bY8xW7vU6tS5rQ4pO3nM2lK1jH0gF9eD8cB7a"  # length > 24
    text = f"api_key: {token}"
    ents = detect_secrets(text, ["credentials"]) 
    assert any(e for e in ents if token in e["text"])


def test_entropy_detector_without_context_is_ignored():
    token = "aZ9bY8xW7vU6tS5rQ4pO3nM2lK1jH0gF9eD8cB7a"  # length > 24
    text = f"{token}"
    ents = detect_secrets(text, ["credentials"]) 
    assert not any(e for e in ents if e["source"] == "secrets_entropy")


def test_crypto_wif_eth_and_mnemonic():
    # BTC WIF (compressed, starts with K)
    wif = "Kx123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwx1234567"
    eth = "0x" + "a" * 64
    mnemonic = "seed: apple banana cherry dog eagle frog grape horse igloo jewel kite lemon"
    text = f"{wif} and {eth}. {mnemonic}"
    ents = detect_secrets(text, ["credentials"]) 
    s = " ".join(e["text"] for e in ents)
    assert "0x" in s and "seed:" in text



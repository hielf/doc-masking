import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from python_backend.detectors.domain import detect_domain_sensitive  # type: ignore


def test_vin_plate_legal_commercial_emailhdr_employment_special_children():
    text = (
        "VIN 1HGCM82633A004352 license plate: ABC-1234 Case No: 2:25-cv-1234 Dkt. 10 "
        "Attorney-Client Privileged Settlement Terms pricing $1,299.00 religion dna "
        "From: alice@example.com\nSubject: Meeting agenda\n "
        "Employee ID EMP-12345 GPA 3.9 race and minor under 18"
    )
    ents = detect_domain_sensitive(text, ["metadata"]) 
    sources = set(e["source"] for e in ents)
    assert {"vin", "license_plate", "legal_case", "docket", "privileged", "settlement"}.issubset(sources)
    assert "commercial" in sources and "email_header" in sources and "employment_education" in sources
    assert "special_gdpr" in sources and "children" in sources


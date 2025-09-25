import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from python_backend.detectors.phi import detect_phi  # type: ignore


def test_icd10_and_cpt_and_mrn():
    text = (
        "Diagnoses: E11.9, Z00 Encounter; CPT codes: 99213, 93000. MRN: ABC12345 Member ID XYZ789012"
    )
    ents = detect_phi(text, ["health"]) 
    sources = set(e["source"] for e in ents)
    assert "icd10" in sources and "cpt" in sources and "mrn_or_insurance" in sources


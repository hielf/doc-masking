import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from python_backend.aggregator import merge_overlaps, filter_by_policy  # type: ignore


def test_merge_overlaps_basic():
    ents = [
        {"type": "email", "start": 5, "end": 10, "score": 0.8},
        {"type": "email", "start": 8, "end": 12, "score": 0.9},
        {"type": "phone", "start": 20, "end": 30, "score": 0.7},
    ]
    merged = merge_overlaps(ents)
    assert len(merged) == 2
    e = merged[0]
    assert e["start"] == 5 and e["end"] == 12 and e["score"] == 0.9


def test_filter_by_policy_thresholds():
    ents = [
        {"type": "email", "start": 0, "end": 5, "score": 0.5},
        {"type": "email", "start": 6, "end": 10, "score": 0.9},
        {"type": "phone", "start": 11, "end": 15, "score": 0.95},
    ]
    policy = {"entities": ["email", "phone"], "thresholds": {"email": 0.7}}
    filtered = filter_by_policy(ents, policy)
    types = [e["type"] for e in filtered]
    assert types.count("email") == 1 and "phone" in types



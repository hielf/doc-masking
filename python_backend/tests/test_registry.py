from python_backend.registry import build_default_registry


def test_registry_runs_all_detectors_safely():
    reg = build_default_registry()
    out = reg.run_selected("Contact alice@example.com", ["email"])  # should at least include rules email
    assert any(e.get("type") == "email" for e in out)



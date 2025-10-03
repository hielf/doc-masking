from python_backend.evaluation import evaluate_entities


def test_evaluate_entities_precision_recall_and_f1():
    true = [
        {"type": "email", "start": 6, "end": 23},
        {"type": "phone", "start": 34, "end": 46},
    ]
    pred = [
        {"type": "email", "start": 6, "end": 23},  # TP
        {"type": "phone", "start": 33, "end": 46},  # TP (overlap)
        {"type": "email", "start": 0, "end": 5},    # FP
    ]
    m = evaluate_entities(true, pred)
    assert m["tp"] == 2.0 and m["fp"] == 1.0 and m["fn"] == 0.0
    assert 0.0 < m["precision"] < 1.0 and 0.0 < m["recall"] <= 1.0 and 0.0 < m["f1"] <= 1.0



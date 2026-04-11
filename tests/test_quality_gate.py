from app.quality.gate import passes_quality_gate


def test_quality_gate_accepts_non_empty_result() -> None:
    assert passes_quality_gate({"status": "ok"}) is True

from app.quality.gate import QualityGate


def test_quality_gate_accepts_analysis_payload() -> None:
    gate = QualityGate()

    result = gate.evaluate(
        workflow="analysis",
        result={
            "reformulation": "Test",
            "ambiguities": ["Ambiguity"],
            "open_questions": ["Question"],
        },
    )

    assert "result_not_empty" in result["quality_checks"]
    assert "analysis_reformulation_present" in result["quality_checks"]
    assert result["warnings"] == []

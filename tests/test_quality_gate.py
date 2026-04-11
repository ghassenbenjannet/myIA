from app.quality.gate import QualityGate
from app.schemas.analysis import AnalysisResult
from app.schemas.documentation import DocumentationResult
from app.schemas.ticket import TicketResult


def test_quality_gate_analysis_checks_expected_fields() -> None:
    gate = QualityGate()

    result = gate.evaluate(
        workflow="analysis",
        result=AnalysisResult(
            reformulation="Reformulation",
            request_summary="Summary",
            context_hint=None,
            detected_type="analysis",
            ambiguities=["Ambiguity"],
            risks=["Risk"],
            open_questions=["Question"],
            recommended_next_step="Next step",
        ),
    )

    assert "result_not_empty" in result["quality_checks"]
    assert "analysis_reformulation_present" in result["quality_checks"]
    assert "analysis_ambiguities_present" in result["quality_checks"]
    assert "analysis_open_questions_present" in result["quality_checks"]


def test_quality_gate_ticket_checks_expected_fields() -> None:
    gate = QualityGate()

    result = gate.evaluate(
        workflow="ticket",
        result=TicketResult(
            ticket_type="bug",
            title="[BUG] Paiement KO",
            description="Paiement KO en production",
            context="Incident critique",
            business_goal="Corriger le bug",
            acceptance_criteria=["Le comportement attendu est defini"],
            dependencies=[],
            open_points=[],
        ),
    )

    assert "ticket_title_present" in result["quality_checks"]
    assert "ticket_description_present" in result["quality_checks"]
    assert "ticket_acceptance_criteria_present" in result["quality_checks"]


def test_quality_gate_documentation_checks_expected_fields() -> None:
    gate = QualityGate()

    result = gate.evaluate(
        workflow="documentation",
        result=DocumentationResult(
            document_type="working_draft",
            title="Documentation support",
            summary="Resume",
            context="Contexte",
            sections=[{"title": "Contexte", "content": "Texte"}],
            detected_type="documentation",
        ),
    )

    assert "documentation_title_present" in result["quality_checks"]
    assert "documentation_sections_present" in result["quality_checks"]


def test_quality_gate_returns_empty_result_warning() -> None:
    gate = QualityGate()

    result = gate.evaluate(workflow="analysis", result={})

    assert result["quality_checks"] == []
    assert result["warnings"] == ["empty_result"]

from app.modules.ticket.service import TicketService
from app.schemas.analysis import AnalysisResult


def test_ticket_service_can_build_ticket_from_analysis() -> None:
    service = TicketService()
    analysis = AnalysisResult(
        reformulation="Le calcul de remise doit etre clarifie pour les commandes web.",
        request_summary="Analyse orientee PO avec impacts metier et techniques identifies.",
        context_hint="Sujet metier a cadrer",
        detected_type="analysis",
        current_behavior="La remise ne se calcule plus correctement sur certaines commandes web.",
        expected_behavior="La remise doit etre calculee correctement sur les commandes web et via l'API.",
        business_impacts=["Le calcul des remises peut etre incorrect."],
        technical_impacts=["Des interfaces API peuvent etre impactees."],
        dependencies=["Verifier les regles de calcul de remise.", "Verifier les API ou services exposes."],
        ambiguities=["Le perimetre exact des cas concernes reste a confirmer."],
        risks=["Risque de regression technique si les composants impactes ne sont pas identifies."],
        open_questions=["Quels cas de commandes sont reellement concernes ?"],
        recommended_next_step="Transformer cette analyse en draft ticket avec description, impacts et criteres d'acceptation.",
        recommended_output="ticket",
    )

    ticket = service.from_analysis(analysis)

    assert ticket.title
    assert ticket.description
    assert ticket.business_goal
    assert ticket.current_behavior == analysis.current_behavior
    assert ticket.expected_behavior == analysis.expected_behavior
    assert ticket.dependencies == analysis.dependencies
    assert ticket.open_points
    assert ticket.acceptance_criteria
    assert ticket.description.startswith("Analyse orientee PO")
    assert ticket.context.startswith("Ticket derive d'une analyse prealable.")


def test_ticket_service_preserves_analysis_uncertainty() -> None:
    service = TicketService()
    analysis = AnalysisResult(
        reformulation="Sujet a cadrer avant execution.",
        request_summary="Analyse orientee PO preliminaire.",
        context_hint=None,
        detected_type="analysis",
        current_behavior=None,
        expected_behavior=None,
        business_impacts=[],
        technical_impacts=[],
        dependencies=[],
        ambiguities=["Le comportement actuel n'est pas suffisamment explicite."],
        risks=["Risque de mauvaise priorisation."],
        open_questions=["Quel est le comportement cible attendu par le metier ?"],
        recommended_next_step="Clarifier les zones d'incertitude avant de produire un livrable.",
        recommended_output="ticket",
    )

    ticket = service.from_analysis(analysis)

    assert "Le comportement actuel n'est pas suffisamment explicite." in ticket.open_points
    assert "Quel est le comportement cible attendu par le metier ?" in ticket.open_points

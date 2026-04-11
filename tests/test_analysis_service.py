from app.modules.analysis.service import AnalysisService


def test_analysis_service_does_not_treat_produits_as_production_signal() -> None:
    service = AnalysisService()

    result = service.run(
        user_input=(
            "Le metier dit que la remise ne se calcule plus pareil pour les produits desactives, "
            "mais on ne sait pas si ca concerne aussi les imports batch."
        ),
        context_hint=None,
        classification={"request_type": "analysis"},
    )

    assert "Risque operationnel plus eleve si le sujet concerne deja la production." not in result.risks
    assert "Le sujet est-il reproducible et quantifie en production ?" not in result.open_questions

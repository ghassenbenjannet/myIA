from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_process_with_ambiguous_text_returns_200() -> None:
    response = client.post(
        "/process",
        json={
            "user_input": "Peux-tu regarder ce sujet metier a clarifier ?",
            "target_output": "auto",
        },
    )

    assert response.status_code == 200


def test_process_with_bug_text_routes_to_ticket() -> None:
    response = client.post(
        "/process",
        json={
            "user_input": "Bug en production sur le paiement, erreur bloquante pour les utilisateurs",
            "context_hint": "Incident critique",
            "target_output": "auto",
        },
    )

    assert response.status_code == 200
    assert response.json()["selected_workflow"] == "ticket"


def test_process_with_documentation_text_routes_to_documentation() -> None:
    response = client.post(
        "/process",
        json={
            "user_input": "Documenter le mode operatoire confluence pour le support",
            "target_output": "auto",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["selected_workflow"] == "documentation"
    assert [section["title"] for section in payload["result"]["sections"]] == [
        "Contexte",
        "Objectif",
        "Points cles",
        "Questions ouvertes",
        "Prochaines etapes",
    ]


def test_process_analysis_response_contains_enriched_analysis_fields() -> None:
    response = client.post(
        "/process",
        json={
            "user_input": (
                "La remise ne se calcule plus pour la commande web. "
                "Le calcul attendu doit s'appliquer aussi au flux API et batch."
            ),
            "context_hint": "Sujet metier a cadrer",
            "target_output": "analysis",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    result = payload["result"]
    assert payload["selected_workflow"] == "analysis"
    assert "current_behavior" in result
    assert "expected_behavior" in result
    assert "business_impacts" in result
    assert "technical_impacts" in result
    assert "dependencies" in result
    assert "recommended_output" in result


def test_process_analysis_can_use_readonly_context() -> None:
    response = client.post(
        "/process",
        json={
            "user_input": "La remise ne se calcule plus sur certaines commandes web.",
            "context_hint": "Sujet metier a analyser",
            "target_output": "analysis",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["selected_workflow"] == "analysis"
    assert payload["context_used"] is not None
    assert payload["context_used"]["source_name"] == "stub_confluence"
    assert payload["context_used"]["snippets"]


def test_process_analysis_without_matching_context_keeps_context_used_null() -> None:
    response = client.post(
        "/process",
        json={
            "user_input": "Besoin flou a analyser sur un sujet organisationnel interne.",
            "target_output": "analysis",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["selected_workflow"] == "analysis"
    assert payload["context_used"] is None


def test_process_ticket_response_contains_enriched_ticket_fields() -> None:
    response = client.post(
        "/process",
        json={
            "user_input": (
                "Bug en production: le paiement ne fonctionne plus pour certains utilisateurs. "
                "Le comportement attendu doit permettre un paiement valide via l'API."
            ),
            "context_hint": "Incident critique sur le parcours de commande",
            "target_output": "auto",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    result = payload["result"]
    assert payload["selected_workflow"] == "ticket"
    assert "title" in result
    assert "description" in result
    assert "context" in result
    assert "business_goal" in result
    assert "business_impacts" in result
    assert "technical_impacts" in result
    assert "dependencies" in result
    assert "open_points" in result
    assert "acceptance_criteria" in result
    assert payload["intermediate_analysis"] is None


def test_process_with_fuzzy_ticket_request_uses_intermediate_analysis() -> None:
    response = client.post(
        "/process",
        json={
            "user_input": "Sujet a clarifier sur la facturation, le comportement attendu est a confirmer.",
            "context_hint": "Besoin de ticket mais informations encore floues",
            "target_output": "ticket",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["selected_workflow"] == "ticket"
    assert payload["intermediate_analysis"] is not None
    assert "title" in payload["result"]
    assert "description" in payload["result"]
    assert "Le perimetre exact ou certaines hypotheses restent a confirmer." in payload["result"]["open_points"]
    assert "Quel est le perimetre exact du sujet et des cas concernes ?" in payload["result"]["open_points"]


def test_process_with_clear_ticket_request_skips_intermediate_analysis() -> None:
    response = client.post(
        "/process",
        json={
            "user_input": "Bug paiement en production, erreur bloquante, le paiement doit etre valide via l'API.",
            "context_hint": "Incident critique",
            "target_output": "ticket",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["selected_workflow"] == "ticket"
    assert payload["intermediate_analysis"] is None


def test_process_analysis_route_keeps_api_contract() -> None:
    response = client.post(
        "/process",
        json={
            "user_input": "Besoin flou a analyser sur la facturation",
            "target_output": "auto",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "request_type" in payload
    assert "selected_workflow" in payload
    assert "confidence" in payload
    assert "result" in payload
    assert "intermediate_analysis" in payload
    assert "context_used" in payload
    assert "quality_checks" in payload
    assert "warnings" in payload

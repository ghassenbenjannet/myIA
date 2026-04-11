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
    assert response.json()["selected_workflow"] == "documentation"


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
    assert "quality_checks" in payload
    assert "warnings" in payload

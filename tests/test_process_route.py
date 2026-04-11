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


def test_process_response_contains_expected_fields() -> None:
    response = client.post(
        "/process",
        json={
            "user_input": "Besoin flou a analyser",
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

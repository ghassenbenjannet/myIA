from fastapi.testclient import TestClient

from app.main import app


def test_process_route_returns_structured_response() -> None:
    client = TestClient(app)

    response = client.post(
        "/process",
        json={
            "user_input": "Bug en production sur l'API de paiement",
            "context_hint": "Incident critique",
            "target_output": "auto",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["request_type"] == "bug"
    assert payload["selected_workflow"] == "ticket"
    assert "result" in payload
    assert "quality_checks" in payload

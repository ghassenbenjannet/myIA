from fastapi.testclient import TestClient

from app.api.routes_process import jira_read_service, source_summary_service
from app.main import app

client = TestClient(app)


class FakeSourceReader:
    def __init__(self, payload=None, should_raise: bool = False) -> None:
        self.payload = payload or {
            "url": "https://example.com/article",
            "title": "Example Source",
            "text": "Premier point utile. Deuxieme point utile. Troisieme point utile.",
        }
        self.should_raise = should_raise

    def read_url(self, url: str) -> dict:
        if self.should_raise:
            raise RuntimeError("source unavailable")
        return self.payload


class FakeJiraReadService:
    def __init__(self, result=None, should_raise: bool = False) -> None:
        self.result = result
        self.should_raise = should_raise

    def read_issue(self, request) -> dict | None:
        if self.should_raise:
            raise RuntimeError("jira unavailable")
        return self.result


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
    assert "run_id" in response.json()


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
    assert payload["context_used"] is None


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
    assert payload["context_used"] is not None
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
    assert payload["context_used"] is None


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
    assert "run_id" in payload
    assert "request_type" in payload
    assert "selected_workflow" in payload
    assert "confidence" in payload
    assert "result" in payload
    assert "intermediate_analysis" in payload
    assert "context_used" in payload
    assert "quality_checks" in payload
    assert "warnings" in payload


def test_process_persists_run_and_allows_readback() -> None:
    process_response = client.post(
        "/process",
        json={
            "user_input": "Sujet a clarifier sur la facturation, le comportement attendu est a confirmer.",
            "context_hint": "Besoin de ticket mais informations encore floues",
            "target_output": "ticket",
        },
    )

    assert process_response.status_code == 200
    process_payload = process_response.json()
    run_id = process_payload["run_id"]

    run_response = client.get(f"/runs/{run_id}")

    assert run_response.status_code == 200
    run_payload = run_response.json()
    assert run_payload["run_id"] == run_id
    assert run_payload["raw_input"] == "Sujet a clarifier sur la facturation, le comportement attendu est a confirmer."
    assert run_payload["final_workflow"] == "ticket"
    assert run_payload["result"] == process_payload["result"]
    assert run_payload["intermediate_analysis"] == process_payload["intermediate_analysis"]


def test_continue_run_from_analysis_to_ticket_creates_child_run() -> None:
    process_response = client.post(
        "/process",
        json={
            "user_input": "La remise ne se calcule plus pour la commande web et le comportement attendu doit etre clarifie.",
            "target_output": "analysis",
        },
    )
    parent_run_id = process_response.json()["run_id"]

    continue_response = client.post(
        f"/runs/{parent_run_id}/continue",
        json={"action": "draft_ticket"},
    )

    assert continue_response.status_code == 200
    child_payload = continue_response.json()
    assert child_payload["run_id"] != parent_run_id
    assert child_payload["selected_workflow"] == "ticket"
    assert "title" in child_payload["result"]

    child_run_response = client.get(f"/runs/{child_payload['run_id']}")
    child_run_payload = child_run_response.json()
    assert child_run_payload["parent_run_id"] == parent_run_id
    assert child_run_payload["continuation_action"] == "draft_ticket"


def test_continue_run_from_analysis_to_documentation_creates_child_run() -> None:
    process_response = client.post(
        "/process",
        json={
            "user_input": "La facturation doit etre clarifiee pour les commandes web.",
            "target_output": "analysis",
        },
    )
    parent_run_id = process_response.json()["run_id"]

    continue_response = client.post(
        f"/runs/{parent_run_id}/continue",
        json={"action": "draft_documentation"},
    )

    assert continue_response.status_code == 200
    payload = continue_response.json()
    assert payload["selected_workflow"] == "documentation"
    assert payload["run_id"] != parent_run_id
    assert [section["title"] for section in payload["result"]["sections"]] == [
        "Contexte",
        "Objectif",
        "Points cles",
        "Questions ouvertes",
        "Prochaines etapes",
    ]


def test_get_unknown_run_returns_404() -> None:
    response = client.get("/runs/unknown-run-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Run not found"


def test_continue_unknown_run_returns_404() -> None:
    response = client.post("/runs/unknown-run-id/continue", json={"action": "draft_ticket"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Run not found"


def test_continue_with_invalid_action_returns_422() -> None:
    process_response = client.post(
        "/process",
        json={
            "user_input": "La remise ne se calcule plus pour la commande web.",
            "target_output": "analysis",
        },
    )
    run_id = process_response.json()["run_id"]

    response = client.post(f"/runs/{run_id}/continue", json={"action": "publish"})

    assert response.status_code == 422


def test_source_summary_creates_run_and_returns_summary() -> None:
    original_reader = source_summary_service.source_reader
    source_summary_service.source_reader = FakeSourceReader()
    try:
        response = client.post(
            "/source-summary",
            json={
                "source_type": "url",
                "source_ref": "https://example.com/article",
                "context_hint": "Sujet de travail",
            },
        )
    finally:
        source_summary_service.source_reader = original_reader

    assert response.status_code == 200
    payload = response.json()
    assert "run_id" in payload
    assert payload["result"]["summary"]
    assert payload["result"]["key_points"]

    run_response = client.get(f"/runs/{payload['run_id']}")
    assert run_response.status_code == 200
    assert run_response.json()["result"]["source_ref"] == "https://example.com/article"


def test_source_summary_reader_error_returns_502_without_crash() -> None:
    original_reader = source_summary_service.source_reader
    source_summary_service.source_reader = FakeSourceReader(should_raise=True)
    try:
        response = client.post(
            "/source-summary",
            json={
                "source_type": "url",
                "source_ref": "https://example.com/unavailable",
            },
        )
    finally:
        source_summary_service.source_reader = original_reader

    assert response.status_code == 502
    assert response.json()["detail"] == "Source could not be read"


def test_source_summary_invalid_request_returns_422() -> None:
    response = client.post(
        "/source-summary",
        json={
            "source_type": "file",
            "source_ref": "abc",
        },
    )

    assert response.status_code == 422


def test_jira_read_creates_run_and_returns_structured_issue() -> None:
    original_service = jira_read_service.read_issue
    jira_read_service.read_issue = FakeJiraReadService(
        result={
            "issue_key": "PO-123",
            "title": "Remise incorrecte sur commande web",
            "description": "Le calcul de remise ne s'applique pas dans certains cas.",
            "status": "In Progress",
            "issue_type": "Bug",
            "priority": "High",
            "assignee": "Jane Doe",
            "labels": ["remise", "web"],
            "url": "https://jira.example.com/browse/PO-123",
            "summary": "Issue Jira lue: Remise incorrecte sur commande web. Type: Bug. Statut: In Progress. Priorite: High.",
            "open_points": [],
        }
    ).read_issue
    try:
        response = client.post(
            "/jira-read",
            json={"issue_key": "PO-123"},
        )
    finally:
        jira_read_service.read_issue = original_service

    assert response.status_code == 200
    payload = response.json()
    assert "run_id" in payload
    assert payload["result"]["issue_key"] == "PO-123"
    assert payload["result"]["title"] == "Remise incorrecte sur commande web"

    run_response = client.get(f"/runs/{payload['run_id']}")
    assert run_response.status_code == 200
    assert run_response.json()["result"]["issue_key"] == "PO-123"


def test_jira_read_unknown_issue_returns_404() -> None:
    original_service = jira_read_service.read_issue
    jira_read_service.read_issue = FakeJiraReadService(result=None).read_issue
    try:
        response = client.post(
            "/jira-read",
            json={"issue_key": "PO-404"},
        )
    finally:
        jira_read_service.read_issue = original_service

    assert response.status_code == 404
    assert response.json()["detail"] == "Jira issue not found"


def test_jira_read_invalid_request_returns_422() -> None:
    response = client.post(
        "/jira-read",
        json={"issue_key": ""},
    )

    assert response.status_code == 422


def test_continue_source_summary_to_documentation_creates_child_run() -> None:
    original_reader = source_summary_service.source_reader
    source_summary_service.source_reader = FakeSourceReader()
    try:
        source_response = client.post(
            "/source-summary",
            json={
                "source_type": "url",
                "source_ref": "https://example.com/article",
            },
        )
    finally:
        source_summary_service.source_reader = original_reader

    parent_run_id = source_response.json()["run_id"]
    continue_response = client.post(
        f"/runs/{parent_run_id}/continue",
        json={"action": "draft_documentation"},
    )

    assert continue_response.status_code == 200
    payload = continue_response.json()
    assert payload["run_id"] != parent_run_id
    assert payload["selected_workflow"] == "documentation"
    assert [section["title"] for section in payload["result"]["sections"]] == [
        "Contexte",
        "Objectif",
        "Points cles",
        "Questions ouvertes",
        "Prochaines etapes",
    ]

    child_run_response = client.get(f"/runs/{payload['run_id']}")
    child_run_payload = child_run_response.json()
    assert child_run_payload["parent_run_id"] == parent_run_id
    assert child_run_payload["continuation_action"] == "draft_documentation"


def test_continue_source_summary_to_analysis_creates_child_run() -> None:
    original_reader = source_summary_service.source_reader
    source_summary_service.source_reader = FakeSourceReader(
        payload={
            "url": "https://example.com/article",
            "title": "Remise web",
            "text": "La remise ne se calcule plus pour certaines commandes web via API.",
        }
    )
    try:
        source_response = client.post(
            "/source-summary",
            json={
                "source_type": "url",
                "source_ref": "https://example.com/article",
            },
        )
    finally:
        source_summary_service.source_reader = original_reader

    parent_run_id = source_response.json()["run_id"]
    continue_response = client.post(
        f"/runs/{parent_run_id}/continue",
        json={"action": "refine_analysis"},
    )

    assert continue_response.status_code == 200
    payload = continue_response.json()
    assert payload["selected_workflow"] == "analysis"
    assert payload["result"]["request_summary"]
    assert "source" in payload["result"]["context_hint"].lower()


def test_continue_source_summary_to_ticket_uses_derived_analysis() -> None:
    original_reader = source_summary_service.source_reader
    source_summary_service.source_reader = FakeSourceReader(
        payload={
            "url": "https://example.com/article",
            "title": "Paiement web",
            "text": "Le paiement ne fonctionne plus pour certains utilisateurs sur la commande web.",
        }
    )
    try:
        source_response = client.post(
            "/source-summary",
            json={
                "source_type": "url",
                "source_ref": "https://example.com/article",
            },
        )
    finally:
        source_summary_service.source_reader = original_reader

    parent_run_id = source_response.json()["run_id"]
    continue_response = client.post(
        f"/runs/{parent_run_id}/continue",
        json={"action": "draft_ticket"},
    )

    assert continue_response.status_code == 200
    payload = continue_response.json()
    assert payload["selected_workflow"] == "ticket"
    assert payload["intermediate_analysis"] is not None
    assert payload["result"]["title"]

    child_run_response = client.get(f"/runs/{payload['run_id']}")
    child_run_payload = child_run_response.json()
    assert child_run_payload["parent_run_id"] == parent_run_id
    assert child_run_payload["continuation_action"] == "draft_ticket"


def test_continue_jira_run_to_documentation_creates_child_run() -> None:
    original_service = jira_read_service.read_issue
    jira_read_service.read_issue = FakeJiraReadService(
        result={
            "issue_key": "PO-200",
            "title": "Facturation a clarifier",
            "description": "La facturation ne suit pas toujours la regle attendue sur les commandes web.",
            "status": "To Do",
            "issue_type": "Story",
            "priority": "Medium",
            "assignee": None,
            "labels": ["facturation", "web"],
            "url": "https://jira.example.com/browse/PO-200",
            "summary": "Issue Jira lue: Facturation a clarifier. Type: Story. Statut: To Do. Priorite: Medium.",
            "open_points": ["Le comportement attendu doit etre confirme avec le metier."],
        }
    ).read_issue
    try:
        jira_response = client.post("/jira-read", json={"issue_key": "PO-200"})
    finally:
        jira_read_service.read_issue = original_service

    parent_run_id = jira_response.json()["run_id"]
    continue_response = client.post(
        f"/runs/{parent_run_id}/continue",
        json={"action": "draft_documentation"},
    )

    assert continue_response.status_code == 200
    payload = continue_response.json()
    assert payload["selected_workflow"] == "documentation"
    assert payload["run_id"] != parent_run_id

    child_run_response = client.get(f"/runs/{payload['run_id']}")
    child_run_payload = child_run_response.json()
    assert child_run_payload["parent_run_id"] == parent_run_id
    assert child_run_payload["continuation_action"] == "draft_documentation"


def test_continue_jira_run_to_analysis_creates_child_run() -> None:
    original_service = jira_read_service.read_issue
    jira_read_service.read_issue = FakeJiraReadService(
        result={
            "issue_key": "PO-201",
            "title": "Paiement web en erreur",
            "description": "Le paiement ne fonctionne plus pour certains utilisateurs sur la commande web.",
            "status": "In Progress",
            "issue_type": "Bug",
            "priority": "High",
            "assignee": "Jane Doe",
            "labels": ["paiement", "commande"],
            "url": "https://jira.example.com/browse/PO-201",
            "summary": "Issue Jira lue: Paiement web en erreur. Type: Bug. Statut: In Progress. Priorite: High.",
            "open_points": [],
        }
    ).read_issue
    try:
        jira_response = client.post("/jira-read", json={"issue_key": "PO-201"})
    finally:
        jira_read_service.read_issue = original_service

    parent_run_id = jira_response.json()["run_id"]
    continue_response = client.post(
        f"/runs/{parent_run_id}/continue",
        json={"action": "refine_analysis"},
    )

    assert continue_response.status_code == 200
    payload = continue_response.json()
    assert payload["selected_workflow"] == "analysis"
    assert payload["result"]["request_summary"]
    assert payload["result"]["current_behavior"]


def test_continue_jira_run_to_ticket_uses_derived_analysis() -> None:
    original_service = jira_read_service.read_issue
    jira_read_service.read_issue = FakeJiraReadService(
        result={
            "issue_key": "PO-202",
            "title": "Remise web incoherente",
            "description": "Le calcul de remise ne s'applique pas sur certaines commandes web.",
            "status": "To Do",
            "issue_type": "Bug",
            "priority": "High",
            "assignee": "John Doe",
            "labels": ["remise", "commande", "web"],
            "url": "https://jira.example.com/browse/PO-202",
            "summary": "Issue Jira lue: Remise web incoherente. Type: Bug. Statut: To Do. Priorite: High.",
            "open_points": ["Le comportement attendu doit etre precise."],
        }
    ).read_issue
    try:
        jira_response = client.post("/jira-read", json={"issue_key": "PO-202"})
    finally:
        jira_read_service.read_issue = original_service

    parent_run_id = jira_response.json()["run_id"]
    continue_response = client.post(
        f"/runs/{parent_run_id}/continue",
        json={"action": "draft_ticket"},
    )

    assert continue_response.status_code == 200
    payload = continue_response.json()
    assert payload["selected_workflow"] == "ticket"
    assert payload["intermediate_analysis"] is not None
    assert payload["result"]["title"]

    child_run_response = client.get(f"/runs/{payload['run_id']}")
    child_run_payload = child_run_response.json()
    assert child_run_payload["parent_run_id"] == parent_run_id
    assert child_run_payload["continuation_action"] == "draft_ticket"

from app.orchestrator.router import WorkflowRouter


def test_router_sends_bug_to_ticket_workflow() -> None:
    router = WorkflowRouter()

    assert router.route("bug") == "ticket"


def test_router_respects_explicit_target_output() -> None:
    router = WorkflowRouter()

    assert router.route("analysis", target_output="documentation") == "documentation"

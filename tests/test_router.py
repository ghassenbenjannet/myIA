from app.orchestrator.router import WorkflowRouter


def test_router_routes_documentation_to_documentation() -> None:
    router = WorkflowRouter()

    assert router.route("documentation") == "documentation"


def test_router_routes_bug_to_ticket() -> None:
    router = WorkflowRouter()

    assert router.route("bug") == "ticket"


def test_router_routes_evolution_to_ticket() -> None:
    router = WorkflowRouter()

    assert router.route("evolution") == "ticket"


def test_router_routes_analysis_to_analysis() -> None:
    router = WorkflowRouter()

    assert router.route("analysis") == "analysis"


def test_router_routes_unknown_to_analysis() -> None:
    router = WorkflowRouter()

    assert router.route("unknown") == "analysis"


def test_router_respects_explicit_target_output() -> None:
    router = WorkflowRouter()

    assert router.route("bug", target_output="documentation") == "documentation"
    assert router.route("documentation", target_output="analysis") == "analysis"
    assert router.route("analysis", target_output="ticket") == "ticket"

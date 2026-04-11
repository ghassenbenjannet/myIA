from app.orchestrator.router import select_route


def test_select_route_returns_classification() -> None:
    assert select_route("analysis") == "analysis"

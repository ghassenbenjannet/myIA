from app.api.routes_process import router


def test_process_router_prefix() -> None:
    assert router["prefix"] == "/process"

from app.services.context_provider import ReadOnlyContextProvider


class FakeConfluenceClient:
    def __init__(self, payload=None, should_raise: bool = False) -> None:
        self.payload = payload
        self.should_raise = should_raise

    def search_relevant_context(self, query: str):
        if self.should_raise:
            raise RuntimeError("confluence unavailable")
        return self.payload


def test_context_provider_without_confluence_config_falls_back_to_stub() -> None:
    provider = ReadOnlyContextProvider(confluence_client=FakeConfluenceClient(payload=None))

    context = provider.fetch(
        user_input="Sujet sur la remise appliquee a la commande web",
        context_hint=None,
        request_type="analysis",
    )

    assert context is not None
    assert context.source_name == "stub_confluence"


def test_context_provider_uses_confluence_when_client_returns_payload() -> None:
    provider = ReadOnlyContextProvider(
        confluence_client=FakeConfluenceClient(
            payload={
                "source_name": "confluence",
                "summary": "Contexte recupere depuis Confluence.",
                "snippets": ["Règle de remise projetée".replace("è", "e")],
                "confidence_hint": 0.81,
            }
        )
    )

    context = provider.fetch(
        user_input="Sujet sur la remise a analyser",
        context_hint=None,
        request_type="analysis",
    )

    assert context is not None
    assert context.source_name == "confluence"
    assert context.summary == "Contexte recupere depuis Confluence."


def test_context_provider_confluence_error_falls_back_cleanly() -> None:
    provider = ReadOnlyContextProvider(confluence_client=FakeConfluenceClient(should_raise=True))

    context = provider.fetch(
        user_input="Sujet sur la facturation a analyser",
        context_hint=None,
        request_type="analysis",
    )

    assert context is not None
    assert context.source_name == "stub_confluence"

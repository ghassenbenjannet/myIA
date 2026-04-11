from app.connectors.confluence.client import ConfluenceClient
from app.core.config import CONFLUENCE_API_TOKEN, CONFLUENCE_BASE_URL, CONFLUENCE_ENABLED
from app.schemas.context import ContextUsed


class ReadOnlyContextProvider:
    """
    Minimal readonly context provider.

    It prefers a real Confluence readonly lookup when configured, then falls
    back to a deterministic local stub for a few known business topics.
    """

    def __init__(self, confluence_client: ConfluenceClient | None = None) -> None:
        self.confluence_client = confluence_client or ConfluenceClient(
            base_url=CONFLUENCE_BASE_URL,
            api_token=CONFLUENCE_API_TOKEN,
            enabled=CONFLUENCE_ENABLED,
        )

    def fetch(
        self,
        user_input: str,
        context_hint: str | None,
        request_type: str | None = None,
    ) -> ContextUsed | None:
        lowered = self._normalize(f"{user_input} {context_hint or ''}")
        query = self._build_query(lowered)
        if query is None:
            return None

        confluence_context = self._fetch_from_confluence(query)
        if confluence_context is not None:
            return confluence_context

        return self._fallback_stub(lowered)

    def _fetch_from_confluence(self, query: str) -> ContextUsed | None:
        try:
            payload = self.confluence_client.search_relevant_context(query)
        except Exception:
            return None

        if payload is None:
            return None

        return ContextUsed(**payload)

    def _fallback_stub(self, lowered: str) -> ContextUsed | None:
        if any(keyword in lowered for keyword in ("remise", "facturation", "commande")):
            return ContextUsed(
                source_name="stub_confluence",
                summary="Contexte documentaire simulé sur les règles de commande, remise et facturation.",
                snippets=[
                    "Les remises doivent respecter les règles de calcul validées par le métier.",
                    "Les traitements batch et les commandes web doivent rester cohérents sur les cas standards.",
                ],
                confidence_hint=0.72,
            )
        return None

    def _build_query(self, lowered: str) -> str | None:
        keywords = [keyword for keyword in ("remise", "facturation", "commande") if keyword in lowered]
        if not keywords:
            return None
        return " ".join(keywords[:2])

    def _normalize(self, value: str) -> str:
        replacements = {
            "é": "e",
            "è": "e",
            "ê": "e",
            "à": "a",
            "â": "a",
            "ù": "u",
            "û": "u",
            "î": "i",
            "ï": "i",
            "ô": "o",
            "ç": "c",
        }
        normalized = value.lower()
        for source, target in replacements.items():
            normalized = normalized.replace(source, target)
        return normalized

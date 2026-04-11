import httpx


class ConfluenceClient:
    """
    Minimal readonly Confluence client.

    The client is intentionally small: one targeted search call, no write path,
    no pagination logic, and graceful fallback to None when disabled.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | None = None,
        enabled: bool = False,
        timeout: float = 2.0,
    ) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self.api_token = api_token
        self.enabled = enabled and bool(self.base_url) and bool(self.api_token)
        self.timeout = timeout

    def search_relevant_context(self, query: str) -> dict | None:
        if not self.enabled:
            return None

        response = httpx.get(
            f"{self.base_url}/wiki/rest/api/search",
            params={"cql": f'text~"{query}"', "limit": 2},
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Accept": "application/json",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results", [])
        if not results:
            return None

        snippets: list[str] = []
        for item in results[:2]:
            title = item.get("title") or "Contenu Confluence"
            excerpt = item.get("excerpt") or ""
            snippets.append(f"{title}: {excerpt}".strip())

        return {
            "source_name": "confluence",
            "summary": "Contexte documentaire cible recupere depuis Confluence.",
            "snippets": snippets,
            "confidence_hint": 0.78,
        }

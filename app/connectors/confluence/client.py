import httpx
from html import unescape
import re


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

    def get_page(self, page_id: str) -> dict | None:
        if not self.enabled:
            return None

        response = httpx.get(
            f"{self.base_url}/wiki/rest/api/content/{page_id}",
            params={"expand": "space,body.storage"},
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Accept": "application/json",
            },
            timeout=self.timeout,
        )
        if response.status_code == 404:
            return None

        response.raise_for_status()
        payload = response.json()
        storage = ((payload.get("body") or {}).get("storage") or {}).get("value") or ""
        preview = self._extract_text(storage)
        space = payload.get("space") or {}
        return {
            "page_id": str(payload.get("id", page_id)),
            "title": payload.get("title") or page_id,
            "space_key": space.get("key"),
            "url": f"{self.base_url}/wiki{payload.get('_links', {}).get('webui', '')}" if payload.get("_links", {}).get("webui") else None,
            "content_preview": preview,
        }

    def _extract_text(self, html: str) -> str | None:
        if not html:
            return None
        text = re.sub(r"<[^>]+>", " ", html)
        text = unescape(text)
        normalized = " ".join(text.split())
        return normalized or None

from app.connectors.confluence.client import ConfluenceClient
from app.core.config import CONFLUENCE_API_TOKEN, CONFLUENCE_BASE_URL, CONFLUENCE_ENABLED
from app.schemas.confluence_request import ConfluenceReadRequest
from app.schemas.confluence_result import ConfluencePageResult


class ConfluenceNotConfiguredError(Exception):
    pass


class ConfluencePageNotFoundError(Exception):
    pass


class ConfluenceReadFailedError(Exception):
    pass


class ConfluenceReadService:
    """
    Minimal readonly Confluence service.

    It reads a single page and maps it to a compact work artifact.
    """

    def __init__(self, confluence_client: ConfluenceClient | None = None) -> None:
        self.confluence_client = confluence_client or ConfluenceClient(
            base_url=CONFLUENCE_BASE_URL,
            api_token=CONFLUENCE_API_TOKEN,
            enabled=CONFLUENCE_ENABLED,
        )

    def read_page(self, request: ConfluenceReadRequest) -> ConfluencePageResult:
        if not self.confluence_client.enabled:
            raise ConfluenceNotConfiguredError("Confluence client is not configured")

        try:
            payload = self.confluence_client.get_page(request.page_id)
        except Exception as exc:
            raise ConfluenceReadFailedError(f"Confluence page could not be read: {request.page_id}") from exc

        if payload is None:
            raise ConfluencePageNotFoundError(f"Confluence page not found: {request.page_id}")

        preview = self._normalize_text(payload.get("content_preview"))
        title = payload.get("title") or request.page_id
        return ConfluencePageResult(
            page_id=payload["page_id"],
            title=title,
            space_key=payload.get("space_key"),
            url=payload.get("url"),
            summary=self._build_summary(title=title, space_key=payload.get("space_key"), preview=preview),
            content_preview=preview,
            key_points=self._build_key_points(title=title, space_key=payload.get("space_key"), preview=preview),
            open_points=self._build_open_points(preview=preview),
        )

    def _build_summary(self, title: str, space_key: str | None, preview: str | None) -> str:
        parts = [f"Page Confluence lue: {title}."]
        if space_key:
            parts.append(f"Espace: {space_key}.")
        if preview:
            parts.append(preview[:220].strip())
        return " ".join(parts)

    def _build_key_points(self, title: str, space_key: str | None, preview: str | None) -> list[str]:
        points = [f"Titre: {title}."]
        if space_key:
            points.append(f"Espace source: {space_key}.")
        if preview:
            sentences = [chunk.strip() for chunk in preview.split(".") if chunk.strip()]
            points.extend(sentences[:2])
        return points[:3]

    def _build_open_points(self, preview: str | None) -> list[str]:
        if not preview:
            return ["Le contenu Confluence est vide ou trop pauvre pour etre exploite tel quel."]
        if len(preview) < 80:
            return ["Le contenu Confluence reste partiel et doit etre complete."]
        return []

    def _normalize_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None

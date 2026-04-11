import httpx


class JiraClient:
    """
    Minimal readonly Jira client.

    The client reads a single issue by key, with no write path and no search.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | None = None,
        user_email: str | None = None,
        enabled: bool = False,
        timeout: float = 2.0,
    ) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self.api_token = api_token
        self.user_email = user_email
        self.enabled = enabled and bool(self.base_url) and bool(self.api_token) and bool(self.user_email)
        self.timeout = timeout

    def get_issue(self, issue_key: str) -> dict | None:
        if not self.enabled:
            return None

        response = httpx.get(
            f"{self.base_url}/rest/api/3/issue/{issue_key}",
            params={"fields": "summary,description,status,issuetype,priority,assignee,labels"},
            auth=(self.user_email, self.api_token),
            headers={"Accept": "application/json"},
            timeout=self.timeout,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        payload = response.json()
        fields = payload.get("fields", {})
        assignee = fields.get("assignee") or {}
        return {
            "issue_key": payload.get("key", issue_key),
            "title": fields.get("summary"),
            "description": self._extract_description(fields.get("description")),
            "status": (fields.get("status") or {}).get("name"),
            "issue_type": (fields.get("issuetype") or {}).get("name"),
            "priority": (fields.get("priority") or {}).get("name"),
            "assignee": assignee.get("displayName"),
            "labels": fields.get("labels") or [],
            "url": f"{self.base_url}/browse/{payload.get('key', issue_key)}",
        }

    def _extract_description(self, description: dict | str | None) -> str | None:
        if description is None:
            return None
        if isinstance(description, str):
            return self._normalize_text(description)

        parts = self._extract_text_nodes(description)
        if not parts:
            return None
        return self._normalize_text(" ".join(parts))

    def _extract_text_nodes(self, node) -> list[str]:
        if node is None:
            return []
        if isinstance(node, str):
            return [node]
        if not isinstance(node, dict):
            return []

        parts: list[str] = []
        text = node.get("text")
        if text:
            parts.append(text)

        for child in node.get("content", []):
            parts.extend(self._extract_text_nodes(child))
        return parts

    def _normalize_text(self, value: str) -> str:
        return " ".join(value.split())

from app.connectors.jira.client import JiraClient
from app.core.config import JIRA_API_TOKEN, JIRA_BASE_URL, JIRA_ENABLED, JIRA_USER_EMAIL
from app.schemas.jira_request import JiraReadRequest
from app.schemas.jira_result import JiraIssueResult


class JiraReadService:
    """
    Minimal readonly Jira service.

    It reads a single issue and maps it to a compact work artifact.
    """

    def __init__(self, jira_client: JiraClient | None = None) -> None:
        self.jira_client = jira_client or JiraClient(
            base_url=JIRA_BASE_URL,
            api_token=JIRA_API_TOKEN,
            user_email=JIRA_USER_EMAIL,
            enabled=JIRA_ENABLED,
        )

    def read_issue(self, request: JiraReadRequest) -> JiraIssueResult | None:
        payload = self.jira_client.get_issue(request.issue_key)
        if payload is None:
            return None

        description = payload.get("description")
        status = payload.get("status")
        issue_type = payload.get("issue_type")
        priority = payload.get("priority")
        assignee = payload.get("assignee")
        labels = payload.get("labels") or []

        return JiraIssueResult(
            issue_key=payload["issue_key"],
            title=payload.get("title") or request.issue_key,
            description=description,
            status=status,
            issue_type=issue_type,
            priority=priority,
            assignee=assignee,
            labels=labels,
            url=payload.get("url"),
            summary=self._build_summary(
                title=payload.get("title") or request.issue_key,
                status=status,
                issue_type=issue_type,
                priority=priority,
            ),
            open_points=self._build_open_points(
                description=description,
                assignee=assignee,
                priority=priority,
            ),
        )

    def _build_summary(
        self,
        title: str,
        status: str | None,
        issue_type: str | None,
        priority: str | None,
    ) -> str:
        parts = [f"Issue Jira lue: {title}."]
        if issue_type:
            parts.append(f"Type: {issue_type}.")
        if status:
            parts.append(f"Statut: {status}.")
        if priority:
            parts.append(f"Priorite: {priority}.")
        return " ".join(parts)

    def _build_open_points(
        self,
        description: str | None,
        assignee: str | None,
        priority: str | None,
    ) -> list[str]:
        open_points: list[str] = []
        if not description:
            open_points.append("La description Jira doit etre completee ou confirmee.")
        if not assignee:
            open_points.append("L'owner ou l'assignation doivent etre confirmes.")
        if not priority:
            open_points.append("La priorite doit etre confirmee.")
        return open_points

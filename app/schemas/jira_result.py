from typing import Literal

from pydantic import BaseModel, Field


class JiraIssueResult(BaseModel):
    result_type: Literal["jira_read"] = "jira_read"
    issue_key: str
    title: str
    description: str | None = None
    status: str | None = None
    issue_type: str | None = None
    priority: str | None = None
    assignee: str | None = None
    labels: list[str] = Field(default_factory=list)
    url: str | None = None
    summary: str
    open_points: list[str] = Field(default_factory=list)

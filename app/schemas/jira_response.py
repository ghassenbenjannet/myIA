from pydantic import BaseModel, Field

from app.schemas.jira_result import JiraIssueResult


class JiraReadResponse(BaseModel):
    run_id: str = Field(..., description="Identifier of the stored work memory run.")
    topic_id: str = Field(..., description="Identifier of the parent work topic.")
    result: JiraIssueResult

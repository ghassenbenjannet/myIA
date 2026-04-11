from pydantic import BaseModel, Field


class JiraReadRequest(BaseModel):
    issue_key: str = Field(..., min_length=1)

from pydantic import BaseModel, Field

from app.schemas.confluence_result import ConfluencePageResult


class ConfluenceReadResponse(BaseModel):
    run_id: str = Field(..., description="Identifier of the stored work memory run.")
    topic_id: str = Field(..., description="Identifier of the parent work topic.")
    result: ConfluencePageResult

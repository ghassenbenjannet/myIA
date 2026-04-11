from pydantic import BaseModel, Field

from app.schemas.source_summary import SourceSummaryResult


class SourceSummaryResponse(BaseModel):
    run_id: str = Field(..., description="Identifier of the stored work memory run.")
    topic_id: str = Field(..., description="Identifier of the parent work topic.")
    result: SourceSummaryResult

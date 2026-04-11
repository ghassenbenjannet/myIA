from pydantic import BaseModel, Field


class SourceSummaryResult(BaseModel):
    source_type: str
    source_ref: str
    source_title: str | None = None
    summary: str
    key_points: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    next_step_hint: str

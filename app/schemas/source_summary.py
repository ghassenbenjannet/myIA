from typing import Literal

from pydantic import BaseModel, Field


class SourceSummaryResult(BaseModel):
    result_type: Literal["source_summary"] = "source_summary"
    source_type: str
    source_ref: str
    source_title: str | None = None
    summary: str
    key_points: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    next_step_hint: str

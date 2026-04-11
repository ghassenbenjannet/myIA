from typing import Literal

from pydantic import BaseModel, Field


class SourceSummaryRequest(BaseModel):
    source_type: Literal["url"] = Field(..., description="Supported source type.")
    source_ref: str = Field(..., min_length=5, description="Source reference, for now a URL.")
    context_hint: str | None = Field(default=None, description="Optional reading context.")

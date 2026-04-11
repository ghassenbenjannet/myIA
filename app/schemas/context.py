from pydantic import BaseModel, Field


class ContextUsed(BaseModel):
    source_name: str
    snippets: list[str] = Field(default_factory=list)
    summary: str
    confidence_hint: float = Field(..., ge=0.0, le=1.0)

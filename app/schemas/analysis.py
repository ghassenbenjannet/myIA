from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    reformulation: str
    request_summary: str
    context_hint: str | None = None
    detected_type: str
    ambiguities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    recommended_next_step: str

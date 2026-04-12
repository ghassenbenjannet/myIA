from typing import Literal

from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    result_type: Literal["analysis"] = "analysis"
    reformulation: str
    request_summary: str
    context_hint: str | None = None
    detected_type: str
    current_behavior: str | None = None
    expected_behavior: str | None = None
    business_impacts: list[str] = Field(default_factory=list)
    technical_impacts: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    recommended_next_step: str
    recommended_output: str

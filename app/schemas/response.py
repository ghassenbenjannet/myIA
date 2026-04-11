from typing import Any

from pydantic import BaseModel, Field


class ProcessResponse(BaseModel):
    request_type: str = Field(..., description="Detected request type.")
    selected_workflow: str = Field(..., description="Workflow selected by the router.")
    confidence: float = Field(..., ge=0.0, le=1.0)
    result: dict[str, Any] = Field(..., description="Structured business result.")
    quality_checks: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

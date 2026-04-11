from pydantic import BaseModel, Field

from app.schemas.analysis import AnalysisResult
from app.schemas.documentation import DocumentationResult
from app.schemas.ticket import TicketResult

ProcessResult = AnalysisResult | TicketResult | DocumentationResult


class ProcessResponse(BaseModel):
    request_type: str = Field(..., description="Detected request type.")
    selected_workflow: str = Field(..., description="Workflow selected by the router.")
    confidence: float = Field(..., ge=0.0, le=1.0)
    result: ProcessResult = Field(..., description="Structured business result.")
    quality_checks: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.analysis import AnalysisResult
from app.schemas.context import ContextUsed
from app.schemas.documentation import DocumentationResult
from app.schemas.ticket import TicketResult

WorkResult = AnalysisResult | TicketResult | DocumentationResult


class WorkMemoryRun(BaseModel):
    run_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"
    raw_input: str
    target_output: str
    request_type: str
    final_workflow: str
    result: WorkResult
    intermediate_analysis: AnalysisResult | None = None
    context_used: ContextUsed | None = None

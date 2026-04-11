from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.schemas.analysis import AnalysisResult
from app.schemas.context import ContextUsed
from app.schemas.documentation import DocumentationResult
from app.schemas.jira_result import JiraIssueResult
from app.schemas.source_summary import SourceSummaryResult
from app.schemas.ticket import TicketResult

WorkResult = AnalysisResult | TicketResult | DocumentationResult | SourceSummaryResult | JiraIssueResult


class WorkMemoryRun(BaseModel):
    run_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = "completed"
    parent_run_id: str | None = None
    continuation_action: str | None = None
    raw_input: str
    target_output: str
    request_type: str
    final_workflow: str
    result: WorkResult
    intermediate_analysis: AnalysisResult | None = None
    context_used: ContextUsed | None = None

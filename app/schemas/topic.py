from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.schemas.analysis import AnalysisResult
from app.schemas.documentation import DocumentationResult
from app.schemas.jira_result import JiraIssueResult
from app.schemas.source_summary import SourceSummaryResult
from app.schemas.ticket import TicketResult
from app.schemas.work_memory import WorkMemoryRun


class WorkTopic(BaseModel):
    topic_id: str
    topic_label: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    root_run_id: str
    latest_run_id: str
    run_ids: list[str] = Field(default_factory=list)
    status: str = "active"


class TopicSummary(BaseModel):
    topic_id: str
    topic_label: str
    created_at: datetime
    updated_at: datetime
    root_run_id: str
    latest_run_id: str
    status: str
    run_count: int


class TopicRunView(WorkMemoryRun):
    available_actions: list[str] = Field(default_factory=list)


class TopicDetailResponse(BaseModel):
    topic: WorkTopic
    runs: list[TopicRunView] = Field(default_factory=list)
    root_run: TopicRunView | None = None
    latest_run: TopicRunView | None = None


def build_available_actions(run: WorkMemoryRun) -> list[str]:
    if isinstance(run.result, (AnalysisResult, SourceSummaryResult, JiraIssueResult)):
        return ["refine_analysis", "draft_ticket", "draft_documentation"]

    if run.intermediate_analysis is not None:
        return ["refine_analysis", "draft_ticket", "draft_documentation"]

    if isinstance(run.result, (TicketResult, DocumentationResult)):
        return []

    return []


def build_topic_run_view(run: WorkMemoryRun) -> TopicRunView:
    return TopicRunView(**run.model_dump(), available_actions=build_available_actions(run))

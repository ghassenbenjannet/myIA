from datetime import UTC, datetime

from pydantic import BaseModel, Field

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


class TopicDetailResponse(BaseModel):
    topic: WorkTopic
    runs: list[WorkMemoryRun] = Field(default_factory=list)

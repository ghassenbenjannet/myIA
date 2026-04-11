from fastapi import APIRouter, HTTPException

from app.orchestrator.engine import ProcessEngine
from app.schemas.continuation import ContinueRunRequest
from app.schemas.jira_request import JiraReadRequest
from app.schemas.jira_response import JiraReadResponse
from app.schemas.request import ProcessRequest
from app.schemas.response import ProcessResponse
from app.schemas.source_request import SourceSummaryRequest
from app.schemas.source_response import SourceSummaryResponse
from app.schemas.topic import TopicDetailResponse, TopicSummary, build_topic_run_view
from app.schemas.work_memory import WorkMemoryRun
from app.services.jira_read_service import (
    JiraIssueNotFoundError,
    JiraNotConfiguredError,
    JiraReadService,
)
from app.services.source_summary_service import SourceSummaryService
from app.services.topic_repository import topic_repository
from app.services.work_memory_repository import work_memory_repository

router = APIRouter(tags=["process"])
engine = ProcessEngine()
source_summary_service = SourceSummaryService()
jira_read_service = JiraReadService()


@router.post("/process", response_model=ProcessResponse)
def process(request: ProcessRequest) -> ProcessResponse:
    return engine.process(request)


@router.get("/runs/{run_id}", response_model=WorkMemoryRun)
def get_run(run_id: str) -> WorkMemoryRun:
    run = work_memory_repository.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/topics", response_model=list[TopicSummary])
def list_topics() -> list[TopicSummary]:
    return topic_repository.list_topic_summaries()


@router.get("/topics/{topic_id}", response_model=TopicDetailResponse)
def get_topic(topic_id: str) -> TopicDetailResponse:
    topic = topic_repository.get_topic(topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    runs = [build_topic_run_view(run) for run in topic_repository.get_topic_runs(topic_id)]
    root_run = next((run for run in runs if run.run_id == topic.root_run_id), None)
    latest_run = next((run for run in runs if run.run_id == topic.latest_run_id), None)
    return TopicDetailResponse(
        topic=topic,
        runs=runs,
        root_run=root_run,
        latest_run=latest_run,
    )


@router.post("/runs/{run_id}/continue", response_model=ProcessResponse)
def continue_run(run_id: str, request: ContinueRunRequest) -> ProcessResponse:
    return engine.continue_run(run_id, request.action)


@router.post("/source-summary", response_model=SourceSummaryResponse)
def source_summary(request: SourceSummaryRequest) -> SourceSummaryResponse:
    try:
        result = source_summary_service.summarize(request)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Source could not be read") from exc
    run = work_memory_repository.create_run(
        raw_input=request.source_ref,
        target_output="source_summary",
        request_type="source_summary",
        final_workflow="source_summary",
        result=result,
    )
    topic = topic_repository.create_topic(
        run_id=run.run_id,
        topic_label=topic_repository.build_default_label(raw_input=request.source_ref, result=result),
    )
    work_memory_repository.assign_topic(run.run_id, topic.topic_id)
    return SourceSummaryResponse(run_id=run.run_id, topic_id=topic.topic_id, result=result)


@router.post("/jira-read", response_model=JiraReadResponse)
def jira_read(request: JiraReadRequest) -> JiraReadResponse:
    try:
        result = jira_read_service.read_issue(request)
    except JiraNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail="Jira is not configured") from exc
    except JiraIssueNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Jira issue not found") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Jira issue could not be read") from exc

    run = work_memory_repository.create_run(
        raw_input=request.issue_key,
        target_output="jira_read",
        request_type="jira_read",
        final_workflow="jira_read",
        result=result,
    )
    topic = topic_repository.create_topic(
        run_id=run.run_id,
        topic_label=topic_repository.build_default_label(raw_input=request.issue_key, result=result),
    )
    work_memory_repository.assign_topic(run.run_id, topic.topic_id)
    return JiraReadResponse(run_id=run.run_id, topic_id=topic.topic_id, result=result)

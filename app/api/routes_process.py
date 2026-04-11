from fastapi import APIRouter, HTTPException

from app.orchestrator.engine import ProcessEngine
from app.schemas.continuation import ContinueRunRequest
from app.schemas.request import ProcessRequest
from app.schemas.response import ProcessResponse
from app.schemas.source_request import SourceSummaryRequest
from app.schemas.source_response import SourceSummaryResponse
from app.schemas.work_memory import WorkMemoryRun
from app.services.source_summary_service import SourceSummaryService
from app.services.work_memory_repository import work_memory_repository

router = APIRouter(tags=["process"])
engine = ProcessEngine()
source_summary_service = SourceSummaryService()


@router.post("/process", response_model=ProcessResponse)
def process(request: ProcessRequest) -> ProcessResponse:
    return engine.process(request)


@router.get("/runs/{run_id}", response_model=WorkMemoryRun)
def get_run(run_id: str) -> WorkMemoryRun:
    run = work_memory_repository.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


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
    return SourceSummaryResponse(run_id=run.run_id, result=result)

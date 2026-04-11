from fastapi import APIRouter, HTTPException

from app.orchestrator.engine import ProcessEngine
from app.schemas.request import ProcessRequest
from app.schemas.response import ProcessResponse
from app.schemas.work_memory import WorkMemoryRun
from app.services.work_memory_repository import work_memory_repository

router = APIRouter(tags=["process"])
engine = ProcessEngine()


@router.post("/process", response_model=ProcessResponse)
def process(request: ProcessRequest) -> ProcessResponse:
    return engine.process(request)


@router.get("/runs/{run_id}", response_model=WorkMemoryRun)
def get_run(run_id: str) -> WorkMemoryRun:
    run = work_memory_repository.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

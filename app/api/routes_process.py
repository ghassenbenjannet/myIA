from fastapi import APIRouter

from app.orchestrator.engine import ProcessEngine
from app.schemas.request import ProcessRequest
from app.schemas.response import ProcessResponse

router = APIRouter(tags=["process"])
engine = ProcessEngine()


@router.post("/process", response_model=ProcessResponse)
def process(request: ProcessRequest) -> ProcessResponse:
    return engine.process(request)

from pydantic import BaseModel
from typing import Any


class ProcessResponse(BaseModel):
    request_type: str
    selected_workflow: str
    confidence: float
    result: dict[str, Any]
    quality_checks: list[str]
    warnings: list[str]
from typing import Any

from pydantic import BaseModel, Field


class DocumentationResult(BaseModel):
    document_type: str
    title: str
    summary: str
    context: str
    sections: list[dict[str, Any]] = Field(default_factory=list)
    detected_type: str

from typing import Any, Literal

from pydantic import BaseModel, Field


class DocumentationResult(BaseModel):
    result_type: Literal["documentation"] = "documentation"
    document_type: str
    title: str
    summary: str
    context: str
    sections: list[dict[str, Any]] = Field(default_factory=list)
    detected_type: str

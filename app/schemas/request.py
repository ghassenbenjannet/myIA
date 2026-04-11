from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    user_input: str = Field(..., min_length=3)
    context_hint: str | None = None
    target_output: str | None = None
from typing import Literal

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    user_input: str = Field(
        ...,
        min_length=3,
        description="Raw user input to analyze and transform.",
    )
    context_hint: str | None = Field(
        default=None,
        description="Optional hint about the business or technical context.",
    )
    target_output: Literal["auto", "analysis", "ticket", "documentation"] = Field(
        default="auto",
        description="Optional preferred output type.",
    )
    mode: Literal["deterministic", "assisted"] = Field(
        default="deterministic",
        description="Processing mode. 'assisted' routes through the configured LLM provider.",
    )

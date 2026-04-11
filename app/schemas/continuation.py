from typing import Literal

from pydantic import BaseModel


class ContinueRunRequest(BaseModel):
    action: Literal["refine_analysis", "draft_ticket", "draft_documentation"]

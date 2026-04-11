from pydantic import BaseModel, Field


class ConfluenceReadRequest(BaseModel):
    page_id: str = Field(..., min_length=1, description="Confluence page identifier to read.")

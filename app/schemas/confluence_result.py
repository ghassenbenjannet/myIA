from pydantic import BaseModel, Field


class ConfluencePageResult(BaseModel):
    page_id: str
    title: str
    space_key: str | None = None
    url: str | None = None
    summary: str
    content_preview: str | None = None
    key_points: list[str] = Field(default_factory=list)
    open_points: list[str] = Field(default_factory=list)

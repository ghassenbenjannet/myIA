from pydantic import BaseModel, Field


class TicketResult(BaseModel):
    ticket_type: str
    title: str
    description: str
    context: str
    business_goal: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    open_points: list[str] = Field(default_factory=list)

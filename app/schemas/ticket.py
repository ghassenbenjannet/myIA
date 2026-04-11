from pydantic import BaseModel, Field


class TicketResult(BaseModel):
    ticket_type: str
    title: str
    description: str
    context: str
    current_behavior: str | None = None
    expected_behavior: str | None = None
    business_goal: str
    business_impacts: list[str] = Field(default_factory=list)
    technical_impacts: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    open_points: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)

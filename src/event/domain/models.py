import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class Status(StrEnum):
    """Event status for filtering and display."""

    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    PAST = "past"
    FULL = "full"
    CANCELED = "canceled"


class Event(BaseModel):
    """Domain entity representing an event."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    description: str | None = None
    start_date: datetime
    end_date: datetime
    capacity: int
    status: Status = Status.UPCOMING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def _validate_dates(self) -> "Event":
        """Validate that end_date is strictly after start_date."""
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        return self

    @model_validator(mode="after")
    def _validate_capacity(self) -> "Event":
        """Validate that capacity is a positive integer."""
        if self.capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        return self

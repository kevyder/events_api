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


class Session(BaseModel):
    """Domain entity representing a session within an event."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_id: uuid.UUID
    title: str
    speaker: str
    start_time: datetime
    end_time: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def _validate_time_range(self) -> "Session":
        """Validate that end_time is strictly after start_time."""
        if self.end_time <= self.start_time:
            raise ValueError("Session end time must be after start time")
        return self

    @model_validator(mode="after")
    def _validate_required_strings(self) -> "Session":
        """Validate that title and speaker are not blank."""
        if not self.title.strip():
            raise ValueError("Session title is required")
        if not self.speaker.strip():
            raise ValueError("Session speaker is required")
        return self


class Event(BaseModel):
    """Domain entity representing an event."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    description: str | None = None
    start_date: datetime
    end_date: datetime
    capacity: int
    status: Status = Status.UPCOMING
    sessions: list[Session] = Field(default_factory=list)
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

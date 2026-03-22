from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class Status(StrEnum):
    """Event status for filtering and display."""

    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    PAST = "past"
    FULL = "full"
    CANCELED = "canceled"


class Event(BaseModel):
    """Domain entity representing an event."""

    name: str
    description: str
    start_date: datetime
    end_date: datetime
    capacity: int
    status: Status = Status.UPCOMING
    id: str = Field(default_factory=lambda: str(uuid4()))

    def validate_date(self):
        """Validate if date is in the future for upcoming events."""
        if self.status == Status.UPCOMING and self.start_date <= datetime.now():
            raise ValueError("Upcoming events must have a future start date.")

    def validate_dates(self):
        """Validate that end date is after start date."""
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date.")

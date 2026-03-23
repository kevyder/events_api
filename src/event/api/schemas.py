import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.event.domain.models import Status


class EventCreateRequest(BaseModel):
    """Request body for creating an event."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    start_date: datetime
    end_date: datetime
    capacity: int = Field(..., gt=0)


class EventUpdateRequest(BaseModel):
    """Request body for partially updating an event (PATCH)."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    capacity: int | None = Field(default=None, gt=0)
    status: Status | None = None


class SessionCreateRequest(BaseModel):
    """Request body for creating a session."""

    title: str = Field(..., min_length=1, max_length=255)
    speaker: str = Field(..., min_length=1, max_length=255)
    start_time: datetime
    end_time: datetime


class SessionUpdateRequest(BaseModel):
    """Request body for partially updating a session."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    speaker: str | None = Field(default=None, min_length=1, max_length=255)
    start_time: datetime | None = None
    end_time: datetime | None = None


class SessionResponse(BaseModel):
    """Response body representing a session."""

    id: uuid.UUID
    event_id: uuid.UUID
    title: str
    speaker: str
    start_time: datetime
    end_time: datetime
    created_at: datetime
    updated_at: datetime


class EventResponse(BaseModel):
    """Response body representing an event."""

    id: uuid.UUID
    name: str
    description: str | None
    start_date: datetime
    end_date: datetime
    capacity: int
    status: str
    created_at: datetime
    updated_at: datetime


class EventDetailResponse(EventResponse):
    """Response body representing an event with its sessions."""

    sessions: list[SessionResponse]

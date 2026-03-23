import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class SessionModel(SQLModel, table=True):
    """SQLModel ORM model for event sessions."""

    __tablename__ = "sessions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: uuid.UUID = Field(foreign_key="events.id")
    title: str = Field(max_length=255)
    speaker: str = Field(max_length=255)
    start_time: datetime = Field()
    end_time: datetime = Field()
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

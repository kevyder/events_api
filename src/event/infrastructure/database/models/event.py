import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class EventModel(SQLModel, table=True):
    """SQLModel ORM model for events."""

    __tablename__ = "events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)
    start_date: datetime = Field()
    end_date: datetime = Field()
    capacity: int = Field()
    status: str = Field(default="upcoming", max_length=20)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class EventParticipantModel(SQLModel, table=True):
    """SQLModel ORM model for event participants (join table)."""

    __tablename__ = "event_participants"

    event_id: uuid.UUID = Field(foreign_key="events.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

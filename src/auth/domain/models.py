import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


class Role(StrEnum):
    """User roles for authorization."""

    ADMIN = "admin"
    USER = "user"


class User(BaseModel):
    """Domain entity representing a user."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: EmailStr
    hashed_password: str
    role: Role = Role.USER
    created_at: datetime = Field(default_factory=datetime.now)

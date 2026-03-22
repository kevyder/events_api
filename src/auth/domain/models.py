import uuid
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


class Role(StrEnum):
    """User roles for authorization."""

    ADMIN = "admin"
    USER = "user"


class User(BaseModel):
    """Domain entity representing a user."""

    email: EmailStr
    hashed_password: str
    role: Role = Role.USER
    id: uuid.UUID = Field(default_factory=uuid.uuid4)

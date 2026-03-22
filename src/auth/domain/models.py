from enum import StrEnum
from uuid import uuid4

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
    id: str = Field(default_factory=lambda: str(uuid4()))

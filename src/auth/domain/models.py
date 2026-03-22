from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class Role(StrEnum):
    """User roles for authorization."""

    ADMIN = "admin"
    USER = "user"


@dataclass
class User:
    """Domain entity representing a user."""

    email: str
    hashed_password: str
    role: Role = Role.USER
    id: str = field(default_factory=lambda: str(uuid4()))

from abc import ABC, abstractmethod

from src.auth.domain.models import User


class UserRepository(ABC):
    """Port for user persistence operations."""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by email. Returns None if not found."""

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        """Retrieve a user by ID. Returns None if not found."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Persist a new user and return it."""

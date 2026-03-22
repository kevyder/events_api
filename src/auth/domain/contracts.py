from abc import ABC, abstractmethod

from src.auth.domain.models import User


class PasswordHasher(ABC):
    """Contract for password hashing operations."""

    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash a plain-text password."""

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """Verify a plain-text password against a hash."""


class TokenService(ABC):
    """Contract for JWT token operations."""

    @abstractmethod
    def create_access_token(self, user: User) -> str:
        """Create an access token for the given user."""

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        """Decode and validate a token. Returns the payload dict."""

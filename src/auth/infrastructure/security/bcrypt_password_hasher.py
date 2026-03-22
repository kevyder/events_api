import bcrypt

from src.auth.domain.contracts import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    """Bcrypt implementation of the PasswordHasher contract."""

    def hash(self, password: str) -> str:
        """Hash a plain-text password using bcrypt."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a plain-text password against a bcrypt hash."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

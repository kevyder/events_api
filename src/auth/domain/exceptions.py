class DomainException(Exception):
    """Base exception for all domain errors."""


class AuthenticationError(DomainException):
    """Raised when authentication fails (bad credentials, invalid token)."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message)


class UserAlreadyExistsError(DomainException):
    """Raised when attempting to register an email that already exists."""

    def __init__(self, email: str):
        super().__init__(f"User '{email}' already exists")


class AuthorizationError(DomainException):
    """Raised when the user does not have the required role."""

    def __init__(self, required_role: str):
        super().__init__(f"Role '{required_role}' is required")

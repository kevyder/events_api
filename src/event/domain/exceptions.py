class EventDomainException(Exception):
    """Base exception for event domain errors."""


class EventNotFoundError(EventDomainException):
    """Raised when an event cannot be found."""

    def __init__(self, event_id: str):
        super().__init__(f"Event '{event_id}' not found")


class InvalidEventError(EventDomainException):
    """Raised when event data fails domain validation."""

    def __init__(self, message: str):
        super().__init__(message)


class SessionNotFoundError(EventDomainException):
    """Raised when a session cannot be found."""

    def __init__(self, session_id: str):
        super().__init__(f"Session '{session_id}' not found")


class InvalidSessionError(EventDomainException):
    """Raised when session data fails domain validation."""

    def __init__(self, message: str):
        super().__init__(message)


class EventFullError(EventDomainException):
    """Raised when a user tries to participate in a full event."""

    def __init__(self, event_id: str):
        super().__init__(f"Event '{event_id}' is full")


class EventNotUpcomingError(EventDomainException):
    """Raised when a user tries to participate in an event that is not upcoming."""

    def __init__(self, event_id: str):
        super().__init__(f"Event '{event_id}' is not accepting participants")


class AlreadyParticipatingError(EventDomainException):
    """Raised when a user tries to join an event they already participate in."""

    def __init__(self, event_id: str):
        super().__init__(f"Already participating in event '{event_id}'")

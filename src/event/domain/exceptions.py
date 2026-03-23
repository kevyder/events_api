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

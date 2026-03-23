import uuid
from abc import ABC, abstractmethod
from typing import Any

from src.event.domain.models import Event, Session


class EventRepository(ABC):
    """Port for event persistence operations."""

    @abstractmethod
    async def list_all(self) -> Any:
        """Retrieve all events with pagination.

        Returns a paginated result whose concrete type is determined by the adapter.
        """

    @abstractmethod
    async def search_by_name(self, name: str) -> Any:
        """Search events by name with pagination.

        Returns a paginated result whose concrete type is determined by the adapter.
        """

    @abstractmethod
    async def get_by_id(self, event_id: uuid.UUID) -> Event | None:
        """Retrieve an event by ID. Returns None if not found."""

    @abstractmethod
    async def get_by_id_with_sessions(self, event_id: uuid.UUID) -> Event | None:
        """Retrieve an event by ID with its sessions eagerly loaded.

        Returns an Event with its sessions list populated (sorted by start_time asc),
        or None if the event does not exist.  Implementations should fetch the event
        and its sessions in a single query when possible.
        """

    @abstractmethod
    async def list_sessions_by_event(self, event_id: uuid.UUID) -> list[Session]:
        """Retrieve all sessions for an event ordered by start time."""

    @abstractmethod
    async def get_session_by_id(self, event_id: uuid.UUID, session_id: uuid.UUID) -> Session | None:
        """Retrieve a session by event ID and session ID."""

    @abstractmethod
    async def create_session(self, session: Session) -> Session:
        """Persist a new session and return it."""

    @abstractmethod
    async def update_session(self, session: Session) -> Session:
        """Update an existing session and return it."""

    @abstractmethod
    async def delete_session(self, event_id: uuid.UUID, session_id: uuid.UUID) -> None:
        """Delete a session by event ID and session ID."""

    @abstractmethod
    async def create(self, event: Event) -> Event:
        """Persist a new event and return it."""

    @abstractmethod
    async def update(self, event: Event) -> Event:
        """Update an existing event and return it."""

    @abstractmethod
    async def delete(self, event_id: uuid.UUID) -> None:
        """Delete an event by ID."""

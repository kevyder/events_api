import uuid
from abc import ABC, abstractmethod
from typing import Any

from src.event.domain.models import Event


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
    async def create(self, event: Event) -> Event:
        """Persist a new event and return it."""

    @abstractmethod
    async def update(self, event: Event) -> Event:
        """Update an existing event and return it."""

    @abstractmethod
    async def delete(self, event_id: uuid.UUID) -> None:
        """Delete an event by ID."""

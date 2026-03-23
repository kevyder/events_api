import uuid

from src.event.domain.exceptions import EventNotFoundError
from src.event.domain.models import Event
from src.event.domain.repositories import EventRepository


class GetEvent:
    """Use case for retrieving a single event by ID."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(self, event_id: uuid.UUID) -> Event:
        """Return the event or raise EventNotFoundError."""
        event = await self._event_repository.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError(str(event_id))
        return event

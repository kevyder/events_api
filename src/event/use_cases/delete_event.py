import uuid

from src.event.domain.exceptions import EventNotFoundError
from src.event.domain.repositories import EventRepository


class DeleteEvent:
    """Use case for deleting an event."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(self, event_id: uuid.UUID) -> None:
        """Delete the event or raise EventNotFoundError if it does not exist."""
        existing = await self._event_repository.get_by_id(event_id)
        if existing is None:
            raise EventNotFoundError(str(event_id))
        await self._event_repository.delete(event_id)

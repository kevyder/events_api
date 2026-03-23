import uuid

from src.event.domain.exceptions import EventNotFoundError, SessionNotFoundError
from src.event.domain.repositories import EventRepository


class DeleteSession:
    """Use case for deleting a session from an event."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(self, event_id: uuid.UUID, session_id: uuid.UUID) -> None:
        """Delete a session if both event and session exist."""
        event = await self._event_repository.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError(str(event_id))

        session = await self._event_repository.get_session_by_id(event_id, session_id)
        if session is None:
            raise SessionNotFoundError(str(session_id))

        await self._event_repository.delete_session(event_id, session_id)

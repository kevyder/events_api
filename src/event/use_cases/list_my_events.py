import uuid
from typing import Any

from src.event.domain.repositories import EventRepository


class ListMyEvents:
    """Use case for retrieving paginated events the current user is participating in."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(self, user_id: uuid.UUID) -> Any:
        """Return paginated events the user has joined."""
        return await self._event_repository.list_participating_events(user_id)

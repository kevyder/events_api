from typing import Any

from src.event.domain.repositories import EventRepository


class ListEvents:
    """Use case for retrieving paginated events."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(self) -> Any:
        """Return paginated events."""
        return await self._event_repository.list_all()

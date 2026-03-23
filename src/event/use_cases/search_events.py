from typing import Any

from src.event.domain.repositories import EventRepository


class SearchEvents:
    """Use case for searching paginated events by name."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(self, name: str) -> Any:
        """Return paginated events matching the provided name."""
        return await self._event_repository.search_by_name(name)

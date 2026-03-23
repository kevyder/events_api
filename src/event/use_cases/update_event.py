import uuid
from datetime import datetime
from typing import Any

from src.event.domain.exceptions import EventNotFoundError, InvalidEventError
from src.event.domain.models import Event, Status
from src.event.domain.repositories import EventRepository

_UNSET: Any = object()


class UpdateEvent:
    """Use case for partially updating an existing event (PATCH semantics)."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(
        self,
        event_id: uuid.UUID,
        name: str | None = None,
        description: str | None = _UNSET,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        capacity: int | None = None,
        status: Status | None = None,
    ) -> Event:
        """Merge provided fields into the existing event and persist."""
        existing = await self._event_repository.get_by_id(event_id)
        if existing is None:
            raise EventNotFoundError(str(event_id))

        try:
            updated = Event(
                id=existing.id,
                name=name if name is not None else existing.name,
                description=description if description is not _UNSET else existing.description,
                start_date=start_date if start_date is not None else existing.start_date,
                end_date=end_date if end_date is not None else existing.end_date,
                capacity=capacity if capacity is not None else existing.capacity,
                status=status if status is not None else existing.status,
                created_at=existing.created_at,
            )
        except ValueError as err:
            raise InvalidEventError(str(err)) from err

        return await self._event_repository.update(updated)

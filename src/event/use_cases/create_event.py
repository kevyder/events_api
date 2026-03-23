from datetime import datetime

from src.event.domain.exceptions import InvalidEventError
from src.event.domain.models import Event, Status
from src.event.domain.repositories import EventRepository


class CreateEvent:
    """Use case for creating a new event."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(
        self,
        name: str,
        description: str | None,
        start_date: datetime,
        end_date: datetime,
        capacity: int,
        status: Status = Status.UPCOMING,
    ) -> Event:
        """Create and persist a new event."""
        try:
            event = Event(
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                capacity=capacity,
                status=status,
            )
        except ValueError as err:
            raise InvalidEventError(str(err)) from err

        return await self._event_repository.create(event)

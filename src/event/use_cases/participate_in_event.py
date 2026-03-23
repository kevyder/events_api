import uuid

from src.event.domain.exceptions import (
    AlreadyParticipatingError,
    EventFullError,
    EventNotFoundError,
    EventNotUpcomingError,
)
from src.event.domain.models import Event, Status
from src.event.domain.repositories import EventRepository


class ParticipateInEvent:
    """Use case for a regular user joining an event."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(self, event_id: uuid.UUID, user_id: uuid.UUID) -> Event:
        """Register the user as a participant and sync event status."""
        event = await self._event_repository.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError(str(event_id))

        if event.status != Status.UPCOMING:
            raise EventNotUpcomingError(str(event_id))

        if await self._event_repository.is_participant(event_id, user_id):
            raise AlreadyParticipatingError(str(event_id))

        participant_count = await self._event_repository.count_participants(event_id)
        if participant_count >= event.capacity:
            raise EventFullError(str(event_id))

        await self._event_repository.add_participant(event_id, user_id)

        # Sync status: if we just filled the last spot, mark event as full
        if participant_count + 1 >= event.capacity:
            event.status = Status.FULL
            await self._event_repository.update(event)

        return event

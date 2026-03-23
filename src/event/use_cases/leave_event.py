import uuid

from src.event.domain.exceptions import EventNotFoundError
from src.event.domain.models import Event, Status
from src.event.domain.repositories import EventRepository


class LeaveEvent:
    """Use case for a user leaving an event they previously joined."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(self, event_id: uuid.UUID, user_id: uuid.UUID) -> Event:
        """Remove the user from participants and sync event status."""
        event = await self._event_repository.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError(str(event_id))

        await self._event_repository.remove_participant(event_id, user_id)

        # Sync status: if event was full and now has room, set back to upcoming
        if event.status == Status.FULL:
            participant_count = await self._event_repository.count_participants(event_id)
            if participant_count < event.capacity:
                event.status = Status.UPCOMING
                await self._event_repository.update(event)

        return event

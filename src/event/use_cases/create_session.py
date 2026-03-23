import uuid
from datetime import UTC, datetime

from src.event.domain.exceptions import EventNotFoundError, InvalidSessionError
from src.event.domain.models import Session
from src.event.domain.repositories import EventRepository


class CreateSession:
    """Use case for creating a session within an event."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(
        self,
        event_id: uuid.UUID,
        title: str,
        speaker: str,
        start_time: datetime,
        end_time: datetime,
    ) -> Session:
        """Create and persist a new session within the event range."""
        event = await self._event_repository.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError(str(event_id))

        try:
            session = Session(
                event_id=event_id,
                title=title,
                speaker=speaker,
                start_time=start_time,
                end_time=end_time,
            )
        except ValueError as err:
            raise InvalidSessionError(str(err)) from err

        self._ensure_within_event_window(session, event.start_date, event.end_date)
        existing_sessions = await self._event_repository.list_sessions_by_event(event_id)
        self._ensure_no_overlap(session, existing_sessions)
        return await self._event_repository.create_session(session)

    @staticmethod
    def _ensure_within_event_window(session: Session, event_start: datetime, event_end: datetime) -> None:
        """Ensure the session fits within the event date range."""
        normalized_start_time = CreateSession._normalize_datetime(session.start_time)
        normalized_end_time = CreateSession._normalize_datetime(session.end_time)
        normalized_event_start = CreateSession._normalize_datetime(event_start)
        normalized_event_end = CreateSession._normalize_datetime(event_end)

        if normalized_start_time < normalized_event_start or normalized_end_time > normalized_event_end:
            raise InvalidSessionError("Session schedule must be within the event start and end date")

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        """Normalize datetimes to UTC for safe comparison."""
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @staticmethod
    def _ensure_no_overlap(session: Session, existing_sessions: list[Session]) -> None:
        """Ensure the session does not overlap another session in the same event."""
        normalized_start_time = CreateSession._normalize_datetime(session.start_time)
        normalized_end_time = CreateSession._normalize_datetime(session.end_time)

        for existing_session in existing_sessions:
            existing_start = CreateSession._normalize_datetime(existing_session.start_time)
            existing_end = CreateSession._normalize_datetime(existing_session.end_time)
            if normalized_start_time < existing_end and normalized_end_time > existing_start:
                raise InvalidSessionError("Session schedule must not overlap with another session")

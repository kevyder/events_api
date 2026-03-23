import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.event.domain.exceptions import EventNotFoundError, InvalidSessionError
from src.event.domain.models import Event, Session, Status
from src.event.domain.repositories import EventRepository
from src.event.use_cases.create_session import CreateSession


def _make_event(**overrides) -> Event:
    now = datetime.now()
    defaults = {
        "id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        "name": "Test Event",
        "start_date": now + timedelta(days=1),
        "end_date": now + timedelta(days=2),
        "capacity": 100,
        "status": Status.UPCOMING,
        "created_at": now,
        "updated_at": now,
        "sessions": [],
    }
    defaults.update(overrides)
    return Event.model_construct(**defaults)


async def test_create_session_success():
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    repo.get_by_id.return_value = event
    repo.list_sessions_by_event.return_value = []
    repo.create_session.side_effect = lambda session: session
    use_case = CreateSession(repo)

    result = await use_case.execute(
        event_id=event.id,
        title="Opening Keynote",
        speaker="Jane Doe",
        start_time=event.start_date + timedelta(hours=1),
        end_time=event.start_date + timedelta(hours=2),
    )

    assert result.title == "Opening Keynote"
    assert result.speaker == "Jane Doe"
    repo.create_session.assert_awaited_once()


async def test_create_session_event_not_found():
    repo = AsyncMock(spec=EventRepository)
    repo.get_by_id.return_value = None
    use_case = CreateSession(repo)

    with pytest.raises(EventNotFoundError):
        await use_case.execute(
            event_id=uuid.uuid4(),
            title="Opening Keynote",
            speaker="Jane Doe",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
        )


async def test_create_session_outside_event_window():
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    repo.get_by_id.return_value = event
    repo.list_sessions_by_event.return_value = []
    use_case = CreateSession(repo)

    with pytest.raises(InvalidSessionError, match="Session schedule must be within the event start and end date"):
        await use_case.execute(
            event_id=event.id,
            title="Opening Keynote",
            speaker="Jane Doe",
            start_time=event.start_date - timedelta(minutes=1),
            end_time=event.start_date + timedelta(hours=1),
        )


async def test_create_session_invalid_time_range():
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    repo.get_by_id.return_value = event
    repo.list_sessions_by_event.return_value = []
    use_case = CreateSession(repo)

    with pytest.raises(InvalidSessionError, match="Session end time must be after start time"):
        await use_case.execute(
            event_id=event.id,
            title="Opening Keynote",
            speaker="Jane Doe",
            start_time=event.start_date + timedelta(hours=2),
            end_time=event.start_date + timedelta(hours=1),
        )


async def test_create_session_accepts_utc_aware_datetimes_when_event_dates_are_naive():
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    repo.get_by_id.return_value = event
    repo.list_sessions_by_event.return_value = []
    repo.create_session.side_effect = lambda session: session
    use_case = CreateSession(repo)

    result = await use_case.execute(
        event_id=event.id,
        title="Opening Keynote",
        speaker="Jane Doe",
        start_time=event.start_date.replace(tzinfo=UTC) + timedelta(hours=1),
        end_time=event.start_date.replace(tzinfo=UTC) + timedelta(hours=2),
    )

    assert result.title == "Opening Keynote"
    repo.create_session.assert_awaited_once()


async def test_create_session_rejects_overlapping_schedule():
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    repo.get_by_id.return_value = event
    repo.list_sessions_by_event.return_value = [
        Session.model_construct(
            id=uuid.uuid4(),
            event_id=event.id,
            title="Existing Session",
            speaker="Jane Doe",
            start_time=event.start_date + timedelta(hours=1),
            end_time=event.start_date + timedelta(hours=2),
        )
    ]
    use_case = CreateSession(repo)

    with pytest.raises(InvalidSessionError, match="Session schedule must not overlap with another session"):
        await use_case.execute(
            event_id=event.id,
            title="Opening Keynote",
            speaker="Jane Doe",
            start_time=event.start_date + timedelta(hours=1, minutes=30),
            end_time=event.start_date + timedelta(hours=2, minutes=30),
        )

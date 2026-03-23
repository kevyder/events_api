import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.event.domain.exceptions import EventNotFoundError, InvalidSessionError, SessionNotFoundError
from src.event.domain.models import Event, Session, Status
from src.event.domain.repositories import EventRepository
from src.event.use_cases.update_session import UpdateSession


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


def _make_session(event_id: uuid.UUID, **overrides) -> Session:
    now = datetime.now()
    defaults = {
        "id": uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        "event_id": event_id,
        "title": "Opening Keynote",
        "speaker": "Jane Doe",
        "start_time": now + timedelta(days=1, hours=1),
        "end_time": now + timedelta(days=1, hours=2),
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return Session.model_construct(**defaults)


async def test_update_session_success():
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    session = _make_session(event.id)
    repo.get_by_id.return_value = event
    repo.get_session_by_id.return_value = session
    repo.list_sessions_by_event.return_value = [session]
    repo.update_session.side_effect = lambda updated: updated
    use_case = UpdateSession(repo)

    result = await use_case.execute(event.id, session.id, title="Updated Title")

    assert result.title == "Updated Title"
    assert result.speaker == "Jane Doe"


async def test_update_session_event_not_found():
    repo = AsyncMock(spec=EventRepository)
    repo.get_by_id.return_value = None
    use_case = UpdateSession(repo)

    with pytest.raises(EventNotFoundError):
        await use_case.execute(uuid.uuid4(), uuid.uuid4(), title="Updated")


async def test_update_session_not_found():
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    repo.get_by_id.return_value = event
    repo.get_session_by_id.return_value = None
    use_case = UpdateSession(repo)

    with pytest.raises(SessionNotFoundError):
        await use_case.execute(event.id, uuid.uuid4(), title="Updated")


async def test_update_session_outside_event_window():
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    session = _make_session(event.id)
    repo.get_by_id.return_value = event
    repo.get_session_by_id.return_value = session
    repo.list_sessions_by_event.return_value = [session]
    use_case = UpdateSession(repo)

    with pytest.raises(InvalidSessionError, match="Session schedule must be within the event start and end date"):
        await use_case.execute(event.id, session.id, start_time=event.start_date - timedelta(minutes=1))


async def test_update_session_rejects_overlapping_schedule():
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    session = _make_session(
        event.id,
        start_time=event.start_date + timedelta(hours=1),
        end_time=event.start_date + timedelta(hours=2),
    )
    other_session = _make_session(
        event.id,
        id=uuid.uuid4(),
        start_time=event.start_date + timedelta(hours=3),
        end_time=event.start_date + timedelta(hours=4),
    )
    repo.get_by_id.return_value = event
    repo.get_session_by_id.return_value = session
    repo.list_sessions_by_event.return_value = [session, other_session]
    use_case = UpdateSession(repo)

    with pytest.raises(InvalidSessionError, match="Session schedule must not overlap with another session"):
        await use_case.execute(
            event.id,
            session.id,
            start_time=event.start_date + timedelta(hours=3, minutes=30),
            end_time=event.start_date + timedelta(hours=4, minutes=30),
        )

import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.event.domain.exceptions import EventNotFoundError
from src.event.domain.models import Event, Status
from src.event.domain.repositories import EventRepository
from src.event.use_cases.leave_event import LeaveEvent


def _make_event(**overrides) -> Event:
    now = datetime.now()
    defaults = {
        "id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        "name": "Test Event",
        "start_date": now + timedelta(days=1),
        "end_date": now + timedelta(days=2),
        "capacity": 2,
        "status": Status.UPCOMING,
        "created_at": now,
        "updated_at": now,
        "sessions": [],
    }
    defaults.update(overrides)
    return Event.model_construct(**defaults)


async def test_leave_event_success():
    """Test a user can leave an event."""
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    repo.get_by_id.return_value = event
    use_case = LeaveEvent(repo)

    user_id = uuid.uuid4()
    result = await use_case.execute(event.id, user_id)

    assert result.id == event.id
    repo.remove_participant.assert_awaited_once_with(event.id, user_id)


async def test_leave_event_restores_upcoming_from_full():
    """Test that leaving a full event restores status to upcoming."""
    repo = AsyncMock(spec=EventRepository)
    event = _make_event(status=Status.FULL, capacity=2)
    repo.get_by_id.return_value = event
    repo.count_participants.return_value = 1
    repo.update.side_effect = lambda e: e
    use_case = LeaveEvent(repo)

    user_id = uuid.uuid4()
    result = await use_case.execute(event.id, user_id)

    assert result.status == Status.UPCOMING
    repo.update.assert_awaited_once()


async def test_leave_event_keeps_full_when_still_at_capacity():
    """Test that leaving when event is still full does not change status."""
    repo = AsyncMock(spec=EventRepository)
    event = _make_event(status=Status.FULL, capacity=2)
    repo.get_by_id.return_value = event
    repo.count_participants.return_value = 2
    use_case = LeaveEvent(repo)

    user_id = uuid.uuid4()
    result = await use_case.execute(event.id, user_id)

    assert result.status == Status.FULL
    repo.update.assert_not_awaited()


async def test_leave_event_not_found():
    """Test that a missing event raises EventNotFoundError."""
    repo = AsyncMock(spec=EventRepository)
    repo.get_by_id.return_value = None
    use_case = LeaveEvent(repo)

    with pytest.raises(EventNotFoundError):
        await use_case.execute(uuid.uuid4(), uuid.uuid4())

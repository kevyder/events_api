import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.event.domain.exceptions import (
    AlreadyParticipatingError,
    EventFullError,
    EventNotFoundError,
    EventNotUpcomingError,
)
from src.event.domain.models import Event, Status
from src.event.domain.repositories import EventRepository
from src.event.use_cases.participate_in_event import ParticipateInEvent


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


async def test_participate_success():
    """Test a user can join an upcoming event with available capacity."""
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    repo.get_by_id.return_value = event
    repo.is_participant.return_value = False
    repo.count_participants.return_value = 0
    use_case = ParticipateInEvent(repo)

    user_id = uuid.uuid4()
    result = await use_case.execute(event.id, user_id)

    assert result.id == event.id
    repo.add_participant.assert_awaited_once_with(event.id, user_id)
    repo.update.assert_not_awaited()


async def test_participate_fills_last_spot_sets_status_full():
    """Test status changes to full when the last spot is filled."""
    repo = AsyncMock(spec=EventRepository)
    event = _make_event(capacity=2)
    repo.get_by_id.return_value = event
    repo.is_participant.return_value = False
    repo.count_participants.return_value = 1
    repo.update.side_effect = lambda e: e
    use_case = ParticipateInEvent(repo)

    user_id = uuid.uuid4()
    result = await use_case.execute(event.id, user_id)

    assert result.status == Status.FULL
    repo.add_participant.assert_awaited_once()
    repo.update.assert_awaited_once()


async def test_participate_event_not_found():
    """Test that a missing event raises EventNotFoundError."""
    repo = AsyncMock(spec=EventRepository)
    repo.get_by_id.return_value = None
    use_case = ParticipateInEvent(repo)

    with pytest.raises(EventNotFoundError):
        await use_case.execute(uuid.uuid4(), uuid.uuid4())


async def test_participate_event_not_upcoming():
    """Test that participating in a non-upcoming event is rejected."""
    repo = AsyncMock(spec=EventRepository)
    event = _make_event(status=Status.ONGOING)
    repo.get_by_id.return_value = event
    use_case = ParticipateInEvent(repo)

    with pytest.raises(EventNotUpcomingError):
        await use_case.execute(event.id, uuid.uuid4())


async def test_participate_already_participating():
    """Test that a duplicate participation is rejected."""
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    repo.get_by_id.return_value = event
    repo.is_participant.return_value = True
    use_case = ParticipateInEvent(repo)

    with pytest.raises(AlreadyParticipatingError):
        await use_case.execute(event.id, uuid.uuid4())


async def test_participate_event_full():
    """Test that joining a full event is rejected."""
    repo = AsyncMock(spec=EventRepository)
    event = _make_event(capacity=2)
    repo.get_by_id.return_value = event
    repo.is_participant.return_value = False
    repo.count_participants.return_value = 2
    use_case = ParticipateInEvent(repo)

    with pytest.raises(EventFullError):
        await use_case.execute(event.id, uuid.uuid4())

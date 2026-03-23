import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.event.domain.exceptions import EventNotFoundError, InvalidEventError
from src.event.domain.models import Event, Session, Status
from src.event.domain.repositories import EventRepository
from src.event.use_cases.update_event import UpdateEvent


def _make_event(**overrides) -> Event:
    """Create a domain Event with sensible defaults."""
    now = datetime.now()
    defaults = {
        "id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        "name": "Original Event",
        "description": "Original description",
        "start_date": now + timedelta(days=1),
        "end_date": now + timedelta(days=2),
        "capacity": 100,
        "status": Status.UPCOMING,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return Event.model_construct(**defaults)


async def test_update_event_name_only():
    """Test updating just the name preserves other fields."""
    repo = AsyncMock(spec=EventRepository)
    existing = _make_event()
    repo.get_by_id.return_value = existing
    repo.list_sessions_by_event.return_value = []
    repo.update.side_effect = lambda event: event
    use_case = UpdateEvent(repo)

    result = await use_case.execute(event_id=existing.id, name="Updated Name")

    assert result.name == "Updated Name"
    assert result.description == "Original description"
    assert result.capacity == 100
    repo.update.assert_awaited_once()


async def test_update_event_clear_description():
    """Test that description can be explicitly set to None."""
    repo = AsyncMock(spec=EventRepository)
    existing = _make_event()
    repo.get_by_id.return_value = existing
    repo.list_sessions_by_event.return_value = []
    repo.update.side_effect = lambda event: event
    use_case = UpdateEvent(repo)

    result = await use_case.execute(event_id=existing.id, description=None)

    assert result.description is None


async def test_update_event_not_found():
    """Test updating a non-existent event raises EventNotFoundError."""
    repo = AsyncMock(spec=EventRepository)
    repo.get_by_id.return_value = None
    use_case = UpdateEvent(repo)

    with pytest.raises(EventNotFoundError):
        await use_case.execute(event_id=uuid.uuid4(), name="Updated")


async def test_update_event_invalid_capacity():
    """Test that updating with zero capacity raises InvalidEventError."""
    repo = AsyncMock(spec=EventRepository)
    existing = _make_event()
    repo.get_by_id.return_value = existing
    repo.list_sessions_by_event.return_value = []
    use_case = UpdateEvent(repo)

    with pytest.raises(InvalidEventError, match="Capacity must be a positive integer"):
        await use_case.execute(event_id=existing.id, capacity=0)

    repo.update.assert_not_awaited()


async def test_update_event_invalid_dates():
    """Test that updating dates to an invalid range raises InvalidEventError."""
    repo = AsyncMock(spec=EventRepository)
    existing = _make_event()
    repo.get_by_id.return_value = existing
    repo.list_sessions_by_event.return_value = []
    use_case = UpdateEvent(repo)

    with pytest.raises(InvalidEventError, match="End date must be after start date"):
        await use_case.execute(
            event_id=existing.id,
            start_date=existing.end_date + timedelta(days=1),
        )


async def test_update_event_rejects_dates_outside_existing_sessions():
    """Test that shrinking event dates around existing sessions raises InvalidEventError."""
    repo = AsyncMock(spec=EventRepository)
    existing = _make_event()
    repo.get_by_id.return_value = existing
    repo.list_sessions_by_event.return_value = [
        Session.model_construct(
            id=uuid.uuid4(),
            event_id=existing.id,
            title="Closing",
            speaker="Jane Doe",
            start_time=existing.end_date - timedelta(hours=2),
            end_time=existing.end_date - timedelta(hours=1),
        )
    ]
    use_case = UpdateEvent(repo)

    with pytest.raises(InvalidEventError, match="Event dates must include all existing sessions"):
        await use_case.execute(event_id=existing.id, end_date=existing.end_date - timedelta(hours=3))

    repo.update.assert_not_awaited()


async def test_update_event_capacity_decrease_sets_full():
    """Test that reducing capacity to current participants sets status to full."""
    repo = AsyncMock(spec=EventRepository)
    existing = _make_event(capacity=10, status=Status.UPCOMING)
    repo.get_by_id.return_value = existing
    repo.list_sessions_by_event.return_value = []
    repo.count_participants.return_value = 5
    repo.update.side_effect = lambda event: event
    use_case = UpdateEvent(repo)

    result = await use_case.execute(event_id=existing.id, capacity=5)

    assert result.status == Status.FULL
    repo.update.assert_awaited_once()


async def test_update_event_capacity_increase_restores_upcoming():
    """Test that increasing capacity on a full event restores upcoming status."""
    repo = AsyncMock(spec=EventRepository)
    existing = _make_event(capacity=5, status=Status.FULL)
    repo.get_by_id.return_value = existing
    repo.list_sessions_by_event.return_value = []
    repo.count_participants.return_value = 5
    repo.update.side_effect = lambda event: event
    use_case = UpdateEvent(repo)

    result = await use_case.execute(event_id=existing.id, capacity=10)

    assert result.status == Status.UPCOMING
    repo.update.assert_awaited_once()

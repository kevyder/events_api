import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.event.domain.exceptions import EventNotFoundError
from src.event.domain.models import Event
from src.event.domain.repositories import EventRepository
from src.event.use_cases.delete_event import DeleteEvent


def _make_event(**overrides) -> Event:
    """Create a domain Event with sensible defaults."""
    now = datetime.now()
    defaults = {
        "id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        "name": "Test Event",
        "start_date": now + timedelta(days=1),
        "end_date": now + timedelta(days=2),
        "capacity": 100,
    }
    defaults.update(overrides)
    return Event.model_construct(**defaults)


async def test_delete_event_success():
    """Test deleting an existing event."""
    repo = AsyncMock(spec=EventRepository)
    existing = _make_event()
    repo.get_by_id.return_value = existing
    use_case = DeleteEvent(repo)

    await use_case.execute(existing.id)

    repo.delete.assert_awaited_once_with(existing.id)


async def test_delete_event_not_found():
    """Test that deleting a non-existent event raises EventNotFoundError."""
    repo = AsyncMock(spec=EventRepository)
    repo.get_by_id.return_value = None
    use_case = DeleteEvent(repo)

    with pytest.raises(EventNotFoundError):
        await use_case.execute(uuid.uuid4())

    repo.delete.assert_not_awaited()

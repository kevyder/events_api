import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.event.domain.exceptions import EventNotFoundError
from src.event.domain.models import Event
from src.event.domain.repositories import EventRepository
from src.event.use_cases.get_event import GetEvent


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


async def test_get_event_success():
    """Test retrieving an existing event."""
    repo = AsyncMock(spec=EventRepository)
    event = _make_event()
    repo.get_by_id.return_value = event
    use_case = GetEvent(repo)

    result = await use_case.execute(event.id)

    assert result.name == "Test Event"
    repo.get_by_id.assert_awaited_once_with(event.id)


async def test_get_event_not_found():
    """Test that a missing event raises EventNotFoundError."""
    repo = AsyncMock(spec=EventRepository)
    repo.get_by_id.return_value = None
    use_case = GetEvent(repo)

    event_id = uuid.uuid4()
    with pytest.raises(EventNotFoundError):
        await use_case.execute(event_id)

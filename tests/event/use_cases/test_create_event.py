from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.event.domain.exceptions import InvalidEventError
from src.event.domain.models import Status
from src.event.domain.repositories import EventRepository
from src.event.use_cases.create_event import CreateEvent


async def test_create_event_success():
    """Test successful event creation."""
    repo = AsyncMock(spec=EventRepository)
    repo.create.side_effect = lambda event: event
    use_case = CreateEvent(repo)

    now = datetime.now()
    event = await use_case.execute(
        name="New Event",
        description="A description",
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=2),
        capacity=50,
    )

    assert event.name == "New Event"
    assert event.description == "A description"
    assert event.capacity == 50
    assert event.status == Status.UPCOMING
    repo.create.assert_awaited_once()


async def test_create_event_invalid_dates():
    """Test that invalid dates raise InvalidEventError."""
    repo = AsyncMock(spec=EventRepository)
    use_case = CreateEvent(repo)

    now = datetime.now()
    with pytest.raises(InvalidEventError, match="End date must be after start date"):
        await use_case.execute(
            name="Bad Event",
            description=None,
            start_date=now + timedelta(days=2),
            end_date=now + timedelta(days=1),
            capacity=10,
        )

    repo.create.assert_not_awaited()


async def test_create_event_zero_capacity():
    """Test that zero capacity raises InvalidEventError."""
    repo = AsyncMock(spec=EventRepository)
    use_case = CreateEvent(repo)

    now = datetime.now()
    with pytest.raises(InvalidEventError, match="Capacity must be a positive integer"):
        await use_case.execute(
            name="Zero Cap",
            description=None,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
            capacity=0,
        )


async def test_create_event_with_custom_status():
    """Test creating an event with a non-default status."""
    repo = AsyncMock(spec=EventRepository)
    repo.create.side_effect = lambda event: event
    use_case = CreateEvent(repo)

    now = datetime.now()
    event = await use_case.execute(
        name="Ongoing Event",
        description=None,
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=2),
        capacity=10,
        status=Status.ONGOING,
    )

    assert event.status == Status.ONGOING

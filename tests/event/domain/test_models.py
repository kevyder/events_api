import uuid
from datetime import datetime, timedelta

import pytest

from src.event.domain.models import Event, Session, Status


def test_event_creation_defaults():
    """Test that an event gets a UUID id and default status."""
    now = datetime.now()
    event = Event(
        name="Test Event",
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=2),
        capacity=100,
    )
    assert isinstance(event.id, uuid.UUID)
    assert event.status == Status.UPCOMING
    assert event.description is None
    assert event.capacity == 100


def test_event_with_all_fields():
    """Test creating an event with all fields provided."""
    now = datetime.now()
    event_id = uuid.uuid4()
    event = Event(
        id=event_id,
        name="Full Event",
        description="A full event",
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=2),
        capacity=50,
        status=Status.ONGOING,
    )
    assert event.id == event_id
    assert event.name == "Full Event"
    assert event.description == "A full event"
    assert event.status == Status.ONGOING


def test_event_invalid_dates():
    """Test that end_date must be after start_date."""
    now = datetime.now()
    with pytest.raises(ValueError, match="End date must be after start date"):
        Event(
            name="Bad Dates",
            start_date=now + timedelta(days=2),
            end_date=now + timedelta(days=1),
            capacity=10,
        )


def test_event_equal_dates():
    """Test that equal start_date and end_date is rejected."""
    now = datetime.now()
    same_time = now + timedelta(days=1)
    with pytest.raises(ValueError, match="End date must be after start date"):
        Event(
            name="Same Dates",
            start_date=same_time,
            end_date=same_time,
            capacity=10,
        )


def test_event_zero_capacity():
    """Test that capacity of zero is rejected."""
    now = datetime.now()
    with pytest.raises(ValueError, match="Capacity must be a positive integer"):
        Event(
            name="Zero Cap",
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
            capacity=0,
        )


def test_event_negative_capacity():
    """Test that negative capacity is rejected."""
    now = datetime.now()
    with pytest.raises(ValueError, match="Capacity must be a positive integer"):
        Event(
            name="Neg Cap",
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
            capacity=-5,
        )


def test_status_values():
    """Test that all Status enum values are accessible."""
    assert Status.UPCOMING == "upcoming"
    assert Status.ONGOING == "ongoing"
    assert Status.PAST == "past"
    assert Status.FULL == "full"
    assert Status.CANCELED == "canceled"


def test_session_creation_defaults():
    """Test that a session gets a UUID id."""
    now = datetime.now()
    session = Session(
        event_id=uuid.uuid4(),
        title="Opening Keynote",
        speaker="Jane Doe",
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, hours=1),
    )
    assert isinstance(session.id, uuid.UUID)
    assert session.title == "Opening Keynote"
    assert session.speaker == "Jane Doe"


def test_session_invalid_time_range():
    """Test that session end_time must be after start_time."""
    now = datetime.now()
    with pytest.raises(ValueError, match="Session end time must be after start time"):
        Session(
            event_id=uuid.uuid4(),
            title="Bad Session",
            speaker="Jane Doe",
            start_time=now + timedelta(days=1, hours=2),
            end_time=now + timedelta(days=1, hours=1),
        )


def test_session_blank_title():
    """Test that blank title is rejected."""
    now = datetime.now()
    with pytest.raises(ValueError, match="Session title is required"):
        Session(
            event_id=uuid.uuid4(),
            title="   ",
            speaker="Jane Doe",
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=1),
        )


def test_session_blank_speaker():
    """Test that blank speaker is rejected."""
    now = datetime.now()
    with pytest.raises(ValueError, match="Session speaker is required"):
        Session(
            event_id=uuid.uuid4(),
            title="Opening Keynote",
            speaker="   ",
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=1),
        )

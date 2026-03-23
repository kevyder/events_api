import uuid
from unittest.mock import AsyncMock

from src.event.domain.repositories import EventRepository
from src.event.use_cases.list_my_events import ListMyEvents


async def test_list_my_events_delegates_to_repository():
    """Test that execute() passes user_id to the repository and returns its result."""
    repo = AsyncMock(spec=EventRepository)
    sentinel = object()
    repo.list_participating_events.return_value = sentinel
    use_case = ListMyEvents(repo)
    user_id = uuid.uuid4()

    result = await use_case.execute(user_id)

    assert result is sentinel
    repo.list_participating_events.assert_awaited_once_with(user_id)

from unittest.mock import AsyncMock

from src.event.domain.repositories import EventRepository
from src.event.use_cases.list_events import ListEvents


async def test_list_events_delegates_to_repository():
    """Test that execute() returns whatever the repository returns."""
    repo = AsyncMock(spec=EventRepository)
    sentinel = object()
    repo.list_all.return_value = sentinel
    use_case = ListEvents(repo)

    result = await use_case.execute()

    assert result is sentinel
    repo.list_all.assert_awaited_once()

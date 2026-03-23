from unittest.mock import AsyncMock

from src.event.domain.repositories import EventRepository
from src.event.use_cases.search_events import SearchEvents


async def test_search_events_delegates_to_repository():
    """Test that execute() returns whatever the repository search returns."""
    repo = AsyncMock(spec=EventRepository)
    sentinel = object()
    repo.search_by_name.return_value = sentinel
    use_case = SearchEvents(repo)

    result = await use_case.execute("python")

    assert result is sentinel
    repo.search_by_name.assert_awaited_once_with("python")

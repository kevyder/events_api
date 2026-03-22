from unittest.mock import AsyncMock, Mock

import pytest

from src.auth.domain.contracts import TokenService
from src.auth.domain.exceptions import AuthenticationError
from src.auth.domain.models import User
from src.auth.domain.repositories import UserRepository
from src.auth.use_cases.get_current_user import GetCurrentUser


def _make_use_case() -> tuple[GetCurrentUser, AsyncMock, Mock]:
    """Create a GetCurrentUser use case with mocked dependencies."""
    repo = AsyncMock(spec=UserRepository)
    token_svc = Mock(spec=TokenService)
    return GetCurrentUser(repo, token_svc), repo, token_svc


async def test_get_current_user_success():
    """Test getting current user from a valid token."""
    use_case, repo, token_svc = _make_use_case()
    user = User(email="alice@example.com", hashed_password="hashed", id="user-id-1")
    token_svc.decode_token.return_value = {"sub": "user-id-1", "email": "alice@example.com", "role": "user"}
    repo.get_by_id.return_value = user

    result = await use_case.execute(token="valid-token")

    assert result.email == "alice@example.com"
    assert result.id == "user-id-1"
    token_svc.decode_token.assert_called_once_with("valid-token")
    repo.get_by_id.assert_awaited_once_with("user-id-1")


async def test_get_current_user_invalid_token():
    """Test that an invalid token raises AuthenticationError."""
    use_case, _repo, token_svc = _make_use_case()
    token_svc.decode_token.side_effect = AuthenticationError("Invalid token")

    with pytest.raises(AuthenticationError):
        await use_case.execute(token="invalid-token")


async def test_get_current_user_missing_sub():
    """Test that a token without 'sub' claim raises AuthenticationError."""
    use_case, _repo, token_svc = _make_use_case()
    token_svc.decode_token.return_value = {"email": "alice@example.com", "role": "user"}

    with pytest.raises(AuthenticationError, match="Invalid token payload"):
        await use_case.execute(token="token-without-sub")


async def test_get_current_user_user_not_found():
    """Test that a valid token for a deleted user raises AuthenticationError."""
    use_case, repo, token_svc = _make_use_case()
    token_svc.decode_token.return_value = {"sub": "deleted-id", "email": "ghost@example.com", "role": "user"}
    repo.get_by_id.return_value = None

    with pytest.raises(AuthenticationError, match="User not found"):
        await use_case.execute(token="token-for-deleted-user")

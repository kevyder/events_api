from unittest.mock import AsyncMock, Mock

import pytest

from src.auth.domain.contracts import PasswordHasher, TokenService
from src.auth.domain.exceptions import AuthenticationError
from src.auth.domain.models import User
from src.auth.domain.repositories import UserRepository
from src.auth.use_cases.login_user import LoginUser


def _make_use_case() -> tuple[LoginUser, AsyncMock, Mock, Mock]:
    """Create a LoginUser use case with mocked dependencies."""
    repo = AsyncMock(spec=UserRepository)
    hasher = Mock(spec=PasswordHasher)
    token_svc = Mock(spec=TokenService)
    return LoginUser(repo, hasher, token_svc), repo, hasher, token_svc


async def test_login_success():
    """Test successful login returns a token string."""
    use_case, repo, hasher, token_svc = _make_use_case()
    user = User(email="alice@example.com", hashed_password="hashed", id="user-id-1")
    repo.get_by_email.return_value = user
    hasher.verify.return_value = True
    token_svc.create_access_token.return_value = "jwt-token-string"

    result = await use_case.execute(email="alice@example.com", password="password123")

    assert result == "jwt-token-string"
    hasher.verify.assert_called_once_with("password123", "hashed")
    token_svc.create_access_token.assert_called_once_with(user)


async def test_login_wrong_password():
    """Test that login with wrong password raises AuthenticationError."""
    use_case, repo, hasher, _token_svc = _make_use_case()
    user = User(email="alice@example.com", hashed_password="hashed")
    repo.get_by_email.return_value = user
    hasher.verify.return_value = False

    with pytest.raises(AuthenticationError):
        await use_case.execute(email="alice@example.com", password="wrong_password")


async def test_login_nonexistent_user():
    """Test that login with unknown email raises AuthenticationError."""
    use_case, repo, _hasher, _token_svc = _make_use_case()
    repo.get_by_email.return_value = None

    with pytest.raises(AuthenticationError):
        await use_case.execute(email="nobody@example.com", password="password123")

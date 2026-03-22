from unittest.mock import AsyncMock, Mock

import pytest

from src.auth.domain.contracts import PasswordHasher
from src.auth.domain.exceptions import UserAlreadyExistsError
from src.auth.domain.models import Role, User
from src.auth.domain.repositories import UserRepository
from src.auth.use_cases.register_user import RegisterUser


def _make_use_case() -> tuple[RegisterUser, AsyncMock, Mock]:
    """Create a RegisterUser use case with mocked dependencies."""
    repo = AsyncMock(spec=UserRepository)
    hasher = Mock(spec=PasswordHasher)
    hasher.hash.return_value = "hashed_password"
    return RegisterUser(repo, hasher), repo, hasher


async def test_register_success():
    """Test successful user registration."""
    use_case, repo, hasher = _make_use_case()
    repo.get_by_email.return_value = None
    repo.create.side_effect = lambda user: user

    user = await use_case.execute(email="alice@example.com", password="password123")

    assert user.email == "alice@example.com"
    assert user.role == Role.USER
    assert user.hashed_password == "hashed_password"
    assert user.id is not None
    repo.get_by_email.assert_awaited_once_with("alice@example.com")
    repo.create.assert_awaited_once()
    hasher.hash.assert_called_once_with("password123")


async def test_register_duplicate_email():
    """Test that registering a duplicate email raises UserAlreadyExistsError."""
    use_case, repo, _hasher = _make_use_case()
    repo.get_by_email.return_value = User(email="alice@example.com", hashed_password="hashed")

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute(email="alice@example.com", password="password123")


async def test_register_admin():
    """Test registering a user with admin role."""
    use_case, repo, _hasher = _make_use_case()
    repo.get_by_email.return_value = None
    repo.create.side_effect = lambda user: user

    user = await use_case.execute(email="admin@example.com", password="password123", role=Role.ADMIN)

    assert user.role == Role.ADMIN

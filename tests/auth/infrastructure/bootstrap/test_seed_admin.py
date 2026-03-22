from unittest.mock import patch

from sqlalchemy import select

from src.auth.domain.models import Role, User
from src.auth.infrastructure.bootstrap.seed_admin import seed_admin
from src.auth.infrastructure.database.models.user import UserModel
from src.auth.infrastructure.database.repositories.user_repository import SQLAlchemyUserRepository
from src.auth.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher


async def test_seed_admin_creates_admin_when_missing(async_session):
    """Seed should create an admin user when the email does not exist."""
    with (
        patch("src.auth.infrastructure.bootstrap.seed_admin.settings") as mock_settings,
    ):
        mock_settings.DEFAULT_ADMIN_EMAIL = "admin@example.com"
        mock_settings.DEFAULT_ADMIN_PASSWORD = "supersecret"

        await seed_admin(async_session)

    result = await async_session.execute(select(UserModel).where(UserModel.email == "admin@example.com"))
    row = result.scalar_one_or_none()

    assert row is not None
    assert row.email == "admin@example.com"
    assert row.role == Role.ADMIN.value

    # Verify the password was hashed correctly
    hasher = BcryptPasswordHasher()
    assert hasher.verify("supersecret", row.hashed_password)


async def test_seed_admin_skips_when_admin_already_exists(async_session):
    """Seed should not overwrite or duplicate when the admin email already exists."""
    # Pre-create an admin user
    repo = SQLAlchemyUserRepository(async_session)
    hasher = BcryptPasswordHasher()
    existing_user = User(
        email="admin@example.com",
        hashed_password=hasher.hash("originalpassword"),
        role=Role.ADMIN,
    )
    await repo.create(existing_user)

    with (
        patch("src.auth.infrastructure.bootstrap.seed_admin.settings") as mock_settings,
    ):
        mock_settings.DEFAULT_ADMIN_EMAIL = "admin@example.com"
        mock_settings.DEFAULT_ADMIN_PASSWORD = "newpassword"

        await seed_admin(async_session)

    # Should still be exactly one user
    result = await async_session.execute(select(UserModel).where(UserModel.email == "admin@example.com"))
    rows = result.scalars().all()
    assert len(rows) == 1

    # Password should NOT have changed
    assert hasher.verify("originalpassword", rows[0].hashed_password)


async def test_seed_admin_skips_when_env_vars_unset(async_session):
    """Seed should do nothing when DEFAULT_ADMIN_EMAIL or PASSWORD are empty."""
    with (
        patch("src.auth.infrastructure.bootstrap.seed_admin.settings") as mock_settings,
    ):
        mock_settings.DEFAULT_ADMIN_EMAIL = ""
        mock_settings.DEFAULT_ADMIN_PASSWORD = ""

        await seed_admin(async_session)

    result = await async_session.execute(select(UserModel))
    rows = result.scalars().all()
    assert len(rows) == 0


async def test_seed_admin_skips_when_email_exists_as_regular_user(async_session):
    """Seed should not promote an existing regular user to admin."""
    repo = SQLAlchemyUserRepository(async_session)
    hasher = BcryptPasswordHasher()
    existing_user = User(
        email="admin@example.com",
        hashed_password=hasher.hash("userpassword"),
        role=Role.USER,
    )
    await repo.create(existing_user)

    with (
        patch("src.auth.infrastructure.bootstrap.seed_admin.settings") as mock_settings,
    ):
        mock_settings.DEFAULT_ADMIN_EMAIL = "admin@example.com"
        mock_settings.DEFAULT_ADMIN_PASSWORD = "adminpassword"

        await seed_admin(async_session)

    result = await async_session.execute(select(UserModel).where(UserModel.email == "admin@example.com"))
    row = result.scalar_one()

    # Role should remain USER — no promotion
    assert row.role == Role.USER.value
    # Password should remain original
    assert hasher.verify("userpassword", row.hashed_password)

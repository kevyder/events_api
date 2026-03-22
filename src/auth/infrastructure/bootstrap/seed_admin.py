import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.domain.models import Role, User
from src.auth.infrastructure.database.repositories.user_repository import SQLAlchemyUserRepository
from src.auth.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from src.config import settings

logger = logging.getLogger(__name__)


async def seed_admin(session: AsyncSession) -> None:
    """Create a default admin user if configured and not already present.

    Reads DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD from settings.
    Does nothing when either is empty. If the email already exists (any role),
    the user is left untouched — no promotion, no password overwrite.
    """
    email = settings.DEFAULT_ADMIN_EMAIL
    password = settings.DEFAULT_ADMIN_PASSWORD

    if not email or not password:
        logger.debug("DEFAULT_ADMIN_EMAIL/PASSWORD not set — skipping admin seed.")
        return

    repository = SQLAlchemyUserRepository(session)
    existing = await repository.get_by_email(email)

    if existing is not None:
        logger.info("Admin seed skipped — user %s already exists.", email)
        return

    hasher = BcryptPasswordHasher()
    user = User(email=email, hashed_password=hasher.hash(password), role=Role.ADMIN)
    await repository.create(user)
    logger.info("Default admin user created: %s", email)

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.domain.models import Role, User
from src.auth.domain.repositories import UserRepository
from src.auth.infrastructure.database.models.user import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """Async SQLAlchemy implementation of the UserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by email."""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_domain(row)

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Retrieve a user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_domain(row)

    async def create(self, user: User) -> User:
        """Persist a new user."""
        model = UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role.value,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        """Map a SQLAlchemy model to a domain entity."""
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            role=Role(model.role),
        )

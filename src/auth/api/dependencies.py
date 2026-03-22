from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.domain.exceptions import AuthorizationError
from src.auth.domain.models import User
from src.auth.infrastructure.database.repositories.user_repository import SQLAlchemyUserRepository
from src.auth.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from src.auth.infrastructure.security.jwt_token_service import JwtTokenService
from src.auth.use_cases.get_current_user import GetCurrentUser
from src.auth.use_cases.login_user import LoginUser
from src.auth.use_cases.register_user import RegisterUser
from src.database import get_async_session

security_scheme = HTTPBearer()

# Singletons for stateless services
_password_hasher = BcryptPasswordHasher()
_token_service = JwtTokenService()


def get_register_user(session: AsyncSession = Depends(get_async_session)) -> RegisterUser:
    """Inject a RegisterUser use case."""
    repository = SQLAlchemyUserRepository(session)
    return RegisterUser(repository, _password_hasher)


def get_login_user(session: AsyncSession = Depends(get_async_session)) -> LoginUser:
    """Inject a LoginUser use case."""
    repository = SQLAlchemyUserRepository(session)
    return LoginUser(repository, _password_hasher, _token_service)


def get_get_current_user(session: AsyncSession = Depends(get_async_session)) -> GetCurrentUser:
    """Inject a GetCurrentUser use case."""
    repository = SQLAlchemyUserRepository(session)
    return GetCurrentUser(repository, _token_service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    use_case: GetCurrentUser = Depends(get_get_current_user),
) -> User:
    """Extract and validate the JWT from the Authorization header."""
    return await use_case.execute(credentials.credentials)


def require_role(role: str) -> Callable:
    """Dependency factory that enforces a specific role."""

    async def _check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != role:
            raise AuthorizationError(role)
        return current_user

    return _check_role

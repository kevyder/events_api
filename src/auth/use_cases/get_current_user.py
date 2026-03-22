from src.auth.domain.contracts import TokenService
from src.auth.domain.exceptions import AuthenticationError
from src.auth.domain.models import User
from src.auth.domain.repositories import UserRepository


class GetCurrentUser:
    """Use case for validating a JWT token and returning the corresponding user."""

    def __init__(self, user_repository: UserRepository, token_service: TokenService) -> None:
        self._user_repository = user_repository
        self._token_service = token_service

    async def execute(self, token: str) -> User:
        """Validate the token and return the domain User entity."""
        payload = self._token_service.decode_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token payload")

        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise AuthenticationError("User not found")

        return user

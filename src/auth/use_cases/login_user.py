from src.auth.domain.contracts import PasswordHasher, TokenService
from src.auth.domain.exceptions import AuthenticationError
from src.auth.domain.repositories import UserRepository


class LoginUser:
    """Use case for authenticating a user and returning a JWT token."""

    def __init__(
        self, user_repository: UserRepository, password_hasher: PasswordHasher, token_service: TokenService
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_service = token_service

    async def execute(self, email: str, password: str) -> str:
        """Authenticate the user and return a raw JWT access token string."""
        user = await self._user_repository.get_by_email(email)
        if user is None or not self._password_hasher.verify(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        return self._token_service.create_access_token(user)

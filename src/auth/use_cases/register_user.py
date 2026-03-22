from src.auth.domain.contracts import PasswordHasher
from src.auth.domain.exceptions import UserAlreadyExistsError
from src.auth.domain.models import Role, User
from src.auth.domain.repositories import UserRepository


class RegisterUser:
    """Use case for registering a new user."""

    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(self, email: str, password: str, role: Role = Role.USER) -> User:
        """Register a new user and return the created domain entity."""
        existing = await self._user_repository.get_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsError(email)

        hashed_password = self._password_hasher.hash(password)
        user = User(email=email, hashed_password=hashed_password, role=role)
        return await self._user_repository.create(user)

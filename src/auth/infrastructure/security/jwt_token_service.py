from datetime import UTC, datetime, timedelta

import jwt

from src.auth.domain.contracts import TokenService
from src.auth.domain.exceptions import AuthenticationError
from src.auth.domain.models import User
from src.config import settings


class JwtTokenService(TokenService):
    """PyJWT implementation of the TokenService contract."""

    def create_access_token(self, user: User) -> str:
        """Create a JWT access token for the given user."""
        expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
        payload = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value,
            "exp": expire,
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_token(self, token: str) -> dict:
        """Decode and validate a JWT token."""
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError as err:
            raise AuthenticationError("Token has expired") from err
        except jwt.InvalidTokenError as err:
            raise AuthenticationError("Invalid token") from err

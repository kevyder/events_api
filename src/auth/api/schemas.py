import uuid

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Request body for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response body containing an access token."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response body representing a user."""

    id: uuid.UUID
    email: EmailStr
    role: str

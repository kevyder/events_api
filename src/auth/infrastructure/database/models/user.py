import uuid

from sqlmodel import Field, SQLModel


class UserModel(SQLModel, table=True):
    """SQLModel ORM model for users."""

    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=254)
    hashed_password: str = Field(max_length=255)
    role: str = Field(default="user", max_length=20)

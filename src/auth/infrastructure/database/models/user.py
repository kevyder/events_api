import sqlalchemy as sa

from src.database import Base


class UserModel(Base):
    """SQLAlchemy ORM model for users."""

    __tablename__ = "users"

    id = sa.Column(sa.String(36), primary_key=True)
    email = sa.Column(sa.String(254), unique=True, nullable=False, index=True)
    hashed_password = sa.Column(sa.String(255), nullable=False)
    role = sa.Column(sa.String(20), nullable=False, default="user")

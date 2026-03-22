"""Create user table

Revision ID: a04b8cda648e
Revises:
Create Date: 2026-03-22 14:07:02.288421

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel.sql.sqltypes

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a04b8cda648e"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=254), nullable=False),
        sa.Column("hashed_password", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("role", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

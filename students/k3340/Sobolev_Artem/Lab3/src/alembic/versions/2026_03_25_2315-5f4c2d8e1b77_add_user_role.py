"""add user role

Revision ID: 5f4c2d8e1b77
Revises: 3c1d7b2a9e11
Create Date: 2026-03-25 23:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5f4c2d8e1b77"
down_revision: Union[str, Sequence[str], None] = "3c1d7b2a9e11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=16),
            nullable=False,
            server_default="user",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "role")

"""split users and profiles

Revision ID: 8d1e5c4a2f90
Revises: 5f4c2d8e1b77
Create Date: 2026-04-06 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8d1e5c4a2f90"
down_revision: Union[str, Sequence[str], None] = "5f4c2d8e1b77"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("work_experience", sa.Text(), nullable=True),
        sa.Column("project_preferences", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_profiles_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_profiles")),
        sa.UniqueConstraint("user_id", name=op.f("uq_profiles_user_id")),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO profiles (
                user_id,
                full_name,
                bio,
                skills,
                work_experience,
                project_preferences,
                created_at,
                updated_at
            )
            SELECT
                id,
                full_name,
                bio,
                skills,
                work_experience,
                project_preferences,
                created_at,
                updated_at
            FROM users
            """
        )
    )

    op.drop_column("users", "project_preferences")
    op.drop_column("users", "work_experience")
    op.drop_column("users", "skills")
    op.drop_column("users", "bio")
    op.drop_column("users", "full_name")


def downgrade() -> None:
    op.add_column("users", sa.Column("full_name", sa.String(length=120), nullable=True))
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("skills", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("work_experience", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("project_preferences", sa.Text(), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE users
            SET
                full_name = profiles.full_name,
                bio = profiles.bio,
                skills = profiles.skills,
                work_experience = profiles.work_experience,
                project_preferences = profiles.project_preferences
            FROM profiles
            WHERE profiles.user_id = users.id
            """
        )
    )

    op.drop_table("profiles")

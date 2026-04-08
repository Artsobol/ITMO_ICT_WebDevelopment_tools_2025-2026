"""remove book slug and make genre optional

Revision ID: d4a6c8f1b2e3
Revises: 8d1e5c4a2f90
Create Date: 2026-04-06 19:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d4a6c8f1b2e3"
down_revision: Union[str, Sequence[str], None] = "8d1e5c4a2f90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(op.f("uq_books_slug"), "books", type_="unique")
    op.drop_column("books", "slug")
    op.alter_column("books", "genre_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.add_column("books", sa.Column("slug", sa.String(length=128), nullable=True))
    op.execute("UPDATE books SET slug = 'book-' || id WHERE slug IS NULL")
    op.alter_column("books", "slug", existing_type=sa.String(length=128), nullable=False)
    op.create_unique_constraint(op.f("uq_books_slug"), "books", ["slug"])

    op.execute(
        sa.text(
            """
            INSERT INTO genres (title, description, slug, version)
            VALUES ('Uncategorized', 'Fallback genre for migration downgrade', 'uncategorized', 1)
            ON CONFLICT (slug) DO NOTHING
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE books
            SET genre_id = (SELECT id FROM genres WHERE slug = 'uncategorized')
            WHERE genre_id IS NULL
            """
        )
    )
    op.alter_column("books", "genre_id", existing_type=sa.Integer(), nullable=False)

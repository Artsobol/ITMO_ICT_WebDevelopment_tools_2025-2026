"""create books and book_authors tables

Revision ID: 9f2a18b4aa01
Revises: 0d9e81e4b54c
Create Date: 2026-03-22 14:50:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9f2a18b4aa01"
down_revision: Union[str, Sequence[str], None] = "0d9e81e4b54c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "books",
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["genre_id"], ["genres.id"], name=op.f("fk_books_genre_id_genres")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_books")),
        sa.UniqueConstraint("slug", name=op.f("uq_books_slug")),
    )

    op.create_table(
        "book_authors",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["authors.id"],
            name=op.f("fk_book_authors_author_id_authors"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_book_authors_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("book_id", "author_id", name=op.f("pk_book_authors")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("book_authors")
    op.drop_table("books")

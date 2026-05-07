import re
from dataclasses import dataclass

import asyncpg
import requests
from bs4 import BeautifulSoup


@dataclass
class ParsedBook:
    title: str
    description: str | None
    genre: str


def make_slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9а-яё]+", "-", value)
    value = value.strip("-")

    if not value:
        value = "unknown"

    return value[:128]


def truncate(value: str, max_length: int) -> str:
    return value[:max_length]


def parse_book_page(html: str) -> ParsedBook:
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.select_one(".product_main h1")
    if title_tag is None:
        raise ValueError("Cannot find book title")

    title = title_tag.get_text(strip=True)

    breadcrumb_links = soup.select("ul.breadcrumb li a")
    if len(breadcrumb_links) >= 3:
        genre = breadcrumb_links[2].get_text(strip=True)
    else:
        genre = "Unknown"

    description = None
    description_header = soup.select_one("#product_description")
    if description_header is not None:
        description_tag = description_header.find_next_sibling("p")
        if description_tag is not None:
            description = description_tag.get_text(strip=True)

    return ParsedBook(
        title=truncate(title, 128),
        description=description,
        genre=truncate(genre, 64),
    )


def load_and_parse(url: str) -> ParsedBook:
    response = requests.get(
        url,
        headers={"User-Agent": "Lab3Parser/1.0"},
        timeout=15,
    )
    response.raise_for_status()

    return parse_book_page(response.text)


async def save_book(pool: asyncpg.Pool, book: ParsedBook) -> bool:
    async with pool.acquire() as connection:
        async with connection.transaction():
            genre_slug = make_slug(book.genre)

            genre_id = await connection.fetchval(
                """
                INSERT INTO genres (title, description, slug, version)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (slug)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    updated_at = now()
                RETURNING id
                """,
                book.genre,
                f"Parsed genre: {book.genre}",
                genre_slug,
                1,
            )

            existing_book_id = await connection.fetchval(
                """
                SELECT id
                FROM books
                WHERE title = $1 AND genre_id = $2
                LIMIT 1
                """,
                book.title,
                genre_id,
            )

            if existing_book_id is not None:
                return False

            await connection.execute(
                """
                INSERT INTO books (title, description, genre_id)
                VALUES ($1, $2, $3)
                """,
                book.title,
                book.description,
                genre_id,
            )

    return True

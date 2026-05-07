import asyncio
import time

import aiohttp
import asyncpg

from common import DB_URL, URLS, ParsedBook, parse_book_page, make_slug


async def load_and_parse_async(session: aiohttp.ClientSession, url: str) -> ParsedBook:
    async with session.get(url, timeout=15) as response:
        response.raise_for_status()
        html = await response.text()

    return parse_book_page(html)


async def save_book(pool: asyncpg.Pool, book: ParsedBook) -> None:
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

            if existing_book_id is None:
                await connection.execute(
                    """
                    INSERT INTO books (title, description, genre_id)
                    VALUES ($1, $2, $3)
                    """,
                    book.title,
                    book.description,
                    genre_id,
                )


async def parse_and_save(
    session: aiohttp.ClientSession,
    pool: asyncpg.Pool,
    url: str,
) -> None:
    try:
        book = await load_and_parse_async(session, url)
        await save_book(pool, book)

        print(f"Saved: {book.title} [{book.genre}]")
    except Exception as exception:
        print(f"Error while processing {url}: {exception}")


async def main_async() -> None:
    start_time = time.perf_counter()

    pool = await asyncpg.create_pool(
        dsn=DB_URL,
        min_size=1,
        max_size=4,
    )

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(parse_and_save(session, pool, url))
            for url in URLS
        ]

        await asyncio.gather(*tasks)

    await pool.close()

    end_time = time.perf_counter()

    print()
    print("Асинхронность")
    print(f"Задачи: {len(URLS)}")
    print(f"Ссылки: {len(URLS)}")
    print(f"Время: {end_time - start_time:.4f} секунд")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
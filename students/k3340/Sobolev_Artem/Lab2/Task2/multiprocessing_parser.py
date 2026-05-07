import multiprocessing
import time

import psycopg2

from common import DB_URL, URLS, ParsedBook, load_and_parse, make_slug


def save_book(book: ParsedBook) -> None:
    with psycopg2.connect(DB_URL) as connection:
        with connection.cursor() as cursor:
            genre_slug = make_slug(book.genre)

            cursor.execute(
                """
                INSERT INTO genres (title, description, slug, version)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (slug)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    updated_at = now()
                RETURNING id
                """,
                (book.genre, f"Parsed genre: {book.genre}", genre_slug, 1),
            )

            genre_id = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT id
                FROM books
                WHERE title = %s AND genre_id = %s
                LIMIT 1
                """,
                (book.title, genre_id),
            )

            existing_book = cursor.fetchone()

            if existing_book is None:
                cursor.execute(
                    """
                    INSERT INTO books (title, description, genre_id)
                    VALUES (%s, %s, %s)
                    """,
                    (book.title, book.description, genre_id),
                )


def parse_and_save(url: str) -> str:
    book = load_and_parse(url)
    save_book(book)

    return f"Saved: {book.title} [{book.genre}]"


def main() -> None:
    workers_count = 4

    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=workers_count) as pool:
        results = pool.map(parse_and_save, URLS)

    end_time = time.perf_counter()

    for result in results:
        print(result)

    print()
    print("Многопроцессность")
    print(f"Процессы: {workers_count}")
    print(f"Ссылки: {len(URLS)}")
    print(f"Время: {end_time - start_time:.4f} секунд")


if __name__ == "__main__":
    main()
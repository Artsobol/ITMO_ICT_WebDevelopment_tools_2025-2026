import threading
import time

import psycopg2

from common import DB_URL, URLS, ParsedBook, load_and_parse, make_slug


print_lock = threading.Lock()


def safe_print(message: str) -> None:
    with print_lock:
        print(message, flush=True)


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


def parse_and_save(url: str) -> None:
    book = load_and_parse(url)
    save_book(book)

    safe_print(f"Saved: {book.title} [{book.genre}]")


def worker(urls: list[str]) -> None:
    for url in urls:
        try:
            parse_and_save(url)
        except Exception as exception:
            safe_print(f"Error while processing {url}: {exception}")


def split_urls(urls: list[str], parts: int) -> list[list[str]]:
    result = [[] for _ in range(parts)]

    for index, url in enumerate(urls):
        result[index % parts].append(url)

    return result


def main() -> None:
    workers_count = 4
    url_parts = split_urls(URLS, workers_count)

    threads = []

    start_time = time.perf_counter()

    for urls in url_parts:
        thread = threading.Thread(target=worker, args=(urls,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.perf_counter()

    print()
    print("Многопоточность")
    print(f"Потоки: {workers_count}")
    print(f"Ссылки: {len(URLS)}")
    print(f"Время: {end_time - start_time:.4f} секунду")


if __name__ == "__main__":
    main()
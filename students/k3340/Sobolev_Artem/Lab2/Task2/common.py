import os
import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


DB_URL = os.getenv(
    "DB_URL",
    "postgresql://postgres:postgres@localhost:5433/book_crossing_v2"
)


URLS = [
    "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
    "https://books.toscrape.com/catalogue/soumission_998/index.html",
    "https://books.toscrape.com/catalogue/sharp-objects_997/index.html",
    "https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html",
    "https://books.toscrape.com/catalogue/the-requiem-red_995/index.html",
    "https://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html",
    "https://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html",
    "https://books.toscrape.com/catalogue/the-boys-in-the-boat-nine-americans-and-their-epic-quest-for-gold-at-the-1936-berlin-olympics_992/index.html",
    "https://books.toscrape.com/catalogue/the-black-maria_991/index.html",
]


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
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    return parse_book_page(response.text)

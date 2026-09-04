"""
extract.py — turns saved HTML into raw fields. No cleaning happens
here; that's normalize.py's job. This module only answers "which parts
of the page do I need."
"""

from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

RATING_WORDS = {"One", "Two", "Three", "Four", "Five"}


def parse_catalogue_page(html: str, page_url: str):
    """Return (book_urls, next_url_or_None) for one catalogue page."""
    soup = BeautifulSoup(html, "html.parser")

    book_urls = []
    for article in soup.select("article.product_pod"):
        link = article.select_one("h3 a")
        if link and link.get("href"):
            book_urls.append(urljoin(page_url, link["href"]))

    next_link = soup.select_one("li.next a")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None

    return book_urls, next_url


def parse_book_page(html: str, product_url: str, source_page: str) -> dict:
    """Extract the eight raw fields from one book detail page."""
    soup = BeautifulSoup(html, "html.parser")
    main = soup.select_one("div.product_main")

    title = None
    if main:
        heading = main.select_one("h1")
        if heading:
            title = heading.get_text(strip=True)

    price_text = None
    if main:
        price_el = main.select_one("p.price_color")
        if price_el:
            price_text = price_el.get_text(strip=True)

    availability_text = None
    if main:
        availability_el = main.select_one("p.availability")
        if availability_el:
            availability_text = availability_el.get_text(strip=True)

    rating_text = None
    if main:
        rating_el = main.select_one("p.star-rating")
        if rating_el:
            for cls in rating_el.get("class", []):
                if cls in RATING_WORDS:
                    rating_text = cls
                    break

    # Description lives in a <p> right after #product_description — some
    # books genuinely have none. Store null; never invent text.
    description = None
    desc_heading = soup.select_one("#product_description")
    if desc_heading:
        desc_p = desc_heading.find_next_sibling("p")
        if desc_p:
            description = desc_p.get_text(strip=True)

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

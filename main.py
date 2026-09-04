"""
main.py — the pipeline, one stage after another:
fetch -> extract -> normalize -> validate -> store -> report.

Run:
    python src/main.py
"""

import json
import os
import time
from datetime import datetime, timezone

from pydantic import ValidationError

from fetch import fetch, check_robots
from extract import parse_catalogue_page, parse_book_page
from normalize import normalize
from schema import BookRecord

BASE_URL = "https://books.toscrape.com/"
FIRST_CATALOGUE_URL = BASE_URL + "catalogue/page-1.html"
MAX_CATALOGUE_PAGES = 3

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

# For Stage 5's checkpoint: add a fake URL here to prove one broken page
# doesn't take the run down. Leave empty for a normal run.
#   EXTRA_TEST_URLS = ["https://books.toscrape.com/catalogue/does-not-exist/index.html"]
EXTRA_TEST_URLS = []


def cache_name_for(url: str) -> str:
    """Turn a URL into a filesystem-safe cache filename."""
    safe = url.replace("https://", "").replace("http://", "")
    safe = safe.replace("/", "_")
    if not safe.endswith(".html"):
        safe += ".html"
    return safe


def discover_book_urls(stats: dict):
    """Stage 2: walk the catalogue's own 'next' links, collect unique book URLs."""
    book_urls = []
    page_url = FIRST_CATALOGUE_URL
    pages_seen = 0

    while page_url and pages_seen < MAX_CATALOGUE_PAGES:
        pages_seen += 1
        html, _ = fetch(page_url, f"catalogue-page-{pages_seen}.html", stats)
        if html is None:
            break

        urls, next_url = parse_catalogue_page(html, page_url)
        book_urls.extend(urls)
        page_url = next_url

    unique_urls = list(dict.fromkeys(book_urls))  # de-dupe, keep order
    print(f"catalogue_pages={pages_seen} discovered={len(book_urls)} unique_urls={len(unique_urls)}")
    return unique_urls


def extract_and_validate(book_urls, stats):
    """Stage 3 + 4: fetch each book page, normalize it, validate it."""
    valid_records = []
    invalid_records = []

    for url in book_urls:
        html, _ = fetch(url, cache_name_for(url), stats)
        if html is None:
            continue  # already logged in stats["failed_pages"] by fetch()

        raw = parse_book_page(html, product_url=url, source_page=FIRST_CATALOGUE_URL)
        normalized = normalize(raw)

        try:
            record = BookRecord(**normalized)
            valid_records.append(json.loads(record.model_dump_json()))
        except ValidationError as exc:
            invalid_records.append({"record": normalized, "reason": str(exc)})

    return valid_records, invalid_records


def dedupe_by_product_url(records):
    """Canonical URL is identity — the same book counted twice counts once."""
    seen = {}
    for record in records:
        seen[record["product_url"]] = record
    return list(seen.values())


def write_json(path, data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    start = time.time()
    stats = {
        "pages_fetched": 0,
        "cache_hits": 0,
        "failed_pages": [],
    }

    robots_note = check_robots(BASE_URL)
    print(robots_note)

    book_urls = discover_book_urls(stats)
    book_urls.extend(EXTRA_TEST_URLS)

    valid_records, invalid_records = extract_and_validate(book_urls, stats)
    valid_records = dedupe_by_product_url(valid_records)

    write_json(os.path.join(OUTPUT_DIR, "books.json"), valid_records)
    write_json(os.path.join(OUTPUT_DIR, "errors.json"), invalid_records)

    duration_seconds = round(time.time() - start, 2)
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": duration_seconds,
        "pages_fetched": stats["pages_fetched"],
        "cache_hits": stats["cache_hits"],
        "valid_records": len(valid_records),
        "invalid_records": len(invalid_records),
        "failed_pages": len(stats["failed_pages"]),
        "failed_page_details": stats["failed_pages"],
    }
    write_json(os.path.join(OUTPUT_DIR, "run-report.json"), report)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

# The polite scraper — Books to Scrape

A small pipeline that downloads the first three catalogue pages of
[Books to Scrape](https://books.toscrape.com), visits all 60 book pages,
and turns the HTML into clean, schema-checked JSON. Fetch → extract →
normalize → validate → store → report.

## Target classification

- **Site:** [books.toscrape.com](https://books.toscrape.com) — the
  [toscrape.com](https://toscrape.com) project explicitly describes
  itself as a sandbox built for people to practise scraping on, with
  no real business behind it.
- **Scope:** the first 3 catalogue pages only (60 books total) — not
  the whole site.
- **Data collected:** title, price, availability, star rating, and
  description for each book — all publicly rendered in the page HTML,
  nothing behind a login.
- **robots.txt result:** *(fill in after running `python src/main.py`
  once — the run prints the robots.txt contents or "no robots file
  found" at the top of its output)*
- **Why this is appropriate here:** the target is a public sandbox
  built for exactly this exercise, the data is already public in the
  HTML the server sends, and the scraper never authenticates or
  bypasses anything.

**I will not reuse this code on another site without checking its
rules and terms first.**

## Setup & run

```
cd scraper
pip install -r requirements.txt
python src/main.py
```

Outputs land in `output/`:
- `books.json` — up to 60 validated records
- `errors.json` — any record that failed schema validation, with a reason
- `run-report.json` — counts and timing for the run

Run it twice — the second run reads mostly from `cache/` and still
produces exactly 60 records in `books.json`, not 120.

## Politeness rules

- **User-agent:** every request identifies itself as
  `FlyRankInternshipA9/1.0 (+https://github.com/kapurV06/FlyRank-AI)`.
- **Timeout:** every request gives up after 10 seconds.
- **Delay:** at least 500ms between real (non-cached) requests.
- **Cache:** every fetched page is saved to `cache/`; a second run
  reads the saved copy instead of asking the site again.
- **Status check:** only a `200` is treated as a page; `404`/`403` are
  never retried, a `5xx` or timeout is retried once.

## Record schema

```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "...",
  "source_page": "https://books.toscrape.com/catalogue/page-1.html",
  "fetched_at": "2026-08-06T10:00:00+00:00"
}
```

`product_url` is each record's canonical identity — the same book
counted twice still counts once. `description` is `null` when a book
has none; nothing is invented.

## Surviving a broken page

Uncomment `EXTRA_TEST_URLS` in `src/main.py` with a made-up book URL,
run once, and confirm: the run still finishes, `books.json` still has
the 60 good records, and `run-report.json` shows `failed_pages: 1`.

## Why no browser

The data needed here (title, price, availability, rating, description)
is already present in the HTML the server sends on first response —
confirmed by viewing page source before writing any selector. A
headless browser would add real cost (memory, startup time, a
Chromium dependency) for zero benefit on a server-rendered site like
this one.

## Sample run report

*(Paste one real `run-report.json` here before submitting.)*

```json
{
  "started_at": "PASTE_HERE",
  "duration_seconds": 0,
  "pages_fetched": 0,
  "cache_hits": 0,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}
```

## Ethics note

Use an official API when one exists instead of scraping. Never bypass
logins, paywalls, CAPTCHAs, or explicit blocks. Collect only the data
needed for the stated purpose, identify the scraper honestly, and
respect a site's stated rate limits and rules.

## Known limitation

*(Write one honest limitation here — e.g. selectors are tied to Books
to Scrape's current HTML structure and would break if the site's
markup changed.)*

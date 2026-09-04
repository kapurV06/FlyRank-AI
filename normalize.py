"""
normalize.py — turns raw text into clean values. The raw text is kept
alongside the clean value, never discarded.
"""


def normalize(raw: dict) -> dict:
    record = dict(raw)

    price_text = raw.get("price_text") or ""
    # Books to Scrape sometimes serves the pound sign as a mis-encoded
    # "Â£" — strip both forms rather than trust one.
    cleaned = price_text.replace("Â£", "").replace("£", "").strip()
    try:
        record["price_gbp"] = float(cleaned)
    except ValueError:
        record["price_gbp"] = None

    return record

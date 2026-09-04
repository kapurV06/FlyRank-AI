"""
fetch.py — the only place that talks to the network.

Every real request: identifies itself with a user-agent, has a timeout,
waits between requests, checks the status code, and is cached to disk so
re-running the pipeline during development never re-hits the site.
"""

import os
import time
import requests

USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/kapurV06/FlyRank-AI)"
TIMEOUT_SECONDS = 10
DELAY_SECONDS = 0.5  # between real (non-cached) requests only

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")


def _cache_path(cache_name: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, cache_name)


def fetch(url: str, cache_name: str, stats: dict, max_retries: int = 1):
    """
    Return (html, from_cache). Returns (None, False) if the page could
    not be fetched — the caller decides what that means for the run.

    Retries once on a timeout or a 5xx (transient). Never retries a 404
    (the page doesn't exist) or a 403 (the site said no).
    """
    path = _cache_path(cache_name)

    if os.path.exists(path):
        stats["cache_hits"] += 1
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT {url} ({len(html)} bytes)")
        return html, True

    attempts = 0
    while True:
        attempts += 1
        try:
            response = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=TIMEOUT_SECONDS,
            )
        except requests.exceptions.RequestException as exc:
            if attempts <= max_retries:
                time.sleep(1)
                continue
            stats["failed_pages"].append({"url": url, "reason": f"request error: {exc}"})
            return None, False

        stats["pages_fetched"] += 1
        time.sleep(DELAY_SECONDS)

        if response.status_code == 200:
            with open(path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"FETCH {url} ({len(response.content)} bytes)")
            return response.text, False

        if response.status_code in (404, 403):
            stats["failed_pages"].append(
                {"url": url, "reason": f"status {response.status_code}"}
            )
            return None, False

        if response.status_code >= 500 and attempts <= max_retries:
            time.sleep(1)
            continue

        stats["failed_pages"].append(
            {"url": url, "reason": f"status {response.status_code}"}
        )
        return None, False


def check_robots(base_url: str) -> str:
    """One-off robots.txt check for Stage 0. Returns a human-readable note."""
    robots_url = base_url.rstrip("/") + "/robots.txt"
    try:
        response = requests.get(
            robots_url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS
        )
    except requests.exceptions.RequestException as exc:
        return f"could not reach {robots_url}: {exc}"

    if response.status_code == 200 and response.text.strip():
        return f"robots.txt found at {robots_url}:\n{response.text.strip()}"
    return f"no robots file found at {robots_url} (status {response.status_code})"

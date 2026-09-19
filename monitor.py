import json
import sys
from pathlib import Path

import config
import notifier
import scraper

# Listing titles can contain Hungarian characters (ő, ű, …) that aren't in
# Windows' default cp1252 console/file encoding — without this, printing (or
# redirecting output to log.txt via Task Scheduler/cron) can crash.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

SEEN_LISTINGS_FILE = Path(__file__).parent / "seen_listings.json"


def load_seen_ids():
    if not SEEN_LISTINGS_FILE.exists():
        return set()
    with open(SEEN_LISTINGS_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_seen_ids(seen_ids):
    with open(SEEN_LISTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen_ids), f, indent=2)


def matches_filters(listing):
    if listing["price"] is not None and listing["price"] > config.MAX_PRICE_HUF:
        return False

    if listing["seller_positive_rating"] < config.MIN_SELLER_POSITIVE_RATING:
        return False

    title_lower = listing["title"].lower()
    return any(keyword.lower() in title_lower for keyword in config.KEYWORDS)


def main():
    seen_ids = load_seen_ids()
    first_run = len(seen_ids) == 0

    html = scraper.fetch_page(config.SEARCH_URL)
    listings = scraper.parse_listings(html)

    if not listings:
        print("No listings found — check SELECTORS in scraper.py against the live page.")

    new_ids = set()
    for listing in listings:
        if listing["id"] in seen_ids:
            continue

        new_ids.add(listing["id"])

        if first_run:
            continue

        if matches_filters(listing):
            print(f"New matching listing: {listing['title']} — notifying.")
            notifier.notify_listing(listing)
        else:
            print(f"New listing (filtered out): {listing['title']}")

    if new_ids:
        save_seen_ids(seen_ids | new_ids)

    if first_run:
        print(f"First run — recorded {len(new_ids)} existing listing(s), no notifications sent.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

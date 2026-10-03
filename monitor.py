import json
import re
import sys
from pathlib import Path

import requests

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

EXCLUDE_RE = re.compile("|".join(f"(?:{p})" for p in config.EXCLUDE_TITLE_PATTERNS))
SIZE_RE = re.compile(r"(\d+)(?:\s*[-–]\s*\d+)?\s*(tb|t|gb|g)(?![a-z0-9])")
NO_UNIT_STORAGE_RE = re.compile(r"(\d+)\s*(?:ssd|nvme|hdd)\b")
RAM_SUFFIX_RE = re.compile(r"^\s*(ram|ddr\d?|memória|memoria)\b")
RAM_PREFIX_RE = re.compile(r"(ram|memória|memoria)\s*:?\s*$")
STORAGE_SUFFIX_RE = re.compile(r"^\s*(ssd|nvme|hdd|m\.?2|tárhely|tarhely)\b")
STORAGE_PREFIX_RE = re.compile(r"(ssd|nvme|hdd|tárhely|tarhely)\s*:?\s*$")
GPU_SUFFIX_RE = re.compile(r"^\s*(vga|vram|gddr\d?|videó|gpu|rtx|gtx|radeon|geforce|quadro)\b")
GPU_PREFIX_RE = re.compile(r"\b(rtx|gtx|rx|radeon|quadro|geforce|mx|gpu|vga)\s*[\w.-]*\s*$")
MAX_UNLABELED_RAM_GB = 128
CPU_RE = re.compile(r"\bi([57])[- ]?(\d{4,5})")
DISTRICT_RE = re.compile(r"[ivxlc]+\. kerület")


def load_seen_ids():
    if not SEEN_LISTINGS_FILE.exists():
        return set()
    with open(SEEN_LISTINGS_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_seen_ids(seen_ids):
    with open(SEEN_LISTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen_ids), f, indent=2)


def parse_specs(title):
    text = title.lower()
    ram_gb = []
    storage_gb = []

    for match in SIZE_RE.finditer(text):
        value = int(match.group(1))
        unit = match.group(2)
        prefix = text[max(0, match.start() - 15):match.start()]
        suffix = text[match.end():match.end() + 15]

        if unit in ("tb", "t"):
            storage_gb.append(value * 1024)
        elif RAM_SUFFIX_RE.match(suffix):
            ram_gb.append(value)
        elif STORAGE_SUFFIX_RE.match(suffix):
            storage_gb.append(value)
        elif RAM_PREFIX_RE.search(prefix):
            ram_gb.append(value)
        elif STORAGE_PREFIX_RE.search(prefix):
            storage_gb.append(value)
        elif GPU_SUFFIX_RE.match(suffix) or GPU_PREFIX_RE.search(prefix):
            continue
        elif value <= MAX_UNLABELED_RAM_GB:
            ram_gb.append(value)
        else:
            storage_gb.append(value)

    for match in NO_UNIT_STORAGE_RE.finditer(text):
        storage_gb.append(int(match.group(1)))

    return (max(ram_gb) if ram_gb else 0, max(storage_gb) if storage_gb else 0)


def is_cpu_ok(title):
    match = CPU_RE.search(title.lower())
    if not match:
        return False
    family, digits = match.groups()
    if family == "7":
        return True
    two_digit_generation = len(digits) == 5 or digits[0] == "1"
    generation = int(digits[:2]) if two_digit_generation else int(digits[0])
    return generation >= config.MIN_I5_GENERATION


def in_pickup_area(city):
    for part in city.split(","):
        name = part.strip()
        if name in config.PICKUP_TOWNS or DISTRICT_RE.fullmatch(name.lower()):
            return True
    return False


def matches_title(listing):
    price = listing["price"]
    if price is None or not (config.MIN_PRICE_HUF <= price <= config.MAX_PRICE_HUF):
        return False

    if listing["seller_positive_rating"] < config.MIN_SELLER_POSITIVE_RATING:
        return False

    if not in_pickup_area(listing["city"]):
        return False

    if EXCLUDE_RE.search(listing["title"].lower()):
        return False

    if not is_cpu_ok(listing["title"]):
        return False

    ram_gb, storage_gb = parse_specs(listing["title"])
    return ram_gb >= config.MIN_RAM_GB and storage_gb >= config.MIN_STORAGE_GB


def get_offer_condition(listing):
    details = scraper.parse_detail(scraper.fetch_page(listing["link"]))
    if details.get("intent") != "kínál":
        return None
    return details.get("condition")


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

        if first_run:
            new_ids.add(listing["id"])
            continue

        if not matches_title(listing):
            new_ids.add(listing["id"])
            print(f"New listing (filtered out): {listing['title']}")
            continue

        try:
            condition = get_offer_condition(listing)
        except requests.RequestException as exc:
            print(f"Could not check condition for {listing['link']}: {exc}")
            continue

        new_ids.add(listing["id"])
        if condition in config.ALLOWED_CONDITIONS:
            listing["condition"] = condition
        elif condition == "használt" and re.search(config.LIKE_NEW_TITLE_PATTERN, listing["title"].lower()):
            listing["condition"] = "újszerű (listed as used)"
        else:
            print(f"New listing (condition {condition!r} or not for sale): {listing['title']}")
            continue

        print(f"New matching listing ({listing['condition']}): {listing['title']} — notifying.")
        notifier.notify_listing(listing)

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

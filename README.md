# HardverApro Notifier

Small script that watches HardverApro's non-Apple laptop listings for brand-new
machines with at least 16 GB RAM and 512 GB storage, priced 100 000–150 000 Ft,
and emails you when a new one shows up.

## How it works

1. On each run, the script fetches the newest laptop listings page
   (`SEARCH_URL`) and parses each listing's title, price, seller rating, link
   and ID.
2. It compares the IDs against a local `seen_listings.json` file and only looks
   at listings it hasn't seen before.
3. Title filters are applied first: price range, seller location, seller rating,
   exclude words, processor (i5 12th gen or newer, or any i7), and RAM/storage
   read from the title. Listings that fail any of them are recorded as seen and
   skipped.
4. For the rest, the listing's detail page is fetched to confirm it is
   `Állapot: új` or `használt` (used) and `Szándék: kínál` (for sale, not
   wanted). Only then is an email sent, with the condition and location in it.
5. A scheduler (cron, or Windows Task Scheduler) runs the script every
   10–15 minutes.

Filtering happens in the script, not on the site: HardverApro's price, new/used
and exclude-word search fields are ignored for anonymous requests.

## Setup

### 1. Configure

Copy `config.example.py` to `config.py` and fill in the SMTP settings. The
search and filter settings are already set for laptops:

- `SEARCH_URL` — the non-Apple laptop category (`/aprok/notebook/pc/`)
- `MIN_PRICE_HUF` / `MAX_PRICE_HUF` — 100 000 / 150 000
- `MIN_RAM_GB` / `MIN_STORAGE_GB` — 16 / 512. Listings that don't state RAM and
  storage in the title are skipped, since they can't be verified.
- `MIN_I5_GENERATION` / CPU — i5 must be 12th gen or newer; i7 any generation.
  Other CPUs (Ryzen, i9, Core Ultra) and listings with no CPU in the title are
  skipped.
- `PICKUP_TOWNS` — Budapest, its districts, and Pest county towns. Listings
  outside this list are skipped. The list is hand-written, so towns missing from
  it will be skipped until you add them.
- `ALLOWED_CONDITIONS` — `új` and `használt`. Used listings are included, so check
  the photos and seller details before buying.
- `EXCLUDE_TITLE_PATTERNS` — regexes matched against the lowercase title
  (broken, part-only, chargers, docks, screens, tablets, wanted ads, etc.)
- `MIN_SELLER_POSITIVE_RATING` — skip sellers with fewer positive ratings

**Don't commit `config.py`** — it holds your email credentials. `.gitignore`
already excludes it; only `config.example.py` (no real values) should go in
git or anywhere public.

### 2. Install dependencies

```bash
pip install requests beautifulsoup4
```

### 3. Run once to test

```bash
python monitor.py
```

The first run only records the listings currently on the page (no emails), so
you don't get flooded on first launch. Later runs email new matches.

### 4. Schedule it

**macOS/Linux (cron):**

```bash
crontab -e
# every 15 minutes:
*/15 * * * * cd /path/to/hardverapro-monitor && /usr/bin/python3 monitor.py >> log.txt 2>&1
```

**Windows:** use Task Scheduler, "Run whether user is logged on or not",
trigger every 15 minutes, action = `python.exe monitor.py` with the working
directory set to the project folder.

## Files

| File                  | Purpose                                          |
|-----------------------|---------------------------------------------------|
| `config.example.py`   | Template config — safe to share/commit            |
| `config.py`           | Your real config — **never commit this**          |
| `scraper.py`          | Fetches + parses the listing and detail pages     |
| `notifier.py`         | Sends the email via SMTP                          |
| `monitor.py`          | Glue: title filters, condition check, notify      |
| `seen_listings.json`  | Local memory of listing IDs already handled       |

## Notes / gotchas

- The CSS selectors in `scraper.py` were verified against the live laptop
  category page. If HardverApro changes their template and the script starts
  finding zero listings on a page you know has results, open the page in your
  browser, right-click a listing → Inspect, and update the `SELECTORS` dict at
  the top of `scraper.py`.
- Only the newest 100 listings on the first page are checked on each run.
- Be a decent citizen: a 10–15 minute interval is plenty for a personal
  price watch and won't hammer their servers.

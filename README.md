# HardverApro Notifier
 
Small script that watches a HardverApro search for iPhone 15 Plus (or newer/better)
listings under a price cap, and emails you when a new one shows up.
 
## How it works
 
1. You give it the **search URL** for what you're watching (copy it straight
   from your browser after setting up the search on hardverapro.hu — category,
   keyword, and max price filter).
2. On each run, the script fetches that page, parses out the listings
   (title, price, link, listing ID), and compares them against a local
   `seen_listings.json` file.
3. Any listing that's new **and** matches your filters (keyword + price cap)
   triggers an email.
4. A scheduler (cron, or Windows Task Scheduler) runs the script every
   10–15 minutes so it behaves like a notification service.
## Setup
 
### 1. Get your search URL
 
- Go to hardverapro.hu
- Search under the phone/mobiltelefon category for "iPhone 15"
- Set the max price filter to 150 000 Ft
- Copy the resulting URL — this goes in `SEARCH_URL` in `config.py`
Note: HardverApro's HTML structure isn't something I could verify directly
while building this, so the CSS selectors in `scraper.py` are a best-effort
starting point. If the script finds zero listings on a page you know has
results, open the search page in your browser, right-click a listing →
Inspect, and update the `SELECTORS` dict at the top of `scraper.py` to match
what you see (the class names on the listing container, title, price, and link).
 
### 2. Configure
 
Copy `config.example.py` to `config.py` and fill in:
 
```python
SEARCH_URL = "https://hardverapro.hu/..."   # your saved search
MAX_PRICE_HUF = 150_000
KEYWORDS = ["iphone 15 plus", "iphone 15 pro", "iphone 16", "iphone 17"]
CHECK_INTERVAL_MINUTES = 15
 
# Email (SMTP) — works with any provider, not just Gmail
SMTP_HOST = "smtp.yourprovider.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@example.com"
SMTP_PASSWORD = "your-app-password-or-account-password"
EMAIL_FROM = "your-email@example.com"
EMAIL_TO = "your-email@example.com"        # <-- put your real address here locally, never commit it
```
 
**Don't commit `config.py`** — it holds your email credentials. `.gitignore`
already excludes it; only `config.example.py` (no real values) should go in
git or anywhere public.
 
### 3. Install dependencies
 
```bash
pip install requests beautifulsoup4
```
 
### 4. Run once to test
 
```bash
python monitor.py
```
 
First run will just populate `seen_listings.json` with whatever's already
there (no emails for pre-existing listings) — that's intentional, so you
don't get flooded on first launch.
 
### 5. Schedule it
 
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
| `scraper.py`          | Fetches + parses the HardverApro search page      |
| `notifier.py`         | Sends the email via SMTP                          |
| `monitor.py`          | Glue: run scraper → diff against seen → notify    |
| `seen_listings.json`  | Local memory of listing IDs already notified on   |
 
## Notes / gotchas
 
- If HardverApro requires cookies or blocks default `requests` user-agents,
  set a browser-like `User-Agent` header in `scraper.py` (already included
  as a starting point).
- Be a decent citizen: a 10–15 minute interval is plenty for a personal
  price watch and won't hammer their servers.
- If listings ever stop being detected, it's almost always a changed CSS
  selector — check there first.

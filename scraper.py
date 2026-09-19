import re

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

BASE_URL = "https://hardverapro.hu"

# Verified against the live markup of https://hardverapro.hu/aprok/mobil/index.html
# (Sep 2026). Each listing is an <li class="media" data-uadid="...">; if
# HardverApro changes their template and this stops finding listings, re-check
# a listing element in your browser and update these to match.
SELECTORS = {
    "listing": "li.media[data-uadid]",
    "title": ".uad-col-title h1 a",
    "price": ".uad-col-price .uad-price span.text-nowrap",
    "link": ".uad-col-title h1 a",
    "rating": ".uad-user .uad-rating",
}


def fetch_page(url):
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def _parse_price(text):
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else None


def _parse_seller_positive_rating(rating_el):
    if rating_el is None:
        return 0

    # Sellers with both positive and negative ratings nest them as separate
    # spans (e.g. "+234 | -1"); pure-positive or no-rating ("n.a.") sellers
    # don't have a nested span, so fall back to the element's own text.
    positive_el = rating_el.select_one(".uad-rating-positive")
    text = positive_el.get_text(strip=True) if positive_el else rating_el.get_text(strip=True)

    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


def parse_listings(html):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    for element in soup.select(SELECTORS["listing"]):
        listing_id = element.get("data-uadid")
        title_el = element.select_one(SELECTORS["title"])
        price_el = element.select_one(SELECTORS["price"])
        link_el = element.select_one(SELECTORS["link"])
        rating_el = element.select_one(SELECTORS["rating"])

        if not listing_id or not title_el or not link_el:
            continue

        title = title_el.get_text(strip=True)
        link = link_el.get("href", "")
        if link.startswith("/"):
            link = BASE_URL + link

        price = _parse_price(price_el.get_text(strip=True) if price_el else "")
        seller_positive_rating = _parse_seller_positive_rating(rating_el)

        listings.append({
            "id": listing_id,
            "title": title,
            "price": price,
            "link": link,
            "seller_positive_rating": seller_positive_rating,
        })

    return listings

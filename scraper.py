import re

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

BASE_URL = "https://hardverapro.hu"

# Verified against the live markup of https://hardverapro.hu/aprok/notebook/pc/index.html
# (Oct 2026). Each listing is an <li class="media" data-uadid="...">. The price
# in the title column is the full value; the one in .uad-col-price is abbreviated
# ("3,00M Ft") for large amounts and must not be used.
SELECTORS = {
    "listing": "li.media[data-uadid]",
    "title": ".uad-col-title h1 a",
    "price": ".uad-col-title .uad-price span.text-nowrap",
    "link": ".uad-col-title h1 a",
    "rating": ".uad-user .uad-rating",
    "city": ".uad-cities",
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
        city_el = element.select_one(SELECTORS["city"])

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
            "city": city_el.get_text(strip=True) if city_el else "",
        })

    return listings


def parse_detail(html):
    soup = BeautifulSoup(html, "html.parser")
    details = {}
    for th in soup.select("table th"):
        label = th.get_text(strip=True)
        td = th.find_next_sibling("td")
        if td is None:
            continue
        if label == "Állapot:":
            details["condition"] = td.get_text(strip=True).lower()
        elif label == "Szándék:":
            details["intent"] = td.get_text(strip=True).lower()
    description_el = soup.select_one(".rtif-content.uad-content")
    details["description"] = description_el.get_text(" ", strip=True) if description_el else ""
    return details

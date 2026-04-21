#!/usr/bin/env python3
"""
Minimal Amazon product scraper - Python version.

WHAT THIS DOES
    Fetches the Amazon product detail page for a given ASIN and extracts
    title, price, rating, and ASIN. That's it.

WHAT THIS DOESN'T DO (see the repo README for the full list)
    - Handle Amazon's robot page / CAPTCHA
    - Rotate proxies on failure
    - Extract reviews, variants, images, Buy Box, seller offers
    - Handle marketplace quirks beyond the three domains below
    - Retry with exponential backoff

Usage:
    python basic_product.py <ASIN> [domain]
    python basic_product.py B09HN3Q81F com
    python basic_product.py B000ALVUM6 de

Dependencies:
    pip install requests beautifulsoup4

BYO proxy: see PROXY_URL env var below.
"""

from __future__ import annotations

import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: basic_product.py <ASIN> [domain]", file=sys.stderr)
        return 1

    asin = sys.argv[1]
    domain = sys.argv[2] if len(sys.argv) > 2 else "com"

    # Plug in any HTTP/HTTPS proxy URL via the PROXY_URL env var.
    # Examples:
    #   export PROXY_URL=http://user:pass@gate.provider.com:8000
    #   export PROXY_URL=http://user:pass_country-US@rp.provider.com:1000
    # If unset, requests go direct - they will be blocked on ~30% of
    # attempts from a datacenter IP. This is why you need a proxy.
    proxy_url = os.environ.get("PROXY_URL")
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

    url = f"https://www.amazon.{domain}/dp/{asin}"
    try:
        resp = requests.get(
            url,
            proxies=proxies,
            headers={
                # Anything more realistic than requests' default UA helps - a little.
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    "Version/17.0 Safari/605.1.15"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=30,
        )
    except requests.RequestException as e:
        print(f"error: network failure - {e}", file=sys.stderr)
        return 1

    if not resp.ok:
        print(
            f"error: HTTP {resp.status_code} - Amazon likely blocked us. "
            "Try a different proxy, or use the managed API at https://amazonscraperapi.com",
            file=sys.stderr,
        )
        return 1

    html = resp.text

    # Cheap signal that Amazon served a robot page instead of the product.
    if "captchacharacters" in html or "Enter the characters you see below" in html:
        print(
            "error: Amazon showed a robot check. This scraper does not solve it. "
            "Use a residential proxy or the managed API.",
            file=sys.stderr,
        )
        return 1

    soup = BeautifulSoup(html, "html.parser")

    # These selectors are correct as of 2026-04 but Amazon rewrites them often.
    # If any return empty/None, that's the whole point of this repo's README.
    title_el = soup.select_one("#productTitle")
    title = title_el.get_text(strip=True) if title_el else None

    price_whole_el = soup.select_one(".a-price .a-price-whole")
    price_frac_el = soup.select_one(".a-price .a-price-fraction")
    price = None
    if price_whole_el:
        whole = re.sub(r"[^0-9]", "", price_whole_el.get_text())
        frac = re.sub(r"[^0-9]", "", price_frac_el.get_text()) if price_frac_el else "00"
        if whole:
            price = float(f"{whole}.{frac or '00'}")

    rating_attr = soup.select_one("#acrPopover")
    rating_text = (
        rating_attr.get("title")
        if rating_attr
        else (soup.select_one(".a-icon-star .a-icon-alt") or {}).get_text()
        if soup.select_one(".a-icon-star .a-icon-alt")
        else None
    )
    rating = None
    if rating_text:
        m = re.search(r"([0-9.]+)", rating_text)
        if m:
            rating = float(m.group(1))

    reviews_el = soup.select_one("#acrCustomerReviewText")
    review_count = (
        int(re.sub(r"[^0-9]", "", reviews_el.get_text())) if reviews_el else None
    )

    result = {
        "asin": asin,
        "domain": domain,
        "url": url,
        "title": title,
        "price": price,
        "rating": rating,
        "reviewCount": review_count,
    }

    if not title:
        print(
            "warning: extraction returned no title. Amazon may have changed "
            "selectors or served a stripped page.",
            file=sys.stderr,
        )
        print(
            "for the structured, maintained version: https://amazonscraperapi.com",
            file=sys.stderr,
        )

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Naukri scraper — uses Bright Data Web Unlocker to scrape live job listings."""
from __future__ import annotations
import time
from typing import Iterator
from bs4 import BeautifulSoup
from scraper.registry import register
from scraper.fetcher import fetch_html


@register("naukri", "Naukri")
def scrape_naukri(
    query: str = "software engineer",
    location: str = "",
    pages: int = 1,
    delay: float = 2.0,
    **kwargs,
) -> Iterator[dict]:
    """Scrape Naukri job listings via Bright Data Web Unlocker.

    Yields dicts with keys: title, company, location, source, url, description.
    """
    if not query:
        query = "software engineer"

    seen: set[str] = set()

    for page in range(1, pages + 1):
        # Naukri URL pattern
        slug = query.replace(" ", "-").lower()
        loc_slug = f"-in-{location.replace(' ', '-').lower()}" if location else ""
        url = f"https://www.naukri.com/{slug}-jobs{loc_slug}?pageNo={page}"

        try:
            print(f"[naukri] Fetching page {page}: {url}")
            html = fetch_html(url, timeout=120)
            soup = BeautifulSoup(html, "html.parser")

            # Naukri uses <article> tags with class containing "tuple" for job cards
            cards = soup.select("article.srpTuple, article.cardListing, div.tuple-container")

            # Fallback: try generic article tags
            if not cards:
                cards = soup.select("article")

            for card in cards:
                try:
                    # Title
                    title_el = card.select_one("a.title, h2 a, a.fontSemibold")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)
                    href = title_el.get("href", "")
                    job_url = href if href.startswith("http") else f"https://www.naukri.com{href}"

                    if job_url in seen:
                        continue
                    seen.add(job_url)

                    # Company
                    company_el = card.select_one("a.subTitle, .companyName a, .company")
                    company = company_el.get_text(strip=True) if company_el else "Unknown"

                    # Location
                    loc_el = card.select_one(".location, .subTitle .location, span.locWdth")
                    job_location = loc_el.get_text(strip=True) if loc_el else ""

                    # Description snippet
                    desc_el = card.select_one(".jobDescription, .description, .job-desc")
                    description = desc_el.get_text(strip=True)[:500] if desc_el else ""

                    yield {
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "source": "naukri",
                        "url": job_url,
                        "description": description,
                    }
                except Exception as e:
                    print(f"[naukri] Error parsing card: {e}")
                    continue

            print(f"[naukri] Page {page}: found {len(cards)} cards, {len(seen)} total unique jobs")

        except Exception as e:
            print(f"[naukri] Error fetching page {page}: {e}")

        if page < pages:
            time.sleep(delay)

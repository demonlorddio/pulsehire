"""Indeed scraper — fetches job listings via Bright Data Web Unlocker API.

Bright Data Web Unlocker handles proxy rotation, anti-bot, and CAPTCHA
solving.  We send a simple HTTP request and get back clean HTML.

Usage (called from main.py's _run_scrape_sync):
    jobs = scrape_indeed(query="python developer", pages=2)
    for job in jobs:
        # job = {title, company, location, url, description, posted_date}
"""
from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Iterator
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Ensure .env is loaded regardless of working directory.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# ── Bright Data config ───────────────────────────────────────────────────────

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY", "")
BRIGHTDATA_ZONE = os.getenv("BRIGHTDATA_ZONE", "")
BRIGHTDATA_ENDPOINT = "https://api.brightdata.com/request"

# ── Indeed config ────────────────────────────────────────────────────────────

INDEED_BASE = "https://www.indeed.com"
JOBS_PER_PAGE = 10  # Indeed returns ~10 results per page

def _get_user_agent() -> str:
    """Use the user agent from .env, or fall back to a sensible default."""
    return os.getenv(
        "SCRAPE_USER_AGENT",
        "PulseHire/1.0 (Hackathon Project)",
    )


# ── Bright Data fetcher ─────────────────────────────────────────────────────


def _fetch_via_brightdata(url: str) -> str:
    """Fetch a URL through Bright Data Web Unlocker.  Returns raw HTML."""
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
    }
    payload = {
        "zone": BRIGHTDATA_ZONE,
        "url": url,
        "format": "raw",
    }

    resp = requests.post(BRIGHTDATA_ENDPOINT, json=payload, headers=auth_headers, timeout=120)
    if not resp.ok:
        print(f"[indeed] Bright Data error {resp.status_code}: {resp.text[:500]}")
    resp.raise_for_status()
    return resp.text


# ── Indeed URL builder ───────────────────────────────────────────────────────


def _build_indeed_url(query: str, location: str = "", start: int = 0) -> str:
    """Build an Indeed search URL."""
    params = {"q": quote_plus(query), "start": start}
    if location:
        params["l"] = quote_plus(location)

    parts = [f"{k}={v}" for k, v in params.items()]
    return f"{INDEED_BASE}/jobs?{'&'.join(parts)}"


# ── HTML parsers ─────────────────────────────────────────────────────────────


def _parse_job_card(card: BeautifulSoup) -> dict | None:
    """Extract job info from a single Indeed job card element."""
    try:
        # Title + URL — Indeed uses <h2> with an <a> inside
        title_el = card.select_one("h2.jobTitle a, h2 a, a.jcs-JobTitle")
        if not title_el:
            # Fallback: any link that looks like a job link
            title_el = card.select_one("a[href*='/rc/clk'], a[href*='jk=']")
        if not title_el:
            return None

        title = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        if href.startswith("/"):
            url = INDEED_BASE + href
        elif href.startswith("http"):
            url = href
        else:
            return None

        # Company
        company_el = card.select_one(
            "span[data-testid='company-name'], "
            "span.companyName, "
            "span.company_secondary_header, "
            "[data-testid='company-name']"
        )
        company = company_el.get_text(strip=True) if company_el else None

        # Location
        loc_el = card.select_one(
            "div[data-testid='text-location'], "
            "div.companyLocation, "
            "[data-testid='text-location']"
        )
        location = loc_el.get_text(strip=True) if loc_el else None

        # Snippet / description (short summary on search page)
        snippet_el = card.select_one(
            "div.job-snippet, "
            "table.jobCardShelfContainer td.jobCardShelfItem, "
            "[class*='snippet'], "
            ".jobsearch-SerpJobCard-snippet"
        )
        description = snippet_el.get_text(strip=True) if snippet_el else None

        # Posted date
        date_el = card.select_one("span.date, span[data-testid='myJobsStateDate']")
        posted_date = _parse_relative_date(date_el.get_text(strip=True)) if date_el else None

        return {
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "description": description,
            "posted_date": posted_date,
        }
    except Exception:
        return None


def _parse_relative_date(text: str) -> str | None:
    """Turn '3 days ago', 'just now', etc. into an ISO date string."""
    from datetime import date, timedelta

    text = text.lower().strip()
    today = date.today()

    if "just posted" in text or "just now" in text:
        return today.isoformat()
    if "today" in text:
        return today.isoformat()
    if "yesterday" in text:
        return (today - timedelta(days=1)).isoformat()

    # "3 days ago", "1 day ago"
    m = re.search(r"(\d+)\s+days?\s+ago", text)
    if m:
        return (today - timedelta(days=int(m.group(1)))).isoformat()

    # "1 hour ago", "5 hours ago"
    m = re.search(r"(\d+)\s+hours?\s+ago", text)
    if m:
        return today.isoformat()

    # "30+ days ago"
    m = re.search(r"(\d+)\+?\s+days?\s+ago", text)
    if m:
        return (today - timedelta(days=30)).isoformat()

    return None


def _parse_jobs_from_html(html: str) -> list[dict]:
    """Parse Indeed search results HTML into a list of job dicts."""
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict] = []

    # Indeed wraps each result in various container classes depending on
    # the page version.  Try the most common selectors.
    cards = soup.select(
        "div.job_seen_beacon, "
        "div.jobsearch-ResultsList > div, "
        "div.resultContent, "
        "td.resultContent, "
        "div.jobsearch-ResultsList .result, "
        "div[data-testid='searcherResults'] > div"
    )

    if not cards:
        # Broader fallback: any div that has a job title link
        cards = soup.find_all("div", class_=re.compile(r"job|result", re.I))

    for card in cards:
        job = _parse_job_card(card)
        if job and job.get("title") and job.get("url"):
            jobs.append(job)

    return jobs


# ── Public API ───────────────────────────────────────────────────────────────


def scrape_indeed(
    query: str = "software engineer",
    location: str = "",
    pages: int = 2,
    delay: float = 2.0,
) -> Iterator[dict]:
    """Yield job dicts from Indeed search results.

    Parameters
    ----------
    query : str
        Search term (e.g., "python developer").
    location : str
        Optional location filter.
    pages : int
        Number of result pages to fetch (~10 jobs per page).
    delay : float
        Seconds to wait between pages (be polite, even through Bright Data).

    Yields
    ------
    dict
        {title, company, location, url, description, posted_date}
    """
    # Default query when None is passed (frontend doesn't always send query).
    if not query:
        query = "software engineer"

    if not BRIGHTDATA_API_KEY:
        raise RuntimeError("BRIGHTDATA_API_KEY is not set in environment / .env")
    if not BRIGHTDATA_ZONE:
        raise RuntimeError("BRIGHTDATA_ZONE is not set in environment / .env")

    seen_urls: set[str] = set()

    for page in range(pages):
        start = page * JOBS_PER_PAGE
        url = _build_indeed_url(query, location, start)
        print(f"[indeed] Fetching page {page + 1}/{pages}: {url}")

        try:
            html = _fetch_via_brightdata(url)
        except requests.HTTPError as e:
            print(f"[indeed] HTTP error on page {page + 1}: {e}")
            break
        except requests.RequestException as e:
            print(f"[indeed] Request error on page {page + 1}: {e}")
            break

        jobs = _parse_jobs_from_html(html)
        print(f"[indeed] Parsed {len(jobs)} jobs from page {page + 1}")

        for job in jobs:
            if job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                yield job

        if page < pages - 1:
            time.sleep(delay)

    print(f"[indeed] Done. Total unique jobs yielded: {len(seen_urls)}")


# ── CLI test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    results = list(scrape_indeed("python developer", pages=1))
    print(f"\n=== Scraped {len(results)} jobs ===")
    for i, job in enumerate(results[:5], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job.get('company', '?')}")
        print(f"   Location: {job.get('location', '?')}")
        print(f"   URL: {job['url']}")

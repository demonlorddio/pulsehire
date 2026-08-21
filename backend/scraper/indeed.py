"""Indeed scraper — hybrid approach: Web Unlocker search + Dataset API structured data."""
from __future__ import annotations

import time
from typing import Iterator
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from scraper.fetcher import fetch_html, scrape_dataset
from scraper.registry import register

BASE = "https://www.indeed.com"


def _build_search_url(query: str, location: str = "", start: int = 0) -> str:
    params = f"q={quote_plus(query)}&start={start}"
    if location:
        params += f"&l={quote_plus(location)}"
    return f"{BASE}/jobs?{params}"


def _extract_job_urls(html: str) -> list[str]:
    """Extract Indeed job detail URLs from search results HTML."""
    soup = BeautifulSoup(html, "html.parser")
    urls = []

    # Find all job card links
    cards = soup.select(
        "div.job_seen_beacon, div.jobsearch-ResultsList > div, td.resultContent"
    )

    for card in cards:
        try:
            title_el = card.select_one("h2.jobTitle a, h2 a, a.jcs-JobTitle")
            if not title_el:
                title_el = card.select_one("a[href*='/rc/clk'], a[href*='jk=']")
            if not title_el:
                continue
            href = title_el.get("href", "")
            if href.startswith("/"):
                href = BASE + href
            if href.startswith("http") and "jk=" in href:
                urls.append(href)
        except Exception:
            continue

    # Broader fallback: find any /viewjob or jk= links
    if not urls:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/viewjob" in href or "jk=" in href:
                if href.startswith("/"):
                    href = BASE + href
                if href.startswith("http"):
                    urls.append(href)

    return list(dict.fromkeys(urls))  # dedupe, preserve order


def _normalize_dataset_record(record: dict) -> dict:
    """Convert a Bright Data Dataset API record to our standard job dict."""
    return {
        "title": record.get("job_title", ""),
        "company": record.get("company_name"),
        "location": record.get("job_location"),
        "url": record.get("url", ""),
        "description": record.get("job_summary"),
        "posted_date": record.get("job_posted_time"),
    }


@register("indeed", "Indeed")
def scrape_indeed(query="software engineer", location="", pages=1, delay=2.0):
    """Scrape Indeed: Web Unlocker for search → Dataset API for structured data."""
    if not query:
        query = "software engineer"

    # Step 1: Collect job URLs via Web Unlocker
    all_urls = []
    for page in range(pages):
        start = page * 10
        url = _build_search_url(query, location, start)
        print(f"[indeed] Searching page {page+1}/{pages}: {url}")
        try:
            html = fetch_html(url)
            job_urls = _extract_job_urls(html)
            print(f"[indeed] Found {len(job_urls)} job URLs on page {page+1}")
            all_urls.extend(job_urls)
        except Exception as e:
            print(f"[indeed] Search error on page {page+1}: {e}")
            break
        if page < pages - 1:
            time.sleep(delay)

    # Dedupe
    all_urls = list(dict.fromkeys(all_urls))
    print(f"[indeed] Total unique URLs: {len(all_urls)}")

    if not all_urls:
        print("[indeed] No job URLs found, falling back to HTML parsing")
        # Fallback: parse directly from search results
        for page in range(pages):
            start = page * 10
            url = _build_search_url(query, location, start)
            try:
                html = fetch_html(url)
                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("div.job_seen_beacon")
                for card in cards:
                    title_el = card.select_one("h2.jobTitle a, h2 a")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)
                    href = title_el.get("href", "")
                    if href.startswith("/"):
                        href = BASE + href
                    company_el = card.select_one("span[data-testid='company-name']")
                    company = company_el.get_text(strip=True) if company_el else None
                    loc_el = card.select_one("div[data-testid='text-location']")
                    location_text = loc_el.get_text(strip=True) if loc_el else None
                    yield {
                        "title": title, "company": company, "location": location_text,
                        "url": href, "description": None, "posted_date": None,
                    }
            except Exception as e:
                print(f"[indeed] Fallback error: {e}")
        return

    # Step 2: Fetch structured data via Dataset API (batch of up to 10)
    batch_size = 10
    for i in range(0, len(all_urls), batch_size):
        batch = all_urls[i:i + batch_size]
        print(f"[indeed] Fetching structured data for URLs {i+1}-{i+len(batch)}...")
        try:
            records = scrape_dataset("indeed", batch, timeout=180)
            for record in records:
                job = _normalize_dataset_record(record)
                if job["title"] and job["url"]:
                    yield job
            print(f"[indeed] Got {len(records)} structured records")
        except Exception as e:
            print(f"[indeed] Dataset API error: {e}")
            # Fallback: yield raw URLs for manual processing
            for u in batch:
                yield {
                    "title": f"Job listing", "company": None, "location": None,
                    "url": u, "description": None, "posted_date": None,
                }

    print(f"[indeed] Done.")

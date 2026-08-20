"""LinkedIn scraper — hybrid: Web Unlocker search + Dataset API structured data."""
from __future__ import annotations
import re
import time
from typing import Iterator
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from scraper.fetcher import fetch_html, scrape_dataset
from scraper.registry import register

BASE = "https://www.linkedin.com"


def _build_search_url(query, location="", start=0):
    params = f"keywords={quote_plus(query)}"
    if location: params += f"&location={quote_plus(location)}"
    if start: params += f"&start={start}"
    return f"{BASE}/jobs/search/?{params}"


def _extract_job_urls(html):
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    # LinkedIn job links contain /jobs/view/
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/jobs/view/" in href:
            if not href.startswith("http"):
                href = BASE + href
            urls.append(href.split("?")[0])  # clean tracking params
    return list(dict.fromkeys(urls))


def _normalize(record):
    return {
        "title": record.get("job_title", ""),
        "company": record.get("company_name"),
        "location": record.get("job_location"),
        "url": record.get("url", ""),
        "description": record.get("job_summary"),
        "posted_date": record.get("job_posted_time"),
    }


@register("linkedin", "LinkedIn")
def scrape_linkedin(query="software engineer", location="", pages=1, delay=2.0):
    if not query: query = "software engineer"
    all_urls = []
    for page in range(pages):
        url = _build_search_url(query, location, start=page * 25)
        print(f"[linkedin] Searching page {page+1}/{pages}: {url}")
        try:
            html = fetch_html(url)
            job_urls = _extract_job_urls(html)
            print(f"[linkedin] Found {len(job_urls)} job URLs")
            all_urls.extend(job_urls)
        except Exception as e:
            print(f"[linkedin] Search error: {e}")
            break
        if page < pages - 1: time.sleep(delay)

    all_urls = list(dict.fromkeys(all_urls))
    print(f"[linkedin] Total unique URLs: {len(all_urls)}")

    if not all_urls:
        print("[linkedin] No URLs found")
        return

    # Fetch structured data via Dataset API
    for i in range(0, len(all_urls), 10):
        batch = all_urls[i:i+10]
        print(f"[linkedin] Fetching structured data for {len(batch)} jobs...")
        try:
            records = scrape_dataset("linkedin", batch, timeout=180)
            for r in records:
                job = _normalize(r)
                if job["title"] and job["url"]:
                    yield job
            print(f"[linkedin] Got {len(records)} structured records")
        except Exception as e:
            print(f"[linkedin] Dataset API error: {e}")
    print("[linkedin] Done.")

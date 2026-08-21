"""Glassdoor scraper — hybrid: Web Unlocker search + Dataset API structured data."""
from __future__ import annotations
import time
from typing import Iterator
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from scraper.fetcher import fetch_html, scrape_dataset
from scraper.registry import register

BASE = "https://www.glassdoor.com"


def _build_search_url(query, location="", page=1):
    params = f"sc.keyword={quote_plus(query)}"
    if location: params += f"&locKeyword={quote_plus(location)}"
    if page > 1: params += f"&p={page}"
    return f"{BASE}/Job/jobs.htm?{params}"


def _extract_job_urls(html):
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/job-listing/" in href or "/job/" in href:
            if not href.startswith("http"):
                href = BASE + href
            urls.append(href.split("?")[0])
    return list(dict.fromkeys(urls))


def _normalize(record):
    return {
        "title": record.get("job_title") or record.get("title", ""),
        "company": record.get("company_name") or record.get("company"),
        "location": record.get("job_location") or record.get("location"),
        "url": record.get("url", ""),
        "description": record.get("job_summary") or record.get("description"),
        "posted_date": record.get("job_posted_time") or record.get("posted_date"),
    }


@register("glassdoor", "Glassdoor")
def scrape_glassdoor(query="software engineer", location="", pages=1, delay=2.0):
    if not query: query = "software engineer"
    all_urls = []
    for page in range(1, pages + 1):
        url = _build_search_url(query, location, page)
        print(f"[glassdoor] Searching page {page}/{pages}: {url}")
        try:
            html = fetch_html(url)
            job_urls = _extract_job_urls(html)
            print(f"[glassdoor] Found {len(job_urls)} job URLs")
            all_urls.extend(job_urls)
        except Exception as e:
            print(f"[glassdoor] Search error: {e}")
            break
        if page < pages: time.sleep(delay)

    all_urls = list(dict.fromkeys(all_urls))
    print(f"[glassdoor] Total unique URLs: {len(all_urls)}")

    if not all_urls:
        print("[glassdoor] No URLs found")
        return

    for i in range(0, len(all_urls), 10):
        batch = all_urls[i:i+10]
        print(f"[glassdoor] Fetching structured data for {len(batch)} jobs...")
        try:
            records = scrape_dataset("glassdoor", batch, timeout=180)
            for r in records:
                job = _normalize(r)
                if job["title"] and job["url"]:
                    yield job
            print(f"[glassdoor] Got {len(records)} structured records")
        except Exception as e:
            print(f"[glassdoor] Dataset API error: {e}")
    print("[glassdoor] Done.")

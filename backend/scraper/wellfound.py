"""Wellfound (AngelList) scraper — startup jobs via Bright Data."""
from __future__ import annotations
import re
from typing import Iterator
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from scraper.fetcher import fetch_html
from scraper.registry import register

BASE = "https://wellfound.com"

def _build_url(query, location="", page=1):
    params = f"role={quote_plus(query)}"
    if location: params += f"&location={quote_plus(location)}"
    return f"{BASE}/jobs?{params}"

def _parse_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    cards = soup.select("div.styles_jobListing__B9Pin, div[data-test='DefaultListJobItem'], a[href*='/jobs/']")
    if not cards: cards = soup.find_all("div", class_=re.compile(r"job|listing", re.I))
    for card in cards:
        try:
            title_el = card.select_one("h2.styles_jobTitle__tqPG2, div[data-test='JobTitle'], h2 a, a[data-test='JobTitle']")
            if not title_el:
                if card.name == "a" and card.get("href", ""): title_el = card
                else: continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "") if title_el.name == "a" else ""
            if not href:
                link = title_el.find("a") or card.find("a")
                href = link.get("href", "") if link else ""
            if not href.startswith("http"): href = BASE + href if href.startswith("/") else href
            if not href: continue
            company_el = card.select_one("div.styles_startupName__We906, a[data-test='StartupLink']")
            company = company_el.get_text(strip=True) if company_el else None
            loc_el = card.select_one("div.styles_jobLocations__k_fy3, span[data-test='job-location']")
            location = loc_el.get_text(strip=True) if loc_el else None
            jobs.append({"title": title, "company": company, "location": location, "url": href, "description": None, "posted_date": None})
        except Exception: continue
    return jobs

@register("wellfound", "Wellfound")
def scrape_wellfound(query="software engineer", location="", pages=1, delay=2.0):
    if not query: query = "software engineer"
    seen = set()
    url = _build_url(query, location)
    print(f"[wellfound] Fetching: {url}")
    try: html = fetch_html(url)
    except Exception as e: print(f"[wellfound] Error: {e}"); return
    for job in _parse_cards(html):
        if job["url"] not in seen: seen.add(job["url"]); yield job
    print(f"[wellfound] Done. {len(seen)} jobs.")

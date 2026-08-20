"""RemoteOK scraper — remote tech jobs via Bright Data."""
from __future__ import annotations
import re
from typing import Iterator
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from scraper.fetcher import fetch_html
from scraper.registry import register

BASE = "https://remoteok.com"

def _build_url(query=""):
    if query:
        q = query.lower().replace(" ", "-")
        return f"{BASE}/remote-{q}-jobs"
    return f"{BASE}/remote-dev-jobs"

def _parse_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    cards = soup.select("tr.job, tr[data-id], div.job-card, td.job")
    if not cards: cards = soup.find_all("tr", class_=re.compile(r"job", re.I))
    for card in cards:
        try:
            title_el = card.select_one("td.company_and_position a h2, td.job-info h2, h2, a[data-company]")
            if not title_el: continue
            title = title_el.get_text(strip=True)
            link_el = card.select_one("a[href*='/remote-jobs/']")
            href = link_el.get("href", "") if link_el else ""
            if not href.startswith("http"): href = BASE + href if href.startswith("/") else href
            if not href: continue
            company_el = card.select_one("td.company_and_position span.company, span.company")
            company = company_el.get_text(strip=True) if company_el else None
            loc_el = card.select_one("td.job-location, span.location")
            location = loc_el.get_text(strip=True) if loc_el else "Remote"
            date_el = card.select_one("td.date time, time")
            posted = None
            if date_el: posted = date_el.get("datetime") or date_el.get_text(strip=True) or None
            jobs.append({"title": title, "company": company, "location": location, "url": href, "description": None, "posted_date": posted})
        except Exception: continue
    return jobs

@register("remoteok", "RemoteOK")
def scrape_remoteok(query="software engineer", location="", pages=1, delay=2.0):
    if not query: query = "software engineer"
    seen = set()
    url = _build_url(query)
    print(f"[remoteok] Fetching: {url}")
    try: html = fetch_html(url)
    except Exception as e: print(f"[remoteok] Error: {e}"); return
    for job in _parse_cards(html):
        if job["url"] not in seen: seen.add(job["url"]); yield job
    print(f"[remoteok] Done. {len(seen)} jobs.")

"""Dice.com scraper — tech-focused job board via Bright Data."""
from __future__ import annotations
import re
from typing import Iterator
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from scraper.fetcher import fetch_html
from scraper.registry import register

BASE = "https://www.dice.com"

def _build_url(query, location="", page=1):
    url = f"{BASE}/jobs?q={quote_plus(query)}&page={page}&pageSize=20&language=en"
    if location: url += f"&city={quote_plus(location)}"
    return url

def _parse_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    cards = soup.select("div[data-testid='job-card'], div.card-body, div.job-card")
    if not cards: cards = soup.find_all("div", class_=re.compile(r"job|card|result", re.I))
    for card in cards:
        try:
            title_el = card.select_one("a[data-testid='job-card-title-link'], a.job-card__title, h5 a, a[href*='/jobs/detail/']")
            if not title_el: continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            if not href.startswith("http"): href = BASE + href if href.startswith("/") else href
            company_el = card.select_one("div[data-testid='company-name'], span.job-card__company-name")
            company = company_el.get_text(strip=True) if company_el else None
            loc_el = card.select_one("div[data-testid='job-location'], span.job-card__location")
            location = loc_el.get_text(strip=True) if loc_el else None
            desc_el = card.select_one("div[data-testid='job-card-description']")
            description = desc_el.get_text(strip=True) if desc_el else None
            date_el = card.select_one("div[data-testid='job-date']")
            posted = date_el.get_text(strip=True) if date_el else None
            jobs.append({"title": title, "company": company, "location": location, "url": href, "description": description, "posted_date": posted})
        except Exception: continue
    return jobs

@register("dice", "Dice")
def scrape_dice(query="software engineer", location="", pages=1, delay=2.0):
    if not query: query = "software engineer"
    seen = set()
    for page in range(1, pages + 1):
        url = _build_url(query, location, page)
        print(f"[dice] Fetching page {page}/{pages}: {url}")
        try: html = fetch_html(url)
        except Exception as e: print(f"[dice] Error: {e}"); break
        for job in _parse_cards(html):
            if job["url"] not in seen: seen.add(job["url"]); yield job
    print(f"[dice] Done. {len(seen)} jobs.")

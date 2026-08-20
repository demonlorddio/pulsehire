"""SimplyHired scraper — job aggregator via Bright Data."""
from __future__ import annotations
import re
from typing import Iterator
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from scraper.fetcher import fetch_html
from scraper.registry import register

BASE = "https://www.simplyhired.com"

def _build_url(query, location="", page=1):
    params = f"q={quote_plus(query)}"
    if location: params += f"&l={quote_plus(location)}"
    if page > 1: params += f"&pn={page}"
    return f"{BASE}/search?{params}"

def _parse_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    cards = soup.select("article.SerpJob, li[data-testid='serp-ia-card'], div.SerpJob-jobCard, article.job-card")
    if not cards: cards = soup.find_all("article", class_=re.compile(r"job|serp", re.I))
    for card in cards:
        try:
            title_el = card.select_one("h2[data-testid='jobposting-title'] a, a.SerpJob-link, h2 a, a[href*='/job/']")
            if not title_el: continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            if not href.startswith("http"): href = BASE + href if href.startswith("/") else href
            company_el = card.select_one("span.SerpJob-company, span[data-testid='companyName']")
            company = company_el.get_text(strip=True) if company_el else None
            loc_el = card.select_one("span.SerpJob-location")
            location = loc_el.get_text(strip=True) if loc_el else None
            desc_el = card.select_one("p.SerpJob-snippet")
            description = desc_el.get_text(strip=True) if desc_el else None
            jobs.append({"title": title, "company": company, "location": location, "url": href, "description": description, "posted_date": None})
        except Exception: continue
    return jobs

@register("simplyhired", "SimplyHired")
def scrape_simplyhired(query="software engineer", location="", pages=1, delay=2.0):
    if not query: query = "software engineer"
    seen = set()
    for page in range(1, pages + 1):
        url = _build_url(query, location, page)
        print(f"[simplyhired] Fetching page {page}/{pages}: {url}")
        try: html = fetch_html(url)
        except Exception as e: print(f"[simplyhired] Error: {e}"); break
        for job in _parse_cards(html):
            if job["url"] not in seen: seen.add(job["url"]); yield job
    print(f"[simplyhired] Done. {len(seen)} jobs.")

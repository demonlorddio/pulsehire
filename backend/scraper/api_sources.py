"""Direct API scrapers — no Bright Data needed, just public JSON APIs.

Sources: RemoteOK, Arbeitnow, Remotive, Jobicy
"""
from __future__ import annotations
import time
from datetime import datetime, timezone
from typing import Iterator
import requests
from scraper.registry import register

# ── RemoteOK ────────────────────────────────────────────────────────
@register("remoteok", "RemoteOK")
def scrape_remoteok(query="python", pages=1, delay=1.0):
    """RemoteOK public JSON API — 100+ remote jobs, no auth."""
    resp = requests.get("https://remoteok.com/api", timeout=30)
    resp.raise_for_status()
    all_jobs = resp.json()
    # First 2 items are metadata
    jobs = [j for j in all_jobs if isinstance(j, dict) and "position" in j]
    
    query_lower = query.lower()
    for job in jobs:
        title = job.get("position", "")
        tags = " ".join(job.get("tags", [])).lower()
        if query_lower and query_lower not in title.lower() and query_lower not in tags:
            continue
        url = job.get("url", "")
        if not url and job.get("slug"):
            url = f"https://remoteok.com/remote-jobs/{job['slug']}"
        posted = job.get("date", "")
        yield {
            "title": title,
            "company": job.get("company", ""),
            "location": job.get("location", "Remote"),
            "url": url,
            "description": job.get("description", ""),
            "posted_date": posted[:10] if posted else None,
        }


# ── Arbeitnow ───────────────────────────────────────────────────────
@register("arbeitnow", "Arbeitnow")
def scrape_arbeitnow(query="python", pages=1, delay=1.0):
    """Arbeitnow public JSON API — 175+ remote jobs, no auth."""
    resp = requests.get("https://www.arbeitnow.com/api/job-board-api", timeout=30)
    resp.raise_for_status()
    data = resp.json()
    jobs = data.get("data", [])
    
    query_lower = query.lower()
    for job in jobs:
        title = job.get("title", "")
        tags = " ".join(job.get("tags", [])).lower()
        desc = (job.get("description", "") or "").lower()
        if query_lower and query_lower not in title.lower() and query_lower not in tags and query_lower not in desc:
            continue
        # Convert unix timestamp to date string
        created = job.get("created_at")
        if isinstance(created, (int, float)):
            posted = datetime.fromtimestamp(created, tz=timezone.utc).strftime("%Y-%m-%d")
        else:
            posted = str(created)[:10] if created else None
        yield {
            "title": title,
            "company": job.get("company_name", ""),
            "location": job.get("location", "Remote"),
            "url": job.get("url", ""),
            "description": job.get("description", ""),
            "posted_date": posted,
        }


# ── Remotive ────────────────────────────────────────────────────────
@register("remotive", "Remotive")
def scrape_remotive(query="python", pages=1, delay=1.0):
    """Remotive public JSON API — 18+ remote jobs, no auth."""
    resp = requests.get("https://remotive.com/api/remote-jobs?limit=100", timeout=30)
    resp.raise_for_status()
    data = resp.json()
    jobs = data.get("jobs", [])
    
    query_lower = query.lower()
    for job in jobs:
        title = job.get("title", "")
        tags = " ".join(job.get("tags", [])).lower()
        category = (job.get("category", "") or "").lower()
        if query_lower and query_lower not in title.lower() and query_lower not in tags and query_lower not in category:
            continue
        posted = job.get("publication_date", "")[:10]
        yield {
            "title": title,
            "company": job.get("company_name", ""),
            "location": job.get("candidate_required_location", "Remote"),
            "url": job.get("url", ""),
            "description": job.get("description", ""),
            "posted_date": posted if posted else None,
        }


# ── Jobicy ──────────────────────────────────────────────────────────
@register("jobicy", "Jobicy")
def scrape_jobicy(query="python", pages=1, delay=1.0):
    """Jobicy public JSON API — remote tech jobs, no auth."""
    resp = requests.get(f"https://jobicy.com/api/v2/remote-jobs?count=50&tag={query}", timeout=30)
    resp.raise_for_status()
    data = resp.json()
    jobs = data.get("jobs", [])
    
    for job in jobs:
        posted = job.get("pubDate", "")[:10]
        tags = job.get("jobTags", [])
        yield {
            "title": job.get("jobTitle", ""),
            "company": job.get("companyName", ""),
            "location": job.get("jobGeo", "Remote"),
            "url": job.get("url", ""),
            "description": job.get("jobDescription", ""),
            "posted_date": posted if posted else None,
        }

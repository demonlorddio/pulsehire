"""Background scraper — silently collects job data on a schedule.

When the site is running, this scraper runs in the background,
fetching a few jobs at a time from each source. It's designed to:
- Use minimal API credits (batch of 5 jobs per source, every 30 min)
- Never block the user-facing app
- Build up the database over time
- Feed the self-healing demo

Usage:
    # Start the background scraper (runs alongside FastAPI)
    from scraper.background_scraper import start_background_scraper
    start_background_scraper()
"""
from __future__ import annotations

import asyncio
import os
import random
import time
from datetime import datetime, timezone
from typing import Optional

from database import db_session
import services.jobs_service as jobs_service
import services.skills_service as skills_service
from scraper.registry import get_scraper, list_sources
from scraper.skills import extract_skill_ids


# Search queries to cycle through
SEARCH_QUERIES = [
    "software engineer",
    "python developer",
    "full stack developer",
    "react developer",
    "devops engineer",
    "data engineer",
    "machine learning engineer",
    "cloud architect",
    "backend developer",
    "frontend developer",
]

# How often to scrape (in seconds)
SCRAPE_INTERVAL = 1800  # 30 minutes
# How many jobs to fetch per batch
BATCH_SIZE = 5


def _scrape_batch(source: str, query: str) -> dict:
    """Scrape a small batch of jobs from a source."""
    try:
        scrape_fn = get_scraper(source)
    except (ValueError, RuntimeError) as e:
        print(f"[bg-scraper] Skipping {source}: {e}")
        return {"scraped": 0, "new": 0}

    with db_session() as conn:
        run_id = jobs_service.start_scrape_run(conn, source=source, query=query)
        skills = conn.execute("SELECT id, slug, name, aliases FROM skills").fetchall()

        scraped = 0
        new = 0
        try:
            # Only fetch a small batch
            jobs_iter = scrape_fn(query=query)
            for i, raw in enumerate(jobs_iter):
                if i >= BATCH_SIZE:
                    break
                scraped += 1
                job_id = jobs_service.insert_job(
                    conn,
                    title=raw["title"],
                    source=source,
                    url=raw["url"],
                    company=raw.get("company"),
                    location=raw.get("location"),
                    description=raw.get("description"),
                    posted_date=raw.get("posted_date"),
                )
                if job_id is None:
                    continue
                new += 1
                # Extract skill mentions
                day = datetime.now(timezone.utc).date().isoformat()
                text = f"{raw.get('title', '')}\n{raw.get('description', '')}"
                for skill in extract_skill_ids(text, skills):
                    jobs_service.record_skill_mention(conn, job_id, skill["id"], mentioned_in="description")
                    skills_service.bump_daily_count(conn, skill["id"], day, source, 1)

            jobs_service.finish_scrape_run(
                conn, run_id, status="ok", jobs_scraped=scraped, jobs_new=new
            )
        except Exception as e:
            jobs_service.finish_scrape_run(
                conn, run_id, status="failed", jobs_scraped=scraped, jobs_new=new, error=str(e)
            )
            print(f"[bg-scraper] Error scraping {source}: {e}")

    return {"scraped": scraped, "new": new}


def _run_background_cycle():
    """Run one cycle of background scraping across all sources."""
    sources = list_sources()
    query = random.choice(SEARCH_QUERIES)

    print(f"[bg-scraper] Starting cycle — query: '{query}', sources: {sources}")

    for source in sources:
        try:
            result = _scrape_batch(source, query)
            print(f"[bg-scraper] {source}: scraped={result['scraped']}, new={result['new']}")
        except Exception as e:
            print(f"[bg-scraper] {source} failed: {e}")

    print(f"[bg-scraper] Cycle complete.")


def start_background_scraper(interval: int = SCRAPE_INTERVAL):
    """Start the background scraper in a daemon thread.
    
    Only runs if ENABLE_SCHEDULER=true (disabled on Render to save credits).
    
    Args:
        interval: Seconds between scrape cycles (default 30 min)
    """
    import os as _os
    if _os.getenv("ENABLE_SCHEDULER", "false").lower() != "true":
        print("[bg-scraper] Disabled (set ENABLE_SCHEDULER=true to enable)")
        return None
    import threading

    def _loop():
        print(f"[bg-scraper] Background scraper started (interval: {interval}s)")
        while True:
            try:
                _run_background_cycle()
            except Exception as e:
                print(f"[bg-scraper] Cycle error: {e}")
            time.sleep(interval)

    thread = threading.Thread(target=_loop, daemon=True, name="bg-scraper")
    thread.start()
    print(f"[bg-scraper] Daemon thread started")
    return thread

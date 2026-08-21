"""APScheduler setup — runs the scraper on a configurable interval.

Used by main.py's lifespan hook when ENABLE_SCHEDULER=true in .env.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

# Default interval in minutes (overridable via SCRAPE_INTERVAL_MINUTES env var).
DEFAULT_INTERVAL_MINUTES = 60


def _run_scrape_job() -> None:
    """Background job: scrape Indeed for the default query."""
    from scraper.registry import get_scraper
    from scraper.skills import extract_skill_ids
    from database import db_session
    import services.jobs_service as jobs_service
    import services.skills_service as skills_service

    query = os.getenv("SCRAPE_QUERY", "software engineer")
    source = os.getenv("SCRAPE_SOURCE", "indeed")
    pages = int(os.getenv("SCRAPE_MAX_PAGES", "3"))

    print(f"[scheduler] Starting scrape: query={query!r}, source={source}, pages={pages}")

    with db_session() as conn:
        run_id = jobs_service.start_scrape_run(conn, source=source, query=query)
        skills = conn.execute("SELECT id, slug, name, aliases FROM skills").fetchall()

        try:
            scraped = 0
            new = 0
            scrape_fn = get_scraper(source)
            for raw in scrape_fn(query=query, pages=pages):
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
                day = datetime.now(timezone.utc).date().isoformat()
                text = f"{raw.get('title', '')}\n{raw.get('description', '')}"
                for skill in extract_skill_ids(text, skills):
                    jobs_service.record_skill_mention(conn, job_id, skill["id"], mentioned_in="description")
                    skills_service.bump_daily_count(conn, skill["id"], day, source, 1)

            jobs_service.finish_scrape_run(conn, run_id, status="ok", jobs_scraped=scraped, jobs_new=new)
            print(f"[scheduler] Scrape finished: {scraped} scraped, {new} new")
        except Exception as e:
            jobs_service.finish_scrape_run(conn, run_id, status="failed", jobs_scraped=0, jobs_new=0, error=str(e))
            print(f"[scheduler] Scrape failed: {e}")


def start_scheduler() -> None:
    """Start the background scheduler. Call from FastAPI lifespan."""
    interval_hours = float(os.getenv("SCRAPE_INTERVAL_HOURS", "1"))
    interval_minutes = int(interval_hours * 60)
    scheduler = BackgroundScheduler()
    scheduler.add_job(_run_scrape_job, "interval", minutes=interval_minutes, id="indeed_scraper")
    scheduler.start()
    print(f"[scheduler] Scheduler started — scraping every {interval_hours}h ({interval_minutes} min)")

"""FastAPI app — all 7 endpoints from README.md, plus CORS for the React frontend.

Run from the project root:
    uvicorn backend.main:app --reload --port 8000
"""
from __future__ import annotations

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Allow `python backend/main.py` from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv  # noqa: E402
from fastapi import FastAPI, HTTPException, Query  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

# Load .env before any module reads it.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

from database import db_session  # noqa: E402
import services.skills_service as skills_service  # noqa: E402
import services.jobs_service as jobs_service  # noqa: E402
from models import (  # noqa: E402
    Job, RefreshResponse, Skill, SkillTrend, StatsResponse, TopSkill, TrendPoint,
)


# ----- Scraper (lazy import — only loads if Bright Data key is present) -----

def _run_scrape_sync(source: str, query: Optional[str]) -> dict:
    """Blocking scrape. Returns the scrape-run row as a dict.

    Raises a clear error if the scraper module is missing so the route can
    turn it into a 503 instead of a generic 500.
    """
    try:
        from scraper.indeed import scrape_indeed
        from scraper.skills import extract_skill_ids
    except ImportError as e:
        raise RuntimeError(
            "Scraper not implemented yet. Run seed_sample_data.py for demo data, "
            "or implement backend/scraper/indeed.py."
        ) from e

    with db_session() as conn:
        run_id = jobs_service.start_scrape_run(conn, source=source, query=query)
        skills = conn.execute("SELECT id, slug, name, aliases FROM skills").fetchall()
        skills_by_slug = {s["slug"]: dict(s) for s in skills}

        try:
            jobs_iter = scrape_indeed(query=query)
            scraped = 0
            new = 0
            for raw in jobs_iter:
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
                # Extract skill mentions and bump daily counts.
                day = datetime.utcnow().date().isoformat()
                text = f"{raw.get('title','')}\n{raw.get('description','')}"
                for skill in extract_skill_ids(text, skills):
                    jobs_service.record_skill_mention(conn, job_id, skill["id"], mentioned_in="description")
                    skills_service.bump_daily_count(conn, skill["id"], day, source, 1)
            jobs_service.finish_scrape_run(
                conn, run_id, status="ok", jobs_scraped=scraped, jobs_new=new
            )
            return {"status": "ok", "jobs_scraped": scraped, "jobs_new": new, "run_id": run_id}
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            jobs_service.finish_scrape_run(
                conn, run_id, status="failed", jobs_scraped=0, jobs_new=0, error=str(e)
            )
            raise


# ----- App + lifecycle ------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: start the scraper scheduler. Shutdown: nothing to clean up."""
    if os.getenv("ENABLE_SCHEDULER", "false").lower() == "true":
        try:
            from scraper.scheduler import start_scheduler
            start_scheduler()
            print("⏰ Scheduler started.")
        except Exception as e:  # noqa: BLE001
            print(f"⚠️ Scheduler failed to start: {e}")
    yield


app = FastAPI(
    title="PulseHire API",
    description="Real-time pulse of the tech job market.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the React dev server.
_origins_raw = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins_raw.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- Endpoints ------------------------------------------------------------

@app.get("/")
def root():
    return {"app": "PulseHire", "docs": "/docs", "version": "0.1.0"}


@app.get("/api/skills/list", response_model=list[Skill])
def list_skills(category: Optional[str] = Query(None, description="Filter by category")):
    rows = skills_service.list_skills(category=category)
    return [dict(r) for r in rows]


@app.get("/api/skills/top", response_model=list[TopSkill])
def top_skills(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    source: Optional[str] = Query(None, description="Filter by source: 'indeed', 'naukri'"),
):
    rows = skills_service.top_skills(limit=limit, days=days, source=source)
    return [dict(r) for r in rows]


@app.get("/api/skills/trend", response_model=SkillTrend)
def skill_trend(
    skill: str = Query(..., description="Skill slug, e.g. 'rust'"),
    days: int = Query(30, ge=1, le=365),
):
    result = skills_service.skill_trend(slug=skill, days=days)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown skill: {skill!r}")
    return {
        "skill": result["skill"],
        "slug": result["slug"],
        "points": [TrendPoint(**p) for p in result["points"]],
    }


@app.get("/api/jobs", response_model=list[Job])
def list_jobs(
    skill: Optional[str] = Query(None, description="Filter by skill slug"),
    location: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    rows = jobs_service.list_jobs(skill=skill, location=location, source=source, limit=limit)
    return [dict(r) for r in rows]


@app.get("/api/locations", response_model=list[str])
def list_locations():
    return skills_service.list_locations()


@app.get("/api/stats", response_model=StatsResponse)
def stats():
    return skills_service.stats()


@app.post("/api/refresh", response_model=RefreshResponse)
async def refresh(source: str = Query("indeed"), query: Optional[str] = Query(None)):
    """Trigger a fresh scrape. Runs synchronously in a thread so we don't block the event loop."""
    if not os.getenv("BRIGHTDATA_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="Scraper not configured: BRIGHTDATA_API_KEY is missing. "
                   "Add it to your .env or use seed_sample_data.py for demo data.",
        )
    try:
        result = await asyncio.to_thread(_run_scrape_sync, source, query)
    except RuntimeError as e:
        # Scraper module not implemented yet — surface as 503, not 500.
        raise HTTPException(status_code=503, detail=str(e)) from e
    return {
        "status": result["status"],
        "source": source,
        "query": query,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "jobs_scraped": result["jobs_scraped"],
        "jobs_new": result["jobs_new"],
        "error_message": None,
    }

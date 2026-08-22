"""FastAPI app — all API endpoints, plus CORS for the React frontend.

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
from scraper.registry import list_source_info  # noqa: E402
from pydantic import BaseModel as _PydanticBase  # noqa: E402
from services.secure_service import parse_in_enclave
from scraper.bdata_scraper import run_bdata_scraper, heal_bdata_scraper, get_collector_id
from scraper.background_scraper import start_background_scraper  # noqa: E402
from models import (  # noqa: E402
    Job, RefreshResponse, Skill, SkillTrend, StatsResponse, TopSkill, TrendPoint,
)




# --- Request model for secure parse endpoint ---
class SecureParseRequest(_PydanticBase):
    job_title: str
    job_description: str

# ----- Scraper (lazy import — only loads if Bright Data key is present) -----

def _run_scrape_sync(source: str, query: Optional[str]) -> dict:
    """Blocking scrape. Returns the scrape-run row as a dict.

    Raises a clear error if the scraper module is missing so the route can
    turn it into a 503 instead of a generic 500.
    """
    try:
        from scraper.registry import get_scraper
        from scraper.skills import extract_skill_ids
    except ImportError as e:
        raise RuntimeError(
            "Scraper registry not found. Run seed_sample_data.py for demo data."
        ) from e

    scrape_fn = get_scraper(source)

    with db_session() as conn:
        run_id = jobs_service.start_scrape_run(conn, source=source, query=query)
        skills = conn.execute("SELECT id, slug, name, aliases FROM skills").fetchall()
        # skills loaded for extraction

        try:
            jobs_iter = scrape_fn(query=query)
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
                day = datetime.now(timezone.utc).date().isoformat()
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
            print(f"[scrape] FAILED source={source} query={query}: {type(e).__name__}: {e}")
            jobs_service.finish_scrape_run(
                conn, run_id, status="failed", jobs_scraped=0, jobs_new=0, error=str(e)
            )
            raise


# ----- App + lifecycle ------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB, start scraper scheduler. Shutdown: nothing to clean up."""
    # Auto-create tables if they don't exist
    try:
        from init_db import init_db
        init_db()
        print("[startup] Database tables verified")
    except Exception as e:
        print(f"[startup] DB init warning: {e}")

    # Start background scraper — silently collects data every 30 min
    try:
        start_background_scraper()
        print("[bg-scraper] Background scraper initialized")
    except Exception as e:
        print(f"[bg-scraper] Failed to start: {e}")

    # Auto-scrape on startup if DB is empty (Render wipes SQLite on restart)
    try:
        with db_session() as conn:
            job_count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        if job_count == 0 and os.getenv("BRIGHTDATA_API_KEY"):
            print("[startup] DB empty — scraping LinkedIn to populate data...")
            def _startup_scrape():
                sources_queries = [
                    ("linkedin", [
                        "python developer", "react developer",
                        "data engineer", "devops engineer",
                        "software engineer", "machine learning engineer",
                    ]),
                ]
                for source, queries in sources_queries:
                    for q in queries:
                        try:
                            _run_scrape_sync(source, q)
                            print(f"[startup] Scraped {source}: {q}")
                        except Exception as e:
                            print(f"[startup] {source} scrape failed for {q}: {e}")
            asyncio.get_event_loop().run_in_executor(None, _startup_scrape)
        else:
            print(f"[startup] DB has {job_count} jobs — skipping auto-scrape")
    except Exception as e:
        print(f"[startup] Auto-scrape check failed: {e}")

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

# CORS — allow all origins for hackathon demo.
_origins_raw = "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- Endpoints ------------------------------------------------------------



@app.post("/api/bdata/run")
async def bdata_run(
    source: str = Query("indeed", description="Source: indeed, linkedin, glassdoor"),
    url: str = Query("https://www.indeed.com/jobs?q=software+engineer", description="URL to scrape"),
):
    """Run a Bright Data Scraper Studio scraper via bdata CLI."""
    collector_id = get_collector_id(source)
    if not collector_id:
        raise HTTPException(
            status_code=404,
            detail=f"No Collector ID for source '{source}'. Run 'bdata scraper create' first."
        )
    try:
        jobs = await asyncio.to_thread(run_bdata_scraper, collector_id, url)
        return {"status": "ok", "source": source, "collector_id": collector_id, "jobs": jobs, "count": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bdata/heal")
async def bdata_heal(
    source: str = Query("indeed"),
    description: str = Query(..., description="What broke"),
):
    """Self-heal a broken scraper via bdata CLI."""
    collector_id = get_collector_id(source)
    if not collector_id:
        raise HTTPException(status_code=404, detail=f"No Collector ID for source '{source}'")
    try:
        result = await asyncio.to_thread(heal_bdata_scraper, collector_id, description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health_check():
    """Health check — verify DB is reachable."""
    try:
        with db_session() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unreachable: {e}")



@app.post("/api/secure/parse")
def secure_parse(req: SecureParseRequest):
    """Parse a job posting inside a simulated TEE secure enclave."""
    return parse_in_enclave(req.job_description, req.job_title)


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
    source: str = Query(None, description="Filter by source slug"),
):
    result = skills_service.skill_trend(slug=skill, days=days, source=source)
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


@app.get("/api/sources")
def list_sources():
    """Return all registered scraping sources."""
    return list_source_info()


@app.get("/api/stats", response_model=StatsResponse)
def stats():
    return skills_service.stats()


@app.post("/api/refresh", response_model=RefreshResponse)
async def refresh(source: str = Query("indeed"), query: Optional[str] = Query(None)):
    """Trigger a fresh scrape for the given source (indeed, linkedin, glassdoor, etc.)."""
    if not os.getenv("BRIGHTDATA_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="Scraper not configured: BRIGHTDATA_API_KEY is missing. "
                   "Add it to your .env or use seed_sample_data.py for demo data.",
        )
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        result = await asyncio.to_thread(_run_scrape_sync, source, query)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Scrape failed: {type(e).__name__}: {e}")
    finished_at = datetime.now(timezone.utc).isoformat()
    return {
        "status": result["status"],
        "source": source,
        "query": query,
        "started_at": started_at,
        "finished_at": finished_at,
        "jobs_scraped": result["jobs_scraped"],
        "jobs_new": result["jobs_new"],
        "error_message": None,
    }

"""SQL queries for job listings and the scrape-run log."""
from __future__ import annotations

import sqlite3
from typing import Optional

from database import db_session


def list_jobs(
    skill: Optional[str] = None,
    location: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 20,
) -> list[sqlite3.Row]:
    """Recent jobs, optionally filtered by skill slug, location, or source.

    Filtering by skill uses the `skill_mentions` join.
    """
    sql = "SELECT DISTINCT j.* FROM jobs j"
    params: list = []
    if skill:
        sql += " JOIN skill_mentions sm ON sm.job_id = j.id JOIN skills s ON s.id = sm.skill_id"
    where = []
    if skill:
        where.append("s.slug = ?")
        params.append(skill)
    if location:
        where.append("j.location = ?")
        params.append(location)
    if source:
        where.append("j.source = ?")
        params.append(source)
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY j.scraped_at DESC LIMIT ?"
    params.append(limit)
    with db_session() as conn:
        return conn.execute(sql, params).fetchall()


def insert_job(
    conn: sqlite3.Connection,
    title: str,
    source: str,
    url: str,
    company: Optional[str] = None,
    location: Optional[str] = None,
    description: Optional[str] = None,
    posted_date: Optional[str] = None,
) -> Optional[int]:
    """Insert a job, ignoring duplicates by URL. Returns the new id, or None if duplicate."""
    # Check if URL already exists to avoid stale lastrowid from INSERT OR IGNORE
    existing = conn.execute("SELECT id FROM jobs WHERE url = ?", (url,)).fetchone()
    if existing:
        return None
    cur = conn.execute(
        "INSERT INTO jobs (title, company, location, source, url, description, posted_date) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (title, company, location, source, url, description, posted_date),
    )
    return cur.lastrowid


def record_skill_mention(
    conn: sqlite3.Connection, job_id: int, skill_id: int, mentioned_in: str = "description"
) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO skill_mentions (job_id, skill_id, mentioned_in) VALUES (?, ?, ?)",
        (job_id, skill_id, mentioned_in),
    )


def start_scrape_run(conn: sqlite3.Connection, source: str, query: Optional[str]) -> int:
    """Create a 'running' log row, return its id."""
    cur = conn.execute(
        "INSERT INTO scrape_runs (source, query, started_at, status) VALUES (?, ?, CURRENT_TIMESTAMP, 'running')",
        (source, query),
    )
    return cur.lastrowid


def finish_scrape_run(
    conn: sqlite3.Connection,
    run_id: int,
    *,
    status: str,
    jobs_scraped: int,
    jobs_new: int,
    error: Optional[str] = None,
) -> None:
    conn.execute(
        "UPDATE scrape_runs SET status = ?, finished_at = CURRENT_TIMESTAMP, "
        "jobs_scraped = ?, jobs_new = ?, error_message = ? WHERE id = ?",
        (status, jobs_scraped, jobs_new, error, run_id),
    )

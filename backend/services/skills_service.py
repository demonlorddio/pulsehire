"""SQL queries for the chart endpoints (top skills, trends, locations, stats).

Routes call these; routes never write SQL themselves.
"""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from typing import Optional

from database import db_session


# ----- Reads ----------------------------------------------------------------

def list_skills(category: Optional[str] = None) -> list[sqlite3.Row]:
    """All tracked skills, optionally filtered by category."""
    sql = "SELECT * FROM skills"
    params: tuple = ()
    if category:
        sql += " WHERE category = ?"
        params = (category,)
    sql += " ORDER BY name"
    with db_session() as conn:
        return conn.execute(sql, params).fetchall()


def get_skill_by_slug(slug: str) -> Optional[sqlite3.Row]:
    with db_session() as conn:
        return conn.execute("SELECT * FROM skills WHERE slug = ?", (slug,)).fetchone()


def top_skills(limit: int = 10, days: int = 30, source: Optional[str] = None) -> list[sqlite3.Row]:
    """Top N skills by mention count in the last `days` days.

    Counts from `daily_skill_counts` (pre-aggregated = fast).
    """
    sql = """
        SELECT
            s.id        AS skill_id,
            s.name      AS skill,
            s.slug      AS slug,
            s.category  AS category,
            s.is_emerging AS is_emerging,
            COALESCE(SUM(d.count), 0) AS count
        FROM skills s
        LEFT JOIN daily_skill_counts d
            ON d.skill_id = s.id
           AND d.date >= DATE('now', ?)
        """
    params: list = [f"-{days} days"]
    if source:
        sql += " AND d.source = ?"
        params.append(source)
    sql += """
        GROUP BY s.id
        ORDER BY count DESC, s.name
        LIMIT ?
    """
    params.append(limit)
    with db_session() as conn:
        return conn.execute(sql, params).fetchall()


def skill_trend(slug: str, days: int = 30, source: Optional[str] = None) -> Optional[dict]:
    """Daily count series for a skill over the last `days` days.

    Returns {skill, slug, points: [{date, count}, ...]} or None if skill unknown.
    Zeros are filled in for days with no data so the line chart doesn't have gaps.
    """
    with db_session() as conn:
        skill = conn.execute("SELECT id, name, slug FROM skills WHERE slug = ?", (slug,)).fetchone()
        if not skill:
            return None
        sql = """
            SELECT date, SUM(count) AS count
            FROM daily_skill_counts
            WHERE skill_id = ? AND date >= DATE('now', ?)
        """
        params: list = [skill["id"], f"-{days} days"]
        if source:
            sql += " AND source = ?"
            params.append(source)
        sql += " GROUP BY date ORDER BY date"
        rows = conn.execute(sql, params).fetchall()

    # Build a dense series so the chart is continuous.
    by_date = {row["date"]: row["count"] for row in rows}
    points = []
    start = date.today() - timedelta(days=days - 1)
    for i in range(days):
        d = start + timedelta(days=i)
        points.append({"date": d.isoformat(), "count": by_date.get(d.isoformat(), 0)})
    return {"skill": skill["name"], "slug": skill["slug"], "points": points}


def list_locations() -> list[str]:
    """Distinct non-null locations, most common first."""
    with db_session() as conn:
        rows = conn.execute(
            "SELECT location, COUNT(*) AS n FROM jobs "
            "WHERE location IS NOT NULL AND location != '' "
            "GROUP BY location ORDER BY n DESC LIMIT 50"
        ).fetchall()
    return [r["location"] for r in rows]


def list_sources() -> list[str]:
    """Distinct job sources currently in the DB."""
    with db_session() as conn:
        rows = conn.execute("SELECT DISTINCT source FROM jobs ORDER BY source").fetchall()
    return [r["source"] for r in rows]


def stats() -> dict:
    """Dashboard-level stats: totals + last refresh info."""
    with db_session() as conn:
        total_jobs = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        total_mentions = conn.execute("SELECT COUNT(*) FROM skill_mentions").fetchone()[0]
        skills_tracked = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
        last_run = conn.execute(
            "SELECT * FROM scrape_runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        sources = [r["source"] for r in conn.execute(
            "SELECT DISTINCT source FROM jobs ORDER BY source"
        ).fetchall()]
    return {
        "total_jobs": total_jobs,
        "total_skill_mentions": total_mentions,
        "skills_tracked": skills_tracked,
        "last_refresh": last_run["finished_at"] if last_run else None,
        "last_refresh_status": last_run["status"] if last_run else None,
        "sources": sources,
    }


# ----- Writes (used by scraper + seeder) ------------------------------------

def bump_daily_count(conn: sqlite3.Connection, skill_id: int, day: str, source: str, delta: int = 1) -> None:
    """Increment a (skill, day, source) counter, creating the row if needed."""
    conn.execute(
        """
        INSERT INTO daily_skill_counts (skill_id, date, source, count)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(skill_id, date, source)
        DO UPDATE SET count = count + excluded.count
        """,
        (skill_id, day, source, delta),
    )

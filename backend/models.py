"""Pydantic models for request/response shapes.

These are the contracts the API exposes. Services return dicts, routes wrap
them in these models so OpenAPI/Swagger gets clean schemas.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

SkillCategory = Literal["language", "frontend", "backend", "ai-ml", "devops", "database", "mobile", "emerging"]
ScrapeStatus = Literal["running", "ok", "failed"]


# ----- Core domain -----------------------------------------------------------

class Skill(BaseModel):
    id: int
    name: str
    slug: str
    category: SkillCategory
    is_emerging: bool
    aliases: Optional[list[str]] = None


class Job(BaseModel):
    id: int
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    source: str
    url: str
    description: Optional[str] = None
    posted_date: Optional[date] = None
    scraped_at: datetime
    is_active: bool


# ----- API responses --------------------------------------------------------

class TopSkill(BaseModel):
    """One row in the top-skills bar chart."""
    skill_id: int
    skill: str
    slug: str
    category: str
    is_emerging: bool
    count: int = Field(..., description="Number of job mentions in the time window")


class TrendPoint(BaseModel):
    """One point on a skill's trend line."""
    date: date
    count: int


class SkillTrend(BaseModel):
    skill: str
    slug: str
    points: list[TrendPoint]


class RefreshResponse(BaseModel):
    status: str
    source: str
    query: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None
    jobs_scraped: int
    jobs_new: int
    error_message: Optional[str] = None


class StatsResponse(BaseModel):
    total_jobs: int
    total_skill_mentions: int
    skills_tracked: int
    last_refresh: Optional[datetime] = None
    last_refresh_status: Optional[ScrapeStatus] = None
    sources: list[str] = []

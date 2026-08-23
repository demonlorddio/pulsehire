# System Architecture — PulseHire

> **Stack:** Python + FastAPI (backend) · React + Tailwind CSS (frontend) · SQLite (database) · Bright Data (scraper)

---

## Why This Stack?

| Choice | Why |
|---|---|
| **FastAPI** | Auto-generates API docs, async support |
| **React + Tailwind** | Industry-standard, beautiful UI |
| **SQLite** | Zero setup, perfect for MVP |
| **Bright Data** | Web Unlocker bypasses anti-bot, Dataset API returns structured JSON |

---

## High-Level Architecture

```
USER (browser) → FRONTEND (React) → REST API → BACKEND (FastAPI) → SCRAPER → SQLite
```

**Data Flow:**
1. User opens dashboard → React calls GET /api/skills/top
2. FastAPI queries SQLite → returns JSON
3. User clicks Refresh → POST /api/refresh
4. Backend runs Bright Data Web Unlocker (30-60s)
5. Dataset API extracts structured job data
6. Inserts jobs into SQLite → charts re-render

---

## Components

### Frontend (React + Tailwind)
- TopSkillsChart — clickable bar chart
- SkillTrendChart — 30-day trend line
- FilterPanel — skill, source, time window
- JobList — real jobs with date grouping
- RefreshButton — triggers live scrape
- FloatingParticles — animated background

### Backend (FastAPI)
- /api/skills/top — top skills by count
- /api/skills/trend — daily counts over time
- /api/jobs — filtered job listings
- /api/refresh — trigger scrape
- /api/sources — registered sources
- /api/secure/parse — TEE simulation
- /docs — auto-generated Swagger UI

### Scraper Sources
| Source | Type | Auth |
|---|---|---|
| LinkedIn | Bright Data Web Unlocker + Dataset API | API key |
| RemoteOK | Free JSON API | None |
| Arbeitnow | Free JSON API | None |
| Remotive | Free JSON API | None |
| Jobicy | Free JSON API | None |

### Bright Data Products
1. **Web Unlocker** — bypasses CAPTCHAs on LinkedIn
2. **Dataset API** — returns structured JSON (no HTML parsing)
3. **Scraper Studio** — self-healing scrapers via bdata CLI

---

## Database (SQLite)

| Table | Purpose |
|---|---|
| jobs | Scraped job postings |
| skills | 34 tracked tech skills |
| skill_mentions | Job-to-skill mapping |
| daily_skill_counts | Pre-aggregated for fast charts |
| scrape_runs | Scrape attempt logging |

---

## Deployment
- Frontend → Vercel (auto-deploy from GitHub)
- Backend → Render (auto-deploy from GitHub)
- Database → SQLite (auto-scrapes on startup)

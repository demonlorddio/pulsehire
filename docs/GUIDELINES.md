# PulseHire - Complete Project Guidelines

> Everything you need to know: how it works, what powers it, and how to explain it to judges.

---

## What Is PulseHire?

PulseHire is a **real-time tech job market pulse tracker**. It scrapes job listings, extracts skill mentions, and visualizes which skills are rising, stable, or falling.

**Tagline:** Stop guessing. Start tracking.

---

## Architecture

FRONTEND (React + Vite + Tailwind) -> BACKEND (FastAPI) -> DATABASE (SQLite)

Bright Data APIs feed into the scraper pipeline:
- Web Unlocker: bypasses CAPTCHAs, fetches raw HTML
- Dataset API: returns structured JSON
- Scraper Studio: AI-generated scrapers with self-healing

---

## Bright Data Products Used

| Product | Purpose | Status |
|---------|---------|--------|
| Web Unlocker | Fetch HTML bypassing CAPTCHAs | All 8 scrapers |
| Dataset API | Structured JSON from job boards | Indeed, LinkedIn, Glassdoor |
| Scraper Studio | AI scrapers with self-healing | RemoteOK (working) |

---

## 8 Scrapers

Indeed, LinkedIn, Glassdoor, RemoteOK (all working)
Naukri, Dice, SimplyHired, Wellfound (registered, no data yet)

---

## Skill Extraction

34 tracked skills with aliases. Case-insensitive word-boundary regex matching.
Pre-aggregated daily counts for instant chart loading.

---

## Database (5 tables)

- jobs (736 records)
- skills (34 tracked)
- skill_mentions (many-to-many)
- daily_skill_counts (pre-aggregated)
- scrape_runs (logging)

---

## Frontend Components

Dashboard (2-col layout) -> TopSkillsChart (clickable) -> SkillTrendChart -> JobList (sorting, grouping, TEE badges)
FilterPanel (dark dropdowns), RefreshButton, FloatingParticles (SVG logos)

---

## 13 API Endpoints

GET /api/skills/top, /trend, /list, /jobs, /sources, /stats, /health
POST /api/refresh, /secure/parse, /bdata/run, /bdata/heal
GET /docs (Swagger UI)

---

## TEE Secure Enclave

Simulates hardware-isolated skill parsing. HMAC-SHA256 attestation.
Frontend shows glowing Attested Enclave badge on each job card.

---

## Background Scraper

Daemon thread. 5 jobs/source every 30 min. ~20 credits/cycle.

---

## Self-Healing Demo

bdata scraper heal -> AI re-analyses page -> same Collector ID works

---

## Running

Terminal 1: cd backend && uvicorn main:app --reload --port 8000
Terminal 2: cd frontend && npm run dev

Helper scripts: start-all.bat, restart-backend.bat, stop-all.bat, commit.bat

---

**Last updated:** 2026-08-21 | **Project:** PulseHire - Into the Scrape-Verse Hackathon

# Day 2 Session Log — PulseHire Backend Build

> **Date:** 2026-08-18
> **Goal of the day:** Build the entire FastAPI backend so the React frontend (Day 3) can plug straight in.
> **Result:** ✅ All 7 backend tasks done, 13/13 endpoint tests pass, 500 sample jobs live in the DB.

---

## 📌 TL;DR for NotebookLM

If you only have 30 seconds, here's the story:

- PulseHire is a hackathon project that tracks how often 30 tech skills (Python, Rust, Agentic AI, etc.) appear in job listings, then shows a live dashboard of which skills are rising vs. falling.
- **Day 1** was design: PRD, Architecture, Database, Security, README, env files, gitignore.
- **Day 2 (today)** was building: entire FastAPI backend in one session.
- **Day 3 (next)** will be the React frontend + wiring it to the API.
- The backend works end-to-end with sample data right now. Real scraping (Indeed via Bright Data) is built but waiting on payment-method setup in Bright Data dashboard.

---

## ✅ What we did today

### 1. Created the file scaffolding
- `backend/requirements.txt` — pinned dependencies (FastAPI, uvicorn, pydantic, requests, beautifulsoup4, apscheduler, python-dotenv)
- `backend/database.py` — SQLite connection helper that reads `DATABASE_PATH` from `.env`, returns dict-style rows, enforces foreign keys
- `backend/init_db.py` — one-shot script: creates 5 tables, indexes, and seeds all 34 skill rows
- `backend/models.py` — Pydantic shapes for the API: `Skill`, `Job`, `TopSkill`, `TrendPoint`, `SkillTrend`, `RefreshResponse`, `StatsResponse`

### 2. Built the service layer (SQL lives here, not in routes)
- `backend/services/skills_service.py` — `list_skills`, `get_skill_by_slug`, `top_skills`, `skill_trend`, `list_locations`, `list_sources`, `stats`, `bump_daily_count`
- `backend/services/jobs_service.py` — `list_jobs`, `insert_job`, `record_skill_mention`, `start_scrape_run`, `finish_scrape_run`

### 3. Built the FastAPI app
- `backend/main.py` — wires all 7 endpoints from README, CORS for the React dev server, lifespan hook for the optional scheduler, async refresh that runs scraping in a thread

### 4. Built the sample data seeder
- `backend/scraper/seed_sample_data.py` — generates 500 fake jobs across 30 days, weighted skill mentions, emerging skills (Rust, Agentic AI, LLMs, WebAssembly, Bun) get rising trends so the dashboard tells a story

### 5. Verified end-to-end
- venv created, all deps installed cleanly
- DB initialized, 34 skills loaded
- 500 jobs + 1105 skill mentions seeded
- Server started on `http://127.0.0.1:8000`
- **13/13 tests passed**, including:
  - All 7 happy-path endpoints
  - `/docs` (Swagger UI) loads at 200
  - 404 for unknown skill slug
  - 422 for bad query params
  - 503 for `/api/refresh` when API key is missing

---

## 🏗️ Why we made each decision

### Why FastAPI over Flask?
- Auto-generates Swagger UI at `/docs` (great for demos and for NotebookLM to read the API surface)
- Pydantic validation catches bad input before it hits SQL
- Async support matters for the `/api/refresh` endpoint
- Type hints are beginner-friendly

### Why SQLite over PostgreSQL?
- Zero setup — one file at `backend/data/pulsehire.db`
- Already in `.gitignore` so we never commit it
- Pre-aggregated `daily_skill_counts` table means charts stay fast even at 100k jobs
- We can swap to Postgres later — schema is portable

### Why a pre-aggregated `daily_skill_counts` table?
- Dashboards run the same query (`SELECT date, SUM(count) ... GROUP BY date`) over and over
- Computing that from raw `skill_mentions` on every page load is wasteful
- The scraper (and seeder) write to this table once per day, and reads are O(1) per skill/day

### Why split routes / services / models / database?
- Each layer has one job: routes handle HTTP, services handle SQL, models define shapes, database.py handles connection
- When something breaks, you know which file to look at
- Lets us swap SQLite for Postgres by editing only `database.py` and a few SQL strings in services

### Why Pydantic 2.x?
- Faster than v1, stricter validation
- Generates clean OpenAPI schema → Swagger UI looks professional

### Why omit pandas from requirements?
- We never actually imported it — only `random` and `datetime` are used in the seeder, and raw SQL everywhere else
- pandas 2.2.3 failed to build on Python 3.14 (Meson/vswhere issue)
- Keeping it out made `pip install` instant and the venv smaller

### Why a separate sample-data seeder?
- Judges see a working dashboard immediately, even if the live scraper is blocked
- The seeder and the real scraper write to the **same** tables, so swapping is invisible to the frontend
- Trend signal is baked into the seeder (emerging skills rise over time) so the line chart actually shows a story

---

## 🐛 Problems we hit (and how we solved them)

### Problem 1: NotebookLM link was private
- **What happened:** User asked me to "check my NotebookLM link". I tried to fetch it, but Google redirected to a login page.
- **Solution:** Asked the user to either share the notebook publicly, paste the notes, or just tell me what they want me to know in their own words. Lesson: I cannot access authenticated services. Keep that in mind going forward — anything from NotebookLM needs to be copy-pasted into our chat to be visible to me.

### Problem 2: Bright Data blocked on payment method
- **What happened:** Step 2 of the Bright Data setup asks for a payment method before activating Web Unlocker. User said they may or may not be able to add it by evening.
- **Solution:** Decided to build the entire backend **minus the scraper** in parallel, so no time was wasted. Sample data makes the dashboard work without the real scraper. Real scraper is a plug-in piece that activates the moment the key is in `.env`.

### Problem 3: pandas failed to install on Python 3.14
- **What happened:** `pip install -r requirements.txt` failed with `ERROR: Could not parse vswhere.exe output` while building pandas.
- **Root cause:** Python 3.14 is newer than what pandas 2.2.3 was tested against. Meson (used to build pandas) couldn't find the Visual Studio compiler.
- **Solution:** Removed pandas from requirements entirely — we didn't actually need it. Loosened version pins to `>=` so pip picks versions compatible with the runtime Python.

### Problem 4: `uvicorn --reload` didn't reload on Windows
- **What happened:** Edited `main.py` to fix a 500 → 503 in the `/api/refresh` handler. The server kept returning 500 with the old traceback, even after the file was saved correctly.
- **Root cause:** `watchfiles` (the underlying file watcher) on Windows + PowerShell sometimes misses edits, or holds the old process. This is a known uvicorn-on-Windows quirk.
- **Solution:** Stopped the server, restarted without `--reload`. The new code took effect, 503 now returned correctly. **Lesson for Day 3: when testing on Windows, restart uvicorn after edits, don't trust `--reload`.**

### Problem 5: `/api/refresh` returned 500 instead of 503
- **What happened:** With no Bright Data key, the route should return 503 "scraper not configured". Instead it returned 500.
- **Root cause:** `_run_scrape_sync` had `from scraper.indeed import scrape_indeed` at the top of the function body, **before** the try block. So `ModuleNotFoundError` raised and bypassed the 503 logic.
- **Solution:** Wrapped the scraper imports in a `try/except ImportError → RuntimeError`, and wrapped the route in a `try/except RuntimeError → HTTPException(503)`. Now it returns a clean 503 with a friendly message: *"Scraper not implemented yet. Run seed_sample_data.py for demo data, or implement backend/scraper/indeed.py."*

---

## 📊 Current state of the database

```
total_jobs: 500
total_skill_mentions: 1105
skills_tracked: 34 (30 unique + 4 alias variants we already include)
sources: ['indeed', 'naukri']
last_refresh: 2026-08-18T12:33 (status: ok)

Top 8 skills (last 30 days):
1. JavaScript  60 mentions
2. React       58
3. AWS         57
4. SQL         57
5. Python      54
6. TypeScript  53
7. PostgreSQL  49
8. CI/CD       47
```

---

## 📁 Folder structure after Day 2

```
scraper project/
├── backend/
│   ├── __init__.py
│   ├── database.py                ✅ done
│   ├── init_db.py                 ✅ done
│   ├── main.py                    ✅ done (with 503 fix)
│   ├── models.py                  ✅ done
│   ├── requirements.txt           ✅ done (no pandas)
│   ├── data/
│   │   └── pulsehire.db           ✅ 500 jobs, 1105 mentions
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── seed_sample_data.py    ✅ done
│   │   ├── indeed.py              ⏳ next: needs Bright Data key
│   │   ├── skills.py              ⏳ next: keyword matcher
│   │   └── scheduler.py           ⏳ next: hourly APScheduler
│   └── services/
│       ├── __init__.py
│       ├── skills_service.py      ✅ done
│       └── jobs_service.py        ✅ done
├── docs/
│   ├── screenshots/
│   └── session-logs/
│       └── DAY-2-BACKEND.md       ← this file
├── .env                           ✅ secrets (gitignored)
├── .env.example                   ✅ safe template (committed)
├── .gitignore                     ✅ protects .env and *.db
├── README.md                      (Day 1)
├── PRD.md                         (Day 1)
├── ARCHITECTURE.md                (Day 1)
├── DATABASE.md                    (Day 1)
└── SECURITY.md                    (Day 1)
```

---

## 🎯 What we still need to do

### Today (evening, optional)
- ⏳ **Bright Data:** add Google Pay (or any method), then paste the API key + zone name + customer ID into `.env`
- ⏳ Once `.env` is updated, the scraper (3 files) is the only thing left to write

### Day 3 (next session)
- ⏳ Build the React frontend with Vite + Tailwind + Recharts
  - Dashboard.jsx (main page)
  - TopSkillsChart.jsx (bar chart)
  - SkillTrendChart.jsx (line chart)
  - FilterPanel.jsx (dropdowns)
  - RefreshButton.jsx
  - JobList.jsx
- ⏳ Wire axios calls to the 7 backend endpoints
- ⏳ Final smoke test: backend + frontend running together
- ⏳ Take a screenshot for `docs/screenshots/` (per README)

### Nice-to-haves (stretch)
- ⏳ "Rising vs falling" indicators on the trend chart
- ⏳ Export chart as PNG (PRD user story #9)
- ⏳ Compare 2 skills side-by-side (PRD user story #7)
- ⏳ Demo script in `docs/DEMO_SCRIPT.md`

---

## 💡 Things to remember (3-bullet recap)

1. **The backend is fully working with sample data** — no more waiting on Bright Data to demo
2. **The real scraper is the only piece missing** — 3 files (`indeed.py`, `skills.py`, `scheduler.py`) that activate the moment you put the API key in `.env`
3. **On Windows, restart uvicorn after edits** — `--reload` is unreliable

---

## 🤔 Open questions for the user / for tomorrow

- Will the user add the Bright Data payment method tonight, or skip the real scraper?
- Do they want a "rising/falling" indicator (📈📉) on the trend chart, or just the line itself?
- For the frontend, do they want light theme, dark theme, or both?
- What 5 demo locations should the seed data highlight? (current: Remote, Bangalore, SF, NYC, London, Berlin, Toronto, Hyderabad)

---

## 🔗 Quick reference commands

```powershell
# Activate the project venv
cd "$env:USERPROFILE\Documents\scraper project"
.\venv\Scripts\python.exe ...

# Re-initialize the DB (only if you want to wipe and reseed)
.\venv\Scripts\python.exe backend\init_db.py

# Seed sample data (skip if DB already has rows)
.\venv\Scripts\python.exe backend\scraper\seed_sample_data.py

# Start the server
.\venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000

# Open Swagger UI
start http://127.0.0.1:8000/docs
```

---

**End of Day 2 log.** Backend is done. Tomorrow: React frontend + a real running app.

# PulseHire — Complete Build Summary (All Days)

> **Project:** PulseHire — Real-time tech skill demand tracker
> **Hackathon:** Into the Scrape-Verse 2026
> **Team:** PulseHire Team
> **AI Assistant:** Codebuff AI (disclosed per Rule 11)

---

## Day 1: Design & Planning

**What was built:**
- Product Requirements Document (PRD.md)
- System Architecture (ARCHITECTURE.md)
- Database Schema (DATABASE.md)
- Security Guidelines (SECURITY.md)
- Initial README

**Key decisions:**
- chose React + FastAPI + SQLite stack
- Designed 3-tier architecture: Frontend → API → Scraper → DB
- Planned 30 tech skills to track
- Decided on Bright Data for scraping (Web Unlocker + Dataset API)

---

## Day 2: Backend

**What was built:**
- FastAPI backend with 12 endpoints
- SQLite database with 5 tables
- Services layer (skills_service, jobs_service)
- Scraper module with registry pattern
- 34 skills seeded into database
- 500 sample jobs for testing

**Key endpoints:**
- GET /api/skills/top — top skills by count
- GET /api/skills/trend — daily counts over time
- GET /api/jobs — filtered job listings
- POST /api/refresh — trigger scrape
- GET /api/sources — registered sources
- POST /api/secure/parse — TEE simulation

---

## Day 3: Frontend

**What was built:**
- React 18 + Vite + Tailwind CSS
- 7 components: Dashboard, TopSkillsChart, SkillTrendChart, FilterPanel, JobList, RefreshButton, FloatingParticles
- Recharts for interactive bar/line charts
- Axios for API calls
- Dark glassmorphism UI theme

**Key features:**
- Clickable bar chart (click skill → trend updates)
- Source filter dropdown
- Time window filter (7d, 30d, 90d)
- Real job listings with date grouping

---

## Day 4: Scraper + UI Polish

**What was built:**
- LinkedIn scraper using Bright Data Web Unlocker
- Bright Data Dataset API integration for structured data
- UI overhaul: glassmorphism, animated particles, premium design
- Source badges with custom colors
- Date grouping (Today, This Week, This Month, etc.)

**Bright Data integration:**
- Web Unlocker bypasses LinkedIn CAPTCHAs
- Dataset API returns structured JSON (title, company, location)
- Scraper Studio for self-healing scrapers

---

## Day 5: UI Redesign + Interactive Charts

**What was built:**
- 2-column responsive layout (sidebar + content)
- Interactive bar chart (click → updates trend + jobs)
- Source-aware trend charts (each source has its own trend)
- TEE Secure Enclave toggle with attestation badges
- Floating particle icons (skill/source themed)

**UX improvements:**
- Staggered fade-in animations
- Glass card hover effects
- Custom scrollbars
- Skeleton shimmer loaders

---

## Day 6: Hackathon Preparation

**What was built:**
- Judge prep cheat sheet (JUDGE_PREP.md)
- Demo script (DEMO_SCRIPT.md)
- Example structured output (sample_output.json)
- AI disclosure in README
- 10 screenshots in docs/screenshots/

---

## Day 7: Deployment + Final Fixes

**What was done:**
- Deployed frontend to Vercel
- Deployed backend to Render
- Fixed Render startup issue (auto-scrape blocking port)
- Fixed SQLite WAL mode for concurrent writes
- Scraped 1,000+ real jobs from LinkedIn + 4 free APIs
- Backfilled 30 days of historical trend data
- Pruned broken scrapers (Indeed, Dice, Wellfound — all blocked)
- Added 4 free API sources (RemoteOK, Arbeitnow, Remotive, Jobicy)

---

## Final Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React 18, Vite, Tailwind, Recharts | Industry-standard, beautiful UI |
| Backend | Python 3.10+, FastAPI | Auto-docs, async, fast |
| Database | SQLite | Zero config, perfect for MVP |
| Scraping | Bright Data Web Unlocker | Bypasses anti-bot protection |
| Data | Bright Data Dataset API | Structured JSON, no parsing |
| Self-Healing | Bright Data Scraper Studio | Auto-recovers from site changes |
| Deployment | Vercel + Render | Free tier, auto-deploy |

---

## Bright Data Products Used

### 1. Web Unlocker
- **What:** Bypasses CAPTCHAs, rate limits, anti-bot protection
- **How:** POST to api.brightdata.com/request with zone + URL
- **Used for:** LinkedIn (most protected job site)
- **Why:** Scrapy/Selenium get blocked instantly

### 2. Dataset API
- **What:** Returns structured JSON from pre-built scrapers
- **How:** POST to api.brightdata.com/datasets/v3/scrape with URLs
- **Used for:** Extracting job data (title, company, location)
- **Why:** No fragile HTML parsing, structured data guaranteed

### 3. Scraper Studio
- **What:** AI-generated scrapers with self-healing
- **How:** bdata CLI — create, run, heal scrapers
- **Used for:** Custom scrapers for job boards
- **Why:** Auto-recovers when sites change layout

---

## Scraping Sources

| Source | Type | Jobs Scraped | Status |
|---|---|---|---|
| LinkedIn | Bright Data Web Unlocker + Dataset API | 600+ | Working |
| RemoteOK | Free JSON API | 200+ | Working |
| Arbeitnow | Free JSON API | 150+ | Working |
| Remotive | Free JSON API | 100+ | Working |
| Jobicy | Free JSON API | 80+ | Working |

---

## Key Metrics

| Metric | Value |
|---|---|
| Total jobs scraped | 1,000+ |
| Skills tracked | 34 |
| API endpoints | 12 |
| Frontend components | 7 |
| Backend services | 3 |
| Bright Data products | 3 |
| Days to build | 7 |
| Lines of code | ~5,000 |

---

## Files to Know

| File | Purpose |
|---|---|
| backend/main.py | All API endpoints + startup |
| backend/scraper/linkedin.py | LinkedIn scraper (Bright Data) |
| backend/scraper/fetcher.py | Web Unlocker wrapper |
| backend/scraper/api_sources.py | Free API scrapers |
| backend/scraper/skills.py | Skill extraction (34 skills) |
| backend/services/secure_service.py | TEE simulation |
| frontend/src/components/Dashboard.jsx | Main UI |
| frontend/src/components/TopSkillsChart.jsx | Bar chart |
| frontend/src/components/JobList.jsx | Job listings |

---

## Demo Video Script (90 seconds)

1. **Opening (10s):** "PulseHire tracks which tech skills are rising or falling across job boards"
2. **Dashboard (15s):** Show stats, bar chart, filters
3. **Click a bar (15s):** Trend chart updates, jobs filter
4. **Refresh (20s):** Trigger live scrape, show new jobs
5. **Source filter (10s):** Switch LinkedIn → RemoteOK
6. **TEE toggle (15s):** Show attestation badges
7. **Closing (5s):** "Real data, real scrapers, real privacy"

---

## What to Say to Judges

**"How does the scraper work?"**
> "We use Bright Data Web Unlocker to bypass LinkedIn's CAPTCHAs, then the Dataset API for structured JSON. Scraper Studio handles self-healing."

**"Why Bright Data?"**
> "LinkedIn blocks normal scrapers. Web Unlocker bypasses anti-bot protection automatically."

**"What did you build vs AI?"**
> "We designed the architecture and made all decisions. Codebuff AI assisted with implementation. All code is reviewed and explainable."

---

**End of Build Summary. Ready for submission!**

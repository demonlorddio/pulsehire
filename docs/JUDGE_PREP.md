# Judge Prep Cheat Sheet — PulseHire

Study this before the demo. Judges will ask about your technical decisions.

---

## Quick Pitch (30 seconds)

"PulseHire tracks which tech skills are rising or falling in the job market.
It scrapes LinkedIn and 4 free job APIs using Bright Data, extracts 34
tracked skills, and shows trends over 30 days. Students can see if Python
or Rust is growing before they invest time learning it."

---

## Key Questions Judges Will Ask

### "How does the scraper work?"

"We use three Bright Data products:

1. **Web Unlocker** fetches LinkedIn search results. LinkedIn blocks normal
   scrapers with CAPTCHAs, but Web Unlocker bypasses them automatically.

2. **Dataset API** takes the job URLs and returns structured JSON — title,
   company, location, description. No fragile HTML parsing.

3. **Scraper Studio** creates self-healing scrapers. If a site changes its
   layout, the scraper re-analyzes the page and recovers automatically.

We also pull from 4 free APIs (RemoteOK, Arbeitnow, Remotive, Jobicy) that
don't need API keys."

### "Why Bright Data instead of Scrapy or Selenium?"

"LinkedIn has aggressive anti-bot protection. Scrapy gets blocked instantly.
Selenium needs a browser and is slow. Bright Data's Web Unlocker handles
CAPTCHAs, rate limits, and fingerprint detection for us. It's the difference
between getting blocked and getting data."

### "Why SQLite instead of PostgreSQL?"

"For a hackathon MVP, SQLite is perfect — zero setup, one file, runs anywhere.
We auto-create tables on startup so it works on Render's free tier without
persistent storage. In production, we'd swap to Postgres."

### "What is the TEE Secure Enclave?"

"It's a simulation of a Trusted Execution Environment — hardware-isolated
memory where sensitive data gets parsed. We generate a SHA-256 attestation
signature for each job to prove it was processed securely. In production,
this would use Intel SGX or ARM TrustZone."

### "How do you handle data freshness?"

"The background scraper runs every 30 minutes via APScheduler. When the
server starts with an empty database, it auto-scrapes 4 LinkedIn queries
to populate data. Users can also click Refresh for instant scraping."

### "What about rate limiting?"

"We respect servers with 2-second delays between requests. Bright Data
handles rate limiting on their end. The free APIs have their own limits
but we only fetch once per query."

### "What did you build vs what did AI help with?"

"We designed the architecture, chose the tech stack, and made all product
decisions. Codebuff AI assisted with implementation — writing boilerplate,
debugging, and documentation. We reviewed and verified all code. The scraper
logic, API integration, and frontend components are all understood and
explainable."

---

## Architecture Diagram (memorize this)

```
Frontend (React) → REST API (FastAPI) → Service Layer → SQLite
                                      ↓
                               Scraper Module
                              ↙     ↓      ↘
                      LinkedIn  RemoteOK  Arbeitnow
                   (Bright Data)  (Free)    (Free)
```

---

## Numbers to Remember

| Metric | Value |
|---|---|
| Skills tracked | 34 |
| Scraping sources | 5 (LinkedIn + 4 free APIs) |
| Jobs in database | 1,000+ |
| API endpoints | 12 |
| Bright Data products | 3 (Web Unlocker, Dataset API, Scraper Studio) |
| Frontend components | 7 |
| Backend services | 3 (skills, jobs, secure) |

---

## Tech Decisions You Made

1. **React over Streamlit** — looks more professional, industry-standard
2. **FastAPI over Flask** — auto-generates API docs, async support
3. **SQLite over Postgres** — zero config for hackathon MVP
4. **Recharts over D3** — easier to implement, still looks great
5. **Tailwind over custom CSS** — faster development, consistent design
6. **Web Unlocker over Scrapy** — handles anti-bot protection
7. **Dataset API over BeautifulSoup** — structured data, no parsing
8. **Pre-aggregated counts** — charts load instantly instead of querying raw data

---

## Files to Know

| File | What it does |
|---|---|
| backend/main.py | All API endpoints + startup logic |
| backend/scraper/linkedin.py | LinkedIn scraper (Bright Data) |
| backend/scraper/fetcher.py | Web Unlocker wrapper |
| backend/scraper/api_sources.py | Free API scrapers |
| backend/scraper/skills.py | Skill extraction (34 skills) |
| backend/services/secure_service.py | TEE simulation |
| frontend/src/components/Dashboard.jsx | Main UI |
| frontend/src/components/TopSkillsChart.jsx | Bar chart |
| frontend/src/components/JobList.jsx | Job listings |

---

## Demo Flow (90 seconds)

1. **Opening** (10s) — "PulseHire tracks skill demand across job boards"
2. **Dashboard** (15s) — show bar chart, metric strip
3. **Click a bar** (15s) — trend chart updates, job listings filter
4. **Refresh** (20s) — trigger live scrape, show new jobs appearing
5. **Source filter** (10s) — switch between LinkedIn, RemoteOK, etc.
6. **TEE toggle** (15s) — show attestation badges
7. **Closing** (5s) — "Real data, real scrapers, real privacy"

---

## If Live Scrape Fails

Don't panic. Say: "We have 1,000+ jobs already scraped. The scraper works
but takes 60-120 seconds due to Bright Data's anti-bot processing."
Then move on to showing the existing data.

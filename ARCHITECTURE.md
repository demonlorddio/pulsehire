# System Architecture — PulseHire

> **Stack:** Python + FastAPI (backend) · React + Tailwind CSS (frontend) · SQLite (database) · APScheduler (scraper)

---

## 🎯 Why This Stack?

| Choice | Why it fits a beginner hackathon |
|---|---|
| **FastAPI** | Easy Python, auto-generates API docs, less code than Flask |
| **React** | Industry-standard, tons of tutorials, judges love it |
| **Tailwind CSS** | No need to write custom CSS — looks pro with utility classes |
| **SQLite** | Zero setup, one file, perfect for MVP |
| **APScheduler** | Python library to run the scraper on a schedule (no extra server) |

---

## 🧱 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                │
│                    (opens in browser)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ clicks around
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND  (React + Tailwind)                │
│   ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│   │  Bar Chart  │  │  Trend Line  │  │  Filters/Form   │   │
│   │  Top Skills │  │  Over Time   │  │  Skill/Location │   │
│   └─────────────┘  └──────────────┘  └─────────────────┘   │
│   Talks to backend via HTTP (fetch / axios)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │  HTTP requests
                           │  GET /api/skills/top
                           │  GET /api/skills/trend?skill=rust
                           │  POST /api/refresh
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND  (FastAPI - Python)                │
│   ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│   │  /skills/top    │  │ /skills/trend   │  │ /refresh   │ │
│   │  Returns counts │  │ Returns series  │  │ Triggers   │ │
│   │                 │  │  over time      │  │  scraper   │ │
│   └────────┬────────┘  └────────┬────────┘  └─────┬──────┘ │
│            └────────────┬───────┘                  │        │
│                         ▼                          │        │
│              ┌──────────────────────┐              │        │
│              │    SERVICE LAYER     │◄─────────────┘        │
│              │  (business logic)    │                       │
│              └──────────┬───────────┘                       │
│                         ▼                                   │
│              ┌──────────────────────┐                       │
│              │   DATABASE (SQLite)  │                       │
│              │  jobs, skill_mentions│                       │
│              └──────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │  reads/writes
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                  SCRAPER  (Python)                          │
│   ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │
│   │ Indeed.py  │  │ Naukri.py  │  │   skills.py        │   │
│   │ Scrapes    │  │ (stretch)  │  │  Keyword matcher   │   │
│   │ job posts  │  │            │  │                    │   │
│   └─────┬──────┘  └─────┬──────┘  └─────────┬──────────┘   │
│         └───────┬───────┘                    │              │
│                 ▼                            │              │
│        ┌─────────────────┐                   │              │
│        │  Scheduler      │                   │              │
│        │ (APScheduler)   │                   │              │
│        │ Runs hourly     │                   │              │
│        └────────┬────────┘                   │              │
│                 │                            │              │
│                 ▼                            ▼              │
│        ┌──────────────────────────────────────────┐         │
│        │  Writes to SQLite (jobs + skill_mentions)│         │
│        └──────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Breakdown

### 1. Frontend — React + Tailwind

**What it does:** What the user sees and clicks.

**Pages/Components:**

| Component | Purpose |
|---|---|
| `<Dashboard />` | Main page, contains everything |
| `<TopSkillsChart />` | Bar chart of top 10 skills |
| `<SkillTrendChart />` | Line chart of a skill over time |
| `<FilterPanel />` | Dropdowns for skill/location |
| `<RefreshButton />` | Triggers backend to re-scrape |
| `<JobList />` | Sample jobs for selected skill |

**Tech you'll use:**
- `react` — UI library
- `recharts` or `chart.js` — for charts (easier than D3)
- `axios` — to call the backend
- `tailwindcss` — for styling (no CSS files needed)

**Folder structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx
│   │   ├── TopSkillsChart.jsx
│   │   ├── SkillTrendChart.jsx
│   │   ├── FilterPanel.jsx
│   │   └── RefreshButton.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css        (just tailwind imports)
├── public/
├── package.json
├── tailwind.config.js
└── vite.config.js
```

---

### 2. Backend — FastAPI (Python)

**What it does:** Serves data to the frontend and runs the scraper on demand.

**API Endpoints (the URLs the frontend calls):**

| Method | Endpoint | What it does |
|---|---|---|
| `GET` | `/api/skills/top?limit=10` | Returns top N skills by count |
| `GET` | `/api/skills/trend?skill=rust&days=30` | Returns daily counts for one skill |
| `GET` | `/api/skills/list` | Returns all 30 tracked skills |
| `GET` | `/api/jobs?skill=python&limit=20` | Returns sample jobs for a skill |
| `GET` | `/api/locations` | Returns available locations |
| `POST` | `/api/refresh` | Triggers scraper manually |
| `GET` | `/api/stats` | Total jobs, last refresh time, etc. |
| `GET` | `/docs` | **Auto-generated API docs (free with FastAPI!)** |

**Folder structure:**
```
backend/
├── main.py              # FastAPI app + all routes
├── database.py          # SQLite connection + queries
├── models.py            # Pydantic models (data shapes)
├── services/
│   ├── skills_service.py
│   └── jobs_service.py
├── scraper/
│   ├── __init__.py
│   ├── indeed.py        # Indeed scraper
│   ├── naukri.py        # (stretch) Naukri scraper
│   ├── skills.py        # Keyword list + matcher
│   └── scheduler.py     # APScheduler setup
├── data/
│   └── pulsehire.db     # SQLite file (auto-created)
├── requirements.txt
└── .env                 # Config (API keys, etc.)
```

---

### 3. Scraper Module (Python)

**What it does:** Pulls job listings from job boards and extracts skills.

**How it works (simple version):**

```python
# scraper/indeed.py (simplified)
def scrape_indeed(query="software engineer", pages=2):
    jobs = []
    for page in range(pages):
        url = f"https://www.indeed.com/jobs?q={query}&start={page*10}"
        html = requests.get(url, headers=HEADERS).text
        soup = BeautifulSoup(html, "html.parser")
        for card in soup.find_all("div", class_="job_seen_beacon"):
            jobs.append({
                "title":    card.find("h2").text,
                "company":  card.find("span", class_="companyName").text,
                "location": card.find("div", class_="companyLocation").text,
                "source":   "indeed",
                "url":      "https://indeed.com" + card.find("a")["href"]
            })
        time.sleep(2)  # be polite
    return jobs
```

**Skill extraction:**
```python
# scraper/skills.py
SKILLS = ["python", "rust", "react", "agentic ai", "langchain", ...]

def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    return [s for s in SKILLS if s in text_lower]
```

---

### 4. Database — SQLite

**Why SQLite?** No server, no install, one file. Perfect for MVP.

**Schema:**

```sql
-- jobs table: one row per scraped job
CREATE TABLE jobs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    company     TEXT,
    location    TEXT,
    source      TEXT,           -- 'indeed', 'naukri'
    url         TEXT UNIQUE,
    scraped_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- skill_mentions: many-to-many bridge
CREATE TABLE skill_mentions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id        INTEGER,
    skill         TEXT,
    mentioned_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- daily_skill_counts: pre-aggregated for fast chart loading
CREATE TABLE daily_skill_counts (
    skill     TEXT,
    date      DATE,
    count     INTEGER,
    PRIMARY KEY (skill, date)
);
```

**Why a pre-aggregated table?** Drawing a chart on raw data = slow. We summarize once → charts load instantly.

---

### 5. Scheduler — APScheduler

**What it does:** Runs the scraper automatically (e.g., every hour) so the data stays fresh.

```python
# scraper/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_all_scrapers, 'interval', hours=1)
    scheduler.start()
```

**Beginner tip:** If APScheduler feels tricky, just have a "Refresh" button in the UI and skip auto-scheduling. Totally fine for MVP.

---

## 🔄 Data Flow

**Example: User opens dashboard, sees top skills**

```
1. User opens http://localhost:5173
2. React app loads <Dashboard />
3. <Dashboard /> calls GET http://localhost:8000/api/skills/top?limit=10
4. FastAPI receives the request
5. skills_service.py queries SQLite:
   "SELECT skill, SUM(count) FROM daily_skill_counts
    WHERE date >= today - 7 days GROUP BY skill LIMIT 10"
6. Returns JSON: [{"skill": "python", "count": 142}, ...]
7. React receives JSON, renders <TopSkillsChart />
8. User sees a beautiful bar chart 📊
```

**Example: User clicks "Refresh"**

```
1. User clicks "🔄 Refresh" button
2. POST http://localhost:8000/api/refresh
3. FastAPI returns immediately: {"status": "scraping started"}
4. Backend runs scraper in background
5. Scraper hits Indeed, parses HTML, saves to SQLite
6. After 30 seconds, database is updated
7. Frontend polls /api/stats to see if done
8. Charts re-render with fresh data
```

---

## 🚀 Deployment (For Demo Day)

For a **hackathon demo**, run everything locally on the judge's laptop:

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev  # opens on http://localhost:5173

# Terminal 3 (optional): Pre-seed data
python scraper/seed_sample_data.py
```

**For a real deploy** (after hackathon):
- Backend → Railway / Render / Fly.io
- Frontend → Vercel / Netlify
- Database → Postgres (instead of SQLite)

---

## 📦 Final Folder Structure

```
scraper project/
├── PRD.md                  ← already done ✅
├── ARCHITECTURE.md         ← this doc
├── README.md               ← how to run the project
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── services/
│   ├── scraper/
│   ├── data/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
└── docs/
    ├── API.md
    └── DEMO_SCRIPT.md
```

---

## ⚖️ Trade-offs (Honest Beginner Notes)

| Decision | Trade-off |
|---|---|
| FastAPI vs Flask | FastAPI is slightly more code, but auto-docs are a lifesaver |
| React vs Streamlit | React looks more "pro" to judges, but Streamlit is 10x faster to build |
| SQLite vs Postgres | SQLite = zero setup, fine for hackathon. Postgres = needed for real launch |
| APScheduler vs Cron | APScheduler runs in the app. Cron is OS-level. For MVP, use APScheduler |
| Pre-aggregated counts | Slightly more code, but charts become instant |

---

## ✅ Architecture Approved When:

- [x] Backend serves data via REST API
- [x] Frontend consumes API, never touches DB directly
- [x] Scraper is independent of the API
- [x] Data flows one way: Scraper → DB → API → Frontend
- [x] One command starts the whole thing
- [x] Beginner can build this in 24 hours

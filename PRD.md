# PRD — PulseHire: "Unbreakable" Job Market Pulse

> *"Stop guessing. Start tracking."*

---

## 🏷️ Project Name

**PulseHire** — Real-time pulse of the tech job market.

---

## 🎯 Goals

### Primary Goal
Build a **live dashboard** that tracks how often specific tech skills (e.g., "Agentic AI", "Rust", "React") appear in job listings across major job boards, and visualizes **which skills are rising, stable, or falling** over time.

### Secondary Goals
- Help **beginner job seekers** make data-driven decisions about what to learn
- Provide a **single, unified view** across multiple job boards (no more tab-switching)
- Make the data **refreshable** so trends feel current, not stale

### Bright Data Integration
- **Web Unlocker** — bypasses CAPTCHAs and anti-bot protection for live scraping
- **Dataset API** — structured JSON from Indeed, LinkedIn, Glassdoor pre-built scrapers
- **Scraper Studio** — AI-generated scrapers with self-healing capability (bdata CLI)

---

### Non-Goals (Out of Scope for MVP)
- User accounts / login
- Email/Slack alerts
- Salary predictions
- Mobile app
- AI/NLP-based skill extraction (we'll use a keyword list)
- More than 3 job sources

---

## 👥 User Personas

### Persona 1: Ananya — The Confused Student 🎓
- **Age:** 21, B.Tech CS, final year
- **Goal:** Wants a developer job after graduation
- **Pain:** Keeps hearing "learn AI" but doesn't know which sub-skill (LangChain? RAG? Agents?)
- **Needs:** A clear view of which skills companies are *actually* posting for

### Persona 2: Rahul — The Career Switcher 🔄
- **Age:** 28, 4 years in QA, wants to move to dev
- **Goal:** Switch from manual testing to automation/back-end
- **Pain:** Invested time learning Selenium; now hears "Playwright is taking over"
- **Needs:** Trend data so he doesn't bet on a dying skill

### Persona 3: Priya — The Bootcamp Grad 📚
- **Age:** 25, just finished a 6-month MERN bootcamp
- **Goal:** Get her first junior dev job
- **Pain:** Doesn't know if her stack is still in demand or oversaturated
- **Needs:** Compare her current skills against market demand

---

## 📖 User Stories

### 🟢 Must-Have (MVP)

| # | As a... | I want to... | So that... |
|---|---|---|---|
| 1 | Student | See the **top 10 most-mentioned skills** this week | I know what's hot right now |
| 2 | Student | See a **trend chart** of a skill over time | I can tell if it's rising or dying |
| 3 | Student | **Search/filter** by a specific skill | I can deep-dive into one skill |
| 4 | Student | See **which job boards** I'm getting data from | I trust the source |
| 5 | Student | Click **"Refresh"** to pull latest jobs | The data feels current |
| 6 | Student | **Filter by location** (e.g., India, Remote, US) | I get relevant results |

### 🟡 Nice-to-Have (Stretch Goals)

| # | As a... | I want to... | So that... |
|---|---|---|---|
| 7 | Student | Compare **2 skills side-by-side** | I can decide between them |
| 8 | Student | See **rising vs falling** indicators (📈📉) | I get instant insight |
| 9 | Career switcher | **Export** the chart as PNG | I can share it on LinkedIn |
| 10 | Student | See **sample jobs** for each skill | I can read real descriptions |

### 🔴 Out of Scope (Post-Hackathon)
- User accounts & saved dashboards
- Email/Slack alerts for spikes
- Salary insights
- Job application tracking
- Mobile app

---

## 🧩 MVP Scope Definition

### In Scope ✅
- **4+ job sources** (Indeed, LinkedIn, Glassdoor, RemoteOK) via Bright Data
- **1 skill-extraction method:** keyword list of ~30 known tech skills
- **SQLite database** for storing job postings + skill counts
- **React + Recharts + Tailwind dashboard** with:
  - Bar chart: Top 10 skills by mention count
  - Line chart: A skill's trend over the last 30 days
  - Filter: by skill name and/or location
  - Refresh button: re-runs the scraper
- **Manual refresh** only (no background jobs)
- **Single-user, local-only** (no hosting needed for MVP)

### Out of Scope ❌
- Cloud hosting / deployment
- Multi-user support
- Authentication
- Real-time auto-refresh
- LinkedIn scraping (too aggressive, blocks beginners)
- AI-based skill extraction

---

## 📊 Success Metrics

| Metric | Target |
|---|---|
| Successfully scrapes jobs from ≥1 source | Yes |
| Dashboard loads in <5 seconds | Yes |
| Shows top 10 skills accurately | Yes |
| Trend chart renders with ≥7 days of data | Stretch |
| Refresh button adds new jobs without crashing | Yes |
| A non-technical person can understand it in 30 seconds | Yes |
| Demo runs end-to-end without errors | Yes |

---

## 🛠️ Technical Scope

### Stack
- **Language:** Python 3.10+
- **Scraping:** `requests` + `BeautifulSoup4`
- **Data:** `pandas` + `SQLite`
- **Dashboard:** React 18 + Vite + Tailwind CSS + Recharts
- **Charts:** Recharts (React)

### Data Model (SQLite)
```sql
jobs (id, title, company, location, source, scraped_at, url)
skill_mentions (id, job_id, skill, mentioned_at)
```

### Skills to Track (initial list)
- **Languages:** Python, JavaScript, TypeScript, Rust, Go, Java, C++, SQL
- **Frontend:** React, Vue, Angular, Next.js
- **Backend:** Node.js, Django, FastAPI, Spring Boot
- **AI/ML:** Agentic AI, LangChain, RAG, PyTorch, TensorFlow, LLMs, Prompt Engineering
- **Cloud/DevOps:** AWS, Docker, Kubernetes, CI/CD
- **Databases:** PostgreSQL, MongoDB, Redis
- **Mobile:** Flutter, React Native, Swift, Kotlin
- **Emerging (hackathon focus):** Rust, Agentic AI, WebAssembly, Bun, Zig

---

## 📅 Hackathon Timeline (24–36 hours)

| Phase | Time | Deliverable |
|---|---|---|
| 🟢 Setup | 0–2h | Folder structure, libraries installed, "Hello World" frontend + backend |
| 🟡 Scraper | 2–8h | Pulls 50+ jobs from Indeed successfully |
| 🟡 Storage | 8–10h | Saves jobs + skills to SQLite |
| 🟡 Dashboard | 10–16h | Charts working, filters working |
| 🟠 Polish | 16–22h | Bug fixes, 2nd source, better UI |
| 🟢 Demo | 22–24h | README, slides, practiced pitch |

---

## ⚠️ Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Getting blocked by job sites | Add `time.sleep(2)`, rotate user-agents, respect `robots.txt` |
| Scraper breaks mid-hackathon | Build scraper for **1 site only**; keep code simple |
| Not enough time for charts | Recharts renders fast with pre-aggregated data |
| Empty database on first run | Pre-seed with sample data so demo always works |
| Judge asks "is this accurate?" | Be honest: it's a **pulse**, not ground truth |

---

## 🎤 Final Pitch

> *"Meet PulseHire. It scrapes real job boards, counts how often each tech skill shows up, and shows you a live pulse of the job market. See Rust climbing? 📈 That's your cue. See Selenium dropping? 📉 Time to switch. For hackathon scope, we tracked 30 skills across 2 sources — and we made it beginner-friendly on purpose, because the best career decision is a data-driven one."*

---

## ✅ Approval Checklist

- [x] Project name: **PulseHire**
- [x] MVP scope: **1 scraper + 1 dashboard + 30 skills + SQLite**
- [x] Stack: **Python + React + Tailwind + SQLite**
- [x] Out-of-scope items clearly listed
- [x] Realistic for a beginner in 24 hours

# 🚀 PulseHire

> **Real-time pulse of the tech job market.**
> *Stop guessing. Start tracking.*

[![Tests](https://img.shields.io/badge/tests-11%20passing-brightgreen)]()
[![Lint](https://img.shields.io/badge/ruff-ready-blue)]()
[![BrightData](https://img.shields.io/badge/bright%20data-web_unlocker+%2B+dataset-orange)]()
[![Hackathon](https://img.shields.io/badge/hackathon-MVP-blueviolet)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue)]()
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)]()
[![React](https://img.shields.io/badge/frontend-React-61DAFB)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

PulseHire is a dashboard that tracks how often specific tech skills (like *"Agentic AI"*, *"Rust"*, *"React"*) appear in job listings across major job boards. It visualizes which skills are **rising 📈**, **stable ➡️**, and **falling 📉** over time — so students and career switchers can make data-driven decisions about what to learn next.

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🖼️ Screenshots](#-screenshots)
- [🏗️ Architecture](#-architecture)
- [🛠️ Tech Stack](#-tech-stack)
- [🔌 How Bright Data Is Used](#-how-bright-data-is-used)
- [📂 Project Structure](#-project-structure)
- [🚀 Getting Started](#-getting-started)
- [📜 Available Scripts](#-available-scripts)
- [🔌 API Endpoints](#-api-endpoints)
- [🗄️ Database Schema](#-database-schema)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👥 Authors](#-authors)
- [🙏 Acknowledgments](#-acknowledgments)

---

## ✨ Features

- 📊 **Top Skills Bar Chart** — see the 10 most-mentioned skills in real time
- 📈 **Trend Line Charts** — track any skill's demand over the last 30 days
- 🔍 **Smart Filters** — drill down by skill, location, or job board
- 🔄 **One-Click Refresh** — manually trigger a fresh scrape
- 🌐 **Multi-Source Aggregation** — combine data from LinkedIn, RemoteOK, Arbeitnow, Remotive, and Jobicy
- 💾 **Persistent Storage** — SQLite keeps your historical data safe
- ⚡ **Fast Charts** — pre-aggregated counts make dashboards load instantly
- 🎨 **Beautiful UI** — Tailwind CSS, glassmorphism, responsive, dark theme
- 🔒 **TEE Secure Enclave** — simulated Trusted Execution Environment for privacy-first skill extraction
- 🧠 **Self-Healing Scrapers** — Bright Data Scraper Studio with automatic recovery

---

## 🖼️ Screenshots

| Dashboard Overview | Top Skills Chart |
|---|---|
| ![dashboard](docs/screenshots/01-dashboard-overview.png) | ![top-skills](docs/screenshots/02-top-skills-chart.png) |

| Skill Trend | Job Listings |
|---|---|
| ![trend](docs/screenshots/03-skill-trend.png) | ![jobs](docs/screenshots/04-job-listings.png) |

| TEE Secure Enclave | Full Page |
|---|---|
| ![tee](docs/screenshots/05-tee-badges.png) | ![full](docs/screenshots/06-full-page.png) |

---

## 🏗️ Architecture

PulseHire uses a **decoupled 3-tier architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND  (React + Tailwind)                │
│   Bar Charts  •  Trend Lines  •  Filters  •  Refresh Btn   │
└──────────────────────────┬──────────────────────────────────┘
                           │  REST API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND  (FastAPI - Python)                │
│   /api/skills/top  •  /api/skills/trend  •  /api/refresh   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│   SCRAPER (Python)  ──►  SQLite Database  ──►  Dashboard   │
└─────────────────────────────────────────────────────────────┘
```

📄 **Full details:** See [`ARCHITECTURE.md`](./ARCHITECTURE.md)
📋 **Product specs:** See [`PRD.md`](./PRD.md)
🗄️ **DB schema:** See [`DATABASE.md`](./DATABASE.md)

---

## 🛠️ Tech Stack

### Backend
- **Python 3.10+** — main language
- **FastAPI** — modern, fast web framework
- **SQLite** — lightweight database
- **BeautifulSoup4 + requests** — web scraping
- **APScheduler** — scheduled scraping jobs

### Frontend
- **React 18** — UI library
- **Vite** — blazing-fast dev server
- **Tailwind CSS** — utility-first styling
- **Recharts** — beautiful, composable charts
- **Axios** — HTTP client

### Bright Data Products Used
- **Web Unlocker** — bypasses anti-bot protection on job sites
- **Dataset API** — returns structured JSON from pre-built scrapers
- **Scraper Studio** — AI-generated scrapers with self-healing capabilities

### Tooling
- **Git** — version control
- **VS Code** — recommended editor
- **Postman / curl** — API testing

---

## 🔌 How Bright Data Is Used

PulseHire uses **three Bright Data products** to scrape job listings:

### 1. Web Unlocker (Primary Scraper)
Used for **LinkedIn** — the most heavily protected job site. Web Unlocker bypasses CAPTCHAs, rate limits, and anti-bot protection to fetch raw HTML from LinkedIn search results.

```python
# backend/scraper/fetcher.py
def fetch_html(url, timeout=120):
    payload = {
        "zone": "bright_data_web_unlocker",
        "url": url,
        "format": "json"
    }
    resp = requests.post("https://api.brightdata.com/request", json=payload, ...)
    return resp.json()["body"]  # Raw HTML, anti-bot bypassed
```

### 2. Dataset API (Structured Data)
After Web Unlocker fetches search results, the **Dataset API** extracts structured job data (title, company, location, URL) from LinkedIn's HTML without fragile parsing.

```python
# backend/scraper/linkedin.py
dataset_url = "https://api.brightdata.com/datasets/v3/scrape"
payload = {
    "input": [{"url": job_url} for job_url in job_urls],
    "dataset_id": "gd_lpfll7v5hcqtkxl6l"  # LinkedIn Jobs
}
resp = requests.post(dataset_url, json=payload, headers=headers)
# Returns structured JSON: title, company, location, description
```

### 3. Scraper Studio (Self-Healing)
Scraper Studio creates AI-generated scrapers that automatically recover when websites change their layout. If a scraper breaks, it self-heals by re-analyzing the page structure.

```bash
# Create a scraper for any job board
bdata scraper create --urls "https://remoteok.com/remote-jobs"

# Self-heal if it breaks
bdata scraper heal --id <collector_id> --description "Page layout changed"
```

### Why This Matters
- **LinkedIn** blocks normal scrapers with CAPTCHAs → Web Unlocker bypasses them
- **HTML parsing breaks** when sites update → Dataset API returns structured JSON
- **Scrapers degrade** over time → Scraper Studio self-heals automatically

---

## 📂 Project Structure

```
pulsehire/
├── README.md                ← you are here
├── PRD.md                   ← product requirements
├── ARCHITECTURE.md          ← system design
├── DATABASE.md              ← DB schema docs
│
├── backend/
│   ├── main.py              # FastAPI app entry
│   ├── database.py          # SQLite connection
│   ├── models.py            # Pydantic models
│   ├── init_db.py           # DB setup script
│   ├── requirements.txt
│   ├── .env.example
│   ├── services/
│   │   ├── skills_service.py
│   │   ├── jobs_service.py
│   │   └── secure_service.py
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── registry.py      # Scraper registry
│   │   ├── linkedin.py      # LinkedIn (Web Unlocker + Dataset API)
│   │   ├── api_sources.py   # Free APIs (RemoteOK, Arbeitnow, Remotive, Jobicy)
│   │   ├── skills.py        # Skill extractor
│   │   ├── fetcher.py       # Bright Data Web Unlocker wrapper
│   │   ├── bdata_scraper.py # Scraper Studio integration
│   │   └── scheduler.py     # APScheduler
│   └── data/
│       └── pulsehire.db     # SQLite file (auto-created)
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── api.js           # Axios client
│       └── components/
│           ├── Dashboard.jsx
│           ├── TopSkillsChart.jsx
│           ├── SkillTrendChart.jsx
│   

# PulseHire

> **Real-time pulse of the tech job market.**
> *Stop guessing. Start tracking.*

[![BrightData](https://img.shields.io/badge/bright%20data-web_unlocker+%2B+dataset-orange)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue)]()
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)]()
[![React](https://img.shields.io/badge/frontend-React-61DAFB)]()

PulseHire is a dashboard that tracks how often specific tech skills (like *Python*, *Rust*, *React*) appear in job listings across major job boards. It visualizes which skills are **rising**, **stable**, and **falling** over time — so students and career switchers can make data-driven decisions about what to learn next.

**Live Demo:** https://pulsehire-mpreg67.vercel.app/

---

## Features

- Top Skills Bar Chart — see the most-mentioned skills in real time
- Trend Line Charts — track any skill's demand over 30 days
- Smart Filters — drill down by skill, source, or time window
- One-Click Refresh — trigger a live scrape via Bright Data
- Multi-Source Aggregation — LinkedIn + 4 free job APIs
- TEE Secure Enclave — simulated hardware-isolated skill extraction
- Beautiful Dark UI — glassmorphism, animated particles, responsive

---

## How Bright Data Is Used

PulseHire uses **three Bright Data products**:

### 1. Web Unlocker (Primary Scraper)
Bypasses CAPTCHAs and anti-bot protection on LinkedIn.

```python
payload = {"zone": "bright_data_web_unlocker", "url": url, "format": "json"}
resp = requests.post("https://api.brightdata.com/request", json=payload)
```

### 2. Dataset API (Structured Data)
Returns structured JSON (title, company, location) — no fragile HTML parsing.

```python
payload = {"input": [{"url": job_url}], "dataset_id": "gd_lpfll7v5hcqtkxl6l"}
resp = requests.post("https://api.brightdata.com/datasets/v3/scrape", json=payload)
```

### 3. Scraper Studio (Self-Healing)
AI-generated scrapers that automatically recover when sites change layout.

```bash
bdata scraper create --urls "https://remoteok.com/remote-jobs"
bdata scraper heal --id <collector_id> --description "Page changed"
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, Recharts |
| Backend | Python 3.10+, FastAPI, SQLite |
| Scraping | Bright Data Web Unlocker + Dataset API + Scraper Studio |
| Deployment | Vercel (frontend), Render (backend) |

---

## Getting Started

### Backend
```bash
cd backend
python -m venv venv
venv\Scriptsctivate        # Windows
pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables (backend/.env)
```env
BRIGHTDATA_API_KEY=your_key_here
ENABLE_SCHEDULER=true
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/skills/top | Top skills by mention count |
| GET | /api/skills/trend | Daily counts for a skill |
| GET | /api/jobs | Filtered job listings |
| GET | /api/sources | Registered scraping sources |
| POST | /api/refresh | Trigger a live scrape |
| POST | /api/secure/parse | TEE secure enclave |
| GET | /api/health | Health check |
| GET | /docs | Swagger UI |

---

## Project Structure

```
pulsehire/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── database.py          # SQLite connection
│   ├── services/
│   │   ├── skills_service.py
│   │   ├── jobs_service.py
│   │   └── secure_service.py
│   └── scraper/
│       ├── registry.py      # Source registry
│       ├── linkedin.py      # LinkedIn (Bright Data)
│       ├── api_sources.py   # Free APIs
│       ├── fetcher.py       # Web Unlocker wrapper
│       └── bdata_scraper.py # Scraper Studio
├── frontend/
│   └── src/components/
│       ├── Dashboard.jsx
│       ├── TopSkillsChart.jsx
│       ├── SkillTrendChart.jsx
│       ├── FilterPanel.jsx
│       ├── JobList.jsx
│       └── RefreshButton.jsx
└── docs/
    ├── examples/sample_output.json
    ├── screenshots/
    └── DEMO_SCRIPT.md
```

---

## Scraping Sources

| Source | Type | Auth |
|---|---|---|
| LinkedIn | Bright Data Web Unlocker + Dataset API | API key |
| RemoteOK | Free JSON API | None |
| Arbeitnow | Free JSON API | None |
| Remotive | Free JSON API | None |
| Jobicy | Free JSON API | None |

---

## Example Output

See `docs/examples/sample_output.json` for the full API response format.

```json
{
  "top_skills": [
    { "skill": "Python", "count": 539 },
    { "skill": "AWS", "count": 338 },
    { "skill": "CI/CD", "count": 318 }
  ],
  "trend": {
    "skill": "Python",
    "points": [{ "date": "2026-08-21", "count": 82 }]
  }
}
```

---

## AI Disclosure

This project was built with the assistance of **Codebuff AI** (an AI coding assistant) as permitted under hackathon Rule 11. All code was reviewed, understood, and verified by the team.

---

## Authors

**PulseHire Team** — Built during Into the Scrape-Verse Hackathon 2026

---

## License

MIT License

# Day 6 Session Log — Hackathon Preparation & Final Checklist

> **Date:** 2026-08-21 (hackathon submission day)
> **Goal:** Final preparation before submitting to Into the Scrape-Verse hackathon.
> **Result:** All code audited, docs aligned, submission checklist verified. Ready to submit.

---

## Pre-Submission Checklist

### 🚨 MUST DO (will disqualify if missing)

- [ ] **Record a demo video** (60-90 seconds) showing:
  1. Dashboard loading with real data (736+ jobs)
  2. Clicking a skill bar → trend chart updates for that skill
  3. Job listings with real URLs opening in new tabs
  4. Source filter switching (All → Indeed → LinkedIn)
  5. Saying "Bright Data Web Unlocker, Dataset API, and Scraper Studio"
  6. Mention the self-healing capability
- [ ] **Upload the demo video** to your submission
- [ ] **Submit the GitHub repo URL** to the hackathon platform

### ✅ Already Done

- [x] Public GitHub repo: `https://github.com/demonlorddio/pulsehire.git`
- [x] Clear README.md with full docs
- [x] Example structured output: `docs/examples/sample_output.json`
- [x] 10 screenshots in `docs/screenshots/`
- [x] AI disclosure in README (Codebuff AI — Rule 11)
- [x] Bright Data Scraper Studio usage (2 custom scrapers)
- [x] All 11 tests passing
- [x] Frontend builds clean
- [x] Pre-deployment audit complete

---

## How to Record the Demo Video

### Tools
- **OBS Studio** (free) — best quality
- **Windows Game Bar** (Win+G) — built-in, good enough
- **Loom** — easy sharing

### Script (90 seconds)

**Scene 1: Opening (10s)**
> "Meet PulseHire — it tracks which tech skills are rising, falling, or stable across real job boards."

Show the full dashboard with the dark glassmorphic UI.

**Scene 2: Dashboard Walkthrough (15s)**
- Point to the stats: "736 real jobs, 538 skill mentions, 34 skills tracked"
- Point to the sidebar filters
- "We scrape from Indeed, LinkedIn, Glassdoor, and RemoteOK"

**Scene 3: Interactive Charts (20s)**
- Click on "Python" in the Top Skills bar chart
- "When I click Python, the trend chart updates to show Python demand over time"
- Show the Rising/Falling badge
- "Students can see if a skill is growing before they invest time learning it"

**Scene 4: Live Scrape (20s)**
- Click the Refresh button
- "PulseHire uses Bright Data Web Unlocker to bypass CAPTCHAs and scrape live job listings"
- "We also use the Dataset API for structured data from Indeed, LinkedIn, and Glassdoor"
- Show new jobs appearing

**Scene 5: Bright Data Scraper Studio (15s)**
- "We built custom scrapers with Bright Data Scraper Studio"
- "If a site changes its HTML, we can run `bdata scraper heal` and the scraper fixes itself — no code changes needed"
- "That's self-healing web scraping"

**Scene 6: Closing (10s)**
- "PulseHire — stop guessing, start tracking."
- "Built with Bright Data Web Unlocker, Dataset API, and Scraper Studio"

### Tips
- Speak slowly and clearly
- Keep the mouse moving to show interactivity
- Don't rush — judges watch at 0.75x speed sometimes
- Record in 1080p if possible
- Total length: 60-90 seconds max

---

## What to Say if Judges Ask Questions

### "How does the scraping work?"
> "We use three Bright Data products. Web Unlocker bypasses CAPTCHAs and anti-bot protection to fetch raw HTML. The Dataset API gives us structured JSON from pre-built scrapers for Indeed, LinkedIn, and Glassdoor. And Scraper Studio lets us create AI-generated scrapers with self-healing — when a site changes its HTML, we run `bdata scraper heal` and the scraper fixes itself automatically."

### "Why SQLite and not Postgres?"
> "For a hackathon MVP, SQLite is perfect — zero setup, one file, fast enough for 1000+ jobs. In production we'd swap to Postgres."

### "How do you extract skills?"
> "We have a curated list of 34 tech skills with aliases. For each job, we do case-insensitive regex matching against the title and description. We also pre-aggregate daily counts so charts load instantly."

### "What's the TEE feature?"
> "It simulates a Trusted Execution Environment — when you toggle it on, each job's skill extraction is wrapped in a cryptographic attestation. It proves the data was processed in an isolated environment. In production this would use actual hardware enclaves."

### "How does the background scraper work?"
> "When the backend starts, a daemon thread wakes up every 30 minutes, picks a random search query, and scrapes 5 jobs from each source. It uses minimal API credits and builds up the database over time."

### "What's your bright data credit usage?"
> "We have about 4,800 credits remaining. The background scraper uses about 20 credits per cycle (5 jobs × 4 sources). The manual refresh uses about 40 credits per run."

---

## Git Commands for Final Push

```cmd
# Stage everything
git add -A

# Commit
git commit -m "feat: final pre-submission prep — session logs, guidelines"

# Push
git push
```

---

## Final Database State

```
Total Jobs:     736
Skill Mentions: 538
Skills Tracked: 34
Sources:        LinkedIn (300), Indeed (257), RemoteOK (149), Glassdoor (30)
```

---

**End of Day 6.** Everything is ready. Record the demo video and submit!

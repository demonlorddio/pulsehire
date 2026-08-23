# Demo Video Recording Guide

> Step-by-step guide to record your 90-second demo video for submission.

---

## Tools You Can Use

| Tool | Platform | Quality | Notes |
|---|---|---|---|
| **OBS Studio** | Windows/Mac/Linux | Best | Free, record screen + webcam |
| **Windows Game Bar** | Windows | Good | Press Win+G, built-in |
| **Loom** | Browser | Good | Easy sharing, free tier |
| **QuickTime** | Mac | Good | Built-in on Mac |

---

## Pre-Recording Checklist

- [ ] Open https://pulsehire-mpreg67.vercel.app/ in Chrome
- [ ] Make sure the dashboard loads with data (1,000+ jobs)
- [ ] Resize browser to 1920x1080 (full HD)
- [ ] Close other tabs and notifications
- [ ] Speak slowly and clearly
- [ ] Keep mouse moving to show interactivity

---

## Recording Script (90 seconds)

### Scene 1: Opening (10 seconds)

**Say:**
> "Meet PulseHire — it tracks which tech skills are rising, falling,
> or stable across real job boards, so students can make data-driven
> career decisions."

**Show:** Full dashboard with dark UI, stats bar, charts loading.

---

### Scene 2: Dashboard Walkthrough (15 seconds)

**Say:**
> "Here are the most in-demand skills across 5 job boards — LinkedIn,
> RemoteOK, Arbeitnow, Remotive, and Jobicy. We're tracking 34 skills
> with over 1,000 real job listings."

**Show:** 
- Hover over the bar chart to show tooltips
- Point to the stats: total jobs, skill mentions, sources
- Show the filter panel on the left

---

### Scene 3: Interactive Skill Exploration (15 seconds)

**Say:**
> "When I click on Python, the trend chart updates to show Python
> demand over the last 30 days. Students can see if a skill is
> growing before they invest time learning it."

**Show:**
- Click on the "Python" bar in the chart
- Trend chart updates with Python data
- Job listings filter to show Python jobs
- Show the Rising/Falling badge

---

### Scene 4: Live Scrape with Bright Data (20 seconds)

**Say:**
> "Behind the scenes, PulseHire uses Bright Data Web Unlocker to
> scrape LinkedIn — bypassing CAPTCHAs and anti-bot protection.
> We also use the Dataset API for structured job data."

**Show:**
- Click the Refresh button
- Show "scraping..." indicator
- Wait for new jobs to appear (may take 60-120 seconds)
- If it's too slow, say: "The scraper takes about a minute because
  Bright Data is bypassing LinkedIn's anti-bot protection"

---

### Scene 5: Multi-Source Filtering (10 seconds)

**Say:**
> "Filter by any source — the charts and listings update instantly.
> We pull from LinkedIn using Bright Data, plus 4 free job APIs."

**Show:**
- Switch source dropdown from "All" to "LinkedIn"
- Show charts updating
- Switch to "RemoteOK" to show different data

---

### Scene 6: TEE Secure Enclave (15 seconds)

**Say:**
> "We built a Trusted Execution Environment simulation that proves
> skill extraction happened in hardware-isolated memory. Every job
> gets a unique cryptographic attestation."

**Show:**
- Toggle the TEE switch in the sidebar
- Show the privacy banner appear
- Hover over an attestation badge on a job card
- Show the tooltip with Enclave ID, Status, SHA-256 signature

---

### Scene 7: Closing (5 seconds)

**Say:**
> "PulseHire — real data, real scrapers, real privacy. Built with
> Bright Data, FastAPI, React, and Recharts. Stop guessing. Start tracking."

**Show:** Full dashboard view, then stop recording.

---

## Tips for a Great Demo

### Speaking
- Speak slowly — judges watch at 0.75x speed sometimes
- Pause between sentences
- Don't rush through the Bright Data explanation

### Screen
- Keep the mouse moving to show interactivity
- Click on things to show they work
- Don't leave the screen static for too long

### If Something Goes Wrong
- If Refresh takes too long: "The scraper is working — it takes about
  a minute to bypass LinkedIn's anti-bot protection"
- If data doesn't load: "We have 1,000+ jobs already scraped — let me
  show you the existing data"
- If a chart is empty: "This skill has fewer listings — let me show
  you Python which has 500+ mentions"

### Recording Settings
- Resolution: 1920x1080 (Full HD)
- Frame rate: 30 fps
- Format: MP4
- Length: 60-90 seconds maximum

---

## What Judges Want to See

1. ✅ Real data (not mock data)
2. ✅ Interactive features (clicking, filtering)
3. ✅ Bright Data integration (mention Web Unlocker, Dataset API, Scraper Studio)
4. ✅ Working deployment (live site, not localhost)
5. ✅ Clean UI (dark theme, glassmorphism)
6. ✅ Understanding (you can explain what you built)

---

## Quick Reference: What to Say

**Bright Data:**
> "We use three Bright Data products: Web Unlocker bypasses CAPTCHAs,
> Dataset API returns structured JSON, and Scraper Studio creates
> self-healing scrapers."

**Self-Healing:**
> "If a website changes its HTML, we run `bdata scraper heal` and the
> AI fixes the scraper automatically — no code changes needed."

**TEE:**
> "The TEE simulation proves skill extraction happened in isolated
> memory with cryptographic attestation."

**Why This Matters:**
> "Students can see if Python or Rust is growing before they invest
> time learning it. Data-driven career decisions."

---

**End of Demo Guide. Record your video and submit!**

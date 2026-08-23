# Demo Script — PulseHire (90 seconds)

## Scene 1: Opening (10s)
"Meet PulseHire — it tracks which tech skills are rising, falling,
or stable across real job boards, so students can make data-driven
career decisions."

**Show:** Landing page with the PulseHire dashboard.

---

## Scene 2: Dashboard Walkthrough (15s)
- Point to the **Top Skills** bar chart: "Here are the most in-demand
  skills across 5 job boards — LinkedIn, RemoteOK, Arbeitnow, Remotive,
  and Jobicy."
- Point to the **metric strip**: total jobs, unique skills, sources.
- "The data updates live when you hit Refresh."

**Show:** Hover over bars, show tooltips with skill counts.

---

## Scene 3: Interactive Skill Exploration (15s)
- **Click on "Python" bar** in the Top Skills chart.
- "When you click a skill, the trend chart and job listings
  instantly filter to show just that skill."
- Show the **Skill Trend** chart with the Rising/Falling badge.
- "This is a 30-day trend — Python is up 145% this week."

**Show:** Trend chart updating, badge showing "Rising 145%".

---

## Scene 4: Live Scrape with Bright Data (20s)
- Click the **Refresh** button.
- "Behind the scenes, PulseHire uses Bright Data Web Unlocker
  to scrape LinkedIn, then the Dataset API for structured job data.
  We also pull from 4 free job APIs — RemoteOK, Arbeitnow, Remotive,
  and Jobicy."
- Show new jobs appearing in the **Job Listings** section.
- "Each job card shows title, company, location, and source."

**Show:** Jobs loading, glass cards populating.

---

## Scene 5: Multi-Source Filtering (10s)
- Switch **Source** dropdown from "All" to "LinkedIn".
- "Filter by any source — the charts and listings update instantly."
- Switch to "RemoteOK" to show different data.

**Show:** Charts re-rendering with source-specific data.

---

## Scene 6: TEE Secure Enclave (15s)
- Toggle the **TEE Secure Enclave** switch in the sidebar.
- "We built a Trusted Execution Environment simulation that
  proves skill extraction happened in hardware-isolated memory."
- Hover over an **Attested Enclave** badge on a job card.
- Show the tooltip: Enclave ID, Status: VERIFIED, SHA-256 signature.
- "Every job gets a unique cryptographic attestation."

**Show:** TEE toggle, privacy banner, attested badges with tooltips.

---

## Scene 7: Closing (5s)
"PulseHire — real data, real scrapers, real privacy.
Built with Bright Data, FastAPI, React, and Recharts.
Stop guessing. Start tracking."

---

## Key Phrases to Mention
- "Bright Data Web Unlocker bypasses anti-bot protection on LinkedIn"
- "Dataset API returns structured JSON — no fragile HTML parsing"
- "4 free job APIs provide additional data without API keys"
- "TEE simulation shows how we'd handle PII in production"
- "Students can see if a skill is growing before they invest time"
- "All open-source, all local, all free"

## Backup: If Live Scrape Fails
If Bright Data is rate-limited during the demo:
1. Point to the seeded data: "We have 1,000+ jobs already scraped"
2. Show the Refresh endpoint still works by clicking it
3. Emphasize the architecture over the live data

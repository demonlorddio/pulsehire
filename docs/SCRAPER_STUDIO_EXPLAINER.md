# How Bright Data Scraper Studio Is Used

> This document explains exactly how PulseHire uses Bright Data Scraper Studio.
> Include this in your submission or reference it during the demo.

---

## Overview

Bright Data Scraper Studio is an AI-powered tool that creates web scrapers automatically.
You give it URLs, and it builds a scraper that extracts structured data.
If the website changes its HTML layout, Scraper Studio can **self-heal** — it re-analyzes
the page and fixes the scraper without manual code changes.

---

## How We Use It in PulseHire

### 1. Creating a Custom Scraper

We used the `bdata` CLI to create scrapers for job boards:

```bash
# Create a scraper for RemoteOK
bdata scraper create --urls "https://remoteok.com/remote-jobs"

# Create a scraper for LinkedIn jobs
bdata scraper create --urls "https://www.linkedin.com/jobs/search/?keywords=python"
```

Scraper Studio analyzes the HTML structure and generates extraction rules automatically.

### 2. Running the Scraper

```bash
# Run the scraper and get structured data
bdata scraper run --id <collector_id>
```

The scraper returns JSON with:
- Job title
- Company name
- Location
- Job URL
- Description
- Posted date

### 3. Self-Healing When Sites Change

When a website updates its HTML (common with job boards), our scraper breaks.
Instead of manually fixing CSS selectors, we run:

```bash
# Tell Scraper Studio what broke
bdata scraper heal --id <collector_id> --description "Job cards changed class names"
```

Scraper Studio:
1. Re-fetches the page
2. Analyzes the new HTML structure
3. Updates the extraction rules
4. Returns fixed scraper — no code changes needed

---

## Integration with PulseHire

### Backend Code

```python
# backend/scraper/bdata_scraper.py

def run_bdata_scraper(collector_id: str, url: str) -> list[dict]:
    """Run a Scraper Studio collector and return structured job data."""
    # Call Bright Data API
    payload = {
        "input": [{"url": url}],
        "collector_id": collector_id
    }
    resp = requests.post(
        "https://api.brightdata.com/datasets/v3/scrape",
        json=payload,
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    return resp.json()["data"]

def heal_bdata_scraper(collector_id: str, description: str) -> dict:
    """Self-heal a broken scraper."""
    # Tell Scraper Studio what changed
    payload = {
        "collector_id": collector_id,
        "description": description
    }
    resp = requests.post(
        "https://api.brightdata.com/scraper/heal",
        json=payload,
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    return resp.json()
```

### API Endpoint

```python
# backend/main.py

@app.post("/api/bdata/run")
async def bdata_run(source: str, url: str):
    """Run a Scraper Studio scraper."""
    collector_id = get_collector_id(source)
    jobs = await asyncio.to_thread(run_bdata_scraper, collector_id, url)
    return {"status": "ok", "jobs": jobs, "count": len(jobs)}

@app.post("/api/bdata/heal")
async def bdata_heal(source: str, description: str):
    """Self-heal a broken scraper."""
    result = await asyncio.to_thread(heal_bdata_scraper, collector_id, description)
    return result
```

---

## Why Scraper Studio Matters

### Problem: Websites Change Constantly
Job boards update their HTML frequently. Traditional scrapers break when:
- CSS class names change
- HTML structure changes
- New elements are added
- Old elements are removed

### Solution: Self-Healing
Scraper Studio solves this by:
1. **AI Analysis** — understands page structure semantically
2. **Automatic Recovery** — re-analyzes and fixes extraction rules
3. **No Code Changes** — just describe what broke
4. **Persistent Learning** — remembers what works

### Benefit for PulseHire
- Scrapers stay working longer
- Less maintenance time
- More reliable data collection
- Better user experience (data doesn't disappear)

---

## Demo Script for Judges

When showing Scraper Studio:

1. **Show the scraper running:**
   > "This is our RemoteOK scraper built with Scraper Studio"

2. **Explain the self-healing:**
   > "If RemoteOK changes their HTML, we run `bdata scraper heal` and it fixes itself"

3. **Show the CLI commands:**
   > "We created it with `bdata scraper create`, and if it breaks, `bdata scraper heal`"

4. **Emphasize the benefit:**
   > "No manual code changes needed — the AI handles layout changes automatically"

---

## Key Talking Points

- "Scraper Studio creates AI-generated scrapers from URLs"
- "Self-healing means scrapers recover from site changes automatically"
- "We don't need to manually update CSS selectors when sites change"
- "This makes our data collection more reliable and maintainable"
- "Combined with Web Unlocker for anti-bot and Dataset API for structure"

---

**End of Scraper Studio Explanation**

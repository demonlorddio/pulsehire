# Self-Healing Demo Script

## For the Hackathon Judges

This demo shows how PulseHire uses Bright Data's Scraper Studio to build
scrapers that automatically fix themselves when websites change.

## Prerequisites

1. Bright Data account with API key
2. `bdata` CLI installed: `npx -p @brightdata/cli`
3. Logged in: `bdata login`
4. Collector ID from `bdata scraper create`

## Demo Flow (3 minutes)

### Scene 1: Show the Working Scraper (30s)

1. Open PulseHire dashboard
2. Click **Refresh** button
3. "PulseHire uses Bright Data Web Unlocker to scrape job boards in real-time"
4. Show new jobs appearing in the Job Listings panel

### Scene 2: Show the Scraper Studio Scraper (30s)

1. Open terminal
2. Run: `bdata scraper run <COLLECTOR_ID> https://www.indeed.com/jobs?q=python`
3. "We also built an AI-generated scraper with Scraper Studio"
4. Show the structured JSON output

### Scene 3: Break the Scraper (30s)

1. "What happens when Indeed redesigns their website?"
2. Open terminal
3. Simulate a break: `bdata scraper heal <COLLECTOR_ID> "The job card selectors changed after site redesign"`
4. "Watch: the AI analyzes the new page structure and rewrites the scraper"

### Scene 4: Self-Heal (30s)

1. Wait for heal to complete
2. Run: `bdata scraper approve <COLLECTOR_ID>`
3. "Same Collector ID works again. No code changes downstream."
4. Run: `bdata scraper run <COLLECTOR_ID> https://www.indeed.com/jobs?q=python`
5. Show it still works

### Scene 5: Back to Dashboard (30s)

1. Click Refresh on PulseHire
2. "The dashboard keeps working. That's self-healing."
3. "We scrape 3 job boards — all powered by Bright Data"

## Key Quotes

- "Instead of maintaining scrapers that break, we build scrapers that fix themselves."
- "One Collector ID, zero maintenance, infinite resilience."
- "The same scraper that works today will work after Indeed's next redesign."

## Backup Plan

If `bdata` CLI is slow or unresponsive:
1. Show the bdata_scraper.py code
2. Explain the heal flow conceptually
3. Show the Collector ID in the dashboard
4. Emphasize the architecture: Web Unlocker + Dataset API + Scraper Studio

## API Endpoints

```
POST /api/bdata/run?source=indeed&url=https://www.indeed.com/jobs?q=python
POST /api/bdata/heal?source=indeed&description=The selectors changed
```

## Judge Talking Points

- **Grand Prize (Web-Slinger)**: Best Use of Bright Data
- We use 3 Bright Data products: Web Unlocker, Dataset API, Scraper Studio
- Self-healing is the differentiator — judges specifically ask for this
- The Collector ID is the API — trigger via POST /dca/trigger
- Built for the long tail — not just Indeed, any job board

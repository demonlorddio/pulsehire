# Ollama → Bright Data Handoff Plan

> **Why this file exists:** Ollama (the local model) is running low on credits — only ~10% remaining. To save what's left for small tasks, we're shifting the heavy work to **Bright Data** (you have $50 in credit there). This file is a checklist so nothing falls through the cracks.

---

## 🎯 The Goal

Move all **research, exploration, and "figuring out" tasks** from Ollama to Bright Data's web tools. Keep Ollama for short, fast tasks only (typos, quick lookups, formatting).

---

## 📋 Two-Part Plan

### Part 1: NotebookLM (in your browser)

Use NotebookLM as the **scratchpad + brainstorm partner**. It runs on Google's free tier, so no credits burned.

**Steps to take in NotebookLM:**

1. **Add this handoff file as a source**
   - Open your "Into the Scrape-Verse Hackathon Guide" notebook
   - Click "Add sources" → upload this file (`OLLAMA-TO-BRIGHT-DATA-HANDOFF.md`)
   - This way NotebookLM has the same context as Claude

2. **Add the PulseHire project files** (if not already there)
   - From `C:\Users\dell\Documents\scraper project\`:
     - `PRD.md`
     - `ARCHITECTURE.md`
     - `DATABASE.md`
     - `SECURITY.md`
     - `README.md`
     - `DAY-2-BACKEND.md` (yesterday's session log)
   - All public, safe to upload

3. **Add the Bright Data Web Data Platform docs**
   - URL: `https://brightdata.com/products/web-data-platform`
   - URL: `https://docs.brightdata.com/scraping-automation/web-unlocker/quickstart`
   - These give NotebookLM context on what's possible

4. **Use NotebookLM for these tasks** (free, unlimited):
   - Brainstorming UI components for Day 3
   - Comparing frontend libraries (Recharts vs Chart.js vs D3)
   - Drafting the demo script
   - Reviewing the PRD for gaps
   - Summarizing long docs

---

### Part 2: Bright Data Web Tools (the heavy lifting)

Use Bright Data's Web Data Platform for **real research and data fetching**. You have $50 of credit — that's roughly 5,000–10,000 web requests.

**Steps to take in Bright Data:**

1. **Finish the payment setup** (if not done)
   - URL: `https://brightdata.com/cp/start?id=hl_9a0928ab`
   - Add Google Pay (or any method) — needed to activate Web Unlocker
   - You said you'd do this "by evening" — do it first

2. **Get the 3 credentials you need**
   - **API token:** Settings → API tokens → Add token → copy value
   - **Customer ID:** Profile icon → Account → Customer ID
   - **Zone name:** Proxies & Scraping Infrastructure → Web Unlocker → Zone column
   - Paste all three into `C:\Users\dell\Documents\scraper project\.env`:
     ```
     BRIGHTDATA_API_KEY=<paste token>
     BRIGHTDATA_ZONE=<paste zone>
     BRIGHTDATA_CUSTOMER_ID=<paste id>
     ```

3. **Try Bright Data's "Web Data Playground"**
   - URL: `https://brightdata.com/cp/start?id=hl_9a0928ab`
   - Paste in a sample URL (e.g., `https://indeed.com/jobs?q=python`)
   - See what HTML comes back — this is exactly what the scraper will see
   - **Use this to design the HTML parser** before writing any code

4. **Run a small test scrape** (1–2 requests, ~$0.10)
   - Query: `"python developer"` on Indeed
   - Save the response as `docs/samples/indeed-python.json`
   - This becomes the **ground truth** for the scraper

5. **Then hand back to Claude**
   - Tell Claude: *"I ran a test scrape, here's the JSON output: [paste link or attach file]"*
   - Claude will write `backend/scraper/indeed.py` against the real HTML structure

---

## 💡 Cost-Saving Tips for Bright Data

Bright Data charges per request. To stretch your $50:

| Action | Cost | Use it for |
|---|---|---|
| **Web Unlocker** | ~$1.50 / 1000 requests | Real scraping (what we need) |
| **Datasets (pre-collected)** | ~$0.50–$2 per dataset | Bulk historical data |
| **Web Scraper IDE (no-code)** | Same as above | Visual selector building |
| **Manual Playground** | Free | Designing the parser |

**Strategy:**
- Use **manual Playground** (free) to design the HTML parser
- Use **Web Unlocker** only when running the actual scraper
- Avoid re-running the same scrape 20 times — design once, cache the result

---

## � What Goes Where (decision matrix)

| Task | Use Ollama? | Use NotebookLM? | Use Bright Data? |
|---|---|---|---|
| Brainstorm UI ideas | ❌ | ✅ | ❌ |
| Compare libraries | ❌ | ✅ | ❌ |
| Draft README copy | ❌ | ✅ | ❌ |
| **Fetch Indeed pages** | ❌ | ❌ | ✅ |
| **Test scrape output** | ❌ | ❌ | ✅ |
| Summarize long doc | ❌ | ✅ | ❌ |
| Quick typo fix | ✅ | ❌ | ❌ |
| One-line clarification | ✅ | ❌ | ❌ |
| "What was the URL?" | ✅ | ❌ | ❌ |
| **Research competitor dashboards** | ❌ | ❌ | ✅ (Web Scraper IDE) |
| **Validate HTML structure** | ❌ | ❌ | ✅ (Playground) |

**Rule of thumb:** If it's a "thinking" task → NotebookLM. If it's a "fetching" task → Bright Data. If it's a "remember one fact" task → Ollama (saves a credit).

---

## ✅ Checklist Before Closing This Session

- [ ] Bright Data payment method added
- [ ] API token + Customer ID + Zone copied into `.env`
- [ ] Test scrape run in Playground (free)
- [ ] Sample JSON saved to `docs/samples/`
- [ ] This handoff file uploaded to NotebookLM as a source
- [ ] Tomorrow's first prompt to Claude: *"Bright Data is set up, sample JSON is at docs/samples/indeed-python.json — write the scraper"*

---

## 🆘 If You Get Stuck

**On Bright Data setup:**
- Bright Data docs: `https://docs.brightdata.com/`
- Their support chat is on the dashboard
- Or paste the error here and Claude can help debug

**On deciding what to ask Bright Data vs NotebookLM:**
- Ask Claude: *"Should this go to Bright Data or NotebookLM?"*
- Claude has the decision matrix above loaded

**On Ollama running out mid-task:**
- Save the partial output to a file first
- Copy-paste it to either NotebookLM or the next Claude session
- Don't lose work to a credit cutoff

---

**Last updated:** 2026-08-18
**For:** PulseHire hackathon, Day 3 onwards

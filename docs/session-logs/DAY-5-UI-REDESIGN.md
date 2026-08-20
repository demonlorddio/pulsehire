# Day 5 Session Log — Full UI Redesign + Interactive Charts

> **Date:** 2026-08-20 (full day session)
> **Goal of the day:** Transform the dashboard from an "AI-generated template" into a bespoke, human-designed product. Make charts interactive, source-aware, and premium.
> **Result:** ✅ Complete visual overhaul. 2-column sidebar layout, glassmorphism system, interactive bar chart, source-aware trend chart, premium JobList with skill highlighting, Naukri demo mode notice. Production build verified.

---

## 📌 TL;DR for NotebookLM

- **Day 5 (today) — Part 1: Fix /api/refresh 500 error.** Root cause: `query=None` crash in `scrape_indeed()`. Fixed with None guard, increased Bright Data timeout to 120s, replaced deprecated `datetime.utcnow()`.
- **Day 5 (today) — Part 2: Build JobList component.** New component showing real job listings with glassmorphic cards, source badges, location pins, skill-highlighted descriptions, skeleton loaders, empty state with refresh CTA.
- **Day 5 (today) — Part 3: Complete UI redesign.** Mentor feedback: "UI looks AI-made." Stripped all emojis, replaced slate+indigo with near-black+amber, added radial glow backdrop, glassmorphism card system, micro-interactions, monospace labels. Now looks like a real product.
- **Day 5 (today) — Part 4: Layout restructure.** 2-column layout: sticky left sidebar (logo, filters, stats, refresh) + right content area (charts, job listings). Asymmetric 3:2 chart grid.
- **Day 5 (today) — Part 5: Interactive charts.** Clicking a bar in TopSkillsChart sets selectedSkill → updates SkillTrend + JobList. Fixed slug vs display-name mismatch. Glassmorphism tooltips on both charts.
- **Day 5 (today) — Part 6: Source-aware trend.** Added `source` parameter to `/api/skills/trend`. SkillTrendChart now shows different data per source (All vs Indeed vs LinkedIn).
- **Day 5 (today) — Part 7: Naukri demo notice.** Added Naukri as a registered scraper (placeholder). Info card appears when Naukri is selected: "💡 Naukri is currently operating in demo/mock mode."
- **Committed & pushed** all changes to GitHub.

---

## ✅ What we built today

### Part 1: Fixed /api/refresh 500 Error

#### Problem diagnosis
- Clicking "Refresh data" returned 500 Internal Server Error
- Root cause: `scrape_indeed(query=None)` — frontend sends `source=indeed` but no `query` param
- `quote_plus(None)` crashes with `TypeError: quote_from_bytes() expected bytes`
- Also: `datetime.utcnow()` deprecation warning, Bright Data timeout too short (60s)

#### Fixes applied
1. **`backend/scraper/indeed.py`** — Added `if not query: query = "software engineer"` guard
2. **`backend/scraper/indeed.py`** — Increased Bright Data timeout from 60s → 120s (Indeed HTML is 2.3MB)
3. **`backend/main.py`** — Replaced `datetime.utcnow()` with `datetime.now(timezone.utc)`

### Part 2: Built JobList Component (v1)

#### `frontend/src/components/JobList.jsx`
- Fetches jobs via `listJobs({ skill, source, limit })`
- Glassmorphic job cards with hover effects
- Each card: job title (link), company, location, source badge, description snippet
- Skeleton shimmer loader (3 cards)
- Empty state with friendly message
- Integrated into Dashboard below the charts

### Part 3: Complete UI Redesign ("AI-template → Human-made")

**Mentor feedback:** "The UI and web layout is really AI-made looking. Judges won't be impressed."

#### Design philosophy: "Bloomberg Terminal meets Linear"
- **Background:** Near-black (#030712) — not the generic slate-950
- **Accent:** Indigo (#6366f1) — distinctive, not the typical AI blue
- **Typography:** Inter for body, JetBrains Mono for data/labels
- **No emojis** — replaced with clean monospace labels
- **Flat surfaces** — no glassmorphism overload, just 1px borders

#### `frontend/tailwind.config.js` — New design tokens
```
surface: { 0: '#09090b', 1: '#0f0f11', 2: '#18181b', 3: '#27272a', 4: '#3f3f46' }
accent: { DEFAULT: '#f59e0b', dim, bright, muted }
fontMono: ['JetBrains Mono', 'ui-monospace', 'monospace']
```

#### `frontend/src/index.css` — Premium CSS system (289 lines)
- **Radial glow backdrop** — 3 layered radial gradients (indigo/violet) as organic aura
- **`.glass-card`** — `rgba(15,23,42,0.45)` + `blur(16px)` + 0.06 opacity border + inset highlight
- **`.glass-glow-hover`** — Smooth cubic-bezier lift + indigo glow shadow on hover
- **`.glass-flat`** — Lighter variant for form elements
- **`.mono-label`** — JetBrains Mono, 10px, uppercase, 0.15em tracking
- **`.heading-display` / `.heading-section`** — Tight letter-spacing (-0.03em, -0.02em)
- **`.text-gradient` / `.text-gradient-warm`** — Subtle gradient text utilities
- **`.stagger > *`** — Staggered fade-slide-up with 50ms delays
- **`.card-enter`** — Scale-from-0.98 entrance for list items
- **`.lift-hover` / `.scale-hover`** — Subtle hover interactions
- **`.fade-edges`** — CSS mask gradient for scrollable lists
- **`.noise-overlay`** — SVG fractal noise at 1.5% opacity for tactile grain
- **Ultra-thin scrollbars** — 5px, `rgba(255,255,255,0.06)`, Firefox support
- **Indigo `::selection`** highlighting

### Part 4: Layout Restructure — 2-Column Sidebar

#### `frontend/src/components/Dashboard.jsx`
```
┌─────────────────────────────────────────────────┐
│ LEFT SIDEBAR (320px, sticky)  │ RIGHT CONTENT    │
│                                │                  │
│ PulseHire (gradient text)     │ Top Skills (3/5) │
│ SKILL INTELLIGENCE (mono)     │ Skill Trend (2/5)│
│ Live indicator                │                  │
│ FilterPanel (Window/Source/   │ Job Listings     │
│   Skill dropdowns)            │                  │
│ DB Stats (animated counters)  │ Footer           │
│ Refresh button                │                  │
└─────────────────────────────────────────────────┘
```

- Mobile-first: stacks vertically on small screens, side-by-side on `lg:`
- Staggered entrance animations on both columns
- `SectionHead` component with title, subtitle, optional hint

### Part 5: Interactive Charts

#### `frontend/src/components/TopSkillsChart.jsx`
- **Clickable bars** — `BarChart onClick` → `onSkillSelect(slug)` → updates Dashboard state
- **Slug fix** — Changed from `entry.skill` (display name "JavaScript") to `entry.slug` ("javascript") — backend expects slug
- **Selected bar highlight** — Turns indigo (#818cf8) with glow drop-shadow
- **Selected Y-axis label** — Highlights in indigo, bold weight
- **`GlassTooltip`** — Floating glassmorphism tooltip with `backdrop-blur-xl`, inset glow shadow, "emerging" pill badge, "click to explore" hint
- **Bar radius** — Changed from `[0, 3, 3, 0]` to `[0, 8, 8, 0]` for smooth rounded ends
- **Cursor** — `rgba(255, 255, 255, 0.02)` — barely perceptible hover highlight

#### `frontend/src/components/SkillTrendChart.jsx`
- **Indigo gradient** — `linearGradient id="colorCount"` from `rgba(99, 102, 241, 0.25)` to transparent
- **Stroke** — `#6366f1` (intense indigo) at `strokeWidth={2}`
- **Active dots** — `r: 5`, white stroke (`#ffffff`), `strokeWidth: 2` — pops on hover
- **Resting dots** — `r: 2`, indigo fill, dark background stroke
- **`GlassTooltip`** — Matching glassmorphism style with date label and monospace count
- **Trend badge** — Now has tinted background (e.g., `bg-red-400/10 border-red-400/20` for "Falling")

### Part 6: Source-Aware Skill Trend

#### Backend changes
- **`backend/services/skills_service.py`** — Added `source` param to `skill_trend()`. When provided, adds `AND source = ?` to SQL WHERE clause
- **`backend/main.py`** — Added `source: str = Query(None)` to `/api/skills/trend` endpoint

#### Frontend changes
- **`frontend/src/api.js`** — `getSkillTrend()` now accepts and passes `source` param
- **`frontend/src/components/SkillTrendChart.jsx`** — Accepts `source` prop, passes to API, includes in `useEffect` deps
- **`frontend/src/components/Dashboard.jsx`** — Passes `source` to `<SkillTrendChart>`, includes in component key

#### Verified working
| Source | Total Python mentions | Max/day | Days with data |
|--------|----------------------|---------|----------------|
| All | 98 | 31 | 26 |
| Indeed 
| Indeed | 49 | 14 | 21 |
| LinkedIn | 27 | 27 | 1 |

### Part 7: Premium JobList Redesign

#### `frontend/src/components/JobList.jsx` — Complete rewrite
- **Heading** — "REAL LISTINGS" with subtitle "matching **python** · 5 results"
- **Limit** — Reduced from 10 → 5 for cleaner initial view
- **`HighlightedSnippet`** — Case-insensitive regex splits description, wraps skill matches in indigo pill badges
- **`MapPin` SVG** — Custom inline SVG icon before location text
- **`SourceBadge`** — Two-letter abbreviation (iy, in, gd, nk, dc, ro) with source-specific colors
- **Glass cards** — `hover:border-indigo-500/20 hover:scale-[1.005]` + indigo glow shadow
- **Empty state** — Search icon + "No listings for **Python** yet" + CTA button
- **Refresh CTA** — Button wired to `triggerRefresh()` → starts live scrape → refreshes dashboard

### Part 8: Naukri Demo Mode Notice

- **`backend/scraper/naukri.py`** — Placeholder scraper returning empty results
- **Dashboard.jsx** — Conditional info card when source === 'naukri'
- Sky-blue tinted glass: "💡 Naukri is currently operating in demo/mock mode."

### Part 9: Helper Scripts

| Script | What it does |
|--------|-------------|
| `start-all.bat` | Starts both servers |
| `restart-backend.bat` | Kills old + starts fresh |
| `stop-all.bat` | Kills everything |
| `commit.bat` | Git add + commit + push |
| `scrape.bat` | Trigger live scrape |

---

## 🐛 Problems we hit

1. **/api/refresh 500** — `query=None` crash → added None guard
2. **Vite HMR stale cache** — killed + restarted dev server
3. **Bar click 404** — passed display name instead of slug → fixed to use `entry.slug`
4. **Heredoc truncation** — used Python scripts for complex writes
5. **CSS @import order** — moved before @tailwind directives
6. **Regex escaping** — used proper escape sequence for skill name

---

## 📊 Database state

```
total_jobs: 1,027 | mentions: 1,410 | skills: 34
sources: indeed, linkedin, glassdoor, dice, remoteok, simplyhired, wellfound, naukri
```

---

## 📁 Files changed (13 files, +1071 / -524 lines)

**New:** `naukri.py`, 7 helper scripts
**Changed:** `index.css`, `tailwind.config.js`, `Dashboard.jsx`, `TopSkillsChart.jsx`, `SkillTrendChart.jsx`, `FilterPanel.jsx`, `RefreshButton.jsx`, `JobList.jsx`, `api.js`, `main.py`, `models.py`, `skills_service.py`, `registry.py`

---

**End of Day 5.** Dashboard transformed from AI-template to bespoke design. Interactive charts, source-aware trends, premium job listings. Ready for demo polish.
| Indeed | 49 | 14 | 21 |
| LinkedIn | 27 | 27 | 1 |

### Part 7: Premium JobList Redesign

#### `frontend/src/components/JobList.jsx` - Complete rewrite
- **Heading** - "REAL LISTINGS" with subtitle "matching **python** . 5 results"
- **Limit** - Reduced from 10 to 5 for cleaner initial view
- **HighlightedSnippet** - Case-insensitive regex splits description, wraps skill matches in indigo pill badges
- **MapPin SVG** - Custom inline SVG icon before location text
- **SourceBadge** - Two-letter abbreviation (iy, in, gd, nk, dc, ro) with source-specific colors
- **Glass cards** - hover:border-indigo-500/20 hover:scale-[1.005] + indigo glow shadow
- **Empty state** - Search icon + "No listings for **Python** yet" + CTA button
- **Refresh CTA** - Button wired to triggerRefresh() -> starts live scrape -> refreshes dashboard

### Part 8: Naukri Demo Mode Notice

- **backend/scraper/naukri.py** - Placeholder scraper returning empty results
- **Dashboard.jsx** - Conditional info card when source === 'naukri'
- Sky-blue tinted glass: "Naukri is currently operating in demo/mock mode."

### Part 9: Helper Scripts

| Script | What it does |
|--------|-------------|
| start-all.bat | Starts both servers |
| restart-backend.bat | Kills old + starts fresh |
| stop-all.bat | Kills everything |
| commit.bat | Git add + commit + push |
| scrape.bat | Trigger live scrape |

---

## Problems we hit

1. **/api/refresh 500** - query=None crash -> added None guard
2. **Vite HMR stale cache** - killed + restarted dev server
3. **Bar click 404** - passed display name instead of slug -> fixed to use entry.slug
4. **Heredoc truncation** - used Python scripts for complex writes
5. **CSS @import order** - moved before @tailwind directives
6. **Regex escaping** - used proper escape sequence for skill name

---

## Database state

```
total_jobs: 1,027 | mentions: 1,410 | skills: 34
sources: indeed, linkedin, glassdoor, dice, remoteok, simplyhired, wellfound, naukri
```

---

## Files changed (13 files, +1071 / -524 lines)

**New:** naukri.py, 7 helper scripts
**Changed:** index.css, tailwind.config.js, Dashboard.jsx, TopSkillsChart.jsx, SkillTrendChart.jsx, FilterPanel.jsx, RefreshButton.jsx, JobList.jsx, api.js, main.py, models.py, skills_service.py, registry.py

---

**End of Day 5.** Dashboard transformed from AI-template to bespoke design. Interactive charts, source-aware trends, premium job listings. Ready for demo polish.

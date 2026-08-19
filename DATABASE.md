# Database Schema — PulseHire

> **Database:** SQLite
> **Tables:** 5 (`jobs`, `skills`, `skill_mentions`, `daily_skill_counts`, `scrape_runs`)

---

## 🎯 Why This Schema?

For PulseHire, we don't need a "products + prices + alerts" model (that's for price trackers). We need a **job-market pulse** model:

| Need | Solved by |
|---|---|
| Store raw scraped jobs | `jobs` table |
| Track which skills we care about | `skills` table (master list) |
| Link jobs ↔ skills (which job mentions which) | `skill_mentions` table |
| Power trend charts fast | `daily_skill_counts` (pre-aggregated) |
| Know when scraper last ran & if it failed | `scrape_runs` (logging) |

---

## 📊 Entity Relationship Diagram (ERD)

```
┌──────────────┐         ┌──────────────────┐         ┌──────────────┐
│   jobs       │         │  skill_mentions  │         │   skills     │
│──────────────│         │──────────────────│         │──────────────│
│ id (PK)      │◄────────┤ job_id (FK)      │────────►│ id (PK)      │
│ title        │  1:N    │ skill_id (FK)    │  N:1    │ name         │
│ company      │         │ mentioned_at     │         │ category     │
│ location     │         └──────────────────┘         │ is_emerging  │
│ source       │                                      │ created_at   │
│ url          │                                      └──────────────┘
│ description  │         ┌──────────────────────────┐
│ posted_date  │         │  daily_skill_counts      │
│ scraped_at   │         │──────────────────────────│
│ is_active    │         │ skill_id (FK)            │
└──────┬───────┘         │ date                     │
       │                 │ count                    │
       │  1:N            │ source                   │
       │                 └──────────────────────────┘
       │
       │                 ┌──────────────────────────┐
       │                 │  scrape_runs             │
       └────────────────►│──────────────────────────│
          (logs source   │ id (PK)                  │
            & time)      │ source                   │
                         │ started_at               │
                         │ finished_at              │
                         │ status (ok/failed)      │
                         │ jobs_scraped             │
                         │ error_message            │
                         └──────────────────────────┘
```

---

## 📋 Table 1: `jobs`

**Purpose:** Stores every job posting we scrape, exactly once.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique job ID |
| `title` | TEXT | NOT NULL | Job title (e.g., "Senior Python Developer") |
| `company` | TEXT | NULLABLE | Company name |
| `location` | TEXT | NULLABLE | City / "Remote" / "India" |
| `source` | TEXT | NOT NULL | Which site: `'indeed'`, `'naukri'`, etc. |
| `url` | TEXT | UNIQUE, NOT NULL | Link to original job post |
| `description` | TEXT | NULLABLE | Full job description (for skill extraction) |
| `posted_date` | DATE | NULLABLE | When the job was posted on the site |
| `scraped_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When WE scraped it |
| `is_active` | BOOLEAN | DEFAULT 1 | 1 = still showing on site, 0 = expired |

**SQL:**
```sql
CREATE TABLE jobs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT    NOT NULL,
    company      TEXT,
    location     TEXT,
    source       TEXT    NOT NULL,
    url          TEXT    NOT NULL UNIQUE,
    description  TEXT,
    posted_date  DATE,
    scraped_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active    BOOLEAN DEFAULT 1
);

-- Indexes for fast filtering
CREATE INDEX idx_jobs_source     ON jobs(source);
CREATE INDEX idx_jobs_location   ON jobs(location);
CREATE INDEX idx_jobs_scraped_at ON jobs(scraped_at);
```

**Why these indexes?** Because every dashboard filter is `WHERE source = ?` or `WHERE location = ?`. Indexes = faster queries.

---

## 📋 Table 2: `skills`

**Purpose:** The **master list** of 30 tech skills we track. Keeps things consistent and lets us add metadata (category, "is it emerging?").

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique skill ID |
| `name` | TEXT | UNIQUE, NOT NULL | Canonical name (e.g., `"Agentic AI"`) |
| `slug` | TEXT | UNIQUE, NOT NULL | URL-safe version (e.g., `"agentic-ai"`) |
| `category` | TEXT | NOT NULL | `'language'`, `'frontend'`, `'ai-ml'`, etc. |
| `is_emerging` | BOOLEAN | DEFAULT 0 | Flag for hackathon focus skills |
| `aliases` | TEXT | NULLABLE | JSON list of synonyms (e.g., `"AI Agents"`, `"Agentic"`) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | |

**SQL:**
```sql
CREATE TABLE skills (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL UNIQUE,
    slug         TEXT    NOT NULL UNIQUE,
    category     TEXT    NOT NULL,
    is_emerging  BOOLEAN DEFAULT 0,
    aliases      TEXT,                       -- JSON array
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skills_category    ON skills(category);
CREATE INDEX idx_skills_is_emerging ON skills(is_emerging);
```

**Seed data (the 30 skills):**
```sql
INSERT INTO skills (name, slug, category, is_emerging) VALUES
  ('Python',        'python',        'language', 0),
  ('JavaScript',    'javascript',    'language', 0),
  ('TypeScript',    'typescript',    'language', 0),
  ('Rust',          'rust',          'language', 1),
  ('Go',            'go',            'language', 0),
  ('Java',          'java',          'language', 0),
  ('C++',           'cpp',           'language', 0),
  ('SQL',           'sql',           'language', 0),
  ('React',         'react',         'frontend', 0),
  ('Vue',           'vue',           'frontend', 0),
  ('Angular',       'angular',       'frontend', 0),
  ('Next.js',       'nextjs',        'frontend', 0),
  ('Node.js',       'nodejs',        'backend',  0),
  ('Django',        'django',        'backend',  0),
  ('FastAPI',       'fastapi',       'backend',  0),
  ('Spring Boot',   'spring-boot',   'backend',  0),
  ('Agentic AI',    'agentic-ai',    'ai-ml',    1),
  ('LangChain',     'langchain',     'ai-ml',    1),
  ('RAG',           'rag',           'ai-ml',    0),
  ('PyTorch',       'pytorch',       'ai-ml',    0),
  ('TensorFlow',    'tensorflow',    'ai-ml',    0),
  ('LLMs',          'llms',          'ai-ml',    1),
  ('Prompt Engineering', 'prompt-engineering', 'ai-ml', 1),
  ('AWS',           'aws',           'devops',   0),
  ('Docker',        'docker',        'devops',   0),
  ('Kubernetes',    'kubernetes',    'devops',   0),
  ('CI/CD',         'cicd',          'devops',   0),
  ('PostgreSQL',    'postgresql',    'database', 0),
  ('MongoDB',       'mongodb',       'database', 0),
  ('Redis',         'redis',         'database', 0),
  ('Flutter',       'flutter',       'mobile',   0),
  ('React Native',  'react-native',  'mobile',   0),
  ('WebAssembly',   'webassembly',   'emerging', 1),
  ('Bun',           'bun',           'emerging', 1);
```

---

## 📋 Table 3: `skill_mentions`

**Purpose:** Bridge table — records that "Job #42 mentioned Skill #7". Many jobs can mention many skills.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | |
| `job_id` | INTEGER | NOT NULL, FOREIGN KEY → `jobs.id` | Which job |
| `skill_id` | INTEGER | NOT NULL, FOREIGN KEY → `skills.id` | Which skill |
| `mentioned_in` | TEXT | DEFAULT `'description'` | Where: `'title'`, `'description'`, `'both'` |
| `mentioned_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When we found it |

**SQL:**
```sql
CREATE TABLE skill_mentions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id        INTEGER NOT NULL,
    skill_id      INTEGER NOT NULL,
    mentioned_in  TEXT    DEFAULT 'description',
    mentioned_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id)   REFERENCES jobs(id)   ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE(job_id, skill_id)     -- prevent duplicate mentions
);

CREATE INDEX idx_mentions_skill_id ON skill_mentions(skill_id);
CREATE INDEX idx_mentions_job_id   ON skill_mentions(job_id);
```

**Why a separate table?** Because a job like *"Senior Python + React Developer"* mentions **2 skills**. This design supports that cleanly.

---

## 📋 Table 4: `daily_skill_counts`

**Purpose:** **Pre-aggregated** daily totals. This is what makes your charts load instantly.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | |
| `skill_id` | INTEGER | NOT NULL, FK → `skills.id` | |
| `date` | DATE | NOT NULL | The day (YYYY-MM-DD) |
| `count` | INTEGER | NOT NULL, DEFAULT 0 | How many jobs mentioned it that day |
| `source` | TEXT | NOT NULL | Which site (so you can filter by source) |

**SQL:**
```sql
CREATE TABLE daily_skill_counts (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    date     DATE    NOT NULL,
    count    INTEGER NOT NULL DEFAULT 0,
    source   TEXT    NOT NULL,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE(skill_id, date, source)
);

CREATE INDEX idx_daily_skill_date ON daily_skill_counts(skill_id, date);
```

**Example query this enables (fast):**
```sql
-- "Show me Rust's last 30 days"
SELECT date, SUM(count) AS total
FROM daily_skill_counts
WHERE skill_id = 4 AND date >= DATE('now', '-30 days')
GROUP BY date
ORDER BY date;
```

**How it gets populated:** A background job (or after each scrape) runs:
```sql
INSERT OR REPLACE INTO daily_skill_counts (skill_id, date, source, count)
SELECT sm.skill_id, DATE(j.scraped_at), j.source, COUNT(*)
FROM skill_mentions sm
JOIN jobs j ON j.id = sm.job_id
WHERE DATE(j.scraped_at) = DATE('now')
GROUP BY sm.skill_id, j.source;
```

---

## 📋 Table 5: `scrape_runs`

**Purpose:** Logging — every time the scraper runs, we record what happened. Crucial for debugging during a hackathon.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | |
| `source` | TEXT | NOT NULL | `'indeed'`, `'naukri'`, etc. |
| `query` | TEXT | NULLABLE | Search term used |
| `started_at` | TIMESTAMP | NOT NULL | |
| `finished_at` | TIMESTAMP | NULLABLE | NULL = still running |
| `status` | TEXT | NOT NULL | `'running'`, `'ok'`, `'failed'` |
| `jobs_scraped` | INTEGER | DEFAULT 0 | How many new jobs added |
| `error_message` | TEXT | NULLABLE | If failed, why |

**SQL:**
```sql
CREATE TABLE scrape_runs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source        TEXT    NOT NULL,
    query         TEXT,
    started_at    TIMESTAMP NOT NULL,
    finished_at   TIMESTAMP,
    status        TEXT    NOT NULL DEFAULT 'running',
    jobs_scraped  INTEGER DEFAULT 0,
    error_message TEXT
);

CREATE INDEX idx_runs_source_status ON scrape_runs(source, status);
```

**Sample usage:**
```sql
-- "Has Indeed been successfully scraped in the last hour?"
SELECT * FROM scrape_runs
WHERE source = 'indeed'
  AND status = 'ok'
  AND finished_at >= DATETIME('now', '-1 hour')
ORDER BY finished_at DESC LIMIT 1;
```

---

## 🔑 Foreign Key Summary

| Child table | FK | → Parent table |
|---|---|---|
| `skill_mentions.job_id` | → | `jobs.id` |
| `skill_mentions.skill_id` | → | `skills.id` |
| `daily_skill_counts.skill_id` | → | `skills.id` |
| `scrape_runs` (no FK) | — | It's a log, decoupled |

---

## 📈 Sample Data Walkthrough

**Scenario:** We scrape Indeed for "Python developer" and find this job:
> **Title:** *"Senior Python + React Developer at Acme"*
> **Description:** *"Looking for Python, React, AWS experience..."*

**Step 1 — Insert into `jobs`:**
```sql
INSERT INTO jobs (title, company, location, source, url, description)
VALUES ('Senior Python + React Developer', 'Acme', 'Remote', 'indeed',
        'https://indeed.com/job/123', 'Looking for Python, React, AWS...');
-- Gets id = 42
```

**Step 2 — Find matching skills (in Python code):**
- "Python" → skill_id 1
- "React" → skill_id 9
- "AWS" → skill_id 24

**Step 3 — Insert into `skill_mentions`:**
```sql
INSERT INTO skill_mentions (job_id, skill_id, mentioned_in) VALUES
  (42, 1,  'description'),
  (42, 9,  'description'),
  (42, 24, 'description');
```

**Step 4 — Aggregate into `daily_skill_counts` (run hourly):**
```sql
-- Python count for today goes from 11 → 12
UPDATE daily_skill_counts
SET count = count + 1
WHERE skill_id = 1 AND date = DATE('now') AND source = 'indeed';
```

**Step 5 — Log the run in `scrape_runs`:**
```sql
UPDATE scrape_runs
SET status = 'ok', finished_at = CURRENT_TIMESTAMP, jobs_scraped = 1
WHERE id = 7;
```

---

## 🛠️ Setup Script (save as `init_db.py`)

```python
import sqlite3, os

DB_PATH = "backend/data/pulsehire.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Run all CREATE TABLE statements here (copy from above)
# Then run INSERT statements for the 30 skills

conn.commit()
conn.close()
print(f"✅ Database initialized at {DB_PATH}")
```

Run once with `python init_db.py` and your DB is ready.

---

## ✅ Schema Approved When:

- [x] Can store raw jobs (with `is_active` so we can mark dead ones)
- [x] Can store a master list of skills with metadata
- [x] Can record "which job mentions which skill" (many-to-many)
- [x] Charts query a fast, pre-aggregated table
- [x] Every scrape run is logged for debugging
- [x] Indexes on every column we filter by
- [x] Foreign keys enforce data integrity
- [x] Easy to seed with 30 skills in one SQL block

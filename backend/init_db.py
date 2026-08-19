"""One-shot DB setup: create tables, indexes, and seed the 30 tracked skills.

Run from the project root:
    python backend/init_db.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `python backend/init_db.py` from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import db_session  # noqa: E402

# 5 tables in dependency order. See DATABASE.md for the rationale.
SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
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
CREATE INDEX IF NOT EXISTS idx_jobs_source     ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_location   ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs(scraped_at);

CREATE TABLE IF NOT EXISTS skills (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL UNIQUE,
    slug         TEXT    NOT NULL UNIQUE,
    category     TEXT    NOT NULL,
    is_emerging  BOOLEAN DEFAULT 0,
    aliases      TEXT,                       -- JSON array of synonyms
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_skills_category    ON skills(category);
CREATE INDEX IF NOT EXISTS idx_skills_is_emerging ON skills(is_emerging);

CREATE TABLE IF NOT EXISTS skill_mentions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id        INTEGER NOT NULL,
    skill_id      INTEGER NOT NULL,
    mentioned_in  TEXT    DEFAULT 'description',
    mentioned_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id)   REFERENCES jobs(id)   ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE(job_id, skill_id)
);
CREATE INDEX IF NOT EXISTS idx_mentions_skill_id ON skill_mentions(skill_id);
CREATE INDEX IF NOT EXISTS idx_mentions_job_id   ON skill_mentions(job_id);

CREATE TABLE IF NOT EXISTS daily_skill_counts (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    date     DATE    NOT NULL,
    count    INTEGER NOT NULL DEFAULT 0,
    source   TEXT    NOT NULL,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE(skill_id, date, source)
);
CREATE INDEX IF NOT EXISTS idx_daily_skill_date ON daily_skill_counts(skill_id, date);

CREATE TABLE IF NOT EXISTS scrape_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT    NOT NULL,
    query           TEXT,
    started_at      TIMESTAMP NOT NULL,
    finished_at     TIMESTAMP,
    status          TEXT    NOT NULL DEFAULT 'running',
    jobs_scraped    INTEGER DEFAULT 0,
    jobs_new        INTEGER DEFAULT 0,
    error_message   TEXT
);
CREATE INDEX IF NOT EXISTS idx_runs_source_status ON scrape_runs(source, status);
"""

# 30 skills, in the same order as DATABASE.md.
SKILLS_SEED = [
    # (name, slug, category, is_emerging)
    ("Python",              "python",              "language", 0),
    ("JavaScript",          "javascript",          "language", 0),
    ("TypeScript",          "typescript",          "language", 0),
    ("Rust",                "rust",                "language", 1),
    ("Go",                  "go",                  "language", 0),
    ("Java",                "java",                "language", 0),
    ("C++",                 "cpp",                 "language", 0),
    ("SQL",                 "sql",                 "language", 0),
    ("React",               "react",               "frontend", 0),
    ("Vue",                 "vue",                 "frontend", 0),
    ("Angular",             "angular",             "frontend", 0),
    ("Next.js",             "nextjs",              "frontend", 0),
    ("Node.js",             "nodejs",              "backend",  0),
    ("Django",              "django",              "backend",  0),
    ("FastAPI",             "fastapi",             "backend",  0),
    ("Spring Boot",         "spring-boot",         "backend",  0),
    ("Agentic AI",          "agentic-ai",          "ai-ml",    1),
    ("LangChain",           "langchain",           "ai-ml",    1),
    ("RAG",                 "rag",                 "ai-ml",    0),
    ("PyTorch",             "pytorch",             "ai-ml",    0),
    ("TensorFlow",          "tensorflow",          "ai-ml",    0),
    ("LLMs",                "llms",                "ai-ml",    1),
    ("Prompt Engineering",  "prompt-engineering",  "ai-ml",    1),
    ("AWS",                 "aws",                 "devops",   0),
    ("Docker",              "docker",              "devops",   0),
    ("Kubernetes",          "kubernetes",          "devops",   0),
    ("CI/CD",               "cicd",                "devops",   0),
    ("PostgreSQL",          "postgresql",          "database", 0),
    ("MongoDB",             "mongodb",             "database", 0),
    ("Redis",               "redis",               "database", 0),
    ("Flutter",             "flutter",             "mobile",   0),
    ("React Native",        "react-native",        "mobile",   0),
    ("WebAssembly",         "webassembly",         "emerging", 1),
    ("Bun",                 "bun",                 "emerging", 1),
]


def init_db() -> None:
    """Create tables, then insert any skills that don't already exist."""
    with db_session() as conn:
        conn.executescript(SCHEMA)
        # INSERT OR IGNORE keeps the script idempotent — safe to re-run.
        conn.executemany(
            "INSERT OR IGNORE INTO skills (name, slug, category, is_emerging) "
            "VALUES (?, ?, ?, ?)",
            SKILLS_SEED,
        )
        count = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
    print(f"✅ Database initialized — {count} skills loaded.")


if __name__ == "__main__":
    init_db()

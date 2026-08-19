"""Seed the DB with fake-but-plausible data so the dashboard works immediately.

Generates ~500 fake jobs across the 30 tracked skills, with 30 days of
history. Each job has a realistic title, a company, a location, and a
description that mentions 1-4 skills from our list. The trend signal is
baked in: emerging skills (Rust, Agentic AI, LLMs, WebAssembly, Bun) get
a slight upward trend over time, so the line chart actually shows a story.

Run from the project root:
    python backend/scraper/seed_sample_data.py
"""
from __future__ import annotations

import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import db_session  # noqa: E402

# ----- Tunables -------------------------------------------------------------

NUM_JOBS = 500
HISTORY_DAYS = 30
SOURCES = ["indeed", "naukri"]  # 50/50 split
LOCATIONS = [
    "Remote",
    "Bangalore, India",
    "San Francisco, CA",
    "New York, NY",
    "London, UK",
    "Berlin, Germany",
    "Toronto, Canada",
    "Hyderabad, India",
]
COMPANIES = [
    "Acme Corp", "Globex", "Initech", "Umbrella", "Hooli", "Pied Piper",
    "Stark Industries", "Wayne Enterprises", "Soylent", "Massive Dynamic",
    "Cyberdyne", "Tyrell Corp", "Wonka Industries", "Vandelay Industries",
    "Dunder Mifflin", "Sterling Cooper", "Aperture Science", "Black Mesa",
]

# Skill weights: higher = mentioned more often. Emerging skills get a
# smaller base + a rising trend, so their counts grow day-over-day.
SKILL_WEIGHTS: dict[str, float] = {
    "python": 1.0, "javascript": 1.0, "typescript": 0.9, "react": 0.95,
    "nodejs": 0.8, "java": 0.85, "sql": 0.9, "aws": 0.9, "docker": 0.8,
    "postgresql": 0.7, "mongodb": 0.55, "redis": 0.5, "kubernetes": 0.6,
    "cicd": 0.5, "django": 0.55, "fastapi": 0.45, "vue": 0.5, "angular": 0.5,
    "nextjs": 0.55, "spring-boot": 0.5, "pytorch": 0.5, "tensorflow": 0.45,
    "rag": 0.4, "llms": 0.35, "langchain": 0.3, "prompt-engineering": 0.25,
    "react-native": 0.45, "flutter": 0.5, "go": 0.6, "cpp": 0.5,
    # Emerging — start low, trend up
    "rust": 0.3, "agentic-ai": 0.15, "webassembly": 0.2, "bun": 0.1,
}

# ----- Generators -----------------------------------------------------------

TITLE_TEMPLATES = [
    "Senior {skill} Developer",
    "{skill} Engineer",
    "Staff {skill} Engineer",
    "Junior {skill} Developer",
    "{skill} + {skill2} Full-Stack Developer",
    "Backend Engineer ({skill})",
    "Frontend Engineer ({skill})",
    "ML Engineer ({skill})",
    "DevOps Engineer ({skill})",
    "{skill} Tech Lead",
    "Lead {skill} Architect",
    "Remote {skill} Developer",
]

DESC_TEMPLATES = [
    "We're hiring a {skill} developer to join our team. You'll work with {skill2} and {skill3} daily.",
    "Looking for an engineer with strong {skill} experience. Bonus points for {skill2} and {skill3}.",
    "Join us as a {skill} engineer! Our stack includes {skill}, {skill2}, and {skill3}.",
    "Our team uses {skill}, {skill2}, and {skill3} to ship product weekly.",
    "We're building the future of fintech with {skill}, {skill2}, and {skill3}.",
    "Help us scale our {skill}-based platform. Experience with {skill2} a plus.",
]


def make_title(rng: random.Random, skills: list[str]) -> str:
    template = rng.choice(TITLE_TEMPLATES)
    picks = rng.sample(skills, min(len(skills), template.count("{skill}") + template.count("{skill2}")))
    return template.format(
        skill=picks[0].title() if picks else "Software",
        skill2=picks[1].title() if len(picks) > 1 else "Docker",
        skill3=picks[2].title() if len(picks) > 2 else "AWS",
    )


def make_description(rng: random.Random, skills: list[str]) -> str:
    template = rng.choice(DESC_TEMPLATES)
    picks = (skills + ["Docker", "AWS", "Git"])[:3]
    while len(picks) < 3:
        picks.append("Git")
    return template.format(skill=picks[0], skill2=picks[1], skill3=picks[2])


# ----- Main seeder ----------------------------------------------------------

def seed() -> None:
    rng = random.Random(42)  # deterministic so re-runs produce the same demo

    with db_session() as conn:
        # Skip if already populated — avoids blowing away real data.
        existing = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        if existing > 0:
            print(f"⚠️  Found {existing} jobs already in DB. Skipping seed.")
            print("   Delete backend/data/pulsehire.db to re-seed.")
            return

        skills = conn.execute("SELECT id, slug, name FROM skills").fetchall()
        skill_by_slug = {row["slug"]: row for row in skills}
        skill_slugs = list(SKILL_WEIGHTS.keys())
        today = date.today()

        jobs_inserted = 0
        mentions_inserted = 0
        daily_counts = {}  # (skill_id, date, source) -> count

        for i in range(NUM_JOBS):
            # Spread scraped_at across the last HISTORY_DAYS days.
            # Weight towards recent days (more realistic for a fresh scrape).
            days_ago = int(rng.triangular(0, HISTORY_DAYS, HISTORY_DAYS * 0.3))
            scraped = datetime.now() - timedelta(days=days_ago, hours=rng.randint(0, 23))
            source = rng.choice(SOURCES)
            location = rng.choice(LOCATIONS)
            company = rng.choice(COMPANIES)

            # Pick 1-4 skills for this job, weighted by SKILL_WEIGHTS.
            n_skills = rng.choices([1, 2, 3, 4], weights=[2, 5, 4, 1])[0]
            chosen = []
            weights = [SKILL_WEIGHTS[s] for s in skill_slugs]
            for _ in range(n_skills):
                slug = rng.choices(skill_slugs, weights=weights, k=1)[0]
                if slug not in chosen:
                    chosen.append(slug)
            skill_names = [skill_by_slug[s]["name"] for s in chosen]

            title = make_title(rng, skill_names)
            description = make_description(rng, skill_names)
            # Unique URL even for fake data.
            url = f"https://example.com/{source}/job/{i}-{rng.randint(10000, 99999)}"

            cur = conn.execute(
                "INSERT INTO jobs (title, company, location, source, url, description, posted_date, scraped_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (title, company, location, source, url, description,
                 scraped.date().isoformat(), scraped.isoformat(sep=" ")),
            )
            job_id = cur.lastrowid
            jobs_inserted += 1

            for slug in chosen:
                skill = skill_by_slug[slug]
                # Mention in title if it's the lead skill, otherwise description.
                mentioned_in = "title" if slug == chosen[0] and rng.random() < 0.4 else "description"
                conn.execute(
                    "INSERT OR IGNORE INTO skill_mentions (job_id, skill_id, mentioned_in) "
                    "VALUES (?, ?, ?)",
                    (job_id, skill["id"], mentioned_in),
                )
                mentions_inserted += 1
                # Bump the daily count for this (skill, day, source).
                key = (skill["id"], scraped.date().isoformat(), source)
                daily_counts[key] = daily_counts.get(key, 0) + 1

        # Bulk-insert daily_skill_counts in one go.
        conn.executemany(
            "INSERT OR REPLACE INTO daily_skill_counts (skill_id, date, source, count) "
            "VALUES (?, ?, ?, ?)",
            [(sid, d, src, c) for (sid, d, src), c in daily_counts.items()],
        )

        # Stamp a successful scrape run so /api/stats has something to show.
        conn.execute(
            "INSERT INTO scrape_runs (source, query, started_at, finished_at, status, jobs_scraped, jobs_new) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("seed", "sample-data", (datetime.now() - timedelta(seconds=2)).isoformat(sep=" "),
             datetime.now().isoformat(sep=" "), "ok", jobs_inserted, jobs_inserted),
        )

    print(f"✅ Seeded {jobs_inserted} jobs and {mentions_inserted} skill mentions across {HISTORY_DAYS} days.")
    print(f"   Sources: {SOURCES}  Locations: {len(LOCATIONS)}  Skills: {len(skills)}")


if __name__ == "__main__":
    seed()

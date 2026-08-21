"""Scraper registry — maps source names to scrape functions."""
from __future__ import annotations
from typing import Callable, Iterator

_REGISTRY: dict[str, tuple[Callable, str]] = {}

def register(slug: str, display_name: str):
    def decorator(fn):
        _REGISTRY[slug] = (fn, display_name)
        return fn
    return decorator

def get_scraper(source: str) -> Callable:
    if source not in _REGISTRY:
        raise ValueError(f"Unknown source: {source!r}. Available: {list_sources()}")
    fn, _ = _REGISTRY[source]
    return fn

def list_sources() -> list[str]:
    return list(_REGISTRY.keys())

def list_source_info() -> list[dict]:
    """Return only sources that have at least 1 job in the DB."""
    try:
        import sqlite3, os
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'pulsehire.db')
        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT source, COUNT(*) as cnt FROM jobs GROUP BY source HAVING cnt > 0"
        ).fetchall()
        conn.close()
        active = {r[0] for r in rows}
        return [{"slug": s, "name": n} for s, (_, n) in _REGISTRY.items() if s in active]
    except Exception:
        return [{"slug": s, "name": n} for s, (_, n) in _REGISTRY.items()]

def _load_all():
    import scraper.indeed
    import scraper.linkedin
    import scraper.glassdoor
    import scraper.dice
    import scraper.remoteok
    import scraper.simplyhired
    import scraper.wellfound
    import scraper.naukri

_load_all()

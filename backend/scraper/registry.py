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
    """Return all registered sources."""
    return [{"slug": s, "name": n} for s, (_, n) in _REGISTRY.items()]

def _load_all():
    # Working scrapers
    import scraper.linkedin       # Bright Data Web Unlocker + Dataset API
    import scraper.api_sources    # Direct public APIs (no auth needed)

_load_all()

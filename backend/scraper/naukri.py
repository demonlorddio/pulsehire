"""Naukri scraper — demo/mock mode (no live scraping yet)."""
from __future__ import annotations
from typing import Iterator
from scraper.registry import register


@register("naukri", "Naukri")
def scrape_naukri(query: str = "software engineer", **kwargs) -> Iterator[dict]:
    """Placeholder — returns empty. Real scraper TBD."""
    return iter([])

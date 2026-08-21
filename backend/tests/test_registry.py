"""Unit tests for the scraper registry."""
import pytest
from scraper.registry import get_scraper, list_sources, list_source_info


def test_all_sources_registered():
    sources = list_sources()
    assert "indeed" in sources
    assert "linkedin" in sources


def test_get_scraper_returns_callable():
    fn = get_scraper("indeed")
    assert callable(fn)


def test_unknown_source_raises():
    with pytest.raises(ValueError):
        get_scraper("nonexistent")


def test_source_info_has_slug_and_name():
    info = list_source_info()
    for s in info:
        assert "slug" in s
        assert "name" in s

"""Unit tests for the skill extractor."""
from scraper.skills import extract_skill_ids


def _make_skill(skill_id, name, aliases=None):
    return {"id": skill_id, "name": name, "slug": name.lower(), "aliases": aliases}


def test_exact_match():
    skills = [_make_skill(1, "Python"), _make_skill(2, "React")]
    result = extract_skill_ids("We need a Python developer", skills)
    assert len(result) == 1
    assert result[0]["name"] == "Python"


def test_case_insensitive():
    skills = [_make_skill(1, "Rust")]
    result = extract_skill_ids("Looking for RUST experience", skills)
    assert len(result) == 1


def test_no_false_positives():
    # "Go" as a standalone word IS a match, so test a partial/substring case
    skills = [_make_skill(1, "React")]
    result = extract_skill_ids("The reaction was positive", skills)
    assert len(result) == 0


def test_alias_matching():
    skills = [_make_skill(1, "Agentic AI", aliases='["AI Agents", "Agentic"]')]
    result = extract_skill_ids("Experience with AI Agents required", skills)
    assert len(result) == 1


def test_multiple_skills():
    skills = [
        _make_skill(1, "Python"),
        _make_skill(2, "Docker"),
        _make_skill(3, "Kubernetes"),
    ]
    result = extract_skill_ids("Python + Docker + Kubernetes deployment", skills)
    assert len(result) == 3


def test_empty_text():
    skills = [_make_skill(1, "Python")]
    result = extract_skill_ids("", skills)
    assert len(result) == 0


def test_no_match():
    skills = [_make_skill(1, "Python"), _make_skill(2, "Rust")]
    result = extract_skill_ids("We need a Java developer", skills)
    assert len(result) == 0

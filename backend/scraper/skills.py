"""Skill extractor — matches job text against the tracked skill list.

Uses case-insensitive keyword matching.  Each skill row from the DB has a
`name`, `slug`, and optional `aliases` (JSON list).  We match whole-word-ish
patterns so "react" doesn't match "reaction".
"""
from __future__ import annotations

import re
from typing import Any


def extract_skill_ids(text: str, skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the subset of `skills` whose name or alias appears in `text`.

    Parameters
    ----------
    text : str
        The combined title + description of a job posting.
    skills : list[dict]
        Each dict must have at least ``id`` and ``name`` keys.  ``aliases``
        is optional (JSON string or list of strings).

    Returns
    -------
    list[dict]
        The matching skill dicts (same shape as input).
    """
    text_lower = text.lower()
    matched: list[dict[str, Any]] = []

    for skill in skills:
        # Build a list of keywords to test: the canonical name + aliases.
        # Support both dicts and sqlite3.Row objects uniformly.
        skill_id = skill["id"]
        name = skill["name"]
        keywords: list[str] = [name]
        raw_aliases = skill["aliases"] if "aliases" in skill.keys() else None
        if raw_aliases:
            if isinstance(raw_aliases, str):
                # aliases stored as JSON string '["a","b"]'
                import json
                try:
                    aliases = json.loads(raw_aliases)
                except (json.JSONDecodeError, TypeError):
                    aliases = []
            else:
                aliases = raw_aliases
            if isinstance(aliases, list):
                keywords.extend(str(a) for a in aliases)

        for kw in keywords:
            pattern = re.escape(kw.lower())
            # Use word-boundary-ish matching: preceded by start or non-alpha,
            # followed by end or non-alpha.
            if re.search(rf"(?:^|[^\w]){pattern}(?:[^\w]|$)", text_lower):
                matched.append(skill)
                break  # one match per skill is enough

    return matched

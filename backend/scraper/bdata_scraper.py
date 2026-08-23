"""Bright Data Scraper Studio integration via bdata CLI.

This module wraps the bdata CLI to create, run, and heal scrapers
built with Bright Data's Scraper Studio.

Usage:
    from scraper.bdata_scraper import run_bdata_scraper, heal_bdata_scraper
    
    # Run a scraper
    results = run_bdata_scraper("c_mt30519s10fysjo97i", "https://www.indeed.com/jobs?q=python")
    
    # Heal a broken scraper
    heal_bdata_scraper("c_mt30519s10fysjo97i", "The job card selector changed")
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from typing import Optional


# Store collector IDs per source
_COLLECTOR_IDS = {
    "indeed": os.getenv("BDATA_COLLECTOR_INDEED", ""),
    "linkedin": os.getenv("BDATA_COLLECTOR_LINKEDIN", ""),
    "glassdoor": os.getenv("BDATA_COLLECTOR_GLASSDOOR", ""),
    "remoteok": os.getenv("BDATA_COLLECTOR_REMOTEOK", "c_mt61lafrqa337jx3z"),
}


def run_bdata_scraper(
    collector_id: str,
    url: str,
    timeout: int = 600,
    env: Optional[dict] = None,
) -> list[dict]:
    """Run a bdata scraper and return structured job data.
    
    Args:
        collector_id: The Collector ID from `bdata scraper create`
        url: The URL to scrape
        timeout: Max seconds to wait for results
        env: Additional environment variables (merged with current env)
    
    Returns:
        List of job dicts with title, company, location, url, description
    """
    api_key = os.getenv("BRIGHTDATA_API_KEY", "")
    if not api_key:
        raise RuntimeError("BRIGHTDATA_API_KEY not set")
    
    # Build environment with API key
    run_env = os.environ.copy()
    run_env["BRIGHTDATA_API_KEY"] = api_key
    if env:
        run_env.update(env)
    
    # Trigger the scraper
    print(f"[bdata] Running scraper {collector_id} for {url}")
    trigger_cmd = [
        "npx", "-p", "@brightdata/cli",
        "bdata", "scraper", "run", collector_id, url,
    ]
    
    try:
        result = subprocess.run(
            trigger_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=run_env,
            shell=(os.name == "nt"),  # Required on Windows
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"bdata scraper run failed: {result.stderr}")
        
        # Parse the output — bdata returns JSON lines
        jobs = _parse_bdata_output(result.stdout)
        print(f"[bdata] Got {len(jobs)} jobs from scraper")
        return jobs
        
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"bdata scraper run timed out after {timeout}s")
    except FileNotFoundError:
        raise RuntimeError("bdata CLI not found. Install with: npm install -g @brightdata/cli")


def heal_bdata_scraper(
    collector_id: str,
    description: str,
    approve: bool = True,
    env: Optional[dict] = None,
) -> dict:
    """Self-heal a broken scraper using bdata scraper heal.
    
    Args:
        collector_id: The Collector ID to heal
        description: Description of what broke
        approve: Whether to auto-approve the fix
        env: Additional environment variables
    
    Returns:
        Dict with status and details of the heal
    """
    api_key = os.getenv("BRIGHTDATA_API_KEY", "")
    if not api_key:
        raise RuntimeError("BRIGHTDATA_API_KEY not set")
    
    run_env = os.environ.copy()
    run_env["BRIGHTDATA_API_KEY"] = api_key
    if env:
        run_env.update(env)
    
    # Heal the scraper
    print(f"[bdata] Healing scraper {collector_id}: {description}")
    heal_cmd = [
        "npx", "-p", "@brightdata/cli",
        "bdata", "scraper", "heal", collector_id, description,
    ]
    
    result = subprocess.run(
        heal_cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        env=run_env,
        shell=(os.name == "nt"),
    )
    
    output = result.stdout + result.stderr
    if 'Self-healing failed' in output or 'heal did not complete' in output:
        # Scraper wasn't broken or heal couldn't fix it
        return {"status": "unchanged", "message": "Scraper is working — nothing to heal", "details": output[-500:]}
    if result.returncode != 0 and 'Healing scraper' not in output:
        return {"status": "error", "message": output[-500:]}
    
    # Approve the fix if requested
    if approve:
        approve_cmd = [
            "npx", "-p", "@brightdata/cli",
            "bdata", "scraper", "approve", collector_id,
        ]
        subprocess.run(
            approve_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            env=run_env,
            shell=(os.name == "nt"),
        )
    
    return {"status": "healed", "collector_id": collector_id, "fix": description}


def get_collector_id(source: str) -> Optional[str]:
    """Get the Collector ID for a source."""
    return _COLLECTOR_IDS.get(source) or None


def set_collector_id(source: str, collector_id: str) -> None:
    """Set (cache) the Collector ID for a source."""
    _COLLECTOR_IDS[source] = collector_id


def _parse_bdata_output(output: str) -> list[dict]:
    """Parse bdata CLI output into job dicts.
    
    bdata returns either:
    - JSON lines (one JSON object per line)
    - A single JSON array
    - Text output with JSON embedded
    """
    jobs = []
    
    # Try to find JSON in the output
    # Look for JSON array or objects
    for line in output.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("Triggered") or line.startswith("Waiting") or line.startswith("Polling"):
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, list):
                for item in obj:
                    job = _normalize_bdata_record(item)
                    if job:
                        jobs.append(job)
            elif isinstance(obj, dict):
                job = _normalize_bdata_record(obj)
                if job:
                    jobs.append(job)
        except json.JSONDecodeError:
            continue
    
    return jobs


def _normalize_bdata_record(record: dict) -> Optional[dict]:
    """Normalize a bdata record to our standard job format."""
    # bdata may use different field names depending on the scraper
    title = (
        record.get("title")
        or record.get("job_title")
        or record.get("name")
        or record.get("position")
        or ""
    )
    
    if not title:
        return None
    
    url = (
        record.get("url")
        or record.get("link")
        or record.get("job_url")
        or record.get("apply_link")
        or record.get("product_page_url")
        or ""
    )
    
    company = (
        record.get("company")
        or record.get("company_name")
        or record.get("employer")
        or record.get("organization")
        or None
    )
    
    location = (
        record.get("location")
        or record.get("job_location")
        or record.get("city")
        or None
    )
    
    # Tech stack / skills from bdata
    tech_stack = record.get("tech_stack") or []
    if tech_stack and isinstance(tech_stack, list):
        description = "Skills: " + ", ".join(tech_stack[:10])
    else:
        description = (
            record.get("description")
            or record.get("job_description")
            or record.get("summary")
            or record.get("job_summary")
            or None
        )
    
    posted_date = (
        record.get("posted_date")
        or record.get("date_posted")
        or record.get("job_posted_time")
        or record.get("postedAt")
        or None
    )
    
    return {
        "title": title,
        "company": company,
        "location": location,
        "url": url,
        "description": description,
        "posted_date": posted_date,
    }

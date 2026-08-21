"""Shared Bright Data fetcher -- Web Unlocker + Dataset API.

Includes retry with exponential backoff for rate limits and server errors.
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Any
import requests
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY", "")
BRIGHTDATA_ZONE = os.getenv("BRIGHTDATA_ZONE", "")

DATASET_IDS = {
    "indeed":    "gd_l4dx9j9sscpvs7no2",
    "linkedin":  "gd_lpfll7v5hcqtkxl6l",
    "glassdoor": "gd_lpfbbndm1xnopbrcr0",
}


def fetch_html(url: str, timeout: int = 120, retries: int = 3, backoff: int = 5) -> str:
    """Fetch a URL through Bright Data Web Unlocker with retry + exponential backoff."""
    if not BRIGHTDATA_API_KEY:
        raise RuntimeError("BRIGHTDATA_API_KEY is not set")
    if not BRIGHTDATA_ZONE:
        raise RuntimeError("BRIGHTDATA_ZONE is not set")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
    }
    payload = {"zone": BRIGHTDATA_ZONE, "url": url, "format": "raw"}

    for attempt in range(retries):
        try:
            resp = requests.post(
                "https://api.brightdata.com/request",
                json=payload,
                headers=headers,
                timeout=timeout,
            )
            if resp.status_code == 429 or resp.status_code >= 500:
                wait = backoff * (2 ** attempt)
                print(f"[fetcher] Got {resp.status_code}, retrying in {wait}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                wait = backoff * (2 ** attempt)
                print(f"[fetcher] Timeout, retrying in {wait}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"[fetcher] Failed after {retries} attempts for {url}")


def scrape_dataset(source: str, urls: list[str], timeout: int = 120, retries: int = 3, backoff: int = 5) -> list[dict]:
    """Fetch structured job data via Bright Data Dataset API with retry + exponential backoff."""
    if not BRIGHTDATA_API_KEY:
        raise RuntimeError("BRIGHTDATA_API_KEY is not set")
    dataset_id = DATASET_IDS.get(source)
    if not dataset_id:
        raise ValueError(f"No dataset ID for source: {source}")

    endpoint = f"https://api.brightdata.com/datasets/v3/scrape?dataset_id={dataset_id}&notify=false&include_errors=true"
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"input": [{"url": u} for u in urls], "limit_per_input": None}

    for attempt in range(retries):
        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
            if resp.status_code == 429 or resp.status_code >= 500:
                wait = backoff * (2 ** attempt)
                print(f"[fetcher] Dataset API {resp.status_code}, retrying in {wait}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            break
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                wait = backoff * (2 ** attempt)
                print(f"[fetcher] Dataset API timeout, retrying in {wait}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
            else:
                raise
    else:
        raise RuntimeError(f"[fetcher] Dataset API failed after {retries} attempts for source={source}")

    results = []
    for line in resp.text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if "error" in obj and "job_title" not in obj:
                continue
            results.append(obj)
        except json.JSONDecodeError:
            continue
    return results

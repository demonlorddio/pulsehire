"""Shared Bright Data fetcher -- Web Unlocker + Dataset API."""
from __future__ import annotations
import json
import os
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


def fetch_html(url, timeout=120):
    if not BRIGHTDATA_API_KEY:
        raise RuntimeError("BRIGHTDATA_API_KEY is not set")
    if not BRIGHTDATA_ZONE:
        raise RuntimeError("BRIGHTDATA_ZONE is not set")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {BRIGHTDATA_API_KEY}"}
    payload = {"zone": BRIGHTDATA_ZONE, "url": url, "format": "raw"}
    resp = requests.post("https://api.brightdata.com/request", json=payload, headers=headers, timeout=timeout)
    if not resp.ok:
        print(f"[fetcher] Web Unlocker error {resp.status_code}: {resp.text[:300]}")
    resp.raise_for_status()
    return resp.text


def scrape_dataset(source, urls, timeout=120):
    if not BRIGHTDATA_API_KEY:
        raise RuntimeError("BRIGHTDATA_API_KEY is not set")
    dataset_id = DATASET_IDS.get(source)
    if not dataset_id:
        raise ValueError(f"No dataset ID for source: {source}")
    endpoint = f"https://api.brightdata.com/datasets/v3/scrape?dataset_id={dataset_id}&notify=false&include_errors=true"
    headers = {"Authorization": f"Bearer {BRIGHTDATA_API_KEY}", "Content-Type": "application/json"}
    payload = {"input": [{"url": u} for u in urls], "limit_per_input": None}
    resp = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
    if not resp.ok:
        print(f"[fetcher] Dataset API error {resp.status_code}: {resp.text[:300]}")
        resp.raise_for_status()
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

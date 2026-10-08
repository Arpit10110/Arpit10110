#!/usr/bin/env python3
"""
fetch_contributions.py
Fetches real GitHub contribution calendar data for Arpit10110 and calculates
active days, streaks, and calendar day counts.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
import requests

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "profile.json"
DATA_DIR = ROOT_DIR / "data"
CONTRIBS_OUT = DATA_DIR / "contributions.json"


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_from_api(username):
    url = f"https://github-contributions-api.jogruber.de/v4/{username}"
    try:
        r = requests.get(url, timeout=15)
        if r.ok:
            data = r.json()
            raw_contribs = data.get("contributions", [])
            totals = data.get("total", {})
            return raw_contribs, totals
    except Exception as e:
        print(f"Contribution API fetch failed: {e}")
    return None, None


def fetch_from_html(username):
    url = f"https://github.com/users/{username}/contributions"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.ok:
            # Matches data-date="YYYY-MM-DD" and data-level="X"
            pattern = r'data-date=["\']([0-9]{4}-[0-9]{2}-[0-9]{2})["\'][^>]*data-level=["\']([0-4])["\']'
            matches = re.findall(pattern, r.text)
            if matches:
                contribs = []
                for date_str, level_str in matches:
                    level = int(level_str)
                    count = 1 if level > 0 else 0
                    contribs.append({"date": date_str, "count": count, "level": level})
                return contribs, {}
    except Exception as e:
        print(f"Contribution HTML scraper failed: {e}")
    return None, None


def calculate_streaks(chronological_days):
    if not chronological_days:
        return 0, 0

    longest_streak = 0
    current_temp = 0
    
    # Identify longest streak
    for day in chronological_days:
        if day["count"] > 0:
            current_temp += 1
            if current_temp > longest_streak:
                longest_streak = current_temp
        else:
            current_temp = 0

    # Calculate current streak ending at latest date or day before
    current_streak = 0
    # Walk backwards from the most recent day
    for day in reversed(chronological_days):
        if day["count"] > 0:
            current_streak += 1
        elif current_streak == 0:
            # Today might not have commits yet, check if yesterday was active
            continue
        else:
            break

    return current_streak, longest_streak


def main():
    config = load_config()
    username = config.get("identity", {}).get("username", "Arpit10110")
    print(f"Fetching contribution activity for: {username}...")

    raw_contribs, totals = fetch_from_api(username)
    if not raw_contribs:
        print("API failed, attempting fallback to GitHub contributions HTML...")
        raw_contribs, totals = fetch_from_html(username)

    if not raw_contribs:
        print("Warning: Could not fetch fresh contribution activity.")
        if CONTRIBS_OUT.exists():
            print("Preserving existing contributions.json file.")
            return
        sys.exit(1)

    # Sort chronologically by date
    chronological = sorted(raw_contribs, key=lambda x: x["date"])

    # Ensure deduplicated dates
    unique_days_dict = {d["date"]: d for d in chronological}
    all_dates_sorted = [unique_days_dict[k] for k in sorted(unique_days_dict.keys())]

    # Calculate lifetime total
    if totals:
        total_lifetime = sum(totals.values())
    else:
        total_lifetime = sum(d["count"] for d in all_dates_sorted)

    # For the last 52 weeks (364 days plus current partial week)
    # 52 weeks = 364 days. Let's take up to the last 364 or 371 days (integer multiple of 7)
    recent_365 = all_dates_sorted[-365:] if len(all_dates_sorted) >= 365 else all_dates_sorted
    total_past_year = sum(d["count"] for d in recent_365)
    active_days = sum(1 for d in recent_365 if d["count"] > 0)

    current_streak, longest_streak = calculate_streaks(all_dates_sorted)

    # Prepare 52 weeks aligned to Sunday-Saturday or Monday-Sunday
    # Standard GitHub contribution graph displays 52-53 columns, 7 rows (Sunday to Saturday)
    # Let's take the trailing 52 weeks: 52 * 7 = 364 days
    trailing_days = all_dates_sorted[-364:] if len(all_dates_sorted) >= 364 else all_dates_sorted

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "total_lifetime": total_lifetime,
        "total_past_year": total_past_year,
        "active_days_past_year": active_days,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "days": trailing_days
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONTRIBS_OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"✓ Saved contribution data to {CONTRIBS_OUT}")
    print(f"  Total Lifetime: {total_lifetime:,} | Past Year: {total_past_year:,} | Active Days: {active_days} | Longest Streak: {longest_streak} days")


if __name__ == "__main__":
    main()

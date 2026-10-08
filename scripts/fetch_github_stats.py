#!/usr/bin/env python3
"""
fetch_github_stats.py
Fetches real GitHub user statistics and calculates aggregated language percentages
based on actual bytes reported across public repositories.
"""

import json
import os
import sys
from datetime import datetime, timezone
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
CACHE_PATH = DATA_DIR / "repo_languages_cache.json"
LANGUAGES_OUT = DATA_DIR / "languages.json"
STATS_OUT = DATA_DIR / "github-stats.json"


def get_headers():
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Arpit10110-Profile-Stats-Fetcher"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def check_rate_limit(session, headers):
    try:
        r = session.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
        if r.ok:
            data = r.json().get("rate", {})
            return data.get("remaining", 0)
    except Exception as e:
        print(f"Warning: Could not check rate limit: {e}")
    return 60


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_cache():
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def fetch_all_repos(session, username, headers):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        res = session.get(url, headers=headers, timeout=15)
        if not res.ok:
            print(f"Warning: Failed to fetch repos page {page}: {res.status_code}")
            break
        data = res.json()
        if not isinstance(data, list) or len(data) == 0:
            break
        repos.extend(data)
        page += 1
    return repos


def normalize_language_name(name):
    # Standard mapping if needed; GitHub returns canonical names like JavaScript, TypeScript, Python, CSS, HTML, C++
    mapping = {
        "Jupyter Notebook": "Python",
    }
    return mapping.get(name, name)


def main():
    config = load_config()
    username = config.get("identity", {}).get("username", "Arpit10110")
    headers = get_headers()
    session = requests.Session()

    print(f"Fetching GitHub data for user: {username}...")
    user_res = session.get(f"https://api.github.com/users/{username}", headers=headers, timeout=15)
    
    if not user_res.ok:
        print(f"Error fetching user data: {user_res.status_code} {user_res.text}")
        if STATS_OUT.exists() and LANGUAGES_OUT.exists():
            print("Preserving existing generated data due to API failure.")
            return
        sys.exit(1)

    user_data = user_res.json()
    public_repos_count = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)
    following = user_data.get("following", 0)
    avatar_url = user_data.get("avatar_url", "")

    all_repos = fetch_all_repos(session, username, headers)
    print(f"Retrieved {len(all_repos)} total repositories.")

    # Filter out forks and archived repos to measure genuine personal authored code
    owned_repos = [r for r in all_repos if not r.get("fork") and not r.get("archived")]
    print(f"Active non-fork repositories: {len(owned_repos)}")

    total_stars = sum(r.get("stargazers_count", 0) for r in owned_repos)
    total_forks = sum(r.get("forks_count", 0) for r in owned_repos)

    cache = load_cache()
    remaining_reqs = check_rate_limit(session, headers)
    print(f"GitHub API remaining requests: {remaining_reqs}")

    # Sort repos by updated_at or size so most active/substantial projects get refreshed first
    owned_repos.sort(key=lambda x: x.get("size", 0), reverse=True)

    language_totals = {}
    for repo in owned_repos:
        repo_name = repo.get("name")
        pushed_at = repo.get("pushed_at", "")
        cached_entry = cache.get(repo_name)

        lang_data = None
        # Use cache if pushed_at hasn't changed
        if cached_entry and cached_entry.get("pushed_at") == pushed_at and "languages" in cached_entry:
            lang_data = cached_entry["languages"]
        elif remaining_reqs > 3:
            lang_url = repo.get("languages_url")
            if lang_url:
                try:
                    lang_res = session.get(lang_url, headers=headers, timeout=10)
                    remaining_reqs -= 1
                    if lang_res.ok:
                        lang_data = lang_res.json()
                        cache[repo_name] = {
                            "pushed_at": pushed_at,
                            "languages": lang_data
                        }
                except Exception as e:
                    print(f"Could not fetch languages for {repo_name}: {e}")

        # Fallback to cached or primary language with size
        if lang_data is None and cached_entry:
            lang_data = cached_entry.get("languages", {})
        elif lang_data is None and repo.get("language"):
            # If rate limited and not cached, use primary language and repo size in bytes
            primary = repo.get("language")
            size_bytes = (repo.get("size", 10) * 1024)
            lang_data = {primary: size_bytes}

        if lang_data:
            for lang, byte_count in lang_data.items():
                norm = normalize_language_name(lang)
                language_totals[norm] = language_totals.get(norm, 0) + byte_count

    save_cache(cache)

    total_bytes = sum(language_totals.values())
    print(f"Total aggregated code bytes: {total_bytes:,}")

    # Calculate real percentages
    sorted_langs = sorted(language_totals.items(), key=lambda x: x[1], reverse=True)
    lang_list = []
    top_limit = 7

    for idx, (lang, byte_count) in enumerate(sorted_langs):
        pct = round((byte_count / total_bytes) * 100, 1) if total_bytes > 0 else 0
        if idx < top_limit:
            lang_list.append({
                "name": lang,
                "bytes": byte_count,
                "percentage": pct
            })
        else:
            # Group into Other if beyond top_limit
            other_entry = next((item for item in lang_list if item["name"] == "Other"), None)
            if other_entry:
                other_entry["bytes"] += byte_count
            else:
                lang_list.append({
                    "name": "Other",
                    "bytes": byte_count,
                    "percentage": 0
                })

    # Recalculate Other percentage so total sums to ~100
    for item in lang_list:
        if item["name"] == "Other":
            item["percentage"] = round((item["bytes"] / total_bytes) * 100, 1)

    # Validate sum
    pct_sum = sum(l["percentage"] for l in lang_list)
    print(f"Calculated top languages: {len(lang_list)}, percentage sum: {pct_sum:.1f}%")

    languages_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_bytes": total_bytes,
        "repos_analyzed": len(owned_repos),
        "languages": lang_list
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(LANGUAGES_OUT, "w", encoding="utf-8") as f:
        json.dump(languages_payload, f, indent=2)
    print(f"✓ Saved language statistics to {LANGUAGES_OUT}")

    stats_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "public_repos": public_repos_count,
        "owned_repos": len(owned_repos),
        "followers": followers,
        "following": following,
        "stars": total_stars,
        "forks": total_forks,
        "avatar_url": avatar_url,
        "top_language": lang_list[0]["name"] if lang_list else "JavaScript"
    }

    with open(STATS_OUT, "w", encoding="utf-8") as f:
        json.dump(stats_payload, f, indent=2)
    print(f"✓ Saved GitHub stats to {STATS_OUT}")


if __name__ == "__main__":
    main()

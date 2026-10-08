#!/usr/bin/env python3
"""
generate_stats.py
Renders real GitHub metrics, streak, and activity counts into a modern terminal SVG card.
"""

import json
import sys
from pathlib import Path

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
STATS_PATH = ROOT_DIR / "data" / "github-stats.json"
CONTRIBS_PATH = ROOT_DIR / "data" / "contributions.json"
LANGS_PATH = ROOT_DIR / "data" / "languages.json"
ASSETS_DIR = ROOT_DIR / "assets"
STATS_SVG_OUT = ASSETS_DIR / "github-stats.svg"


def load_data():
    stats = {}
    if STATS_PATH.exists():
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            stats = json.load(f)

    contribs = {}
    if CONTRIBS_PATH.exists():
        with open(CONTRIBS_PATH, "r", encoding="utf-8") as f:
            contribs = json.load(f)

    langs = {}
    if LANGS_PATH.exists():
        with open(LANGS_PATH, "r", encoding="utf-8") as f:
            langs = json.load(f)

    return stats, contribs, langs


def build_stats_svg(stats, contribs, langs):
    card_width = 890
    card_height = 200

    public_repos = stats.get("public_repos", 124)
    followers = stats.get("followers", 17)
    stars = stats.get("stars", 30)
    forks = stats.get("forks", 3)

    lifetime_contribs = contribs.get("total_lifetime", 2742)
    past_year_contribs = contribs.get("total_past_year", 1394)
    longest_streak = contribs.get("longest_streak", 29)
    current_streak = contribs.get("current_streak", 0)

    top_lang = "JavaScript"
    top_pct = 39.1
    if langs.get("languages"):
        top_lang = langs["languages"][0].get("name", "JavaScript")
        top_pct = langs["languages"][0].get("percentage", 39.1)

    # 4 Metric Columns
    col_width = 196
    col_gap = 14
    start_x = 30
    box_y = 62
    box_height = 110

    metrics = [
        {
            "icon": "📦",
            "title": "REPOSITORIES",
            "value": f"{public_repos}",
            "sub": f"{stars} Stars · {forks} Forks",
            "color": "#58A6FF"
        },
        {
            "icon": "⚡",
            "title": "CONTRIBUTIONS",
            "value": f"{past_year_contribs:,}",
            "sub": f"{lifetime_contribs:,} Lifetime Total",
            "color": "#39D353"
        },
        {
            "icon": "🔥",
            "title": "BEST STREAK",
            "value": f"{longest_streak} Days",
            "sub": f"{current_streak}d Active Streak",
            "color": "#D29922"
        },
        {
            "icon": "🏆",
            "title": "TOP LANGUAGE",
            "value": f"{top_lang}",
            "sub": f"{top_pct:.1f}% Code Weight",
            "color": "#A371F7"
        }
    ]

    metric_boxes_svg = []
    for i, m in enumerate(metrics):
        bx = start_x + (i * (col_width + col_gap))
        delay = round(0.1 + (i * 0.1), 2)
        box_str = f"""
    <!-- Metric {i+1}: {m['title']} -->
    <g transform="translate({bx}, {box_y})">
      <rect x="0" y="0" width="{col_width}" height="{box_height}" rx="8" fill="#161B22" stroke="#30363D" stroke-width="1" />
      <text x="16" y="26" class="metric-title">{m['icon']}  {m['title']}</text>
      <text x="16" y="65" class="metric-value" fill="{m['color']}">{m['value']}</text>
      <text x="16" y="90" class="metric-sub">{m['sub']}</text>
    </g>"""
        metric_boxes_svg.append(box_str)

    boxes_combined = "\n".join(metric_boxes_svg)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {card_width} {card_height}" width="{card_width}" height="{card_height}">
  <defs>
    <filter id="subtleGlowStats" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <style>
    .terminal-bg {{
      fill: #0D1117;
      stroke: #30363D;
      stroke-width: 1.5;
      rx: 10px;
    }}
    .terminal-header {{
      fill: #161B22;
      stroke: #30363D;
      stroke-width: 1;
    }}
    .dot-red {{ fill: #FF5F56; }}
    .dot-yellow {{ fill: #FFBD2E; }}
    .dot-green {{ fill: #27C93F; }}
    .title-text {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Fira Code", monospace;
      font-size: 11px;
      font-weight: 600;
      fill: #8B949E;
    }}
    .user-tag {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 11px;
      font-weight: 500;
      fill: #8B949E;
    }}
    .metric-title {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 0.5px;
      fill: #8B949E;
    }}
    .metric-value {{
      font-family: "SF Mono", "Fira Code", Consolas, monospace;
      font-size: 24px;
      font-weight: 700;
    }}
    .metric-sub {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 10.5px;
      font-weight: 500;
      fill: #8B949E;
    }}
  </style>

  <!-- Container -->
  <rect x="1" y="1" width="{card_width - 2}" height="{card_height - 2}" class="terminal-bg" filter="url(#subtleGlowStats)" />

  <!-- Terminal Window Bar -->
  <path d="M 1 11 A 10 10 0 0 1 11 1 L {card_width - 11} 1 A 10 10 0 0 1 {card_width - 1} 11 L {card_width - 1} 36 L 1 36 Z" class="terminal-header" />

  <!-- Window Controls -->
  <circle cx="20" cy="18" r="5" class="dot-red" />
  <circle cx="36" cy="18" r="5" class="dot-yellow" />
  <circle cx="52" cy="18" r="5" class="dot-green" />

  <!-- Terminal Title & Verified Tag -->
  <text x="80" y="22" class="title-text">arpit@github:~$ github --stats</text>
  <text x="{card_width - 30}" y="22" class="user-tag" text-anchor="end">Live GitHub Metrics · {followers} Followers</text>

  <!-- Metric Boxes -->
  {boxes_combined}
</svg>
"""
    return svg


def main():
    stats, contribs, langs = load_data()
    print("Generating GitHub stats card SVG...")
    svg_content = build_stats_svg(stats, contribs, langs)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATS_SVG_OUT, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"✓ Saved stats card to {STATS_SVG_OUT}")


if __name__ == "__main__":
    main()

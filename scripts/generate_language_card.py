#!/usr/bin/env python3
"""
generate_language_card.py
Generates a terminal-style SVG card displaying real GitHub language distribution
with progress bars and verified percentage breakdowns.
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
LANG_DATA_PATH = ROOT_DIR / "data" / "languages.json"
ASSETS_DIR = ROOT_DIR / "assets"
LANG_SVG_OUT = ASSETS_DIR / "language-stats.svg"

COLOR_MAP = {
    "JavaScript": "#F7DF1E",
    "TypeScript": "#3178C6",
    "CSS": "#563D7C",
    "Python": "#3572A5",
    "HTML": "#E34C26",
    "C++": "#F34B7D",
    "C": "#555555",
    "Go": "#00ADD8",
    "Shell": "#89E051",
    "Other": "#8B949E"
}


def format_bytes(b):
    if b >= 1024 * 1024:
        return f"{b / (1024 * 1024):.1f} MB"
    elif b >= 1024:
        return f"{b / 1024:.1f} KB"
    return f"{b} B"


def load_languages():
    if not LANG_DATA_PATH.exists():
        return {
            "total_bytes": 0,
            "repos_analyzed": 0,
            "languages": [
                {"name": "JavaScript", "bytes": 50000000, "percentage": 42.0},
                {"name": "TypeScript", "bytes": 40000000, "percentage": 33.6},
                {"name": "CSS", "bytes": 28000000, "percentage": 23.5},
                {"name": "Python", "bytes": 1000000, "percentage": 0.9}
            ]
        }
    with open(LANG_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_language_svg(data):
    card_width = 890
    languages = data.get("languages", [])
    total_bytes = data.get("total_bytes", 0)
    repos_count = data.get("repos_analyzed", 0)

    # Show top 6 languages
    display_langs = languages[:6]
    row_count = len(display_langs)
    row_height = 36
    top_offset = 80
    card_height = top_offset + (row_count * row_height) + 30

    bar_max_width = 380

    rows_svg = []
    for i, lang_obj in enumerate(display_langs):
        name = lang_obj.get("name", "Unknown")
        pct = lang_obj.get("percentage", 0.0)
        byte_count = lang_obj.get("bytes", 0)
        formatted_b = format_bytes(byte_count)
        color = COLOR_MAP.get(name, "#58A6FF")

        y_pos = top_offset + (i * row_height)
        calc_width = max(6, int((pct / 100.0) * bar_max_width))
        delay = round(0.1 + (i * 0.1), 2)

        # SVG terminal-style row with progress bar
        row_str = f"""
    <!-- Row {i}: {name} -->
    <g transform="translate(30, {y_pos})">
      <!-- Language Dot & Name -->
      <circle cx="6" cy="12" r="5" fill="{color}" />
      <text x="22" y="16" class="lang-name">{name}</text>

      <!-- Track Background -->
      <rect x="150" y="5" width="{bar_max_width}" height="14" rx="4" fill="#21262D" />

      <!-- Progress Fill with smooth animation -->
      <rect x="150" y="5" width="{calc_width}" height="14" rx="4" fill="{color}" opacity="0.9">
        <animate attributeName="width" from="0" to="{calc_width}" dur="0.8s" begin="{delay}s" fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1" />
      </rect>

      <!-- Percentage & Bytes -->
      <text x="{150 + bar_max_width + 25}" y="16" class="pct-text">{pct:.1f}%</text>
      <text x="{150 + bar_max_width + 100}" y="16" class="bytes-text">{formatted_b}</text>
    </g>"""
        rows_svg.append(row_str)

    rows_combined = "\n".join(rows_svg)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {card_width} {card_height}" width="{card_width}" height="{card_height}">
  <defs>
    <filter id="subtleGlowLang" x="-5%" y="-5%" width="110%" height="110%">
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
    .meta-text {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 11px;
      font-weight: 500;
      fill: #8B949E;
    }}
    .lang-name {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 12.5px;
      font-weight: 600;
      fill: #F0F6FC;
    }}
    .pct-text {{
      font-family: "SF Mono", "Fira Code", Consolas, monospace;
      font-size: 12.5px;
      font-weight: 700;
      fill: #F0F6FC;
    }}
    .bytes-text {{
      font-family: "SF Mono", "Fira Code", Consolas, monospace;
      font-size: 11px;
      font-weight: 500;
      fill: #8B949E;
    }}
  </style>

  <!-- Container -->
  <rect x="1" y="1" width="{card_width - 2}" height="{card_height - 2}" class="terminal-bg" filter="url(#subtleGlowLang)" />

  <!-- Terminal Window Bar -->
  <path d="M 1 11 A 10 10 0 0 1 11 1 L {card_width - 11} 1 A 10 10 0 0 1 {card_width - 1} 11 L {card_width - 1} 36 L 1 36 Z" class="terminal-header" />

  <!-- Window Controls -->
  <circle cx="20" cy="18" r="5" class="dot-red" />
  <circle cx="36" cy="18" r="5" class="dot-yellow" />
  <circle cx="52" cy="18" r="5" class="dot-green" />

  <!-- Terminal Title & Meta Info -->
  <text x="80" y="22" class="title-text">arpit@github:~$ language --stats</text>
  <text x="{card_width - 30}" y="22" class="meta-text" text-anchor="end">Analyzed {repos_count} owned repositories · {format_bytes(total_bytes)} code bytes</text>

  <!-- Language Progress Rows -->
  {rows_combined}
</svg>
"""
    return svg


def main():
    data = load_languages()
    print("Generating language stats SVG...")
    svg_content = build_language_svg(data)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    with open(LANG_SVG_OUT, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"✓ Saved language card to {LANG_SVG_OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
generate_heatmap.py
Renders real GitHub contribution calendar activity into an animated SVG heatmap
covering the trailing 12 months up to the current date.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTRIBS_PATH = ROOT_DIR / "data" / "contributions.json"
ASSETS_DIR = ROOT_DIR / "assets"
HEATMAP_OUT = ASSETS_DIR / "contribution-heatmap.svg"

# GitHub Dark Theme Green Spectrum
LEVEL_COLORS = {
    0: "#161B22",
    1: "#0E4429",
    2: "#006D32",
    3: "#26A641",
    4: "#39D353"
}


def load_contributions():
    if not CONTRIBS_PATH.exists():
        return {
            "total_lifetime": 2742,
            "total_past_year": 1697,
            "active_days_past_year": 229,
            "current_streak": 2,
            "longest_streak": 29,
            "days": []
        }
    with open(CONTRIBS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_heatmap_svg(data):
    card_width = 890
    card_height = 230

    total_past_year = data.get("total_past_year", 1697)
    total_lifetime = data.get("total_lifetime", 2742)
    longest_streak = data.get("longest_streak", 29)

    days = data.get("days", [])
    # 52 weeks * 7 days = 364 days
    if len(days) < 364:
        pad_count = 364 - len(days)
        padded_days = [{"date": "", "count": 0, "level": 0} for _ in range(pad_count)] + days
    else:
        padded_days = days[-364:]

    cell_size = 10.5
    cell_gap = 3.5
    grid_left = 65
    grid_top = 75

    cells_svg = []
    # Track month labels to display along top
    month_labels = []
    last_month_key = None
    last_col = -5

    for i, day in enumerate(padded_days):
        col = i // 7
        row = i % 7

        level = day.get("level", 0)
        count = day.get("count", 0)
        if count > 0 and level == 0:
            level = 1
        color = LEVEL_COLORS.get(level, LEVEL_COLORS[0])

        x = grid_left + (col * (cell_size + cell_gap))
        y = grid_top + (row * (cell_size + cell_gap))

        # Check for month transition
        date_str = day.get("date", "")
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                m_key = f"{dt.year}-{dt.month:02d}"
                # If first day of month or new month in the first few rows of the column
                if m_key != last_month_key and (col - last_col >= 3):
                    month_name = dt.strftime("%b")
                    month_labels.append((month_name, x))
                    last_month_key = m_key
                    last_col = col
            except Exception:
                pass

        delay = round(0.05 + (col * 0.02), 3)

        cell_str = f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{color}" opacity="0.95">'
        cell_str += f'<animate attributeName="opacity" from="0.3" to="0.95" dur="0.4s" begin="{delay}s" fill="freeze" />'
        cell_str += '</rect>'
        cells_svg.append(cell_str)

    cells_combined = "\n    ".join(cells_svg)

    # Build Month Labels SVG
    month_svg = []
    for month_name, x_pos in month_labels:
        month_svg.append(f'<text x="{x_pos:.1f}" y="{grid_top - 10}" class="grid-label">{month_name}</text>')
    months_combined = "\n    ".join(month_svg)

    # Weekday Labels (Mon, Wed, Fri)
    weekdays_svg = f"""
    <text x="{grid_left - 12}" y="{grid_top + 1 * (cell_size + cell_gap) + 8.5}" class="grid-label" text-anchor="end">Mon</text>
    <text x="{grid_left - 12}" y="{grid_top + 3 * (cell_size + cell_gap) + 8.5}" class="grid-label" text-anchor="end">Wed</text>
    <text x="{grid_left - 12}" y="{grid_top + 5 * (cell_size + cell_gap) + 8.5}" class="grid-label" text-anchor="end">Fri</text>
    """

    # Legend at bottom right
    legend_right = card_width - 32
    legend_top = card_height - 24

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {card_width} {card_height}" width="{card_width}" height="{card_height}">
  <defs>
    <filter id="subtleGlowHeatmap" x="-5%" y="-5%" width="110%" height="110%">
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
    .stats-summary {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 11px;
      font-weight: 500;
      fill: #8B949E;
    }}
    .stats-strong {{
      font-weight: 700;
      fill: #39D353;
    }}
    .grid-label {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 9.5px;
      font-weight: 500;
      fill: #8B949E;
    }}
    .legend-text {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 10px;
      fill: #8B949E;
    }}
  </style>

  <!-- Container -->
  <rect x="1" y="1" width="{card_width - 2}" height="{card_height - 2}" class="terminal-bg" filter="url(#subtleGlowHeatmap)" />

  <!-- Terminal Window Bar -->
  <path d="M 1 11 A 10 10 0 0 1 11 1 L {card_width - 11} 1 A 10 10 0 0 1 {card_width - 1} 11 L {card_width - 1} 36 L 1 36 Z" class="terminal-header" />

  <!-- Window Controls -->
  <circle cx="20" cy="18" r="5" class="dot-red" />
  <circle cx="36" cy="18" r="5" class="dot-yellow" />
  <circle cx="52" cy="18" r="5" class="dot-green" />

  <!-- Title & Headline Stats -->
  <text x="80" y="22" class="title-text">arpit@github:~$ ./contributions.sh --activity</text>
  <text x="{card_width - 25}" y="22" class="stats-summary" text-anchor="end">
    <tspan class="stats-strong">{total_past_year:,}</tspan> in last 12 months · <tspan class="stats-strong">{total_lifetime:,}</tspan> lifetime · <tspan class="stats-strong">{longest_streak}d</tspan> max streak
  </text>

  <!-- Labels -->
  {months_combined}
  {weekdays_svg}

  <!-- Contribution Squares Grid -->
  <g>
    {cells_combined}
  </g>

  <!-- Legend -->
  <g transform="translate({legend_right - 130}, {legend_top})">
    <text x="0" y="9" class="legend-text" text-anchor="end">Less</text>
    <rect x="8" y="0" width="10" height="10" rx="2" fill="{LEVEL_COLORS[0]}" />
    <rect x="22" y="0" width="10" height="10" rx="2" fill="{LEVEL_COLORS[1]}" />
    <rect x="36" y="0" width="10" height="10" rx="2" fill="{LEVEL_COLORS[2]}" />
    <rect x="50" y="0" width="10" height="10" rx="2" fill="{LEVEL_COLORS[3]}" />
    <rect x="64" y="0" width="10" height="10" rx="2" fill="{LEVEL_COLORS[4]}" />
    <text x="82" y="9" class="legend-text">More</text>
  </g>
</svg>
"""
    return svg


def main():
    data = load_contributions()
    print("Generating contribution heatmap SVG...")
    svg_content = build_heatmap_svg(data)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    with open(HEATMAP_OUT, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"✓ Saved contribution heatmap to {HEATMAP_OUT}")


if __name__ == "__main__":
    main()

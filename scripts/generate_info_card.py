#!/usr/bin/env python3
"""
generate_info_card.py
Generates a terminal-style Neofetch / whoami information card SVG.
Reads from config/profile.json and data/github-stats.json.
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
CONFIG_PATH = ROOT_DIR / "config" / "profile.json"
STATS_PATH = ROOT_DIR / "data" / "github-stats.json"
ASSETS_DIR = ROOT_DIR / "assets"
INFO_CARD_OUT = ASSETS_DIR / "info-card.svg"


def load_data():
    config = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

    stats = {}
    if STATS_PATH.exists():
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            stats = json.load(f)

    return config, stats


def xml_escape(text):
    if not isinstance(text, str):
        text = str(text)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_info_card_svg(config, stats):
    card_width = 440
    card_height = 400

    identity = config.get("identity", {})
    skills = config.get("skills", {})
    status = config.get("status", {})

    username = xml_escape(identity.get("username", "Arpit10110"))
    role = xml_escape(identity.get("role", "Full Stack Web Developer"))
    location = xml_escape(identity.get("location", "India 🇮🇳"))
    repos_count = stats.get("public_repos", 124)

    frontend_str = xml_escape("React.js · Next.js · TypeScript · Tailwind")
    backend_str = xml_escape("Node.js · Express.js · NestJS · Python")
    db_str = xml_escape("PostgreSQL · MongoDB · MySQL · Firebase")
    ai_str = xml_escape("Generative AI · Gemini API · System Design")
    metrics_str = xml_escape(f"60+ Projects · {repos_count} Repos · 1000+ GFG DSA")
    building_str = xml_escape("Wapix (WhatsApp Platform & Automation) 🚀")
    learning_str = xml_escape("FastAPI · AI Agents · Microservices")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {card_width} {card_height}" width="{card_width}" height="{card_height}">
  <defs>
    <linearGradient id="infoGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#58A6FF" stop-opacity="0.9" />
      <stop offset="100%" stop-color="#A371F7" stop-opacity="0.9" />
    </linearGradient>
    <filter id="subtleGlowInfo" x="-10%" y="-10%" width="120%" height="120%">
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
    .user-header {{
      font-family: "SF Mono", "Fira Code", Consolas, monospace;
      font-size: 14px;
      font-weight: 700;
      fill: #58A6FF;
    }}
    .divider {{
      stroke: #30363D;
      stroke-width: 1;
      stroke-dasharray: 4, 3;
    }}
    .label {{
      font-family: "SF Mono", "Fira Code", Consolas, monospace;
      font-size: 11px;
      font-weight: 600;
      fill: #8B949E;
    }}
    .value {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 11px;
      font-weight: 500;
      fill: #F0F6FC;
    }}
    .highlight {{
      font-weight: 600;
      fill: #7EE787;
    }}
    .accent-val {{
      font-weight: 600;
      fill: #A371F7;
    }}
    .cyan-val {{
      font-weight: 600;
      fill: #79C0FF;
    }}
    .cursor {{
      animation: blink 1s step-start infinite;
      fill: #58A6FF;
    }}
    @keyframes blink {{
      50% {{ opacity: 0; }}
    }}
    .palette-rect {{
      rx: 2px;
    }}
  </style>

  <!-- Container -->
  <rect x="1" y="1" width="{card_width - 2}" height="{card_height - 2}" class="terminal-bg" filter="url(#subtleGlowInfo)" />

  <!-- Terminal Window Bar -->
  <path d="M 1 11 A 10 10 0 0 1 11 1 L {card_width - 11} 1 A 10 10 0 0 1 {card_width - 1} 11 L {card_width - 1} 36 L 1 36 Z" class="terminal-header" />

  <!-- Window Controls -->
  <circle cx="20" cy="18" r="5" class="dot-red" />
  <circle cx="36" cy="18" r="5" class="dot-yellow" />
  <circle cx="52" cy="18" r="5" class="dot-green" />

  <!-- Terminal Title -->
  <text x="80" y="22" class="title-text">arpit@github:~$ whoami --verbose</text>

  <!-- User Identifier & Divider -->
  <text x="24" y="60" class="user-header">arpit@{username.lower()}</text>
  <line x1="24" y1="70" x2="{card_width - 24}" y2="70" class="divider" />

  <!-- Key-Value System Info -->
  <g transform="translate(24, 90)">
    <!-- Row 1: OS & Role -->
    <text x="0" y="0" class="label">OS</text>
    <text x="85" y="0" class="value">GitHub WebOS · Arch Linux</text>

    <!-- Row 2: Role -->
    <text x="0" y="22" class="label">ROLE</text>
    <text x="85" y="22" class="value cyan-val">{role}</text>

    <!-- Row 3: Location -->
    <text x="0" y="44" class="label">LOCATION</text>
    <text x="85" y="44" class="value">{location}</text>

    <!-- Row 4: Frontend -->
    <text x="0" y="66" class="label">FRONTEND</text>
    <text x="85" y="66" class="value">{frontend_str}</text>

    <!-- Row 5: Backend -->
    <text x="0" y="88" class="label">BACKEND</text>
    <text x="85" y="88" class="value">{backend_str}</text>

    <!-- Row 6: Databases -->
    <text x="0" y="110" class="label">DATABASE</text>
    <text x="85" y="110" class="value">{db_str}</text>

    <!-- Row 7: AI & Cloud -->
    <text x="0" y="132" class="label">AI &amp; CORE</text>
    <text x="85" y="132" class="value accent-val">{ai_str}</text>

    <!-- Row 8: Metrics -->
    <text x="0" y="154" class="label">PROJECTS</text>
    <text x="85" y="154" class="value">{metrics_str}</text>

    <!-- Row 9: Status -->
    <text x="0" y="176" class="label">STATUS</text>
    <text x="85" y="176" class="value highlight">{building_str}</text>

    <!-- Row 10: Learning -->
    <text x="0" y="198" class="label">LEARNING</text>
    <text x="85" y="198" class="value">{learning_str}</text>
  </g>

  <!-- Terminal Color Palette Blocks -->
  <g transform="translate(24, 320)">
    <rect x="0" y="0" width="22" height="11" fill="#0D1117" stroke="#30363D" class="palette-rect" />
    <rect x="26" y="0" width="22" height="11" fill="#FF5F56" class="palette-rect" />
    <rect x="52" y="0" width="22" height="11" fill="#FFBD2E" class="palette-rect" />
    <rect x="78" y="0" width="22" height="11" fill="#27C93F" class="palette-rect" />
    <rect x="104" y="0" width="22" height="11" fill="#58A6FF" class="palette-rect" />
    <rect x="130" y="0" width="22" height="11" fill="#A371F7" class="palette-rect" />
    <rect x="156" y="0" width="22" height="11" fill="#39D353" class="palette-rect" />
    <rect x="182" y="0" width="22" height="11" fill="#F0F6FC" class="palette-rect" />
  </g>

  <!-- Prompt line with blinking cursor -->
  <g transform="translate(24, 360)">
    <text x="0" y="0" class="label" fill="#8B949E">arpit@github:~$ </text>
    <rect x="110" y="-10" width="7" height="13" class="cursor" />
  </g>
</svg>
"""
    return svg


def main():
    config, stats = load_data()
    print("Generating info card SVG...")
    svg_content = build_info_card_svg(config, stats)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    with open(INFO_CARD_OUT, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"✓ Saved info card to {INFO_CARD_OUT}")


if __name__ == "__main__":
    main()

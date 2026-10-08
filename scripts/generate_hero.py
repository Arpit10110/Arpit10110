#!/usr/bin/env python3
"""
generate_hero.py
Generates the animated terminal-style Hero SVG banner for the top of the GitHub profile.
Uses bulletproof SVG positioning compatible with GitHub Markdown Camo image proxy.
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
ASSETS_DIR = ROOT_DIR / "assets"
HERO_SVG_OUT = ASSETS_DIR / "hero.svg"


def load_config():
    if not CONFIG_PATH.exists():
        return {
            "identity": {
                "name": "Arpit Agrahari",
                "role": "Full Stack Web Developer"
            }
        }
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_hero_svg(config):
    card_width = 890
    card_height = 260

    identity = config.get("identity", {})
    name = identity.get("name", "Arpit Agrahari").upper()
    role = identity.get("role", "Full Stack Web Developer").upper()

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {card_width} {card_height}" width="{card_width}" height="{card_height}">
  <defs>
    <linearGradient id="heroTitleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#58A6FF" />
      <stop offset="50%" stop-color="#79C0FF" />
      <stop offset="100%" stop-color="#A371F7" />
    </linearGradient>
    <linearGradient id="pillGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1F242C" />
      <stop offset="100%" stop-color="#161B22" />
    </linearGradient>
    <filter id="heroGlow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="3" stdDeviation="6" flood-color="#000000" flood-opacity="0.6"/>
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
    .prompt {{
      font-family: "SF Mono", "Fira Code", Consolas, monospace;
      font-size: 13px;
      fill: #8B949E;
    }}
    .prompt-cmd {{
      fill: #7EE787;
      font-weight: 600;
    }}
    .hero-name {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Montserrat", "Arial Black", sans-serif;
      font-size: 30px;
      font-weight: 900;
      letter-spacing: 2px;
      fill: url(#heroTitleGrad);
    }}
    .hero-role {{
      font-family: "SF Mono", "Fira Code", Consolas, monospace;
      font-size: 13px;
      font-weight: 600;
      fill: #58A6FF;
      letter-spacing: 0.8px;
    }}
    .hero-desc {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 12.5px;
      font-weight: 400;
      fill: #C9D1D9;
    }}
    .tech-pill {{
      font-family: "SF Mono", "Fira Code", Consolas, monospace;
      font-size: 11.5px;
      font-weight: 500;
      fill: #8B949E;
    }}
    .tech-highlight {{
      fill: #79C0FF;
      font-weight: 600;
    }}
    .tech-purple {{
      fill: #D2A8FF;
      font-weight: 600;
    }}
    .cursor {{
      animation: blink 1s step-start infinite;
      fill: #58A6FF;
    }}
    @keyframes blink {{
      50% {{ opacity: 0; }}
    }}
  </style>

  <!-- Container -->
  <rect x="1" y="1" width="{card_width - 2}" height="{card_height - 2}" class="terminal-bg" filter="url(#heroGlow)" />

  <!-- Terminal Window Bar -->
  <path d="M 1 11 A 10 10 0 0 1 11 1 L {card_width - 11} 1 A 10 10 0 0 1 {card_width - 1} 11 L {card_width - 1} 36 L 1 36 Z" class="terminal-header" />

  <!-- Window Controls -->
  <circle cx="20" cy="18" r="5" class="dot-red" />
  <circle cx="36" cy="18" r="5" class="dot-yellow" />
  <circle cx="52" cy="18" r="5" class="dot-green" />

  <!-- Window Title -->
  <text x="80" y="22" class="title-text">arpit@github:~$ ./welcome.sh --interactive</text>

  <!-- Terminal Command Prompt Line 1 -->
  <text x="32" y="65" class="prompt">arpit@github:~$ <tspan class="prompt-cmd">./welcome.sh</tspan></text>

  <!-- Hero Name -->
  <text x="32" y="106" class="hero-name">{name}</text>

  <!-- Role Badge -->
  <text x="32" y="136" class="hero-role">⚡ {role}</text>

  <!-- Description / Subtitle -->
  <text x="32" y="162" class="hero-desc">Building full-stack web products, robust backend architectures &amp; Generative AI tools.</text>

  <!-- Tech Stack Highlights -->
  <text x="32" y="196" class="tech-pill">
    <tspan class="tech-highlight">React.js</tspan> · 
    <tspan class="tech-highlight">Next.js</tspan> · 
    <tspan class="tech-highlight">TypeScript</tspan> · 
    <tspan class="tech-highlight">Node.js</tspan> · 
    <tspan class="tech-purple">NestJS</tspan> · 
    <tspan class="tech-purple">PostgreSQL</tspan> · 
    <tspan class="tech-highlight">Generative AI</tspan>
  </text>

  <!-- Active Terminal Prompt with Blinking Cursor -->
  <text x="32" y="232" class="prompt">arpit@github:~$ </text>
  <rect x="148" y="220" width="8.5" height="15" class="cursor" />
</svg>
"""
    return svg


def main():
    config = load_config()
    print("Generating Hero banner SVG...")
    svg_content = build_hero_svg(config)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    with open(HERO_SVG_OUT, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"✓ Saved hero banner to {HERO_SVG_OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
generate_ascii.py
Converts user profile photo into a sleek, terminal-styled animated ASCII SVG.
If profile.jpg is missing, downloads GitHub avatar as default, with documentation.
"""

import json
import os
import sys
from pathlib import Path
import requests
from PIL import Image, ImageEnhance

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "profile.json"
ASSETS_DIR = ROOT_DIR / "assets"
PROFILE_IMG = ASSETS_DIR / "profile.jpg"
ASCII_SVG_OUT = ASSETS_DIR / "ascii-profile.svg"
ASSETS_README = ASSETS_DIR / "README.md"

RAMP = " .:-=+*#%@"


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_profile_image(config):
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # Document how user can swap photo
    if not ASSETS_README.exists():
        readme_content = """# Profile Assets

Place your custom profile photograph here:
```text
assets/profile.jpg
```
When `python scripts/generate_profile.py` runs, it will process `profile.jpg` into `assets/ascii-profile.svg`.

If `profile.jpg` is not present, the system automatically uses your public GitHub avatar.
"""
        with open(ASSETS_README, "w", encoding="utf-8") as f:
            f.write(readme_content)

    if not PROFILE_IMG.exists():
        avatar_url = config.get("identity", {}).get("avatar_url", "")
        if avatar_url:
            print(f"Downloading avatar from {avatar_url} to {PROFILE_IMG}...")
            try:
                r = requests.get(avatar_url, timeout=15)
                if r.ok and len(r.content) > 1000:
                    with open(PROFILE_IMG, "wb") as f:
                        f.write(r.content)
                    print("✓ Saved avatar image to assets/profile.jpg")
                    return True
            except Exception as e:
                print(f"Warning: Failed to download avatar: {e}")
        return False
    return True


def image_to_ascii(image_path, target_width=52):
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Failed to open image {image_path}: {e}")
        return None

    # Convert to grayscale
    img = img.convert("L")

    # Enhance contrast for sharp ASCII art
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.4)

    # Calculate target height (terminal fonts are ~2x taller than wide)
    aspect_ratio = img.height / img.width
    target_height = int(target_width * aspect_ratio * 0.48)
    target_height = max(18, min(target_height, 28))

    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    if hasattr(img, "get_flattened_data"):
        pixels = list(img.get_flattened_data())
    else:
        pixels = list(img.getdata())
    ramp_len = len(RAMP)

    lines = []
    for row in range(target_height):
        line_chars = []
        for col in range(target_width):
            pixel = pixels[row * target_width + col]
            # Map 0-255 to ramp index
            char_idx = int((pixel / 255) * (ramp_len - 1))
            line_chars.append(RAMP[char_idx])
        lines.append("".join(line_chars))

    return lines


def generate_fallback_lines():
    return [
        "              .---.              ",
        "             /     \\             ",
        "            | () () |            ",
        "             \\  _  /             ",
        "              `---'              ",
        "           .---'-'---.           ",
        "          /           \\          ",
        "         |  FULL STACK |         ",
        "         |  DEVELOPER  |         ",
        "         |  [ARPIT]    |         ",
        "          \\           /          ",
        "           `---------'           "
    ]


def build_ascii_svg(lines, username="Arpit10110"):
    # SVG Dimensions
    card_width = 440
    card_height = 400
    line_count = len(lines)
    line_height = 11.5
    top_offset = 56

    # Escape XML characters in ascii lines
    escaped_lines = []
    for line in lines:
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        escaped_lines.append(escaped)

    # Generate animated row elements with progressive fade-in
    text_elements = []
    total_anim_duration = 1.2
    step_duration = total_anim_duration / max(1, line_count)

    for i, line in enumerate(escaped_lines):
        y_pos = top_offset + (i * line_height)
        delay = round(i * step_duration, 3)
        text_elements.append(
            f'<tspan x="20" y="{y_pos}" class="row" style="animation-delay: {delay}s;">{line}</tspan>'
        )

    tspan_content = "\n        ".join(text_elements)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {card_width} {card_height}" width="{card_width}" height="{card_height}">
  <defs>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#58A6FF" stop-opacity="0.9" />
      <stop offset="100%" stop-color="#A371F7" stop-opacity="0.9" />
    </linearGradient>
    <linearGradient id="textGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#58A6FF" />
      <stop offset="60%" stop-color="#79C0FF" />
      <stop offset="100%" stop-color="#A371F7" />
    </linearGradient>
    <filter id="subtleGlow" x="-10%" y="-10%" width="120%" height="120%">
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
    .ascii-font {{
      font-family: "SF Mono", "Fira Code", Consolas, "Courier New", monospace;
      font-size: 9.5px;
      fill: url(#textGrad);
      letter-spacing: 0.5px;
      white-space: pre;
    }}
    .row {{
      opacity: 0;
      animation: revealRow 0.4s ease-out forwards;
    }}
    @keyframes revealRow {{
      0% {{
        opacity: 0;
        transform: translateY(3px);
      }}
      100% {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}
  </style>

  <!-- Container -->
  <rect x="1" y="1" width="{card_width - 2}" height="{card_height - 2}" class="terminal-bg" filter="url(#subtleGlow)" />

  <!-- Terminal Window Bar -->
  <path d="M 1 11 A 10 10 0 0 1 11 1 L {card_width - 11} 1 A 10 10 0 0 1 {card_width - 1} 11 L {card_width - 1} 36 L 1 36 Z" class="terminal-header" />

  <!-- Window Controls -->
  <circle cx="20" cy="18" r="5" class="dot-red" />
  <circle cx="36" cy="18" r="5" class="dot-yellow" />
  <circle cx="52" cy="18" r="5" class="dot-green" />

  <!-- Terminal Title -->
  <text x="80" y="22" class="title-text">arpit@github:~$ cat ./portrait.ascii</text>

  <!-- ASCII Content -->
  <text class="ascii-font" xml:space="preserve">
    {tspan_content}
  </text>
</svg>
"""
    return svg


def main():
    config = load_config()
    username = config.get("identity", {}).get("username", "Arpit10110")
    print("Generating ASCII portrait SVG...")

    has_img = ensure_profile_image(config)
    lines = None
    if has_img and PROFILE_IMG.exists():
        lines = image_to_ascii(PROFILE_IMG, target_width=52)

    if not lines:
        print("Using fallback ASCII template...")
        lines = generate_fallback_lines()

    svg_content = build_ascii_svg(lines, username=username)

    with open(ASCII_SVG_OUT, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"✓ Saved ASCII portrait to {ASCII_SVG_OUT}")


if __name__ == "__main__":
    main()

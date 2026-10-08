#!/usr/bin/env python3
"""
generate_profile.py
Master orchestrator script that executes all data fetchers and SVG asset generators
to produce an updated, animated GitHub profile.
"""

import subprocess
import sys
from pathlib import Path

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPTS_DIR = Path(__file__).resolve().parent
PYTHON_EXE = sys.executable


def run_step(step_name, script_name):
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"Error: {script_name} not found.")
        return False

    res = subprocess.run([PYTHON_EXE, str(script_path)], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"✗ Failed {step_name} ({script_name}):")
        print(res.stderr or res.stdout)
        return False
    else:
        print(f"✓ {step_name}")
        return True


def main():
    print("=" * 55)
    print("  🚀 ARPIT10110 GITHUB PROFILE GENERATOR")
    print("=" * 55)
    print()

    print("Fetching GitHub data...")
    ok1 = run_step("Repository & Language statistics", "fetch_github_stats.py")
    ok2 = run_step("Contribution activity & Streaks", "fetch_contributions.py")

    print()
    print("Generating assets...")
    ok3 = run_step("Hero banner", "generate_hero.py")
    ok4 = run_step("ASCII profile portrait", "generate_ascii.py")
    ok5 = run_step("Neofetch info card", "generate_info_card.py")
    ok6 = run_step("Language distribution card", "generate_language_card.py")
    ok7 = run_step("Contribution heatmap", "generate_heatmap.py")
    ok8 = run_step("GitHub statistics card", "generate_stats.py")

    print()
    if all([ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8]):
        print("✓ All profile assets updated successfully!")
    else:
        print("⚠ Profile generated with some warnings (cached/fallback assets preserved).")
    print("=" * 55)


if __name__ == "__main__":
    main()

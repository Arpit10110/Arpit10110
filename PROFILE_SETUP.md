# ⚡ Profile Setup & Maintenance Guide

Welcome to your automated, animated terminal GitHub profile system for **[@Arpit10110](https://github.com/Arpit10110)**!

This repository features a custom-built automation engine that calculates real language weights across your GitHub repositories, tracks genuine GitHub contribution streaks, and renders high-definition dark-terminal animated SVG cards.

---

## 🛠️ How It Works

1. **Real GitHub Language Aggregator (`scripts/fetch_github_stats.py`)**:
   - Queries the GitHub REST API across your public, non-fork repositories.
   - Sums byte counts per language (`sum(language_bytes) / sum(total_bytes) * 100`).
   - Normalizes and outputs exact percentages to `data/languages.json`.
   - Caches repository responses in `data/repo_languages_cache.json` to prevent API rate limits.

2. **Real Contribution Graph & Streaks (`scripts/fetch_contributions.py`)**:
   - Fetches authentic contribution activity across the past 52 weeks.
   - Calculates total contributions, active days, current streak, and longest streak.
   - Saves metrics to `data/contributions.json`.

3. **Terminal SVG Generators (`scripts/generate_*.py`)**:
   - `hero.svg`: Terminal window banner with glowing typography and typewriter prompt.
   - `ascii-profile.svg`: Progressive row-fade ASCII portrait generated from your photo.
   - `info-card.svg`: Neofetch-style system specifications card with live metrics.
   - `language-stats.svg`: Terminal progress bars reflecting actual repository byte weights.
   - `contribution-heatmap.svg`: Interactive-style contribution calendar with custom dark-green palette.
   - `github-stats.svg`: Terminal statistics dashboard (repositories, followers, stars, streaks).

4. **GitHub Actions Automation (`.github/workflows/update-profile.yml`)**:
   - Runs daily via GitHub Actions cron and supports manual trigger (`workflow_dispatch`).
   - Automatically re-computes stats and pushes updated SVGs whenever your repositories or commit streaks update.

---

## 💻 Local Development

### 1. Requirements
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Generate Everything with One Command
```bash
python scripts/generate_profile.py
```
Expected output:
```text
=======================================================
  🚀 ARPIT10110 GITHUB PROFILE GENERATOR
=======================================================

Fetching GitHub data...
✓ Repository & Language statistics
✓ Contribution activity & Streaks

Generating assets...
✓ Hero banner
✓ ASCII profile portrait
✓ Neofetch info card
✓ Language distribution card
✓ Contribution heatmap
✓ GitHub statistics card

✓ All profile assets updated successfully!
=======================================================
```

---

## 🖼️ How to Change Your Profile Photo

1. Place your desired photo at:
   ```text
   assets/profile.jpg
   ```
2. Run the orchestrator:
   ```bash
   python scripts/generate_profile.py
   ```
3. Commit and push the updated `assets/ascii-profile.svg`.

*(If `assets/profile.jpg` is deleted or not provided, the script automatically downloads your latest public GitHub avatar as the source!)*

---

## ⚙️ Customizing Profile Data

All personal links, skills, roles, and featured projects are centralized in:
```text
config/profile.json
```

You can update:
- Headline & Role
- Featured projects (URL, description, technologies)
- Social links & portfolio
- Currently building & currently learning items
- Theme color hex values

After editing `config/profile.json`, simply run:
```bash
python scripts/generate_profile.py
```

---

## 🤖 Running on GitHub Actions

### Automatic Daily Run
The workflow `.github/workflows/update-profile.yml` runs automatically every morning at 06:17 UTC.

### Manual Run (On Demand)
1. Go to your repository on GitHub: `https://github.com/Arpit10110/Arpit10110`
2. Click the **Actions** tab.
3. Select **Update GitHub Profile Stats** from the left sidebar.
4. Click **Run workflow** -> Select `main` branch -> Click **Run workflow**.

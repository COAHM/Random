# LeetCode Daily Runner

Automated runner that solves 2–3 random unsolved LeetCode problems daily across different categories using Google Gemini (`gemini-2.5-flash`) in Dart 3, and commits them at randomized intervals to the target repository configured in `.env`.

## Setup

1. **Local `.env` (untracked):**
   Copy `.env.example` to `.env` and fill in your values (`GEMINI_API_KEY`, `PAT_TOKEN`, `TARGET_REPO`, `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `TARGET_BRANCH`).
   - Run locally anytime with `python solve_leetcode.py` (or `SKIP_DELAY=true python solve_leetcode.py` to test without waiting).

2. **GitHub Actions Secrets (`Settings -> Secrets and variables -> Actions`):**
   - Paste your entire `.env` file contents into a single secret named `ENV_FILE` (or add the individual keys from `.env` as repository secrets).

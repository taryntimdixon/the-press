# The Press quality upgrade

This bundle updates the active daily newsroom workflow so articles are longer, broader-sourced, fact-checked, and balanced across all public desks.

## Replace these files

1. Copy `studio/automation/preserve_old_and_new_issue_v34567.py` into your repo at:

   `studio/automation/preserve_old_and_new_issue_v34567.py`

2. Copy `.github/workflows/daily-ai-newsroom.yml` into your repo at:

   `.github/workflows/daily-ai-newsroom.yml`

3. Commit and push.

## Or apply the patch

From the repo root:

```bash
git apply the_press_quality_upgrade.patch
git add studio/automation/preserve_old_and_new_issue_v34567.py .github/workflows/daily-ai-newsroom.yml
git commit -m "Upgrade newsroom sourcing and desk balance"
git push
```

## What changed

- Expands the active desk list to: Politics, Culture, Technology, Economics, Education, Health, Philosophy, Science, World, Opinion, AI, Geopolitics, Film, Pop Culture, and Niche.
- Rotates section selection so smaller runs still spread attention across desks over time.
- Defaults the workflow to 15 stories so every public desk can receive one story per run.
- Raises article target to 2,500+ words.
- Requires 30–50 distinct HTTPS source URLs per article.
- Adds source-diversity gates, fact-check passes, and repair attempts.
- Updates section pages with the latest generated story for that desk.
- Keeps strict quality gates on by default so under-sourced or under-length stories fail instead of publishing.

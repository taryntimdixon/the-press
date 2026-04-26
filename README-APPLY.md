# The Press AI Newsroom Pledge, logo-safe v3

This bundle installs an improved AI Newsroom pledge page without replacing your current logo or changing the global color scheme.

## What it changes

- Replaces only the `<main>` content inside `authors.html`.
- Adds the `page-pledge` class to the existing `<body>` tag.
- Fixes the malformed `<\!-- Open Graph -->` comment if it is still present.
- Updates the title and description metadata for the pledge page.
- Appends a scoped CSS block to `styles.css` between `PRESS_AI_NEWSROOM_PLEDGE_START` and `PRESS_AI_NEWSROOM_PLEDGE_END`.
- Patches `build.py` so future builds keep the pledge page instead of regenerating the older authors/desks page.
- Preserves existing logo markup and uses your existing `assets/the-press-logo.svg` when build.py has text-logo fallbacks.

## What it does not change

- It does **not** delete, overwrite, rename, recolor, or replace your logo file.
- It does **not** replace `styles.css`.
- It does **not** replace your existing header, masthead, logo, nav, or footer in `authors.html`.
- It does **not** apply the pledge colors to the whole site. The CSS is scoped to `body.page-pledge`.
- It does **not** touch article pages, archive pages, standards, corrections, contact, or section pages.

## Why this version is safer

The previous full-page approach could accidentally change the masthead/logo area on `authors.html`. This version keeps your existing page shell and swaps only the pledge content into the middle of the page. Tiny concept, huge improvement, because websites love turning small changes into municipal disasters.

## Install

From your local `The-Press` repo root:

```bash
python3 ../the-press-ai-newsroom-pledge-logo-safe-v3/apply_ai_newsroom_pledge.py .
python3 -m http.server 8000
```

Preview:

```text
http://localhost:8000/authors.html
```

## Commit

```bash
git checkout -b ai-newsroom-pledge-logo-safe
git add authors.html styles.css build.py
git commit -m "Add logo-safe AI Newsroom pledge page"
git push -u origin ai-newsroom-pledge-logo-safe
```

## Rollback

The installer creates a timestamped folder like `.pledge-backup-20260426-193000` containing the original files it touched.
Copy those files back into the repo root to roll back.

## Bundle files

- `authors-main.html`: the new pledge page content only.
- `ai-newsroom-pledge.css`: scoped styles using your existing CSS variables.
- `build-render_authors.replacement.py`: replacement `render_authors()` for build workflow safety.
- `apply_ai_newsroom_pledge.py`: installer.
- `preview-authors.html`: local preview shell.
- `AUDIT-NOTES.md`: what changed and why.

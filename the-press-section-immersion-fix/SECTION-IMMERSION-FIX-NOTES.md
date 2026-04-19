# Section immersion fix

This pass fixes two category-page issues:

1. The visible `Open Graph` text at the very top of section pages.
2. The flash where the original 1–2 static section cards appear before the full live section archive hydrates.

## What changed

- All `section-*.html` files now use a real HTML comment:
  `<!-- Open Graph -->`
  instead of the escaped text that browsers can render visibly.
- `app.js` now targets the real non-daily section archive grid instead of accidentally grabbing the daily cards grid.
- `app.js` marks the section archive as ready only after hydration finishes, with a short fallback so the page does not stay hidden if live data fails.
- `styles.css` hides the old static archive cards behind a subtle paper-like skeleton until the full archive is ready.
- `tools/fix_category_immersion.py` can be run after future generation passes to keep section Open Graph comments clean.

## Apply

```bash
git apply the-press-section-immersion-fix.patch
python3 tools/fix_category_immersion.py
```

Then preview locally:

```bash
python3 -m http.server 8080
```

Open a section page like `section-economics.html` and hard-refresh.

# Categoryless UI pass for The Press

This pass removes the category/section navigation surfaces so the site reads as a clean article-first newspaper with Archive as the browsing hub.

## What changed

- Removed the top category bar (`section-nav`) and the mobile `Menu` button that existed only to reveal it.
- Removed the homepage desk/category directory.
- Removed the footer `Sections` column while keeping `Archive`, `AI Newsroom`/`Authors`, `Standards`, `Corrections`, and `Contact`.
- Repointed old `section-*.html` anchor links to `archive.html`.
- Fixed the malformed escaped Open Graph marker that was appearing as visible text on section pages.
- Added CSS and JS fallbacks so generated or stale pages cannot bring the category bar back visually.
- Updated `build.py` so future generated pages keep the archive-only browsing model.

## Apply

```bash
git apply the-press-categoryless-ui.patch
python3 tools/remove_category_navigation.py
```

Then preview locally:

```bash
python3 -m http.server 8080
```

## Notes

The archive page and archive filters are intentionally kept. Category pages can still exist as old files in the repository, but the live navigation no longer points readers there.

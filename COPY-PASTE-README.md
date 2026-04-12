# The Press fix pack

Replace these files in your repo:

- `styles.css`
- `app.js`
- `search-index.json`
- `studio/automation/preserve_old_and_new_issue_v34567.py`

Open `preview-homepage-fixes.html` in your browser to preview the homepage cleanup.

What changed:

1. Slower breaking strip
   - ticker now uses a longer duration
   - pause works when the user hovers anywhere over the strip

2. Smaller, cleaner "Today’s 10" cards
   - real grid for `.cards-grid--daily`
   - tighter padding
   - 16:9 image crop
   - title/dek clamp
   - equal-height cards
   - fewer awkward gaps and overflow issues

3. Better fallback image logic
   - tries concrete Wikipedia page thumbnails first
   - tries Wikimedia Commons second
   - rejects archive scans, document pages, logos, icons, and generic placeholders
   - stores image metadata in `search-index.json` and `daily-latest.json`

4. Search index patch
   - current daily stories now have `image` and `imageAlt` fields so section/archive rendering is more stable

Notes:

- The preview file is mostly for layout and ticker speed.
- The smarter topical image fallback applies on the next daily automation run.

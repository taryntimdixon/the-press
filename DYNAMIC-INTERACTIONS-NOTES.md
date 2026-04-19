# The Press — Dynamic Interactions UI Pass

This package adds a progressive interaction layer to the static newsroom UI without changing article content or the publishing workflow.

## Files changed

- `styles.css`
- `app.js`

Both changes are append-only and wrapped with these markers:

- `PRESS_DYNAMIC_INTERACTIONS_START`
- `PRESS_DYNAMIC_INTERACTIONS_END`

## What was added

- Subtle hover-lift and pointer-aware tilt on article cards, river items, lead panels, desk cards, and related list items.
- Soft radial “ink wash” on hover using the existing accent color system.
- Reveal-on-scroll animation for cards and content blocks.
- Smooth same-site page-exit transition for internal links and clickable cards.
- Tactile click ripple on buttons, cards, CTAs, lead buttons, and theme/reader controls.
- Floating “Top” button that appears after scrolling.
- Smoother search modal and mobile menu entrance.
- Gentle paragraph focus highlight in article bodies.
- Full `prefers-reduced-motion` support.

## Install options

### Option A — Replace files

Copy the included `styles.css` and `app.js` into the repository root, replacing the existing files.

### Option B — Apply patch

From the repository root:

```bash
git apply the-press-dynamic-interactions.patch
```

Then preview locally and commit:

```bash
python3 -m http.server 8080
# open http://localhost:8080

git add styles.css app.js
git commit -m "Enhance UI with dynamic interactions"
```

## Validation performed

- `node --check app.js` passes.
- Changes are progressive enhancement only; the site still works if JavaScript animations are unavailable.

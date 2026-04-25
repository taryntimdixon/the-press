# The Press Brand Update

Brand direction locked:

**THE PRESS**  
**AI Powered News**

This package keeps the existing editorial feel of the site and adds the AI identity as a clean masthead tagline instead of a gimmicky icon.

## What is included

- `apply_press_brand.py` — one script to apply the update inside your repo.
- `brand-css.css` — CSS snippet if you want to paste manually instead.
- `assets/the-press-logo.svg` — full light/background logo asset.
- `assets/the-press-logo-reverse.svg` — full dark-background logo asset.
- `assets/the-press-mark.svg` — compact TP mark for favicon/mobile/social later.
- `assets/favicon.svg` — favicon-ready TP mark.
- `preview/brand-preview.html` — local visual preview.

## How to use it

1. Unzip this package.
2. Copy everything into the root of your `The-Press` repo.
3. Run:

```bash
python apply_press_brand.py
```

4. Open `index.html` locally and check the masthead.
5. Commit and push:

```bash
git add .
git commit -m "Add The Press AI Powered News brand lockup"
git push
```

## Why this works with your site

Your current site already has a strong newspaper-style masthead using serif display type, warm paper colors, a red accent, and a sticky header. This update uses those same variables and just makes the brand lockup sharper:

- `The Press` becomes more logo-like through uppercase spacing and heavier display weight.
- `AI Powered News` becomes a small editorial badge beside/under the masthead.
- The header stays text-based, fast, responsive, and accessible.
- SVG assets are included for later use, but the live header does not depend on an image file.

## Optional future steps

Once the website feels locked, use the included `the-press-mark.svg` to create social profile images for X/Twitter, Instagram, Facebook, and the browser/mobile icon set.

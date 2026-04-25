# Manual paste snippets

Use these only if you do not want to run `apply_press_brand.py`.

## 1. Change the tagline wherever it appears

Replace:

```txt
A digital newspaper built for sourced long-form reporting.
```

with:

```txt
AI Powered News
```

Best places to check:

- `master-edition.json`
- `index.html`
- `archive.html`
- `authors.html`
- every `section-*.html`
- story pages
- footer areas

## 2. Add this to the end of `styles.css`

```css
/* paste content from brand-css.css here */
```

## 3. Copy SVG assets

Copy these into `assets/`:

- `the-press-logo.svg`
- `the-press-logo-reverse.svg`
- `the-press-mark.svg`
- `favicon.svg`

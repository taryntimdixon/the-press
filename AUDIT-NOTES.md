# Audit notes: logo-safe v3

## Issue fixed from v2

The polished v2 page used text mastheads in the standalone `authors.html` file. Your current site uses `assets/the-press-logo.svg` in the masthead and footer, so this version avoids replacing those areas.

## Logo safety

- The installer replaces only the `<main>` block of `authors.html`.
- The existing header, masthead, logo image, navigation, and footer remain in place.
- The bundle does not include a replacement logo.
- The installer does not overwrite files inside `assets/`.
- The installer only references `assets/the-press-logo.svg` in build.py if that file already exists.
- The build.py patch preserves existing logo markup and upgrades exact text-masthead fallbacks to the existing SVG logo when found.

## Color safety

The pledge CSS now uses the site’s existing design variables:

- `--bg`
- `--surface`
- `--surface-2`
- `--ink`
- `--muted`
- `--line`
- `--accent`
- `--accent-soft`
- `--shadow`
- `--radius`

That means the pledge page should feel like The Press, not like a different newspaper kicked down the door with a Pinterest board.

## Scope safety

All new pledge styling is scoped to `body.page-pledge` and pledge-specific classes such as `.pledge-hero`, `.pledge-card`, `.pledge-workflow`, `.pledge-receipts`, `.pledge-warning`, and `.pledge-sign`.

## Workflow safety

The installer patches `build.py` because `authors.html` can be regenerated. Without that patch, a future build could erase the pledge page. Computers adore betrayal, so we plan for it.

# Below the Fold Newsstand

The Newsstand turns Below the Fold into a permanent issue system instead of an endlessly growing homepage section.

## Add a normal issue

1. Add a new entry to `data/below-the-fold.json`.
2. Give it a unique lowercase-hyphen `slug`, the next highest positive `issueNumber`, title/dek/date metadata, a thumbnail if available, and a URL exactly like `below-the-fold/<slug>.html`.
3. Put the issue body at `content/below-fold/<slug>.html`.
4. Add `"bodyFile": "content/below-fold/<slug>.html"` to the registry entry.
5. Run:

```bash
PRESS_ALLOW_LEGACY_MASTER_BUILD=1 python3 studio/build.py
```

The build opens the highest-numbered issue inline on the homepage, moves the previous issue into the back-issue shelf, updates `below-the-fold.html`, generates the permanent issue page, and refreshes `sitemap.xml` and `search-index.json`.

The build now validates this workflow. It fails if an issue has a duplicate slug, duplicate issue number, unsafe URL, body file outside `content/below-fold/`, unknown custom renderer, missing issue page, a stacked older issue on the homepage, or a Below the Fold entry leaking into the regular archive/gallery/content indexes.

## Issue order rules

- The oldest issue has the lowest `issueNumber`.
- The newest issue has the highest `issueNumber`.
- The homepage always opens the highest-numbered issue inline.
- The Newsstand lists all issues newest first.
- Previous/next links are generated from `issueNumber`.
- Do not edit `index.html` by hand for Below the Fold ordering; update `data/below-the-fold.json` and rebuild.

## Add a designed issue

Use a custom renderer when an issue needs a highly designed layout like the Makers' Register, Remote Work List, or Artemis issue.

1. Add the issue metadata to `data/below-the-fold.json`.
2. Add the renderer function in `build.py`.
3. Wire the renderer key in the `BELOW_FOLD_RENDERERS` map.
4. Keep image assets under `assets/below-fold/<slug>/`.
5. Run the build command above.

## Generated pages

- `index.html` opens the latest Below the Fold issue inline and keeps older issues in a compact back-issue shelf.
- `below-the-fold.html` is The Newsstand archive.
- `below-the-fold/<slug>.html` is the permanent page for each issue.

Existing regular article pages, section pages, archive pages, On This Day, and the RSS feed remain separate from Below the Fold issues.

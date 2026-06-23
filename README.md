# The Press Studio

This folder turns the static site into a repeatable publishing workflow.

## What controls the site

- `master-edition.json` is the single control file for story metadata, homepage order, section pages, authors, search, and feeds.
- `content/asides/*.html` holds the sidebar modules for each story: key points, table of contents, and reporting notes.
- `content/bodies/*.html` holds the main article body for each story.
- `templates/story-template.html` is the blank story shell for new features.
- `editorial-standards.md` defines the fact-density, source, image, and independent-rail layout rules for future features.
- `build.py` regenerates the public pages.

## Publishing a new story

1. Duplicate `templates/story-template.html` and use it as your drafting shell.
2. Create two files:
   - `content/asides/<slug>.html`
   - `content/bodies/<slug>.html`
3. Add the story metadata to `master-edition.json`.
4. Add the local image file to `assets/`.
5. For illustration-led features, use `.press-editorial-region` with two `.press-editorial-rail` stacks so short modules can move upward independently of taller neighboring modules.
6. Run:

```bash
python studio/build.py
```

## Living article standard

- Every full story should keep `body.page-article`, an `.article` or `.article-shell` wrapper, and an `.article-body` or `[data-article-body]` container.
- Source notes should live in `#source-notes`, `.source-notes`, or `.article-sources` so the Source Board can group the receipts.
- Story headings inside the article body become the Timeline; place and entity lenses come from the local dictionaries in `app.js`.
- `build.py` and the daily automation now include the living kit automatically through `app.js`, so new stories get Place Lens, Share Studio, Source Board, Timeline, Entity Cards, Listen, Focus, Follow Topic, reading memory, and the combined reading-progress/top control without an API.

## Homepage hero standard

- The homepage hero is a permanent 7-story system: 1 center lead plus 3 side cards on the left and 3 on the right.
- Fresh image-ready stories automatically seed the hero before manual `homepage.leadOrder` or `placements.json` entries, so a newly published story with a thumbnail can appear without hand-editing the hero list.
- Manual hero lists still guide the remaining rotation, but they no longer block new stories from entering the hero.
- Keep every hero candidate supplied with a real local `image`, `imageAlt`, and dimensions when possible; the build and app preserve 16:9 side thumbnails so new cards do not squeeze older ones.

## What gets rebuilt

- `index.html`
- `archive.html`
- `authors.html`
- every `section-*.html` page
- every story page listed in `master-edition.json`
- `edition.json`
- `search-index.json`
- `photo-records.json`
- `feed.xml`
- `sitemap.xml`
- `404.html`

## Notes

- The build assumes `styles.css`, `app.js`, and `assets/` stay in the site root.
- Article thumbnails and hero images are local files, so story images still work offline.
- Static trust pages like `about.html`, `standards.html`, `corrections.html`, `contact.html`, and `photo-workflow.html` stay in the public root and can be edited separately.

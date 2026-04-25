#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import datetime
from email.utils import format_datetime
import html
import json
import math

SITE_DIR = Path(__file__).resolve().parents[1]
STUDIO_DIR = SITE_DIR / "studio"
DATA = json.loads((STUDIO_DIR / "master-edition.json").read_text(encoding="utf-8"))

SITE = DATA["site"]
SECTIONS = DATA["sections"]
AUTHORS = DATA["authors"]
STORIES = sorted(DATA["stories"], key=lambda item: item["publishedIso"], reverse=True)
SECTION_BY_SLUG = {section["slug"]: section for section in SECTIONS}
AUTHOR_BY_SLUG = {author["slug"]: author for author in AUTHORS}
STORY_BY_FILE = {story["filename"]: story for story in STORIES}


def h(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def json_script(data: object) -> str:
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def absolute_url(path: str) -> str:
    return SITE["baseUrl"].rstrip("/") + "/" + path.lstrip("/")


def initials(name: str) -> str:
    parts = [part for part in name.split() if part]
    return "".join(part[0] for part in parts[:2]).upper() or "TP"


def read_fragment(rel_path: str) -> str:
    return (STUDIO_DIR / rel_path).read_text(encoding="utf-8")


def search_index() -> list[dict]:
    items = []
    for story in STORIES:
        items.append(
            {
                "title": story["title"],
                "section": story["section"],
                "type": story["type"],
                "dek": story["dek"],
                "url": story["filename"],
                "author": story["author"],
                "published": story["publishedLabel"],
                "keywords": story.get("keywords", []),
            }
        )
    return items


def edition_export() -> list[dict]:
    out = []
    for story in STORIES:
        out.append(
            {
                "title": story["title"],
                "url": story["filename"],
                "section": story["section"],
                "type": story["type"],
                "author": story["author"],
                "publishedLabel": story["publishedLabel"],
                "updatedLabel": story["updatedLabel"],
                "publishedIso": story["publishedIso"],
                "updatedIso": story["updatedIso"],
                "wordCount": story["wordCount"],
                "readTime": story["readTime"],
                "dek": story["dek"],
                "image": story["image"],
                "imageAlt": story["imageAlt"],
                "imageCredit": story["imageCreditPlain"],
            }
        )
    return out


def photo_records() -> list[dict]:
    rows = []
    for story in STORIES:
        rows.append(
            {
                "story": story["title"],
                "page": story["filename"],
                "section": story["section"],
                "image": story["image"],
                "alt": story["imageAlt"],
                "credit": story["imageCreditPlain"],
            }
        )
    return rows


def section_stories(section_slug: str) -> list[dict]:
    return [story for story in STORIES if story["sectionSlug"] == section_slug]


def related_stories(story: dict) -> list[dict]:
    related = [STORY_BY_FILE[file] for file in story.get("related", []) if file in STORY_BY_FILE and file != story["filename"]]
    if len(related) >= 3:
        return related[:3]
    same_section = [item for item in STORIES if item["sectionSlug"] == story["sectionSlug"] and item["filename"] != story["filename"]]
    for item in same_section + STORIES:
        if item["filename"] == story["filename"]:
            continue
        if item not in related:
            related.append(item)
        if len(related) == 3:
            break
    return related[:3]


def story_card(story: dict, extra_class: str = "", archive: bool = False) -> str:
    classes = "story-card"
    if extra_class:
        classes += f" {extra_class}"
    archive_attr = ' archive-card' if archive else ''
    return f"""
<article class="{classes}{archive_attr}" data-section="{h(story['section'])}" data-type="{h(story['type'])}">
  <a class="story-card__image" href="{h(story['filename'])}">
    <img src="{h(story['image'])}" alt="{h(story['imageAlt'])}" loading="lazy" decoding="async"{f' width="{story["imageWidth"]}"' if story.get("imageWidth") else ''}{f' height="{story["imageHeight"]}"' if story.get("imageHeight") else ''} />
  </a>
  <div class="story-card__body">
    <p class="eyebrow eyebrow--compact">{h(story['section'])} • {h(story['type'])}</p>
    <h3 class="story-card__title"><a href="{h(story['filename'])}">{h(story['title'])}</a></h3>
    <p class="story-card__dek">{h(story['dek'])}</p>
    <p class="story-card__meta">By {h(story['author'])} • {h(story['publishedLabel'])} • {h(story['readTime'])}</p>
  </div>
</article>
""".strip()


def river_item(story: dict) -> str:
    return f"""
<article class="river-item">
  <a class="river-item__thumb" href="{h(story['filename'])}">
    <img src="{h(story['image'])}" alt="{h(story['imageAlt'])}" loading="lazy" decoding="async"{f' width="{story["imageWidth"]}"' if story.get("imageWidth") else ''}{f' height="{story["imageHeight"]}"' if story.get("imageHeight") else ''} />
  </a>
  <div class="river-item__body">
    <p class="eyebrow eyebrow--tiny">{h(story['section'])} • {h(story['type'])}</p>
    <h3><a href="{h(story['filename'])}">{h(story['title'])}</a></h3>
    <p>{h(story['excerpt'])}</p>
    <p class="river-item__meta">By {h(story['author'])} • {h(story['publishedLabel'])} • {h(story['readTime'])}</p>
  </div>
</article>
""".strip()


def ranked_list_item(story: dict, rank: int) -> str:
    return f"""
<li class="link-list__item">
  <span class="rank-number">{rank}</span>
  <div>
    <p class="eyebrow eyebrow--tiny">{h(story['section'])} • {h(story['type'])}</p>
    <a href="{h(story['filename'])}">{h(story['title'])}</a>
    <p class="link-list__meta">By {h(story['author'])} • {h(story['publishedLabel'])}</p>
  </div>
</li>
""".strip()


def simple_list_item(story: dict) -> str:
    return f"""
<li class="link-list__item">
  <div>
    <p class="eyebrow eyebrow--tiny">{h(story['section'])} • {h(story['type'])}</p>
    <a href="{h(story['filename'])}">{h(story['title'])}</a>
    <p class="link-list__meta">By {h(story['author'])} • {h(story['publishedLabel'])}</p>
  </div>
</li>
""".strip()


def desk_card(section: dict, top_story: dict) -> str:
    return f"""
<article class="desk-card">
  <p class="desk-card__kicker">{h(section['eyebrow'])}</p>
  <h3><a href="{h(section['filename'])}">{h(section['headline'])}</a></h3>
  <p>{h(section['copy'])}</p>
  <a class="desk-card__story" href="{h(top_story['filename'])}">{h(top_story['title'])}</a>
</article>
""".strip()


def related_block(story: dict) -> str:
    related = related_stories(story)
    if not related:
        return '<section id="related-stories" class="related-block"><h2>Related reading</h2><p class="empty-state">Related stories will appear here as the desk grows.</p></section>'
    cards = "\n".join(story_card(item, extra_class="story-card--related") for item in related)
    return f"""
<section id="related-stories" class="related-block">
  <h2>Related reading</h2>
  <div class="related-grid">
    {cards}
  </div>
</section>
""".strip()




def gallery_block(story: dict) -> str:
    images = story.get("galleryImages") or []
    if not isinstance(images, list) or not images:
        return ""

    figures = []
    for idx, image in enumerate(images[:10], start=1):
        if not isinstance(image, dict):
            continue
        src = str(image.get("src") or "").strip()
        if not src:
            continue
        alt = image.get("alt") or f"AI-generated visual {idx} for {story['title']}"
        style = image.get("style") or "artistic"
        caption_html = image.get("captionHtml") or image.get("relevanceNote") or "AI-generated image by The Press."
        figures.append(
            f'''
<figure class="ai-article-gallery__item" data-ai-art-index="{idx}" data-ai-art-style="{h(style)}">
  <img src="{h(src)}" alt="{h(alt)}" loading="lazy" decoding="async" />
  <figcaption>{caption_html}</figcaption>
</figure>
'''.strip()
        )

    if not figures:
        return ""

    return f'''
<section class="ai-article-gallery" data-ai-article-gallery>
  <div class="ai-article-gallery__header">
    <p class="eyebrow eyebrow--tiny">AI visual brief</p>
    <h2>Scenes and explainers from this story</h2>
    <p>AI-generated visuals built from this article's reporting.</p>
  </div>
  <div class="ai-article-gallery__grid">
    {''.join(figures)}
  </div>
</section>
'''.strip()


def header(current_section: str = "", current_aux: str = "") -> str:
    utility_links = []
    for link in SITE.get("mastheadLinks", []):
        current = ' aria-current="page"' if current_aux == link["href"] else ""
        utility_links.append(f'<a class="utility-link" href="{h(link["href"])}"{current}>{h(link["label"])}</a>')
    return f"""
<header class="site-header" data-site-header>
  <div class="topbar">
    <div class="topbar__inner">
      <p class="edition-note">{h(SITE['editionNote'])}</p>
      <div class="topbar__actions">
        <button class="search-trigger" type="button" data-search-open>Search</button>
      </div>
    </div>
  </div>
  <div class="masthead-row">
    <div class="masthead-wrap">
      <a class="masthead masthead-with-logo" href="index.html" aria-label="The Press home"><img class="masthead-logo" src="assets/the-press-logo.svg" alt="The Press logo" decoding="async" /></a>
    </div>
    <nav class="utility-nav" aria-label="Utility navigation">
      {' '.join(utility_links)}
    </nav>
  </div>
</header>
""".strip()


def footer() -> str:
    newsroom_links = """
<li><a href="archive.html">Archive</a></li>
<li><a href="authors.html">Authors</a></li>
<li><a href="about.html">About</a></li>
<li><a href="standards.html">Standards</a></li>
<li><a href="corrections.html">Corrections</a></li>
<li><a href="photo-workflow.html">Photo workflow</a></li>
<li><a href="contact.html">Contact</a></li>
""".strip()
    return f"""
<footer class="site-footer">
  <div class="footer-grid footer-grid--archive-only">
    <section class="footer-brand">
      <a class="masthead masthead--footer" href="index.html">{h(SITE['name'])}</a>
      <p class="footer-copy">{h(SITE['tagline'])}</p>
      <p class="footer-copy footer-copy--small">Visible AI use, visible standards, visible source notes.</p>
    </section>
    <section>
      <h2 class="footer-heading">Newsroom</h2>
      <ul class="footer-list">
        {newsroom_links}
      </ul>
    </section>
  </div>
  <div class="footer-rule">
    <p class="footer-copy footer-copy--small">© <span data-year></span> {h(SITE['name'])}. Built as a static-first newsroom package.</p>
  </div>
</footer>
""".strip()


def search_overlay(search_data: list[dict]) -> str:
    return f"""
<div class="search-overlay" hidden data-search-overlay>
  <div class="search-panel" role="dialog" aria-modal="true" aria-labelledby="search-title">
    <div class="search-panel__header">
      <h2 id="search-title">Search {h(SITE['name'])}</h2>
      <button class="search-close" type="button" aria-label="Close search" data-search-close>Close</button>
    </div>
    <label class="search-label" for="global-search-input">Search headlines, sections, or topics</label>
    <input class="search-input" id="global-search-input" type="search" placeholder="Search for housing, NASA, attendance, elections…" autocomplete="off" data-search-input />
    <p class="search-hint">Results update as you type. Try: housing, Artemis, voter registration, measles, streaming.</p>
    <div class="search-results" data-search-results>
      <div class="search-empty">
        <p>Start typing to search the full edition.</p>
      </div>
    </div>
  </div>
</div>
<script id="press-search-data" type="application/json">{json_script(search_data)}</script>
""".strip()


def page_head(title: str, description: str, canonical: str, jsonld: str = "", extra_links: str = "") -> str:
    canonical_url = absolute_url(canonical)
    return f"""
<head>
  <meta charset="utf-8" />
  <title>{h(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="{h(description)}" />
  <meta name="theme-color" content="#f4f0e8" />
  <meta name="apple-mobile-web-app-title" content="{h(SITE['name'])}" />
  <meta name="mobile-web-app-capable" content="yes" />
  <link rel="canonical" href="{h(canonical_url)}" />
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml" />
  <link rel="shortcut icon" href="favicon.svg" type="image/svg+xml" />
  <link rel="icon" href="assets/icon-192.png" sizes="192x192" type="image/png" />
  <link rel="apple-touch-icon" href="assets/apple-touch-icon.png" />
  <link rel="stylesheet" href="styles.css" />
  <link rel="manifest" href="site.webmanifest" />
  <link rel="alternate" type="application/rss+xml" title="{h(SITE['name'])} feed" href="feed.xml" />
  {jsonld}
  {extra_links}
</head>
""".strip()


def jsonld_org() -> str:
    obj = {
        "@context": "https://schema.org",
        "@type": "NewsMediaOrganization",
        "name": SITE["name"],
        "url": SITE["baseUrl"],
        "logo": absolute_url("assets/favicon.svg"),
        "slogan": SITE["tagline"],
        "publishingPrinciples": absolute_url("standards.html"),
        "correctionsPolicy": absolute_url("corrections.html"),
        "ethicsPolicy": absolute_url("standards.html"),
        "diversityPolicy": absolute_url("about.html"),
    }
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'


def jsonld_article(story: dict) -> str:
    obj = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": story["title"],
        "description": story["dek"],
        "isAccessibleForFree": True,
        "mainEntityOfPage": {"@type": "WebPage", "@id": absolute_url(story["filename"])},
        "datePublished": story["publishedIso"],
        "dateModified": story["updatedIso"],
        "articleSection": story["section"],
        "wordCount": story.get("wordCountNumber"),
        "author": {
            "@type": "Person",
            "name": story["author"],
            "url": absolute_url(f"authors.html#{story['authorSlug']}"),
        },
        "image": {
            "@type": "ImageObject",
            "url": absolute_url(story["image"]),
            "width": story.get("imageWidth"),
            "height": story.get("imageHeight"),
        },
        "publisher": {
            "@type": "NewsMediaOrganization",
            "name": SITE["name"],
            "url": SITE["baseUrl"],
            "logo": {"@type": "ImageObject", "url": absolute_url("assets/favicon.svg")},
            "ethicsPolicy": absolute_url("standards.html"),
            "correctionsPolicy": absolute_url("corrections.html"),
            "publishingPrinciples": absolute_url("standards.html"),
        },
    }
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'


def layout(title: str, description: str, canonical: str, body_class: str, main_html: str, current_section: str = "", current_aux: str = "", jsonld: str = "", include_progress: bool = False) -> str:
    progress = """
<div class="reading-progress"><div class="reading-progress__bar" data-reading-progress></div></div>
""".strip() if include_progress else ""
    return f"""<!doctype html>
<html lang="en">
{page_head(title, description, canonical, jsonld)}
<body class="{h(body_class)}">
  {search_overlay(search_index())}
  {progress}
  {header(current_section=current_section, current_aux=current_aux)}
  {main_html}
  {footer()}
  <script src="app.js" defer></script>
</body>
</html>
""".strip() + "\n"


def render_homepage() -> str:
    lead_panels = []
    lead_buttons = []
    for idx, filename in enumerate(DATA["homepage"]["leadOrder"]):
        story = STORY_BY_FILE[filename]
        active = " is-active" if idx == 0 else ""
        lead_panels.append(
            f"""
<div class="lead-panel{active}" data-lead-panel id="lead-{idx}">
  <div class="lead-panel__media">
    <img src="{h(story['image'])}" alt="{h(story['imageAlt'])}" loading="eager" decoding="async"{f' width="{story["imageWidth"]}"' if story.get("imageWidth") else ''}{f' height="{story["imageHeight"]}"' if story.get("imageHeight") else ''} />
  </div>
  <div class="lead-panel__body">
    <div>
      <p class="eyebrow">Front Page • {h(story['section'])} • {h(story['type'])}</p>
      <h2><a href="{h(story['filename'])}">{h(story['title'])}</a></h2>
      <p class="lead-panel__dek">{h(story['dek'])}</p>
      <p class="lead-panel__meta">By {h(story['author'])} • {h(story['publishedLabel'])} • {h(story['wordCount'])}</p>
    </div>
    <div class="button-row">
      <a class="button" href="{h(story['filename'])}">Read story</a>
      <a class="button button--ghost" href="archive.html">Open archive</a>
    </div>
  </div>
</div>
""".strip()
        )
        lead_buttons.append(
            f'<button class="lead-nav__button{" is-active" if idx == 0 else ""}" type="button" data-lead-button data-target="lead-{idx}" aria-pressed="{str(idx == 0).lower()}"><span>{h(story["section"])}</span><strong>{h(story["title"])}</strong></button>'
        )
    secondary_cards = "\n".join(story_card(STORY_BY_FILE[file]) for file in DATA["homepage"]["secondary"] if file in STORY_BY_FILE)
    most_read_html = "\n".join(ranked_list_item(STORY_BY_FILE[file], rank + 1) for rank, file in enumerate(DATA["homepage"]["mostRead"]) if file in STORY_BY_FILE)
    editors_html = "\n".join(simple_list_item(STORY_BY_FILE[file]) for file in DATA["homepage"]["editorsPicks"] if file in STORY_BY_FILE)
    latest_html = "\n".join(river_item(story) for story in STORIES[:8])
    main = f"""
<main class="page">
  <section class="home-hero">
    <div class="home-hero__intro">
      <p class="eyebrow">Front page</p>
      <h1>{h(SITE['name'])}</h1>
      <p class="section-copy">{h(SITE['description'])}</p>
    </div>
    <div class="lead-switcher">
      <div class="lead-switcher__panels">
        {' '.join(lead_panels)}
      </div>
      <div class="lead-nav" aria-label="Lead story switcher">
        {' '.join(lead_buttons)}
      </div>
    </div>
  </section>

  <section class="home-grid">
    <div class="home-grid__main">
      <div class="section-heading-row">
        <h2 class="section-heading">More from the edition</h2>
        <a class="section-link" href="archive.html">Open archive</a>
      </div>
      <div class="cards-grid cards-grid--three">
        {secondary_cards}
      </div>
    </div>
    <aside class="home-grid__aside">
      <section class="rail rail--most-read">
        <div class="section-heading-row">
          <h2 class="section-heading">Most Read</h2>
        </div>
        <ul class="link-list">
          {most_read_html}
        </ul>
      </section>
      <section class="rail rail--editors">
        <div class="section-heading-row">
          <h2 class="section-heading">Editors’ Picks</h2>
        </div>
        <ul class="link-list">
          {editors_html}
        </ul>
      </section>
    </aside>
  </section>

  <section class="latest-section">
    <div class="section-heading-row">
      <div>
        <p class="eyebrow">Latest</p>
        <h2 class="section-heading">The newest stories across the desks</h2>
      </div>
      <a class="section-link" href="archive.html">See everything</a>
    </div>
    <div class="river">
      {latest_html}
    </div>
  </section>

  <section class="newsletter-block">
    <div>
      <p class="eyebrow">Newsletter</p>
      <h2 class="section-heading">{h(SITE['newsletterTitle'])}</h2>
      <p class="section-copy">{h(SITE['newsletterCopy'])}</p>
    </div>
    <form class="newsletter-form" data-newsletter-form>
      <input type="email" name="email" placeholder="Email address" aria-label="Email address" required />
      <button type="submit">Join</button>
      <p class="newsletter-status" data-newsletter-status></p>
    </form>
  </section>

  <section class="trust-strip">
    <article class="trust-card">
      <p class="eyebrow eyebrow--tiny">Trust</p>
      <h2>Visible standards</h2>
      <p>Every feature ships with visible dates, bylines, source notes, and corrections status.</p>
    </article>
    <article class="trust-card">
      <p class="eyebrow eyebrow--tiny">Images</p>
      <h2>Local image records</h2>
      <p>Story art is bundled locally, documented in photo records, and no longer disappears on click-through.</p>
    </article>
    <article class="trust-card">
      <p class="eyebrow eyebrow--tiny">Workflow</p>
      <h2>Static-first newsroom</h2>
      <p>The homepage, archive, section pages, feeds, and story pages are all driven from one master edition file.</p>
    </article>
  </section>
</main>
""".strip()
    return layout(f"{SITE['name']} — Front Page", SITE["description"], "index.html", "page-home", main, jsonld=jsonld_org())


def render_archive() -> str:
    filters = ['All'] + [section['name'] for section in SECTIONS] + sorted({story['type'] for story in STORIES})
    filter_buttons = "\n".join(
        f'<button class="filter-chip{" is-active" if value=="All" else ""}" type="button" data-filter="{h(value)}" aria-pressed="{str(value=="All").lower()}">{h(value)}</button>'
        for value in filters
    )
    cards = "\n".join(story_card(story, archive=True) for story in STORIES)
    main = f"""
<main class="page page-archive">
  <section class="page-hero">
    <p class="eyebrow">Archive</p>
    <h1>Every story in the edition</h1>
    <p class="section-copy">Filter by desk or story type. This page is generated from the master edition file, so a new feature automatically lands here after a rebuild.</p>
  </section>
  <section class="filter-toolbar" aria-label="Archive filters">
    {filter_buttons}
  </section>
  <section class="cards-section">
    <div class="cards-grid cards-grid--archive">
      {cards}
    </div>
  </section>
</main>
""".strip()
    return layout(f"Archive — {SITE['name']}", "The full archive of The Press.", "archive.html", "page-archive", main, current_aux="archive.html", jsonld=jsonld_org())


def render_section(section: dict) -> str:
    stories = section_stories(section["slug"])
    if not stories:
        cards = '<p class="empty-state">No stories published in this section yet.</p>'
    else:
        cards = "\n".join(story_card(story, archive=True) for story in stories)
    art = f'<img class="page-art" src="{h(section["artwork"])}" alt="{h(section["headline"])} desk artwork" />' if section.get("artwork") else ""
    main = f"""
<main class="page">
  <section class="section-landing page-hero--with-art">
    <div>
      <p class="eyebrow">{h(section['eyebrow'])}</p>
      <h1>{h(section['headline'])}</h1>
      <p class="section-copy">{h(section['copy'])}</p>
    </div>
    {art}
  </section>
  <section class="cards-section">
    <div class="cards-grid cards-grid--archive">
      {cards}
    </div>
  </section>
</main>
""".strip()
    return layout(f"{section['headline']} — {SITE['name']}", section["copy"], section["filename"], "page-section", main, current_section=section["slug"], jsonld=jsonld_org())


def render_authors() -> str:
    cards = []
    for author in AUTHORS:
        author_stories = [STORY_BY_FILE[file] for file in author.get("stories", []) if file in STORY_BY_FILE]
        story_links = "\n".join(
            f'<li><a href="{h(story["filename"])}">{h(story["title"])}</a><span>{h(story["publishedLabel"])}</span></li>'
            for story in author_stories
        )
        cards.append(
            f"""
<article class="staff-card" id="{h(author['slug'])}">
  <div class="staff-card__header">
    <div class="author-chip author-chip--large">{h(initials(author['name']))}</div>
    <div>
      <h2>{h(author['name'])}</h2>
      <p class="staff-card__role">{h(author['role'])}</p>
    </div>
  </div>
  <p>{h(author['bio'])}</p>
  <p class="staff-card__topics">Coverage: {h(', '.join(author.get('topics', [])))}</p>
  <ul class="staff-card__stories">
    {story_links}
  </ul>
</article>
""".strip()
        )
    main = f"""
<main class="page">
  <section class="page-hero page-hero--with-art">
    <div>
      <p class="eyebrow">Authors</p>
      <h1>Named desks and reporting beats</h1>
      <p class="section-copy">The site is now wired for named staff bylines, grouped coverage areas, and reusable author cards generated from the master edition file.</p>
    </div>
    <img class="page-art" src="assets/team-authors.svg" alt="The Press staff artwork" />
  </section>
  <section class="staff-grid">
    {' '.join(cards)}
  </section>
</main>
""".strip()
    return layout(f"Authors — {SITE['name']}", "Meet the staff desks and bylines behind The Press.", "authors.html", "page-authors", main, current_aux="authors.html", jsonld=jsonld_org())


def render_story(story: dict) -> str:
    aside_html = read_fragment(story["asideFile"])
    body_html = read_fragment(story["bodyFile"])
    gallery_html = gallery_block(story)
    related_html = related_block(story)
    main = f"""
<main class="page page-article">
  <article class="article">
    <header class="article-hero">
      <p class="eyebrow">{h(story['section'])} • {h(story['type'])}</p>
      <h1 class="article-headline">{h(story['title'])}</h1>
      <p class="article-dek">{h(story['dek'])}</p>
      <div class="article-meta">
        <span>By <a href="authors.html#{h(story['authorSlug'])}">{h(story['author'])}</a></span>
        <span>Published {h(story['publishedLabel'])}</span>
        <span>Updated {h(story['updatedLabel'])}</span>
        <span>{h(story['wordCount'])}</span>
        <span>{h(story['readTime'])}</span>
      </div>
      <figure class="hero-figure">
        <img src="{h(story['image'])}" alt="{h(story['imageAlt'])}" loading="eager" decoding="async"{f' width="{story["imageWidth"]}"' if story.get("imageWidth") else ''}{f' height="{story["imageHeight"]}"' if story.get("imageHeight") else ''} />
        <figcaption>{story['imageCaptionHtml']}</figcaption>
      </figure>
    </header>
    <div class="article-shell">
      <aside class="article-aside">
        <div class="sticky-stack">
          {aside_html}
        </div>
      </aside>
      <div class="article-body">
        {body_html}
        {gallery_html}
        {related_html}
      </div>
    </div>
  </article>
</main>
""".strip()
    return layout(f"{story['title']} — {SITE['name']}", story["dek"], story["filename"], "page-article", main, current_section=story["sectionSlug"], jsonld=jsonld_article(story), include_progress=True)


def render_404() -> str:
    main = f"""
<main class="page">
  <section class="page-hero">
    <p class="eyebrow">Not found</p>
    <h1>This page is not in the edition.</h1>
    <p class="section-copy">The link may be old, mistyped, or from a previous build. Head back to the front page or open the archive.</p>
    <div class="button-row">
      <a class="button" href="index.html">Front page</a>
      <a class="button button--ghost" href="archive.html">Archive</a>
    </div>
  </section>
</main>
""".strip()
    return layout(f"404 — {SITE['name']}", "The Press page not found.", "404.html", "page-404", main, jsonld=jsonld_org())


def render_feed() -> str:
    items = []
    for story in STORIES[:20]:
        dt = datetime.fromisoformat(story["publishedIso"])
        items.append(
            f"""
<item>
  <title>{html.escape(story['title'])}</title>
  <link>{html.escape(absolute_url(story['filename']))}</link>
  <guid>{html.escape(absolute_url(story['filename']))}</guid>
  <pubDate>{format_datetime(dt)}</pubDate>
  <description>{html.escape(story['dek'])}</description>
</item>
""".strip()
        )
    build_date = format_datetime(datetime.now().astimezone())
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{html.escape(SITE['name'])}</title>
    <link>{html.escape(absolute_url('index.html'))}</link>
    <description>{html.escape(SITE['description'])}</description>
    <lastBuildDate>{build_date}</lastBuildDate>
    {' '.join(items)}
  </channel>
</rss>
"""


def render_sitemap() -> str:
    urls = ['index.html', 'archive.html', 'authors.html', 'about.html', 'standards.html', 'corrections.html', 'contact.html', 'photo-workflow.html', '404.html']
    urls += [story["filename"] for story in STORIES]
    urlset = []
    for path in urls:
        lastmod = datetime.now().date().isoformat()
        urlset.append(f"<url><loc>{html.escape(absolute_url(path))}</loc><lastmod>{lastmod}</lastmod></url>")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {' '.join(urlset)}
</urlset>
"""


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def build() -> None:
    write_file(SITE_DIR / "index.html", render_homepage())
    write_file(SITE_DIR / "archive.html", render_archive())
    write_file(SITE_DIR / "authors.html", render_authors())
    for section in SECTIONS:
        write_file(SITE_DIR / section["filename"], render_section(section))
    for story in STORIES:
        write_file(SITE_DIR / story["filename"], render_story(story))
    write_file(SITE_DIR / "404.html", render_404())
    write_file(SITE_DIR / "edition.json", json.dumps(edition_export(), indent=2, ensure_ascii=False) + "\n")
    write_file(SITE_DIR / "search-index.json", json.dumps(search_index(), indent=2, ensure_ascii=False) + "\n")
    write_file(SITE_DIR / "photo-records.json", json.dumps(photo_records(), indent=2, ensure_ascii=False) + "\n")
    write_file(SITE_DIR / "feed.xml", render_feed())
    write_file(SITE_DIR / "sitemap.xml", render_sitemap())


if __name__ == "__main__":
    build()

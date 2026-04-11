from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
from pathlib import Path
from typing import Any

from openai import OpenAI

SITE = Path(__file__).resolve().parents[2]
DAILY_DIR = SITE / "daily"
DAILY_DIR.mkdir(parents=True, exist_ok=True)
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "https://thepress.live").rstrip("/")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4-mini")
STORY_COUNT = max(1, min(10, int(os.environ.get("STORY_COUNT", "10"))))
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

DESKS = [
    ("Politics", "analysis"),
    ("Economics", "report"),
    ("Science", "report"),
    ("Film", "feature"),
    ("AI", "analysis"),
    ("Technology", "report"),
    ("Niche", "feature"),
    ("Geopolitics", "analysis"),
    ("Pop Culture", "feature"),
    ("World", "report"),
]

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return re.sub(r"-{2,}", "-", text) or "story"

def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value or "")

def word_count(html_text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", strip_tags(html_text)))

def to_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise
        return json.loads(match.group(0))

def esc(value: str) -> str:
    return html.escape(value or "", quote=True)

def article_shell(title: str, description: str, canonical: str, search_data: str, body: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{esc(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="description" content="{esc(description)}"/>
<meta name="theme-color" content="#f4f0e8"/>
<link rel="canonical" href="{esc(canonical)}"/>
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml"/>
<link rel="stylesheet" href="../styles.css"/>
</head>
<body class="page-article">
<div class="search-overlay" data-search-overlay hidden>
  <div class="search-panel" role="dialog" aria-modal="true" aria-labelledby="search-title">
    <div class="search-panel__header">
      <h2 id="search-title">Search The Press</h2>
      <button class="search-close" type="button" data-search-close aria-label="Close search">Close</button>
    </div>
    <label class="search-label" for="global-search-input">Search headlines, sections, or topics</label>
    <input class="search-input" id="global-search-input" type="search" placeholder="Search the current edition…" autocomplete="off" data-search-input />
    <div class="search-results" data-search-results><div class="search-empty"><p>Start typing to search The Press.</p></div></div>
  </div>
</div>
<script id="press-search-data" type="application/json">{search_data}</script>
<div class="reading-progress"><div class="reading-progress__bar" data-reading-progress></div></div>
<header class="site-header" data-site-header>
  <div class="topbar">
    <div class="topbar__inner">
      <p class="edition-note">Worldwide edition • Updated daily • Reporting, analysis, culture, and breaking news.</p>
      <div class="topbar__actions">
        <button class="search-trigger" data-search-open type="button">Search</button>
        <button class="menu-trigger" data-menu-toggle type="button" aria-controls="site-sections" aria-expanded="false">Menu</button>
      </div>
    </div>
  </div>
  <div class="masthead-row">
    <div class="masthead-wrap">
      <a class="masthead" href="../index.html">The Press</a>
      <p class="masthead-tagline">A digital newspaper built for sourced long-form reporting.</p>
    </div>
    <nav class="utility-nav" aria-label="Utility navigation">
      <a class="utility-link" href="../archive.html">Archive</a>
      <a class="utility-link" href="../breaking-news.html">Breaking</a>
      <a class="utility-link" href="../authors.html">AI Newsroom</a>
      <a class="utility-link" href="../standards.html">Standards</a>
      <a class="utility-link" href="../contact.html">Contact</a>
    </nav>
  </div>
</header>
{body}
<footer class="site-footer">
  <div class="footer-grid">
    <section class="footer-brand">
      <a class="masthead masthead--footer" href="../index.html">The Press</a>
      <p class="footer-copy">Written by Intelligent AI. Curated before publication.</p>
    </section>
  </div>
  <div class="footer-rule"><p class="footer-copy footer-copy--small">© <span data-year></span> The Press.</p></div>
</footer>
<script defer src="../app.js"></script>
</body>
</html>'''

def page_shell(title: str, description: str, canonical: str, body_class: str, search_data: str, body: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{esc(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="description" content="{esc(description)}"/>
<meta name="theme-color" content="#f4f0e8"/>
<link rel="canonical" href="{esc(canonical)}"/>
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"/>
<link rel="stylesheet" href="styles.css"/>
</head>
<body class="{esc(body_class)}">
<div class="search-overlay" data-search-overlay hidden>
  <div class="search-panel" role="dialog" aria-modal="true" aria-labelledby="search-title">
    <div class="search-panel__header">
      <h2 id="search-title">Search The Press</h2>
      <button class="search-close" type="button" data-search-close aria-label="Close search">Close</button>
    </div>
    <label class="search-label" for="global-search-input">Search headlines, sections, or topics</label>
    <input class="search-input" id="global-search-input" type="search" placeholder="Search the current edition…" autocomplete="off" data-search-input />
    <div class="search-results" data-search-results><div class="search-empty"><p>Start typing to search The Press.</p></div></div>
  </div>
</div>
<script id="press-search-data" type="application/json">{search_data}</script>
<header class="site-header" data-site-header>
  <div class="topbar">
    <div class="topbar__inner">
      <p class="edition-note">Worldwide edition • Updated daily • Reporting, analysis, culture, and breaking news.</p>
      <div class="topbar__actions">
        <button class="search-trigger" data-search-open type="button">Search</button>
        <button class="menu-trigger" data-menu-toggle type="button" aria-controls="site-sections" aria-expanded="false">Menu</button>
      </div>
    </div>
  </div>
  <div class="masthead-row">
    <div class="masthead-wrap">
      <a class="masthead" href="index.html">The Press</a>
      <p class="masthead-tagline">A digital newspaper built for sourced long-form reporting.</p>
    </div>
    <nav class="utility-nav" aria-label="Utility navigation">
      <a class="utility-link" href="archive.html">Archive</a>
      <a class="utility-link" href="breaking-news.html">Breaking</a>
      <a class="utility-link" href="authors.html">AI Newsroom</a>
      <a class="utility-link" href="standards.html">Standards</a>
      <a class="utility-link" href="contact.html">Contact</a>
    </nav>
  </div>
  <nav class="section-nav" id="site-sections" aria-label="Sections">
    <div class="section-nav__inner">
      <a class="nav-link" href="archive.html">Politics</a>
      <a class="nav-link" href="archive.html">Economics</a>
      <a class="nav-link" href="archive.html">Science</a>
      <a class="nav-link" href="archive.html">Film</a>
      <a class="nav-link" href="archive.html">AI</a>
      <a class="nav-link" href="archive.html">Technology</a>
      <a class="nav-link" href="archive.html">Niche</a>
      <a class="nav-link" href="archive.html">Geopolitics</a>
      <a class="nav-link" href="archive.html">Pop Culture</a>
      <a class="nav-link" href="archive.html">World</a>
    </div>
  </nav>
</header>
{body}
<footer class="site-footer">
  <div class="footer-grid">
    <section class="footer-brand">
      <a class="masthead masthead--footer" href="index.html">The Press</a>
      <p class="footer-copy">Written by Intelligent AI. Curated before publication.</p>
    </section>
  </div>
  <div class="footer-rule"><p class="footer-copy footer-copy--small">© <span data-year></span> The Press.</p></div>
</footer>
<script defer src="app.js"></script>
</body>
</html>'''

def create_story(client: OpenAI, section: str, story_type: str) -> dict[str, Any]:
    prompt = f"""
Write one rich news article for The Press.

Section: {section}
Story type: {story_type}

Requirements:
- 1400 to 1800 words.
- Current, factual, and sourced with live web research.
- No made-up human byline. Visible byline should be "Written by Intelligent AI".
- Do not mention hidden tools, backend systems, pull requests, workflows, or how the website is built.
- Return valid JSON only with these keys:
  title
  dek
  bullets (array of 3)
  body_html (semantic HTML using <p>, <h2>, <h3>, <ul>, <li>, <blockquote>)
  sources (array of 6 to 8 objects with label and url)
  keywords (array of 5 to 10 strings)
"""
    response = client.responses.create(
        model=MODEL,
        tools=[{"type": "web_search_preview"}],
        input=prompt,
    )
    data = to_json(response.output_text)
    data["section"] = section
    data["story_type"] = story_type.title()
    return data

def article_body(story: dict[str, Any], published: str, words: int) -> str:
    bullets = "".join(f"<li>{esc(item)}</li>" for item in story.get("bullets", [])[:3])
    sources = "".join(f"<li><a href='{esc(src['url'])}' target='_blank' rel='noopener'>{esc(src['label'])}</a></li>" for src in story.get("sources", []))
    return f"""
<main class="page page-article">
  <article class="article">
    <header class="article-hero">
      <p class="eyebrow">{esc(story['section'])} • {esc(story['story_type'])}</p>
      <h1 class="article-headline">{esc(story['title'])}</h1>
      <p class="article-dek">{esc(story['dek'])}</p>
      <p class="article-meta"><span>Written by Intelligent AI</span><span>{esc(published)}</span><span>{words} words</span></p>
    </header>
    <div class="article-grid">
      <aside class="article-aside">
        <section class="info-card">
          <p class="eyebrow eyebrow--tiny">Key points</p>
          <ul class="bullet-list">{bullets}</ul>
        </section>
      </aside>
      <div class="article-body">
        {story['body_html']}
        <section class="source-notes">
          <h2>Source notes</h2>
          <ol class="source-list">{sources}</ol>
        </section>
      </div>
    </div>
  </article>
</main>
"""

def main():
    client = OpenAI(api_key=OPENAI_API_KEY)
    now = dt.datetime.now().astimezone()
    story_specs = DESKS[:STORY_COUNT]
    stories = []
    for idx, (section, story_type) in enumerate(story_specs, start=1):
        raw = create_story(client, section, story_type)
        slug = f"{now.date().isoformat()}-{idx:02d}-{slugify(raw['title'])}"
        url = f"daily/{slug}.html"
        published = now.strftime("%B %d, %Y • %I:%M %p").replace(" 0", " ")
        words = word_count(raw.get("body_html", ""))
        story = {
            "title": raw["title"].strip(),
            "dek": raw["dek"].strip(),
            "section": section,
            "story_type": raw["story_type"],
            "bullets": raw.get("bullets", []),
            "body_html": raw.get("body_html", "").strip(),
            "sources": raw.get("sources", []),
            "keywords": raw.get("keywords", []),
            "url": url,
            "published": published,
            "words": words,
        }
        stories.append(story)

    search_data = json.dumps([{
        "title": s["title"],
        "section": s["section"],
        "type": s["story_type"],
        "dek": s["dek"],
        "url": s["url"],
        "author": "Intelligent AI",
        "published": s["published"],
        "keywords": s["keywords"],
    } for s in stories], ensure_ascii=False)

    for story in stories:
        out = SITE / story["url"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(article_shell(
            f"{story['title']} — The Press",
            story["dek"],
            f"{SITE_BASE_URL}/{story['url']}",
            search_data,
            article_body(story, story["published"], story["words"]),
        ), encoding="utf-8")

    lead = stories[0]
    cards = "".join(f"<article class='story-card'><div class='story-card__body'><p class='eyebrow eyebrow--compact'>{esc(s['section'])} • {esc(s['story_type'])}</p><h3 class='story-card__title'><a href='{esc(s['url'])}'>{esc(s['title'])}</a></h3><p class='story-card__dek'>{esc(s['dek'])}</p><p class='story-card__meta'>Written by Intelligent AI • {esc(s['published'])}</p></div></article>" for s in stories[1:])
    body = f"""
<section class='breaking-strip' aria-labelledby='breaking-title'>
  <div class='breaking-strip__inner'>
    <div class='breaking-strip__label-wrap'>
      <span class='breaking-strip__badge'>Breaking</span>
      <p class='breaking-strip__label' id='breaking-title'>Worldwide watch</p>
    </div>
    <div class='breaking-strip__items'>{''.join(f"<a href='{esc(s['url'])}'>{esc(s['title'])}</a>" for s in stories[:4])}</div>
    <a class='breaking-strip__more' href='breaking-news.html'>Open world wire</a>
  </div>
</section>
<main class='page'>
  <section class='home-hero'>
    <div class='home-hero__intro'>
      <p class='eyebrow'>Front page</p>
      <h1>Today’s Edition</h1>
      <p class='section-copy'>Ten new stories every day across politics, economics, science, film, AI, technology, niche topics, geopolitics, pop culture, and world affairs.</p>
    </div>
    <div class='lead-switcher'>
      <div class='lead-switcher__panels'>
        <div class='lead-panel is-active' data-lead-panel id='lead-0'>
          <div class='lead-panel__body'>
            <div>
              <p class='eyebrow'>Front Page • {esc(lead['section'])} • {esc(lead['story_type'])}</p>
              <h2><a href='{esc(lead['url'])}'>{esc(lead['title'])}</a></h2>
              <p class='lead-panel__dek'>{esc(lead['dek'])}</p>
              <p class='lead-panel__meta'>Written by Intelligent AI • {esc(lead['published'])} • {lead['words']} words</p>
            </div>
            <div class='button-row'>
              <a class='button' href='{esc(lead['url'])}'>Read story</a>
              <a class='button button--ghost' href='archive.html'>Open archive</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
  <section class='latest-section'>
    <div class='section-heading-row'><div><p class='eyebrow'>Latest</p><h2 class='section-heading'>Ten new stories</h2></div><a class='section-link' href='archive.html'>See everything</a></div>
    <div class='cards-grid cards-grid--three'>{cards}</div>
  </section>
</main>
"""

    index_html = page_shell(
        "The Press — Front Page",
        "Ten new rich articles every day across a wide range of topics.",
        f"{SITE_BASE_URL}/index.html",
        "page-home",
        search_data,
        body,
    )
    (SITE / "index.html").write_text(index_html, encoding="utf-8")
    (SITE / "ai-edition.html").write_text(index_html, encoding="utf-8")

    archive_cards = "".join(f"<article class='archive-card'><p class='eyebrow eyebrow--tiny'>{esc(s['section'])} • {esc(s['story_type'])}</p><h3><a href='{esc(s['url'])}'>{esc(s['title'])}</a></h3><p>{esc(s['dek'])}</p><p class='archive-card__meta'>Written by Intelligent AI • {esc(s['published'])}</p></article>" for s in stories)
    archive_body = f"""
<main class='page'>
  <section class='page-hero'>
    <div>
      <p class='eyebrow'>Archive</p>
      <h1>Today’s Archived Edition</h1>
      <p class='section-copy'>Every daily edition is archived with all article pages intact.</p>
    </div>
  </section>
  <section class='cards-grid cards-grid--archive'>{archive_cards}</section>
</main>
"""
    (SITE / "archive.html").write_text(page_shell("Archive — The Press", "Archived daily editions from The Press.", f"{SITE_BASE_URL}/archive.html", "page-archive", search_data, archive_body), encoding="utf-8")

    breaking_cards = "".join(f"<article class='info-card'><p class='eyebrow eyebrow--tiny'>{esc(s['section'])}</p><h2><a href='{esc(s['url'])}'>{esc(s['title'])}</a></h2><p>{esc(s['dek'])}</p></article>" for s in stories[:5])
    breaking_body = f"""
<main class='page'>
  <section class='page-hero'>
    <div>
      <p class='eyebrow'>Breaking</p>
      <h1>Worldwide watch</h1>
      <p class='section-copy'>The fastest-moving headlines from today’s edition.</p>
    </div>
  </section>
  <section class='cards-grid cards-grid--three'>{breaking_cards}</section>
</main>
"""
    (SITE / "breaking-news.html").write_text(page_shell("Breaking News — The Press", "Worldwide breaking items from The Press.", f"{SITE_BASE_URL}/breaking-news.html", "page-breaking", search_data, breaking_body), encoding="utf-8")

    (SITE / "search-index.json").write_text(search_data, encoding="utf-8")

if __name__ == "__main__":
    main()

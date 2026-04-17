#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
ASSETS_DAILY = ROOT / "assets" / "daily"
DAILY_DIR = ROOT / "daily"

SECTIONS: list[tuple[str, str]] = [
    ("politics", "Politics"),
    ("economics", "Economics"),
    ("science", "Science"),
    ("film", "Film"),
    ("ai", "AI"),
    ("technology", "Technology"),
    ("niche", "Niche"),
    ("geopolitics", "Geopolitics"),
    ("pop-culture", "Pop Culture"),
    ("world", "World"),
]

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}


@dataclass
class Story:
    slug: str
    section_slug: str
    section_name: str
    title: str
    dek: str
    body_html: str
    source_notes_html: str
    thumbnail_local: str
    thumbnail_alt: str
    published_label: str
    keywords: list[str]
    thumbnail_caption_html: str = ""
    thumbnail_credit_plain: str = ""


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-") or "story"


def now_labels() -> tuple[str, str]:
    now = datetime.now()
    month = now.strftime("%B")
    hour = now.strftime("%I").lstrip("0") or "0"
    minute = now.strftime("%M")
    ampm = now.strftime("%p").lower().replace("am", "a.m.").replace("pm", "p.m.")
    return now.date().isoformat(), f"{month} {now.day}, {now.year} • {hour}:{minute} {ampm}"


def pick_sections(story_count: int) -> list[tuple[str, str]]:
    capped = max(1, min(10, story_count))
    return SECTIONS[:capped]


def extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]

    return json.loads(cleaned)


def sanitize_fragment(fragment: str, fallback: str) -> str:
    raw = (fragment or "").strip()
    if not raw:
        return fallback

    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup.find_all(["script", "style", "iframe", "object", "embed"]):
        tag.decompose()

    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr.lower().startswith("on"):
                del tag.attrs[attr]

    text = str(soup).strip()
    return text or fallback


def normalize_source_notes(fragment: str) -> str:
    cleaned = sanitize_fragment(fragment, "<ol><li>Source notes unavailable.</li></ol>")
    soup = BeautifulSoup(cleaned, "html.parser")

    if soup.find("ol"):
        return str(soup)

    items = soup.find_all("li")
    if items:
        ol = soup.new_tag("ol")
        for item in items:
            ol.append(item)
        return str(ol)

    p = soup.get_text(" ", strip=True)
    if not p:
        return "<ol><li>Source notes unavailable.</li></ol>"
    return f"<ol><li>{html.escape(p)}</li></ol>"


def call_model(client: OpenAI, section_name: str, date_label: str) -> dict[str, Any]:
    prompt = f"""
You are the newsroom engine for The Press.

Write one current, sourced article for the {section_name} desk.

Return JSON only. No markdown fences. Use exactly this shape:
{{
  "title": "string",
  "dek": "string",
  "keywords": ["string", "string", "string"],
  "thumbnail_search_hint": "string",
  "thumbnail_alt": "string",
  "body_html": "<p>...</p><h2>...</h2>...",
  "source_notes_html": "<ol><li><a href='https://example.com'>Source label</a></li></ol>"
}}

Requirements:
- Choose a genuinely current, newsworthy topic for {section_name}.
- body_html should be roughly 900 to 1300 words.
- Use clean HTML with paragraphs and 2 to 4 h2 subheads.
- Do not use markdown.
- Do not mention being an AI, being prompted, or using tools.
- Do not invent sources.
- source_notes_html must be an ordered list with 6 to 10 live https sources.
- Use concise source link labels.
- thumbnail_search_hint should be a short Wikimedia Commons-friendly search phrase.
- Date context: {date_label}
""".strip()

    tool_candidates = [
        os.getenv("OPENAI_WEB_SEARCH_TOOL", "").strip(),
        "web_search",
        "web_search_preview",
    ]
    tool_candidates = [tool for tool in tool_candidates if tool]
    seen_tools: set[str] = set()
    ordered_tools: list[str] = []
    for tool in tool_candidates:
        if tool not in seen_tools:
            seen_tools.add(tool)
            ordered_tools.append(tool)

    last_error: Exception | None = None
    for tool_type in ordered_tools:
        for attempt in range(2):
            try:
                response = client.responses.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
                    tools=[{"type": tool_type}],
                    input=prompt,
                    max_output_tokens=10000,
                )
                payload = extract_json(getattr(response, "output_text", "") or "")
                return payload
            except Exception as exc:  # pragma: no cover - runtime retry path
                last_error = exc
                if attempt == 1:
                    break
                time.sleep(2 * (attempt + 1))

    assert last_error is not None
    raise last_error


def wiki_thumbnail(query: str) -> str | None:
    search_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": 5,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 1200,
        "format": "json",
    }

    try:
        response = requests.get(search_url, params=params, headers=HTTP_HEADERS, timeout=20)
        response.raise_for_status()
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for _, page in pages.items():
            infos = page.get("imageinfo") or []
            if infos:
                info = infos[0]
                return info.get("thumburl") or info.get("url")
    except Exception:
        return None

    return None


def pexels_thumbnail(query: str) -> dict[str, str] | None:
    api_key = os.getenv("PEXELS_API_KEY", "").strip()
    if not api_key or not query.strip():
        return None

    try:
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            timeout=20,
        )
        response.raise_for_status()
        photos = response.json().get("photos", [])
        for photo in photos:
            src = photo.get("src") or {}
            image_url = (
                src.get("landscape")
                or src.get("large")
                or src.get("large2x")
                or src.get("original")
                or src.get("medium")
                or ""
            )
            if not image_url:
                continue

            alt = (photo.get("alt") or query).strip()
            photographer = (photo.get("photographer") or "Pexels photographer").strip()
            photographer_url = (photo.get("photographer_url") or "https://www.pexels.com/").strip()
            photo_page = (photo.get("url") or "https://www.pexels.com/").strip()

            return {
                "url": image_url,
                "alt": alt,
                "credit_plain": f"{alt}. Photo by {photographer} on Pexels.",
                "caption_html": (
                    f"{html.escape(alt)}. "
                    f'<span class="figure-credit">Photo by '
                    f'<a href="{html.escape(photographer_url)}">{html.escape(photographer)}</a> '
                    f'on <a href="{html.escape(photo_page)}">Pexels</a>.</span>'
                ),
            }
    except Exception as exc:  # pragma: no cover - runtime fallback path
        print(f"Pexels search failed for {query}: {exc}")
        return None

    return None


def guess_ext(url: str) -> str:
    path = urlparse(url).path.lower()
    for ext in (".jpeg", ".jpg", ".png", ".webp", ".gif", ".svg"):
        if path.endswith(ext):
            return ext
    return ".jpg"


def write_placeholder_image(page_slug: str) -> str:
    ASSETS_DAILY.mkdir(parents=True, exist_ok=True)
    target = ASSETS_DAILY / f"{page_slug}.svg"
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675" role="img" aria-labelledby="title desc">
  <title id="title">The Press image placeholder</title>
  <desc id="desc">Fallback image used when a remote thumbnail cannot be downloaded.</desc>
  <rect width="1200" height="675" fill="#f4efe8"/>
  <rect x="40" y="40" width="1120" height="595" rx="24" fill="#ffffff" stroke="#d7cdc0" stroke-width="4"/>
  <text x="600" y="290" text-anchor="middle" font-family="Georgia, serif" font-size="64" fill="#111111">The Press</text>
  <text x="600" y="360" text-anchor="middle" font-family="Arial, sans-serif" font-size="32" fill="#444444">Image unavailable</text>
</svg>
"""
    target.write_text(svg, encoding="utf-8")
    return str(target.relative_to(ROOT)).replace("\\", "/")


def download_image(url: str | None, page_slug: str) -> str:
    ASSETS_DAILY.mkdir(parents=True, exist_ok=True)

    if not url or "No_image_available.svg" in url:
        return write_placeholder_image(page_slug)

    ext = guess_ext(url)
    target = ASSETS_DAILY / f"{page_slug}{ext}"

    try:
        response = requests.get(url, headers=HTTP_HEADERS, timeout=30)
        response.raise_for_status()

        content_type = (response.headers.get("Content-Type") or "").lower()
        if "image" not in content_type and "svg" not in content_type:
            raise RuntimeError(f"Unexpected content type: {content_type}")

        target.write_bytes(response.content)
        return str(target.relative_to(ROOT)).replace("\\", "/")
    except Exception as exc:  # pragma: no cover - runtime fallback path
        print(f"Image download failed for {url}: {exc}")
        return write_placeholder_image(page_slug)


def story_word_count(body_html: str) -> int:
    text = BeautifulSoup(body_html, "html.parser").get_text(" ", strip=True)
    return len(text.split())


def build_story_page(story: Story) -> str:
    speaker_js = """
<script>
document.addEventListener('DOMContentLoaded', function () {
  const readBtn = document.querySelector('[data-read-article]');
  const stopBtn = document.querySelector('[data-stop-reading]');
  const body = document.querySelector('[data-article-body]');
  if (!readBtn || !body || !('speechSynthesis' in window)) return;

  readBtn.addEventListener('click', function () {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(body.innerText);
    utterance.rate = 1;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  });

  if (stopBtn) {
    stopBtn.addEventListener('click', function () {
      window.speechSynthesis.cancel();
    });
  }
});
</script>
""".strip()

    title = html.escape(story.title)
    dek = html.escape(story.dek)
    alt = html.escape(story.thumbnail_alt)
    section = html.escape(story.section_name)
    meta = html.escape(f"Written by Intelligent AI • {story.published_label} • {story_word_count(story.body_html)} words")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title} — The Press</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="{dek}" />
  <link rel="stylesheet" href="../styles.css" />
</head>
<body class="page-article">
  <header class="site-header">
    <div class="topbar">
      <div class="topbar__inner">
        <p class="edition-note">Daily issue</p>
        <a class="topbar__link" href="../index.html">Home</a>
      </div>
    </div>
    <div class="masthead-row">
      <div class="masthead-wrap">
        <a class="masthead" href="../index.html">The Press</a>
        <p class="masthead-tagline">A digital newspaper built for sourced long-form reporting.</p>
      </div>
    </div>
  </header>

  <main class="article-layout">
    <article class="article-shell">
      <p class="eyebrow">{section}</p>
      <h1>{title}</h1>
      <p class="article-dek">{dek}</p>
      <p class="article-meta">{meta}</p>

      <div class="button-row button-row--article">
        <button class="button" type="button" data-read-article>🔊 Listen</button>
        <button class="button button--ghost" type="button" data-stop-reading>Stop</button>
      </div>

      <figure class="article-hero">
        <img src="../{story.thumbnail_local}" alt="{alt}" loading="eager" decoding="async" />
        {f'<figcaption class="article-hero__caption">{story.thumbnail_caption_html}</figcaption>' if story.thumbnail_caption_html else ""}
      </figure>

      <div class="article-body" data-article-body>
        {story.body_html}
      </div>

      <section class="article-sources">
        <h2>Source notes</h2>
        {story.source_notes_html}
      </section>
    </article>
  </main>

  {speaker_js}
</body>
</html>
"""


def daily_card(story: Story) -> str:
    url = f"daily/{story.slug}.html"
    title = html.escape(story.title)
    dek = html.escape(story.dek)
    alt = html.escape(story.thumbnail_alt)
    section = html.escape(story.section_name)
    meta = html.escape(f"Written by Intelligent AI • {story.published_label}")

    return f"""
<article class="story-card story-card--daily" data-section="{section}">
  <a class="story-card__image" href="{url}">
    <img src="{story.thumbnail_local}" alt="{alt}" loading="lazy" decoding="async" />
  </a>
  <div class="story-card__body">
    <p class="eyebrow eyebrow--compact">{section} • Daily Issue</p>
    <h3 class="story-card__title"><a href="{url}">{title}</a></h3>
    <p class="story-card__dek">{dek}</p>
    <p class="story-card__meta">{meta}</p>
    <a class="story-card__cta" href="{url}">Read story</a>
  </div>
</article>
""".strip()


def load_or_minimal_html(path: Path, title: str) -> BeautifulSoup:
    if path.exists():
        return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    minimal = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{html.escape(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <main></main>
</body>
</html>
"""
    return BeautifulSoup(minimal, "html.parser")


def first_real_node(fragment: str) -> Any:
    soup = BeautifulSoup(fragment, "html.parser")
    for child in soup.contents:
        if getattr(child, "name", None):
            return child
    return None


def upsert_section(soup: BeautifulSoup, section_id: str, html_fragment: str, after_selector: str | None = None) -> None:
    existing = soup.find(id=section_id)
    new_node = first_real_node(html_fragment)
    if new_node is None:
        return

    if existing is not None:
        existing.replace_with(new_node)
        return

    anchor = soup.select_one(after_selector) if after_selector else None
    if anchor is not None:
        anchor.insert_after(new_node)
        return

    main = soup.find("main")
    if main is not None:
        main.append(new_node)
    elif soup.body is not None:
        soup.body.append(new_node)


def patch_index(stories: list[Story], edition_date: str) -> None:
    path = ROOT / "index.html"
    soup = load_or_minimal_html(path, "The Press — Front Page")
    cards = "\n".join(daily_card(story) for story in stories)

    html_fragment = f"""
<section id="daily-intelligent-ai-feed" class="daily-home-section">
  <div class="section-heading-row">
    <h2 class="section-heading">Today’s {len(stories)} new stories</h2>
    <a class="section-link" href="archive.html">Open archive</a>
  </div>
  <p class="section-standfirst">Fresh reporting added today. Older front-page stories stay in place below and across the archive.</p>
  <div class="cards-grid cards-grid--daily">
    {cards}
  </div>
</section>
""".strip()

    upsert_section(soup, "daily-intelligent-ai-feed", html_fragment, after_selector=".home-grid, .front-page, .lead-package")
    path.write_text(str(soup), encoding="utf-8")


def patch_archive(stories: list[Story], edition_date: str) -> None:
    path = ROOT / "archive.html"
    soup = load_or_minimal_html(path, "Archive — The Press")
    cards = "\n".join(daily_card(story) for story in stories)

    html_fragment = f"""
<section id="daily-archive-latest" class="daily-archive-section">
  <div class="section-heading-row">
    <h2 class="section-heading">Archive update — {html.escape(edition_date)}</h2>
  </div>
  <div class="cards-grid cards-grid--daily">
    {cards}
  </div>
</section>
""".strip()

    upsert_section(soup, "daily-archive-latest", html_fragment, after_selector="header, .archive-hero")
    path.write_text(str(soup), encoding="utf-8")


def patch_breaking(stories: list[Story], edition_date: str) -> None:
    path = ROOT / "breaking-news.html"
    soup = load_or_minimal_html(path, "Breaking News — The Press")

    items: list[str] = []
    for story in stories[:5]:
        section = html.escape(story.section_name)
        title = html.escape(story.title)
        dek = html.escape(story.dek)
        items.append(
            f"""
<li>
  <p class="eyebrow eyebrow--compact">{section}</p>
  <a href="daily/{story.slug}.html">{title}</a>
  <p>{dek}</p>
</li>
""".strip()
        )

    html_fragment = f"""
<section id="breaking-wire-latest" class="breaking-wire-section">
  <div class="section-heading-row">
    <h2 class="section-heading">Worldwide breaking watch — {html.escape(edition_date)}</h2>
  </div>
  <ul class="breaking-wire-list">
    {"".join(items)}
  </ul>
</section>
""".strip()

    upsert_section(soup, "breaking-wire-latest", html_fragment, after_selector="header, .page-hero")
    path.write_text(str(soup), encoding="utf-8")


def update_search_index(stories: list[Story]) -> None:
    path = ROOT / "search-index.json"
    existing: list[dict[str, Any]] = []

    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                existing = loaded
        except Exception:
            existing = []

    new_items = [
        {
            "title": story.title,
            "section": story.section_name,
            "type": "Daily Issue",
            "dek": story.dek,
            "url": f"daily/{story.slug}.html",
            "author": "Intelligent AI",
            "published": story.published_label,
            "keywords": story.keywords,
        }
        for story in stories
    ]

    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    for item in new_items + existing:
        url = str(item.get("url", "")).strip()
        if url and url not in seen:
            seen.add(url)
            merged.append(item)

    path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_latest_json(stories: list[Story], edition_date: str) -> None:
    data = {
        "edition_date": edition_date,
        "articles": [
            {
                "title": story.title,
                "summary": story.dek,
                "url": f"daily/{story.slug}.html",
                "section": story.section_name,
                "image": story.thumbnail_local,
                "image_credit": story.thumbnail_credit_plain,
                "published": story.published_label,
            }
            for story in stories
        ],
    }
    (ROOT / "daily-latest.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_daily_edition_page(stories: list[Story], edition_date: str) -> None:
    items = "\n".join(
        f'<li><a href="daily/{story.slug}.html">{html.escape(story.title)}</a> — {html.escape(story.section_name)}</li>'
        for story in stories
    )

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Latest AI Edition — The Press</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header class="site-header">
    <div class="topbar">
      <div class="topbar__inner">
        <p class="edition-note">Latest AI Edition</p>
        <a class="topbar__link" href="index.html">Home</a>
      </div>
    </div>
    <div class="masthead-row">
      <div class="masthead-wrap">
        <a class="masthead" href="index.html">The Press</a>
        <p class="masthead-tagline">A digital newspaper built for sourced long-form reporting.</p>
      </div>
    </div>
  </header>

  <main class="article-layout">
    <article class="article-shell">
      <p class="eyebrow">Latest AI Edition</p>
      <h1>{html.escape(edition_date)} — {len(stories)} new stories</h1>
      <p class="article-dek">Today’s full set of new stories across the desks included in the daily workflow.</p>
      <p class="article-meta">Written by Intelligent AI</p>
      <ol>
        {items}
      </ol>
    </article>
  </main>
</body>
</html>
"""
    (ROOT / "ai-edition.html").write_text(page, encoding="utf-8")


def patch_bylines_in_js() -> None:
    path = ROOT / "app.js"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""

    start = "/* PRESS_AI_BYLINE_PATCH_START */"
    end = "/* PRESS_AI_BYLINE_PATCH_END */"
    patch = r"""
/* PRESS_AI_BYLINE_PATCH_START */
document.addEventListener("DOMContentLoaded", () => {
  const selectors = [
    ".byline",
    ".story-card__meta",
    ".lead-panel__meta",
    ".link-list__meta",
    ".article-meta"
  ];

  document.querySelectorAll(selectors.join(",")).forEach((el) => {
    const text = (el.textContent || "").trim();
    if (!text) return;

    if (text.startsWith("By ")) {
      el.textContent = text.replace(/^By\s+[^•]+/, "Written by Intelligent AI");
    }
  });
});
/* PRESS_AI_BYLINE_PATCH_END */
""".strip()

    if start in existing and end in existing:
        updated = re.sub(
            re.escape(start) + r".*?" + re.escape(end),
            lambda _: patch,
            existing,
            flags=re.S,
        )
    else:
        updated = existing.rstrip() + ("\n\n" if existing.strip() else "") + patch + "\n"

    path.write_text(updated, encoding="utf-8")


def patch_styles() -> None:
    path = ROOT / "styles.css"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""

    start = "/* PRESS_DAILY_SECTION_START */"
    end = "/* PRESS_DAILY_SECTION_END */"
    patch = """
/* PRESS_DAILY_SECTION_START */
.daily-home-section,
.daily-archive-section,
.breaking-wire-section {
  margin: 2.5rem auto;
}

.cards-grid--daily {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
}

.story-card--daily .story-card__image img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  display: block;
}

.story-card__cta {
  display: inline-block;
  margin-top: 0.8rem;
  font-weight: 700;
}

.breaking-wire-list {
  display: grid;
  gap: 1rem;
  list-style: none;
  padding-left: 0;
}

.breaking-wire-list li {
  background: #fff;
  border: 1px solid #e3d9cc;
  border-radius: 18px;
  padding: 1rem 1.1rem;
}

.article-layout {
  max-width: 920px;
  margin: 0 auto;
  padding: 2rem 1rem 4rem;
}

.article-shell .article-hero img {
  width: 100%;
  display: block;
  border-radius: 18px;
}

.article-shell .article-hero__caption {
  margin-top: 0.7rem;
  color: #5e584f;
  font-size: 0.95rem;
  line-height: 1.5;
}

.article-shell .article-hero__caption a,
.figure-credit a {
  text-decoration: underline;
}

.figure-credit {
  color: #6b645b;
}

.article-sources ol {
  padding-left: 1.25rem;
}

.article-sources a {
  text-decoration: underline;
}

.button-row--article {
  margin: 1rem 0 1.5rem;
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}
/* PRESS_DAILY_SECTION_END */
""".strip()

    if start in existing and end in existing:
        updated = re.sub(
            re.escape(start) + r".*?" + re.escape(end),
            lambda _: patch,
            existing,
            flags=re.S,
        )
    else:
        updated = existing.rstrip() + ("\n\n" if existing.strip() else "") + patch + "\n"

    path.write_text(updated, encoding="utf-8")


def build_story_from_payload(payload: dict[str, Any], section_slug: str, section_name: str, edition_date: str, published_label: str) -> Story:
    title = str(payload.get("title") or f"{section_name} update").strip()
    dek = str(payload.get("dek") or f"A current {section_name.lower()} story from The Press.").strip()
    keywords = [str(item).strip() for item in payload.get("keywords", []) if str(item).strip()][:8]
    body_html = sanitize_fragment(
        str(payload.get("body_html") or ""),
        "<p>Update coming shortly.</p>",
    )
    source_notes_html = normalize_source_notes(str(payload.get("source_notes_html") or ""))
    page_slug = f"{edition_date}-{slugify(title)}"
    thumb_query = str(payload.get("thumbnail_search_hint") or title).strip()
    thumb_alt = str(payload.get("thumbnail_alt") or title).strip()

    thumbnail_url = wiki_thumbnail(thumb_query) or wiki_thumbnail(title)
    thumbnail_caption_html = ""
    thumbnail_credit_plain = ""

    if not thumbnail_url:
        pexels_meta = pexels_thumbnail(thumb_query) or pexels_thumbnail(title)
        if pexels_meta:
            thumbnail_url = pexels_meta.get("url") or ""
            thumb_alt = (pexels_meta.get("alt") or thumb_alt).strip()
            thumbnail_caption_html = pexels_meta.get("caption_html") or ""
            thumbnail_credit_plain = pexels_meta.get("credit_plain") or ""

    thumbnail_local = download_image(thumbnail_url, page_slug)

    return Story(
        slug=page_slug,
        section_slug=section_slug,
        section_name=section_name,
        title=title,
        dek=dek,
        body_html=body_html,
        source_notes_html=source_notes_html,
        thumbnail_local=thumbnail_local,
        thumbnail_alt=thumb_alt,
        published_label=published_label,
        keywords=keywords,
        thumbnail_caption_html=thumbnail_caption_html,
        thumbnail_credit_plain=thumbnail_credit_plain,
    )


def main() -> int:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is missing")

    client = OpenAI(api_key=api_key)
    story_count = int(os.getenv("STORY_COUNT", "10"))
    edition_date, published_label = now_labels()

    ASSETS_DAILY.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    stories: list[Story] = []

    for section_slug, section_name in pick_sections(story_count):
        payload = call_model(client, section_name, published_label)
        story = build_story_from_payload(
            payload=payload,
            section_slug=section_slug,
            section_name=section_name,
            edition_date=edition_date,
            published_label=published_label,
        )
        stories.append(story)

        page_path = DAILY_DIR / f"{story.slug}.html"
        page_path.write_text(build_story_page(story), encoding="utf-8")
        print(f"Wrote {page_path.relative_to(ROOT)}")

    patch_index(stories, edition_date)
    patch_archive(stories, edition_date)
    patch_breaking(stories, edition_date)
    update_search_index(stories)
    write_latest_json(stories, edition_date)
    write_daily_edition_page(stories, edition_date)
    patch_bylines_in_js()
    patch_styles()

    print(f"Generated {len(stories)} stories for {edition_date}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

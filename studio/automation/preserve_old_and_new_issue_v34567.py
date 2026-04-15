#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
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

SECTIONS = [
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

PLACEHOLDER_COPY = "This link will open the full story page."

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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
    thumbnail_url: str
    thumbnail_local: str
    thumbnail_alt: str
    published_label: str
    keywords: list[str]


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
    order = []
    i = 0
    while len(order) < story_count:
        order.append(SECTIONS[i % len(SECTIONS)])
        i += 1
    return order[:story_count]


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)


def call_model(client: OpenAI, section_name: str, date_label: str) -> dict[str, Any]:
    prompt = f"""
You are the newsroom engine for The Press.

Write one current, rich, sourced article for the {section_name} desk.
Return JSON only with this exact shape:
{{
  "title": "string",
  "dek": "string",
  "keywords": ["string","string","string"],
  "thumbnail_search_hint": "string",
  "thumbnail_alt": "string",
  "body_html": "<p>...</p><h2>...</h2>...",
  "source_notes_html": "<ol><li><a href='https://example.com'>Clean source label</a></li></ol>"
}}

Rules:
- Minimum 1500 words.
- No fake author names.
- No references to workflows, PRs, backend, or being prompted.
- Do not show raw long naked URLs in the body. Use crisp link text.
- Body HTML only inside body_html. Use paragraphs and h2s.
- source_notes_html must have 6 to 10 sources with crisp anchor labels.
- Choose a truly current topic for {section_name}.
- Date context: {date_label}
"""
    resp = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
        tools=[{"type": "web_search_preview"}],
        input=prompt,
        max_output_tokens=12000,
    )
    return extract_json(resp.output_text)


def wiki_thumbnail(query: str) -> tuple[str, str]:
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
    r = requests.get(search_url, params=params, headers=HTTP_HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        infos = page.get("imageinfo") or []
        if infos:
            info = infos[0]
            return info.get("thumburl") or info.get("url"), info.get("descriptionurl") or ""
    raise RuntimeError("No Wikimedia Commons image found")


def guess_ext(url: str) -> str:
    path = urlparse(url).path.lower()
    if path.endswith(".jpeg"):
        return ".jpeg"
    if path.endswith(".jpg"):
        return ".jpg"
    if path.endswith(".png"):
        return ".png"
    if path.endswith(".webp"):
        return ".webp"
    if path.endswith(".gif"):
        return ".gif"
    if path.endswith(".svg"):
        return ".svg"
    return ".jpg"


def write_placeholder_image(slug: str, edition_date: str) -> str:
    ASSETS_DAILY.mkdir(parents=True, exist_ok=True)
    target = ASSETS_DAILY / f"{edition_date}-{slug}.svg"
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


def download_image(url: str, slug: str, edition_date: str) -> str:
    ASSETS_DAILY.mkdir(parents=True, exist_ok=True)

    if not url or "No_image_available.svg" in url:
        return write_placeholder_image(slug, edition_date)

    ext = guess_ext(url)
    target = ASSETS_DAILY / f"{edition_date}-{slug}{ext}"

    try:
        r = requests.get(url, headers=HTTP_HEADERS, timeout=30)
        r.raise_for_status()

        content_type = (r.headers.get("Content-Type") or "").lower()
        if "image" not in content_type and "svg" not in content_type:
            raise RuntimeError(f"Unexpected content type: {content_type}")

        target.write_bytes(r.content)
        return str(target.relative_to(ROOT)).replace("\\", "/")
    except Exception as exc:
        print(f"Image download failed for {url}: {exc}")
        return write_placeholder_image(slug, edition_date)
    



def build_story_page(story: Story) -> str:
    speaker_js = """
<script>
document.addEventListener('DOMContentLoaded', function () {
  const btn = document.querySelector('[data-read-article]');
  const stop = document.querySelector('[data-stop-reading]');
  const body = document.querySelector('[data-article-body]');
  if (!btn || !body || !('speechSynthesis' in window)) return;
  btn.addEventListener('click', () => {
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(body.innerText);
    utter.rate = 1;
    utter.pitch = 1;
    window.speechSynthesis.speak(utter);
  });
  if (stop) stop.addEventListener('click', () => window.speechSynthesis.cancel());
});
</script>
"""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{story.title} — The Press</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="{story.dek}" />
  <link rel="stylesheet" href="../styles.css" />
</head>
<body class="page-article">
  <header class="site-header">
    <div class="topbar"><div class="topbar__inner"><p class="edition-note">Daily issue</p><a class="topbar__link" href="../index.html">Home</a></div></div>
    <div class="masthead-row"><div class="masthead-wrap"><a class="masthead" href="../index.html">The Press</a><p class="masthead-tagline">A digital newspaper built for sourced long-form reporting.</p></div></div>
  </header>
  <main class="article-layout">
    <article class="article-shell">
      <p class="eyebrow">{story.section_name}</p>
      <h1>{story.title}</h1>
      <p class="article-dek">{story.dek}</p>
      <p class="article-meta">Written by Intelligent AI • {story.published_label}</p>
      <div class="button-row button-row--article"><button class="button" type="button" data-read-article>🔊 Listen</button><button class="button button--ghost" type="button" data-stop-reading>Stop</button></div>
      <figure class="article-hero">
        <img src="../{story.thumbnail_local}" alt="{story.thumbnail_alt}" loading="eager" decoding="async" />
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
    return f"""
<article class="story-card story-card--daily" data-section="{story.section_name}">
  <a class="story-card__image" href="{url}">
    <img src="{story.thumbnail_local}" alt="{story.thumbnail_alt}" loading="lazy" decoding="async" />
  </a>
  <div class="story-card__body">
    <p class="eyebrow eyebrow--compact">{story.section_name} • Daily Issue</p>
    <h3 class="story-card__title"><a href="{url}">{story.title}</a></h3>
    <p class="story-card__dek">{story.dek}</p>
    <p class="story-card__meta">Written by Intelligent AI • {story.published_label}</p>
    <a class="story-card__cta" href="{url}">Read story</a>
  </div>
</article>
""".strip()


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
    el.textContent = text.replace(/^By\s+[^•]+/, "Written by Intelligent AI");
  });
});
/* PRESS_AI_BYLINE_PATCH_END */
""".strip()
    if start in existing and end in existing:
        existing = re.sub(re.escape(start) + r".*?" + re.escape(end), patch, existing, flags=re.S)
    else:
        existing = existing.rstrip() + "\n\n" + patch + "\n"
    path.write_text(existing, encoding="utf-8")


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
.daily-home-section .cards-grid--daily,
.daily-archive-section .cards-grid--daily {
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
  margin-top: .8rem;
  font-weight: 700;
}
.breaking-wire-list {
  display: grid;
  gap: 1rem;
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
.article-sources ol {
  padding-left: 1.25rem;
}
.article-sources a {
  text-decoration: underline;
}
.button-row--article {
  margin: 1rem 0 1.5rem;
}
/* PRESS_DAILY_SECTION_END */
""".strip()
    if start in existing and end in existing:
        existing = re.sub(re.escape(start) + r".*?" + re.escape(end), patch, existing, flags=re.S)
    else:
        existing = existing.rstrip() + "\n\n" + patch + "\n"
    path.write_text(existing, encoding="utf-8")


def upsert_section(soup: BeautifulSoup, section_id: str, html_fragment: str, after_selector: str | None = None) -> None:
    old = soup.find(id=section_id)
    new_node = BeautifulSoup(html_fragment, "html.parser")
    top = next((child for child in new_node.contents if getattr(child, "name", None)), None)
    if old and top:
        old.replace_with(top)
        return
    anchor = soup.select_one(after_selector) if after_selector else None
    if anchor and top:
        anchor.insert_after(top)
        return
    main = soup.find("main")
    if main and top:
        main.append(top)
    elif soup.body and top:
        soup.body.append(top)


def patch_index(stories: list[Story], edition_date: str) -> None:
    path = ROOT / "index.html"
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
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
"""
    upsert_section(soup, "daily-intelligent-ai-feed", html_fragment, after_selector=".home-grid, .front-page, .lead-package")
    path.write_text(str(soup), encoding="utf-8")


def patch_archive(stories: list[Story], edition_date: str) -> None:
    path = ROOT / "archive.html"
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    cards = "\n".join(daily_card(story) for story in stories)
    html_fragment = f"""
<section id="daily-archive-latest" class="daily-archive-section">
  <div class="section-heading-row">
    <h2 class="section-heading">Archive update — {edition_date}</h2>
  </div>
  <div class="cards-grid cards-grid--daily">
    {cards}
  </div>
</section>
"""
    upsert_section(soup, "daily-archive-latest", html_fragment, after_selector="header, .archive-hero")
    path.write_text(str(soup), encoding="utf-8")


def patch_breaking(stories: list[Story], edition_date: str) -> None:
    path = ROOT / "breaking-news.html"
    if not path.exists():
        path.write_text(
            "<!doctype html><html><head><meta charset='utf-8'><title>Breaking News — The Press</title><link rel='stylesheet' href='styles.css'></head><body><main></main></body></html>",
            encoding="utf-8",
        )
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    items = []
    for story in stories[:5]:
        items.append(
            f"<li><p class='eyebrow eyebrow--compact'>{story.section_name}</p><a href='daily/{story.slug}.html'>{story.title}</a><p>{story.dek}</p></li>"
        )
    html_fragment = f"""
<section id="breaking-wire-latest" class="breaking-wire-section">
  <div class="section-heading-row"><h2 class="section-heading">Worldwide breaking watch — {edition_date}</h2></div>
  <ul class="breaking-wire-list">
    {''.join(items)}
  </ul>
</section>
"""
    upsert_section(soup, "breaking-wire-latest", html_fragment, after_selector="header, .page-hero")
    path.write_text(str(soup), encoding="utf-8")


def update_search_index(stories: list[Story]) -> None:
    path = ROOT / "search-index.json"
    existing = []
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    new_items = [
        {
            "title": s.title,
            "section": s.section_name,
            "type": "Daily Issue",
            "dek": s.dek,
            "url": f"daily/{s.slug}.html",
            "author": "Intelligent AI",
            "published": s.published_label,
            "keywords": s.keywords,
        }
        for s in stories
    ]
    seen = set()
    merged = []
    for item in new_items + existing:
        key = item.get("url")
        if key and key not in seen:
            seen.add(key)
            merged.append(item)
    path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_latest_json(stories: list[Story], edition_date: str) -> None:
    data = {
        "edition_date": edition_date,
        "articles": [
            {
                "title": s.title,
                "summary": s.dek,
                "url": f"daily/{s.slug}.html",
                "section": s.section_name,
                "image": s.thumbnail_local,
                "published": s.published_label,
            }
            for s in stories
        ],
    }
    (ROOT / "daily-latest.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_daily_edition_page(stories: list[Story], edition_date: str) -> None:
    items = "\n".join(f"<li><a href='daily/{s.slug}.html'>{s.title}</a> — {s.section_name}</li>" for s in stories)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Latest AI Edition — The Press</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="stylesheet" href="styles.css" />
</head>
<body>
<header class="site-header">
  <div class="topbar"><div class="topbar__inner"><p class="edition-note">Latest AI Edition</p><a class="topbar__link" href="index.html">Home</a></div></div>
  <div class="masthead-row"><div class="masthead-wrap"><a class="masthead" href="index.html">The Press</a><p class="masthead-tagline">A digital newspaper built for sourced long-form reporting.</p></div></div>
</header>
<main class="article-layout">
  <article class="article-shell">
    <p class="eyebrow">Latest AI Edition</p>
    <h1>{edition_date} — {len(stories)} new stories</h1>
    <p class="article-dek">Today’s full set of new stories across politics, economics, science, film, AI, technology, niche topics, geopolitics, pop culture, and world coverage.</p>
    <p class="article-meta">Written by Intelligent AI</p>
    <ol>{items}</ol>
  </article>
</main>
</body>
</html>
"""
    (ROOT / "ai-edition.html").write_text(html, encoding="utf-8")


def main() -> int:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY is missing")
    client = OpenAI(api_key=key)
    story_count = max(1, min(10, int(os.getenv("STORY_COUNT", "10"))))
    edition_date, published_label = now_labels()
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    stories: list[Story] = []
    for section_slug, section_name in pick_sections(story_count):
        payload = call_model(client, section_name, published_label)
        title = payload["title"].strip()
        slug = f"{edition_date}-{slugify(title)}"
        try:
            thumb_url, _ = wiki_thumbnail(payload.get("thumbnail_search_hint") or title)
        except Exception:
            thumb_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1200px-No_image_available.svg.png"
        local_thumb = download_image(thumb_url, slug, edition_date)
        story = Story(
            slug=slug,
            section_slug=section_slug,
            section_name=section_name,
            title=title,
            dek=payload["dek"].strip(),
            body_html=payload["body_html"].strip(),
            source_notes_html=payload["source_notes_html"].strip(),
            thumbnail_url=thumb_url,
            thumbnail_local=local_thumb,
            thumbnail_alt=payload.get("thumbnail_alt", title).strip(),
            published_label=published_label,
            keywords=[str(k) for k in payload.get("keywords", [])][:8],
        )
        stories.append(story)
        (DAILY_DIR / f"{story.slug}.html").write_text(build_story_page(story), encoding="utf-8")

    patch_index(stories, edition_date)
    patch_archive(stories, edition_date)
    patch_breaking(stories, edition_date)
    update_search_index(stories)
    write_latest_json(stories, edition_date)
    write_daily_edition_page(stories, edition_date)
    patch_bylines_in_js()
    patch_styles()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

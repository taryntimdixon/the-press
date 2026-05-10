#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import datetime
from email.utils import format_datetime
import html
import json
import math
import os
import re

SITE_DIR = Path(__file__).resolve().parent
STUDIO_DIR = SITE_DIR / "studio"
DATA_DIR = STUDIO_DIR if (STUDIO_DIR / "master-edition.json").exists() else SITE_DIR
DATA = json.loads((DATA_DIR / "master-edition.json").read_text(encoding="utf-8"))

SITE = DATA["site"]
SECTIONS = DATA["sections"]
AUTHORS = DATA["authors"]
STORIES = sorted(DATA["stories"], key=lambda item: item["publishedIso"], reverse=True)
SECTION_BY_SLUG = {section["slug"]: section for section in SECTIONS}
AUTHOR_BY_SLUG = {author["slug"]: author for author in AUTHORS}
STORY_BY_FILE = {story["filename"]: story for story in STORIES}
HOME_HERO_TARGET = int(DATA.get("homepage", {}).get("heroSlots", 7) or 7)
HOME_HERO_AUTO_SEED = min(2, HOME_HERO_TARGET)


def parse_iso_datetime(value: object) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def latest_story_datetime() -> datetime:
    dates = [
        parsed
        for story in STORIES
        for key in ("updatedIso", "publishedIso")
        if (parsed := parse_iso_datetime(story.get(key)))
    ]
    return max(dates) if dates else datetime.now().astimezone()


BUILD_REFERENCE_DT = latest_story_datetime()
try:
  STYLESHEET_VERSION = str(int((SITE_DIR / "styles.css").stat().st_mtime))
except OSError:
  STYLESHEET_VERSION = "1"
try:
  APP_VERSION = str(int((SITE_DIR / "app.js").stat().st_mtime))
except OSError:
  APP_VERSION = "1"


def asset_version(rel_path: str) -> str:
    try:
        return str(int((SITE_DIR / rel_path).stat().st_mtime))
    except OSError:
        return "1"


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"", "0", "false", "no", "off"}


def h(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def json_script(data: object) -> str:
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def absolute_url(path: str) -> str:
    return SITE["baseUrl"].rstrip("/") + "/" + path.lstrip("/")


def preferred_image_path(image_path: str) -> str:
  rel = Path(image_path)
  if not image_path:
    return image_path
  if rel.is_absolute():
    return image_path
  source = SITE_DIR / rel
  if not source.exists():
    return image_path

  # Prefer lossless/local higher-fidelity variants if they exist for the same stem.
  preferred_exts = (".png", ".webp", ".jpg", ".jpeg", ".avif")
  stem = source.with_suffix("")
  for ext in preferred_exts:
    candidate = stem.with_suffix(ext)
    if candidate.exists():
      return str(rel.with_suffix(ext))
  return image_path


def story_has_hero_image(story: dict) -> bool:
    return bool(story.get("image") and story.get("filename"))


def story_is_hero_eligible(story: dict) -> bool:
    return story.get("heroEligible", True) is not False and story_has_hero_image(story)


def add_unique_story(target: list[dict], seen: set[str], story: dict | None) -> None:
    if not story:
        return
    filename = str(story.get("filename") or "")
    if not filename or filename in seen:
        return
    seen.add(filename)
    target.append(story)


def homepage_lead_stories() -> list[dict]:
    """Build the reusable hero set.

    The newest image-ready stories seed the hero first so a freshly published
    article does not require hand-editing homepage lead lists just to appear.
    Manual leadOrder entries still shape the rest of the rotation.
    """

    final: list[dict] = []
    seen: set[str] = set()
    homepage = DATA.get("homepage", {})

    for story in [story for story in STORIES if story_is_hero_eligible(story)][:HOME_HERO_AUTO_SEED]:
        add_unique_story(final, seen, story)

    for filename in homepage.get("leadOrder", []):
        add_unique_story(final, seen, STORY_BY_FILE.get(filename))

    for story in [story for story in STORIES if story_is_hero_eligible(story)]:
        add_unique_story(final, seen, story)

    for story in STORIES:
        add_unique_story(final, seen, story)

    return final[:HOME_HERO_TARGET]


def homepage_recency_stories(hero_stories: list[dict], limit: int = 15) -> list[dict]:
    hero_files = {str(story.get("filename") or "") for story in hero_stories}
    final: list[dict] = []
    seen: set[str] = set(hero_files)

    for story in homepage_recency_pool():
        add_unique_story(final, seen, story)
        if len(final) >= limit:
            break

    return final


def homepage_recency_pool() -> list[dict]:
    index_path = SITE_DIR / "content-index.json"
    if not index_path.exists():
        return STORIES

    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return STORIES

    index_stories = payload.get("stories")
    if not isinstance(index_stories, list):
        return STORIES

    pool: list[dict] = []
    seen: set[str] = set()
    for item in index_stories:
        if not isinstance(item, dict):
            continue
        filename = str(item.get("filename") or item.get("url") or "")
        if not filename or filename in seen:
            continue
        seen.add(filename)
        canonical = STORY_BY_FILE.get(filename)
        if canonical:
            pool.append(canonical)
            continue
        pool.append({
            "filename": filename,
            "title": item.get("title") or "Untitled story",
            "section": item.get("section") or "News",
            "type": item.get("type") or "Story",
            "publishedLabel": item.get("published") or item.get("publishedLabel") or "Recently published",
            "image": item.get("image") or "",
            "imageAlt": item.get("imageAlt") or item.get("title") or "Story thumbnail",
        })

    return pool or STORIES


def initials(name: str) -> str:
    parts = [part for part in name.split() if part]
    return "".join(part[0] for part in parts[:2]).upper() or "TP"


def strip_generated_body_extras(fragment: str) -> str:
  markers = (
    '<section id="related-stories"',
    '<section class="related-block"',
    '<section class="ai-article-gallery"',
    '<section class="social-embed-panel',
  )
  end = len(fragment)
  for marker in markers:
    idx = fragment.find(marker)
    if idx != -1:
      end = min(end, idx)
  return fragment[:end].strip()


def extract_story_fragment(page_html: str, rel_path: str) -> str:
  if "content/asides/" in rel_path:
    pattern = re.compile(
      r'<aside class="article-aside">\s*<div class="sticky-stack">\s*(?P<content>.*?)\s*</div>\s*</aside>',
      re.S,
    )
  elif "content/bodies/" in rel_path:
    pattern = re.compile(
      r'<div class="article-body">\s*(?P<content>.*?)\s*</div>\s*</div>\s*</article>',
      re.S,
    )
  else:
    raise FileNotFoundError(rel_path)

  match = pattern.search(page_html)
  if not match:
    raise FileNotFoundError(rel_path)
  content = match.group("content").strip()
  if "content/bodies/" in rel_path:
    return strip_generated_body_extras(content)
  return content


def read_fragment(rel_path: str) -> str:
  fragment_path = DATA_DIR / rel_path
  if fragment_path.exists():
    return fragment_path.read_text(encoding="utf-8")

  fallback_page = SITE_DIR / Path(rel_path).name
  if fallback_page.exists():
    page_html = fallback_page.read_text(encoding="utf-8")
    return extract_story_fragment(page_html, rel_path)

  return fragment_path.read_text(encoding="utf-8")


def search_index_row(story: dict) -> dict:
    return {
        "title": story["title"],
        "section": story["section"],
        "type": story["type"],
        "dek": story["dek"],
        "url": story["filename"],
        "author": story["author"],
        "published": story["publishedLabel"],
        "publishedIso": story.get("publishedIso", ""),
        "updatedIso": story.get("updatedIso", ""),
        "image": story.get("image", ""),
        "imageAlt": story.get("imageAlt") or story.get("title") or "Story thumbnail",
        "imageWidth": story.get("imageWidth"),
        "imageHeight": story.get("imageHeight"),
        "keywords": story.get("keywords", []),
    }


def normalize_search_item(item: dict) -> dict:
    row = dict(item)
    row["title"] = item.get("title") or item.get("headline") or ""
    row["section"] = item.get("section") or "News"
    row["type"] = item.get("type") or "Report"
    row["dek"] = item.get("dek") or item.get("summary") or ""
    row["url"] = item.get("url") or item.get("filename") or "#"
    row["author"] = item.get("author") or "Intelligent AI"
    row["published"] = item.get("published") or item.get("publishedLabel") or ""
    row["publishedIso"] = item.get("publishedIso") or item.get("published_iso") or ""
    row["updatedIso"] = item.get("updatedIso") or item.get("updated_iso") or ""
    row["image"] = item.get("image") or item.get("imageUrl") or item.get("image_url") or item.get("thumbnail") or ""
    row["imageAlt"] = item.get("imageAlt") or item.get("image_alt") or item.get("alt") or row["title"] or "Story thumbnail"
    row["imageWidth"] = item.get("imageWidth") or item.get("image_width")
    row["imageHeight"] = item.get("imageHeight") or item.get("image_height")
    row["keywords"] = item.get("keywords") if isinstance(item.get("keywords"), list) else []
    return row


def thumbnail_source_index() -> list[dict]:
    rows: list[dict] = []
    candidates = []
    for filename in ("live-index.json", "content-index.json", "edition.json"):
        for base in (DATA_DIR, SITE_DIR):
            path = base / filename
            if path not in candidates and path.exists():
                candidates.append(path)

    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        items = payload.get("stories") if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            items = payload.get("articles") if isinstance(payload, dict) else []
        if not isinstance(items, list):
            continue
        rows.extend(normalize_search_item(item) for item in items if isinstance(item, dict))

    return [row for row in rows if row["title"] and row["url"] != "#"]


def merge_search_row(primary: dict, fallback: dict) -> dict:
    merged = {**fallback, **primary}
    for field in ("image", "imageAlt", "imageWidth", "imageHeight", "publishedIso", "updatedIso", "keywords"):
        if fallback.get(field):
            merged[field] = fallback[field]
    return merged


def richer_existing_search_index() -> list[dict]:
    candidates = []
    for filename in ("search-index.json", "content-index.json"):
        for base in (DATA_DIR, SITE_DIR):
            path = base / filename
            if path not in candidates and path.exists():
                candidates.append(path)

    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rows = payload.get("stories") if isinstance(payload, dict) else payload
        if not isinstance(rows, list) or len(rows) <= len(STORIES):
            continue
        normalized = [normalize_search_item(item) for item in rows if isinstance(item, dict)]
        normalized = [item for item in normalized if item["title"] and item["url"] != "#"]
        if normalized:
            return normalized
    return []


def gallery_story_rows() -> list[dict]:
    rows: list[dict] = []

    for story in STORIES:
        image = str(story.get("image") or "")
        filename = str(story.get("filename") or "")
        if not image or not filename:
            continue
        rows.append(
            {
                "filename": filename,
                "image": preferred_image_path(image),
                "imageAlt": str(story.get("imageAlt") or story.get("title") or "Story thumbnail"),
                "title": str(story.get("title") or "Story"),
                "section": str(story.get("section") or "News"),
                "type": str(story.get("type") or "Report"),
                "publishedIso": str(story.get("publishedIso") or ""),
                "updatedIso": str(story.get("updatedIso") or ""),
                "imageWidth": story.get("imageWidth"),
                "imageHeight": story.get("imageHeight"),
            }
        )

    candidates = []
    for filename in ("content-index.json", "search-index.json"):
        for base in (DATA_DIR, SITE_DIR):
            path = base / filename
            if path not in candidates and path.exists():
                candidates.append(path)

    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        items = payload.get("stories") if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue
            filename = item.get("url") or item.get("filename")
            image = item.get("image") or ""
            if not filename or not image:
                continue
            if not (SITE_DIR / str(filename)).exists():
                continue
            rows.append(
                {
                    "filename": str(filename),
                    "image": preferred_image_path(str(image)),
                    "imageAlt": str(item.get("image_alt") or item.get("imageAlt") or item.get("title") or "Story thumbnail"),
                    "title": str(item.get("title") or "Story"),
                    "section": str(item.get("section") or "News"),
                    "type": str(item.get("type") or "Report"),
                    "publishedIso": str(item.get("published_iso") or item.get("publishedIso") or ""),
                    "updatedIso": str(item.get("updated_iso") or item.get("updatedIso") or ""),
                    "imageWidth": item.get("imageWidth") or item.get("image_width"),
                    "imageHeight": item.get("imageHeight") or item.get("image_height"),
                }
            )

    # Keep one entry per article URL and preserve the newest thumbnail-backed stories first.
    unique_rows: dict[str, dict] = {}
    for row in rows:
        unique_rows.setdefault(row["filename"], row)

    def sort_key(item: dict) -> datetime:
        return (
            parse_iso_datetime(item.get("publishedIso"))
            or parse_iso_datetime(item.get("updatedIso"))
            or datetime.min
        )

    return sorted(unique_rows.values(), key=sort_key, reverse=True)


def search_index() -> list[dict]:
    master_items = [search_index_row(story) for story in STORIES]
    existing_items = richer_existing_search_index()
    if not existing_items:
        return master_items

    merged = {item["url"]: item for item in existing_items}
    for item in thumbnail_source_index() + master_items:
        if item["url"] in merged:
            merged[item["url"]] = merge_search_row(merged[item["url"]], item)
        else:
            merged[item["url"]] = item
    return list(merged.values())


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
    <p class="story-card__meta">Written and Researched by AI • {h(story['publishedLabel'])}</p>
  </div>
</article>
""".strip()


def recency_ticker_item(story: dict, duplicate: bool = False) -> str:
    tab_attr = ' tabindex="-1"' if duplicate else ""
    media_html = (
        f"""
  <span class="home-recency-card__media">
    <img src="{h(story.get('image'))}" alt="{h(story.get('imageAlt') or story.get('title') or 'Story thumbnail')}" loading="lazy" decoding="async"{f' width="{story["imageWidth"]}"' if story.get("imageWidth") else ''}{f' height="{story["imageHeight"]}"' if story.get("imageHeight") else ''} />
  </span>
""".rstrip()
        if story.get("image")
        else '  <span class="home-recency-card__media home-recency-card__media--empty"></span>'
    )
    return f"""
<a class="home-recency-card" href="{h(story.get('filename'))}" aria-label="{h(story.get('title'))}"{tab_attr}>
{media_html}
  <span class="home-recency-card__body">
    <span class="home-recency-card__kicker">{h(story.get('section'))} • {h(story.get('type'))}</span>
    <strong>{h(story.get('title'))}</strong>
    <span class="home-recency-card__meta">{h(story.get('publishedLabel'))}</span>
  </span>
</a>
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
    <p class="river-item__meta">Written and Researched by AI • {h(story['publishedLabel'])}</p>
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
    <p class="link-list__meta">Written and Researched by AI • {h(story['publishedLabel'])}</p>
  </div>
</li>
""".strip()


def simple_list_item(story: dict) -> str:
    return f"""
<li class="link-list__item">
  <div>
    <p class="eyebrow eyebrow--tiny">{h(story['section'])} • {h(story['type'])}</p>
    <a href="{h(story['filename'])}">{h(story['title'])}</a>
    <p class="link-list__meta">Written and Researched by AI • {h(story['publishedLabel'])}</p>
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



def social_embed_platform_label(platform: str) -> str:
    value = (platform or "").strip().lower()
    labels = {
        "x": "X",
        "twitter": "X",
        "bluesky": "Bluesky",
        "bsky": "Bluesky",
        "threads": "Threads",
        "instagram": "Instagram",
        "ig": "Instagram",
        "tiktok": "TikTok",
        "linkedin": "LinkedIn",
        "facebook": "Facebook",
        "fb": "Facebook",
        "youtube": "YouTube",
    }
    return labels.get(value, platform.strip().title() if platform else "Social")


def social_embed_placement_matches(post: dict, placement: str) -> bool:
    raw = str(post.get("placement") or "both").strip().lower()
    aliases = {
        "side": "rail",
        "sidebar": "rail",
        "rail": "rail",
        "right": "rail",
        "bottom": "bottom",
        "footer": "bottom",
        "end": "bottom",
        "both": "both",
        "all": "both",
    }
    normalized = aliases.get(raw, raw)
    if placement == "rail":
        return normalized in {"rail", "both"}
    if placement == "bottom":
        return normalized in {"bottom", "both"}
    return True


def social_embed_scripts(posts: list[dict]) -> str:
    needs_x = False
    needs_bluesky = False
    needs_tiktok = False

    for post in posts:
        platform = str(post.get("platform") or "").lower()
        url = str(post.get("url") or "").lower()
        embed_html = str(post.get("embedHtml") or post.get("html") or "")
        embed_lower = embed_html.lower()

        # X URL-only cards are converted to a real tweet embed below, so load the widget.
        if platform in {"x", "twitter"} or "twitter-tweet" in embed_lower:
            if "platform.twitter.com/widgets.js" not in embed_lower:
                needs_x = True
        # Other platforms load widgets only when the editor supplies actual embed HTML.
        if (embed_html and platform in {"bluesky", "bsky"}) or "bluesky-embed" in embed_lower:
            if "embed.bsky.app/static/embed.js" not in embed_lower:
                needs_bluesky = True
        if (embed_html and platform == "tiktok") or "tiktok-embed" in embed_lower:
            if "tiktok.com/embed.js" not in embed_lower:
                needs_tiktok = True

    scripts = []
    if needs_x:
        scripts.append('<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>')
    if needs_bluesky:
        scripts.append('<script async src="https://embed.bsky.app/static/embed.js" charset="utf-8"></script>')
    if needs_tiktok:
        scripts.append('<script async src="https://www.tiktok.com/embed.js"></script>')
    return "\n".join(scripts)


def social_embed_card(post: dict) -> str:
    platform_raw = str(post.get("platform") or "").strip()
    platform = social_embed_platform_label(platform_raw)
    platform_key = platform_raw.lower()
    label = str(post.get("label") or post.get("title") or "Public conversation").strip()
    author = str(post.get("author") or "").strip()
    handle = str(post.get("handle") or "").strip()
    date = str(post.get("date") or "").strip()
    url = str(post.get("url") or "").strip()
    note = str(post.get("note") or post.get("dek") or post.get("summary") or "").strip()
    embed_html = str(post.get("embedHtml") or post.get("html") or "").strip()

    meta_bits = [bit for bit in [author, handle, date] if bit]
    meta_html = f'<p class="social-embed-card__meta">{h(" • ".join(meta_bits))}</p>' if meta_bits else ""
    note_html = f'<p class="social-embed-card__note">{h(note)}</p>' if note else ""
    link_html = f'<a class="social-embed-card__link" href="{h(url)}" target="_blank" rel="noopener noreferrer">View original post</a>' if url else ""

    if embed_html:
        body_html = f'<div class="social-embed-card__embed">{embed_html}</div>'
    elif url and platform_key in {"x", "twitter"}:
        body_html = f'<div class="social-embed-card__embed"><blockquote class="twitter-tweet" data-dnt="true"><a href="{h(url)}"></a></blockquote></div>'
    else:
        body_html = f"""
        <div class="social-embed-card__fallback">
            {note_html}
            {link_html}
        </div>
        """.strip()

    return f"""
<article class="social-embed-card">
    <div class="social-embed-card__label-row">
        <span class="social-embed-card__platform">{h(platform)}</span>
        <span class="social-embed-card__label">{h(label)}</span>
    </div>
    {meta_html}
    {body_html}
</article>
""".strip()


def social_embeds_block(story: dict, placement: str = "rail") -> str:
    posts = story.get("socialEmbeds") or story.get("socialPosts") or []
    if not isinstance(posts, list):
        return ""

    selected = [post for post in posts if isinstance(post, dict) and social_embed_placement_matches(post, placement)]
    if not selected:
        return ""

    selected = selected[:6]
    title = story.get("socialEmbedsTitle") or "Public conversation"
    intro = story.get("socialEmbedsIntro") or "Curated posts selected for context. Inclusion is not endorsement."
    modifier = "social-embed-panel--rail" if placement == "rail" else "social-embed-panel--bottom"
    cards_html = "\n".join(social_embed_card(post) for post in selected)
    scripts_html = social_embed_scripts(selected)

    return f"""
<section class="social-embed-panel {modifier}" aria-label="{h(title)}">
    <p class="social-embed-panel__eyebrow">Social context</p>
    <h2 class="social-embed-panel__title">{h(title)}</h2>
    <p class="social-embed-panel__intro">{h(intro)}</p>
    <div class="social-post-stack">
        {cards_html}
    </div>
</section>
{scripts_html}
""".strip()

def header(current_section: str = "", current_aux: str = "") -> str:
    utility_links = []
    for link in SITE.get("mastheadLinks", []):
        current = ' aria-current="page"' if current_aux == link["href"] else ""
        utility_links.append(f'<a class="utility-link" href="{h(link["href"])}"{current}>{h(link["label"])}</a>')
    return f"""
<header class="site-header" data-site-header>
  <div class="masthead-row">
    <div class="masthead-wrap">
      <a class="masthead masthead-with-logo" href="index.html" aria-label="The Press home"><img class="masthead-logo" src="assets/the-press-logo.svg" alt="The Press logo" decoding="async" /></a>
    </div>
    <div class="masthead-actions">
      <nav class="utility-nav" aria-label="Utility navigation">
        {' '.join(utility_links)}
      </nav>
      <div class="header-controls">
        <button aria-label="Toggle dark mode" class="theme-toggle" data-theme-toggle title="Toggle dark/light mode" type="button">☀︎</button>
        <button class="search-trigger" type="button" data-search-open>Search</button>
      </div>
    </div>
    <div class="masthead-ticker" aria-label="Latest headlines">
      <div class="masthead-ticker__items" data-masthead-ticker></div>
    </div>
  </div>
</header>
""".strip()


def footer() -> str:
    newsroom_links = """
<li><a href="archive.html">Archive</a></li>
<li><a href="gallery.html">Gallery</a></li>
<li><a href="authors.html">AI Newsroom</a></li>
<li><a href="about.html">About</a></li>
<li><a href="photo-workflow.html">Photo workflow</a></li>
""".strip()
    return f"""
<footer class="site-footer">
  <div class="footer-grid footer-grid--archive-only">
    <section class="footer-brand">
      <a class="masthead masthead--footer" href="index.html">{h(SITE['name'])}</a>
      <p class="footer-copy">{h(SITE['tagline'])}</p>
      <p class="footer-copy footer-copy--small">Visible AI use and visible source notes.</p>
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


def social_meta(
    title: str,
    description: str,
    canonical: str,
    image: str = "",
    image_alt: str = "",
    image_width: object = "",
    image_height: object = "",
    og_type: str = "website",
) -> str:
    canonical_url = absolute_url(canonical)
    image_url = absolute_url(image or "assets/icon-512.png")
    image_ext = Path(str(image or "assets/icon-512.png")).suffix.lower().lstrip(".")
    image_type = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "avif": "image/avif",
        "svg": "image/svg+xml",
    }.get(image_ext)
    card_type = "summary_large_image" if image else "summary"
    lines = [
        f'<meta property="og:type" content="{h(og_type)}" />',
        f'<meta property="og:site_name" content="{h(SITE["name"])}" />',
        f'<meta property="og:title" content="{h(title)}" />',
        f'<meta property="og:description" content="{h(description)}" />',
        f'<meta property="og:url" content="{h(canonical_url)}" />',
        f'<meta property="og:image" content="{h(image_url)}" />',
        f'<meta property="og:image:secure_url" content="{h(image_url)}" />',
        f'<meta name="twitter:card" content="{h(card_type)}" />',
        f'<meta name="twitter:url" content="{h(canonical_url)}" />',
        f'<meta name="twitter:title" content="{h(title)}" />',
        f'<meta name="twitter:description" content="{h(description)}" />',
        f'<meta name="twitter:image" content="{h(image_url)}" />',
    ]
    if image_type:
        lines.append(f'<meta property="og:image:type" content="{h(image_type)}" />')
    if image_alt:
        lines.extend([
            f'<meta property="og:image:alt" content="{h(image_alt)}" />',
            f'<meta name="twitter:image:alt" content="{h(image_alt)}" />',
        ])
    if image_width:
        lines.append(f'<meta property="og:image:width" content="{h(image_width)}" />')
    if image_height:
        lines.append(f'<meta property="og:image:height" content="{h(image_height)}" />')
    return "\n".join(lines)


def page_head(
    title: str,
    description: str,
    canonical: str,
    jsonld: str = "",
    extra_links: str = "",
    social_image: str = "",
    social_image_alt: str = "",
    social_image_width: object = "",
    social_image_height: object = "",
    og_type: str = "website",
    social_title: str = "",
) -> str:
    canonical_url = absolute_url(canonical)
    social = social_meta(
        social_title or title,
        description,
        canonical,
        image=social_image,
        image_alt=social_image_alt,
        image_width=social_image_width,
        image_height=social_image_height,
        og_type=og_type,
    )
    head_extras = "\n".join(
        "\n".join(f"  {line}" for line in block.splitlines())
        for block in (social, jsonld, extra_links)
        if block
    )
    extras_html = f"\n{head_extras}" if head_extras else ""
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
  <link rel="stylesheet" href="styles.css?v={h(STYLESHEET_VERSION)}" />
  <link rel="manifest" href="site.webmanifest" />
  <link rel="alternate" type="application/rss+xml" title="{h(SITE['name'])} feed" href="feed.xml" />{extras_html}
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
        },
    }
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'


def layout(
    title: str,
    description: str,
    canonical: str,
    body_class: str,
    main_html: str,
    current_section: str = "",
    current_aux: str = "",
    jsonld: str = "",
    include_progress: bool = False,
    extra_links: str = "",
    extra_scripts: str = "",
    social_image: str = "",
    social_image_alt: str = "",
    social_image_width: object = "",
    social_image_height: object = "",
    og_type: str = "website",
    social_title: str = "",
) -> str:
    progress = """
<div class="reading-progress"><div class="reading-progress__bar" data-reading-progress></div></div>
""".strip() if include_progress else ""
    scripts = [f'<script src="app.js?v={h(APP_VERSION)}" defer></script>']
    if extra_scripts:
        scripts.append(extra_scripts)
    scripts_html = "\n  ".join(scripts)
    progress_html = f"  {progress}\n" if progress else ""
    return f"""<!doctype html>
<html lang="en">
{page_head(
    title,
    description,
    canonical,
    jsonld,
    extra_links=extra_links,
    social_image=social_image,
    social_image_alt=social_image_alt,
    social_image_width=social_image_width,
    social_image_height=social_image_height,
    og_type=og_type,
    social_title=social_title,
)}
<body class="{h(body_class)}">
  {search_overlay(search_index())}
{progress_html}  {header(current_section=current_section, current_aux=current_aux)}
  {main_html}
  {footer()}
{scripts_html}
</body>
</html>
""".strip() + "\n"


def render_homepage() -> str:
    lead_panels = []
    lead_buttons = []
    lead_stories = homepage_lead_stories()
    for idx, story in enumerate(lead_stories):
        active = " is-active" if idx == 0 else ""
        panel_width = f' width="{story["imageWidth"]}"' if story.get("imageWidth") else ""
        panel_height = f' height="{story["imageHeight"]}"' if story.get("imageHeight") else ""
        panel_media = (
            f'<img src="{h(story["image"])}" alt="{h(story.get("imageAlt") or story.get("title") or "Story thumbnail")}" loading="eager" decoding="async"{panel_width}{panel_height} />'
            if story.get("image")
            else f'<div class="press-image-fallback"><span>{h(story.get("section") or "Story")}</span></div>'
        )
        lead_panels.append(
            f"""
<div class="lead-panel{active}" data-lead-panel id="lead-{idx}">
  <div class="lead-panel__media">
    {panel_media}
  </div>
  <div class="lead-panel__body">
    <div>
      <p class="eyebrow">Front Page • {h(story['section'])} • {h(story['type'])}</p>
      <h2><a href="{h(story['filename'])}">{h(story['title'])}</a></h2>
      <p class="lead-panel__dek">{h(story['dek'])}</p>
      <p class="lead-panel__meta">Written and Researched by AI • {h(story['publishedLabel'])}</p>
    </div>
    <div class="button-row">
      <a class="button" href="{h(story['filename'])}">Read story</a>
      <a class="button button--ghost" href="archive.html">Open archive</a>
    </div>
  </div>
</div>
""".strip()
        )
        thumb_width = f' width="{story["imageWidth"]}"' if story.get("imageWidth") else ""
        thumb_height = f' height="{story["imageHeight"]}"' if story.get("imageHeight") else ""
        thumb = (
            f'<span class="lead-nav__thumb" aria-hidden="true"><img src="{h(story["image"])}" alt="" loading="lazy" decoding="async"{thumb_width}{thumb_height} /></span>'
            if story.get("image")
            else f'<span class="lead-nav__thumb lead-nav__thumb--fallback" aria-hidden="true"><span>{h(story["section"])}</span></span>'
        )
        side_slot = ""
        if 1 <= idx <= 3:
            side_slot = f' data-side-slot="left-{idx}"'
        elif 4 <= idx <= 6:
            side_slot = f' data-side-slot="right-{idx - 3}"'
        lead_buttons.append(
            f'<button class="lead-nav__button{" is-active" if idx == 0 else ""}" type="button" data-lead-button data-target="lead-{idx}" aria-pressed="{str(idx == 0).lower()}"{side_slot}>{thumb}<span class="lead-nav__kicker">{h(story["section"])}</span><strong>{h(story["title"])}</strong></button>'
        )
    recency_stories = homepage_recency_stories(lead_stories)
    recency_cards = "\n".join(recency_ticker_item(story) for story in recency_stories)
    recency_cards_duplicate = "\n".join(recency_ticker_item(story, duplicate=True) for story in recency_stories)
    latest_html = "\n".join(river_item(story) for story in STORIES[:8])
    main = f"""
<main class="page">
  <section class="home-hero">
    <div class="home-hero__intro">
      <p class="eyebrow">Front page</p>
      <h1>{h(SITE['name'])}</h1>
    </div>
    <div class="lead-switcher" data-press-hero-layout="split-rail" data-press-hero-slots="{HOME_HERO_TARGET}">
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
      <div class="home-recency-ticker" data-home-recency-ticker aria-label="The 15 newest stories that are not already in the hero">
        <div class="home-recency-ticker__track">
          <div class="home-recency-ticker__set">
            {recency_cards}
          </div>
          <div class="home-recency-ticker__set" aria-hidden="true">
            {recency_cards_duplicate}
          </div>
        </div>
      </div>
    </div>
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
    social_story = lead_stories[0] if lead_stories else {}
    return layout(
        f"{SITE['name']} — Front Page",
        SITE["description"],
        "",
        "page-home",
        main,
        jsonld=jsonld_org(),
        social_image=social_story.get("image", ""),
        social_image_alt=social_story.get("imageAlt", ""),
        social_image_width=social_story.get("imageWidth", ""),
        social_image_height=social_story.get("imageHeight", ""),
        social_title=SITE["name"],
    )


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


def render_gallery() -> str:
    gallery_rows = gallery_story_rows()
    tiles = "\n".join(
        f"""
<a class="gallery-tile" href="{h(story['filename'])}" aria-label="{h(story['title'])}">
  <img class="gallery-tile__image" src="{h(story['image'])}" alt="{h(story['imageAlt'])}" loading="lazy" decoding="async"{f' width="{story["imageWidth"]}"' if story.get("imageWidth") else ''}{f' height="{story["imageHeight"]}"' if story.get("imageHeight") else ''} />
  <span class="sr-only">{h(story['section'])} {h(story['type'])}: {h(story['title'])}</span>
</a>
""".strip()
        for story in gallery_rows
    )
    main = f"""
<main class="page">
  <section class="gallery-hero">
    <p class="eyebrow">Visual archive</p>
    <h1>Gallery</h1>
    <p>A visual wall of every story thumbnail in The Press. Click any image to open the full article.</p>
  </section>
  <section class="gallery-grid">
    {tiles}
  </section>
</main>
""".strip()
    return layout(
        f"Gallery — {SITE['name']}",
        "A visual gallery of every story thumbnail in The Press.",
        "gallery.html",
        "page-gallery",
        main,
        current_aux="gallery.html",
        jsonld=jsonld_org(),
    )


def render_section(section: dict) -> str:
    stories = section_stories(section["slug"])
    if not stories:
        cards = '<p class="empty-state">No stories published in this section yet.</p>'
    else:
        cards = "\n".join(story_card(story, archive=True) for story in stories)
    art = f'\n    <img class="page-art" src="{h(section["artwork"])}" alt="{h(section["headline"])} desk artwork" />' if section.get("artwork") else ""
    main = f"""
<main class="page">
  <section class="section-landing page-hero--with-art">
    <div>
      <p class="eyebrow">{h(section['eyebrow'])}</p>
      <h1>{h(section['headline'])}</h1>
      <p class="section-copy">{h(section['copy'])}</p>
    </div>{art}
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
    main = """
<main class="page page-pledge__main">

<section class="pledge-hero">
  <div class="pledge-hero__copy">
    <p class="pledge-kicker">AI Newsroom Pledge</p>
    <h1>
      <span>AI-generated journalism,</span>
      <span>disclosed upfront.</span>
    </h1>
    <p class="pledge-hero__dek">
      The Press uses Intelligent AI to draft articles, organize research, and help turn source material
      into readable stories. A human editor reviews the work before publication. The source trail stays visible.
      <strong>Read at your own risk. Form your own conclusions.</strong>
    </p>
    <div class="pledge-hero__actions" aria-label="Pledge links">
      <a class="pledge-btn pledge-btn--primary" href="archive.html">Read the latest stories</a>
      <a class="pledge-btn pledge-btn--ghost" href="gallery.html">Open gallery</a>
    </div>
  </div>

  <aside class="pledge-card" aria-label="AI disclosure summary">
    <p class="pledge-card__label">Disclosure</p>
    <div class="pledge-seal" aria-hidden="true">
      <div class="pledge-seal__ring">
        <span class="pledge-seal__eyebrow">AI</span>
        <strong>The Press</strong>
        <span class="pledge-seal__subline">Newsroom</span>
      </div>
      <div class="pledge-seal__chips">
        <span>Written with AI</span>
        <span>Human reviewed</span>
        <span>Source heavy</span>
      </div>
    </div>
    <p>
      No hidden ghostwriter. No fake staff card. No mystery box pretending to be a newsroom because apparently
      that is where the internet has decided to spend its retirement.
    </p>
  </aside>

  <ul class="pledge-stats" role="list">
    <li>
      <strong>AI-drafted</strong>
      <span>Stories begin with Intelligent AI, not a fake human byline.</span>
    </li>
    <li>
      <strong>Editor-gated</strong>
      <span>A human review pass decides what ships and what gets killed.</span>
    </li>
    <li>
      <strong>Source-heavy</strong>
      <span>Articles are built to be checked, challenged, and corrected.</span>
    </li>
  </ul>
</section>

<section class="pledge-statement">
  <p class="pledge-kicker">The Pledge</p>
  <h2>We will tell you how this paper is made before asking you to trust it.</h2>
  <div class="pledge-prose">
    <p>
      The Press is built around AI-generated drafts and human editorial judgment. That is not a shameful footnote.
      It is the central fact of the publication. The machine helps with speed, structure, synthesis, and first drafts.
      The editor is responsible for what appears on the page.
    </p>
    <p>
      AI can write clean sentences while being confidently wrong, which is a charming little nightmare humanity invented
      and then connected to every workplace. So our standard is simple: no claim should stand unless it can be traced
      back to a source, a record, a dataset, a direct statement, or a clearly labeled inference.
    </p>
    <p>
      We are not asking you to believe the article because the prose sounds polished. We are asking you to inspect the
      evidence, follow the links, compare the claims, and decide for yourself.
    </p>
  </div>
</section>

<section class="pledge-workflow" aria-labelledby="workflow-title">
  <div class="pledge-section-head">
    <p class="pledge-kicker">Behind the Scenes</p>
    <h2 id="workflow-title">What happens before an article goes live.</h2>
    <p>The glossy page is the end of the process. The work underneath is less glamorous and much more important.</p>
  </div>

  <ol class="pledge-workflow__list" role="list">
    <li class="pledge-step">
      <span>01</span>
      <h3>Story radar</h3>
      <p>We look for subjects where the public record has moved: official releases, data, filings, studies, transcripts, and credible reporting.</p>
    </li>
    <li class="pledge-step">
      <span>02</span>
      <h3>Source bundle</h3>
      <p>The article starts with receipts. The draft should be tied to documents the editor and reader can open, not vibes in a trench coat.</p>
    </li>
    <li class="pledge-step">
      <span>03</span>
      <h3>AI draft</h3>
      <p>Intelligent AI turns the source bundle into a structured draft, with the byline and AI disclosure treated as part of the story, not an afterthought.</p>
    </li>
    <li class="pledge-step">
      <span>04</span>
      <h3>Claim audit</h3>
      <p>Names, dates, numbers, causal claims, and quotes are checked against the source trail. Unsupported certainty gets cut.</p>
    </li>
    <li class="pledge-step">
      <span>05</span>
      <h3>Human edit</h3>
      <p>The editor reads for accuracy, tone, overreach, missing context, and the classic AI disease of sounding smarter than it has earned.</p>
    </li>
    <li class="pledge-step">
      <span>06</span>
      <h3>Publish with receipts</h3>
      <p>Stories keep source notes, credits, and context close to the article so readers can audit the work instead of worshiping the output.</p>
    </li>
    <li class="pledge-step">
      <span>07</span>
      <h3>Correct in public</h3>
      <p>When something is wrong, it belongs on the corrections page with a date, a plain explanation, and no theatrical fog machine.</p>
    </li>
  </ol>
</section>

<section class="pledge-receipts" aria-labelledby="receipts-title">
  <div>
    <p class="pledge-kicker">Receipts, Not Mysticism</p>
    <h2 id="receipts-title">The source trail is part of the product.</h2>
  </div>
  <div class="pledge-receipts__grid">
    <article>
      <h3>Primary records first</h3>
      <p>Government documents, datasets, court records, transcripts, official statements, and original research carry more weight than commentary.</p>
    </article>
    <article>
      <h3>Links readers can follow</h3>
      <p>The goal is not to sound authoritative. The goal is to make the authority checkable by someone who does not work here.</p>
    </article>
    <article>
      <h3>Clear uncertainty</h3>
      <p>When the evidence is partial, developing, disputed, or messy, the story should say that instead of cosplaying as a crystal ball.</p>
    </article>
  </div>
</section>

<section class="pledge-promises" aria-labelledby="promises-title">
  <div class="pledge-section-head">
    <p class="pledge-kicker">The Fine Print, Out Loud</p>
    <h2 id="promises-title">What we will do, and what we will not pretend.</h2>
  </div>

  <div class="pledge-promises__grid">
    <article class="pledge-promise pledge-promise--yes">
      <h3>We will</h3>
      <ul role="list">
        <li>Disclose AI authorship clearly on the AI Newsroom page and in publication language.</li>
        <li>Build articles around sources that can be inspected.</li>
        <li>Keep a human editor responsible for the final published page.</li>
        <li>Separate verified facts from analysis, interpretation, and uncertainty.</li>
        <li>Correct meaningful errors publicly and plainly.</li>
      </ul>
    </article>

    <article class="pledge-promise pledge-promise--no">
      <h3>We will not</h3>
      <ul role="list">
        <li>Invent quotes, sources, experts, documents, statistics, or anonymous whispers from nowhere.</li>
        <li>Pretend a model is a person with lived reporting experience.</li>
        <li>Hide the use of AI behind soft little euphemisms built by committee gremlins.</li>
        <li>Publish a claim just because the sentence sounds confident.</li>
        <li>Ask you to trust the machine. Check the machine.</li>
      </ul>
    </article>
  </div>
</section>

<section class="pledge-warning" aria-labelledby="warning-title">
  <p class="pledge-warning__stamp">Reader Advisory</p>
  <h2 id="warning-title">Read at your own risk. Form your own conclusions.</h2>
  <p>
    We can review, source, edit, label, and correct. We cannot think for you, and honestly that would be a terrible
    product feature. Treat every article as an argument with evidence attached. Open the sources. Compare the record.
    Notice what is missing. Push back when the story overreaches.
  </p>
  <p>
    A free press needs skeptical readers. An AI-generated press needs even more skeptical readers. That is not a bug.
    That is the deal.
  </p>
  <div class="pledge-warning__actions">
    <a class="pledge-btn pledge-btn--primary" href="archive.html">Archive</a>
    <a class="pledge-btn pledge-btn--ghost" href="gallery.html">Gallery</a>
    <a class="pledge-btn pledge-btn--ghost" href="index.html">Front page</a>
  </div>
</section>

<section class="pledge-sign">
  <p>Signed on behalf of a publication that would rather disclose the machine than sell you a fake human halo.</p>
  <strong>The Editor, The Press</strong>
  <span>April 2026</span>
</section>

</main>
""".strip()

    return layout(
        f"AI Newsroom Pledge — {SITE['name']}",
      "How The Press uses Intelligent AI, human editorial review, heavy sourcing, and reader skepticism.",
        "authors.html",
        "page-authors page-pledge",
        main,
        current_aux="authors.html",
        jsonld=jsonld_org(),
    )

def render_story(story: dict) -> str:
    aside_html = read_fragment(story["asideFile"])
    body_html = read_fragment(story["bodyFile"])
    gallery_html = gallery_block(story)
    related_html = related_block(story)
    social_rail_html = social_embeds_block(story, "rail")
    social_bottom_html = social_embeds_block(story, "bottom")
    aside_extra_html = f"\n          {social_rail_html}" if social_rail_html else ""
    body_extras = "\n        ".join(block for block in (gallery_html, social_bottom_html, related_html) if block)
    body_extra_html = f"\n        {body_extras}" if body_extras else ""
    hero_image = story.get("heroImage") or story["image"]
    hero_image_width = story.get("heroImageWidth") or story.get("imageWidth")
    hero_image_height = story.get("heroImageHeight") or story.get("imageHeight")
    static_interactive = story.get("staticInteractive") if isinstance(story.get("staticInteractive"), dict) else {}
    static_css = str(static_interactive.get("css") or "").strip()
    static_js = str(static_interactive.get("js") or "").strip()
    extra_links = (
        f'<link rel="stylesheet" href="{h(static_css)}?v={h(asset_version(static_css))}" />'
        if static_css
        else ""
    )
    extra_scripts = (
        f'<script src="{h(static_js)}?v={h(asset_version(static_js))}" defer></script>'
        if static_js
        else ""
    )
    main = f"""
<main class="page page-article">
  <article class="article">
    <header class="article-hero">
      <p class="eyebrow">{h(story['section'])} • {h(story['type'])}</p>
      <h1 class="article-headline">{h(story['title'])}</h1>
      <p class="article-dek">{h(story['dek'])}</p>
      <div class="article-meta">
        <span>Written and Researched by AI</span>
        <span>Published {h(story['publishedLabel'])}</span>
        <span>Updated {h(story['updatedLabel'])}</span>
      </div>
      <figure class="hero-figure">
        <img src="{h(hero_image)}" alt="{h(story['imageAlt'])}" loading="eager" decoding="async"{f' width="{hero_image_width}"' if hero_image_width else ''}{f' height="{hero_image_height}"' if hero_image_height else ''} />
        <figcaption>{story['imageCaptionHtml']}</figcaption>
      </figure>
    </header>
    <div class="article-shell">
      <aside class="article-aside">
        <div class="sticky-stack">
          {aside_html}{aside_extra_html}
        </div>
      </aside>
      <div class="article-body">
        {body_html}{body_extra_html}
      </div>
    </div>
  </article>
</main>
""".strip()
    return layout(
        f"{story['title']} — {SITE['name']}",
        story["dek"],
        story["filename"],
        "page-article",
        main,
        current_section=story["sectionSlug"],
        jsonld=jsonld_article(story),
        include_progress=True,
        extra_links=extra_links,
        extra_scripts=extra_scripts,
        social_image=story.get("image", ""),
        social_image_alt=story.get("imageAlt", ""),
        social_image_width=story.get("imageWidth", ""),
        social_image_height=story.get("imageHeight", ""),
        og_type="article",
        social_title=story["title"],
    )


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
    build_date = format_datetime(BUILD_REFERENCE_DT)
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
    urls = ['index.html', 'archive.html', 'gallery.html', 'authors.html', 'about.html', 'photo-workflow.html', '404.html']
    urls += [story["filename"] for story in STORIES]
    urlset = []
    for path in urls:
        story = STORY_BY_FILE.get(path)
        modified = parse_iso_datetime(story.get("updatedIso") or story.get("publishedIso")) if story else None
        lastmod = (modified or BUILD_REFERENCE_DT).date().isoformat()
        urlset.append(f"<url><loc>{html.escape(absolute_url(path))}</loc><lastmod>{lastmod}</lastmod></url>")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {' '.join(urlset)}
</urlset>
"""


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def build() -> None:
    if richer_existing_search_index() and not env_flag("PRESS_ALLOW_LEGACY_MASTER_BUILD"):
        raise SystemExit(
            "Refusing to run the legacy master-edition build over the richer live site index. "
            "Run tools/build_press_ecosystem.py for current live indexes, or set "
            "PRESS_ALLOW_LEGACY_MASTER_BUILD=1 if you intentionally want the older master-only rebuild."
        )
    write_file(SITE_DIR / "index.html", render_homepage())
    write_file(SITE_DIR / "archive.html", render_archive())
    write_file(SITE_DIR / "gallery.html", render_gallery())
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

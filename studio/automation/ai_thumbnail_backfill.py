#!/usr/bin/env python3
"""
GPT Image 2 thumbnail generator for The Press.

Default behavior:
1. Reads daily-latest.json.
2. Targets only the newest/current issue articles.
3. Generates one high-quality GPT Image 2 thumbnail per selected article.
4. Updates the article hero image, matching front-page/section/archive cards,
   and common JSON indexes.

It does not create article galleries/photos and does not scan the whole historical
site unless AI_ART_SCOPE=all is set explicitly.
"""
from __future__ import annotations

import base64
import html
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from openai import OpenAI


def find_repo_root(script_path: Path) -> Path:
    """Find the repository root whether run from repo root or studio/automation."""
    current = script_path.resolve().parent
    for candidate in [current, *current.parents]:
        if (candidate / "styles.css").exists() and (candidate / "assets").exists():
            return candidate
    return script_path.resolve().parents[2]


ROOT = find_repo_root(Path(__file__))
DAILY_DIR = ROOT / "daily"
ASSETS_DIR = ROOT / "assets"
AI_THUMBNAIL_DIR = ASSETS_DIR / "ai-thumbnails"
AI_ART_DIR = ASSETS_DIR / "ai-article-art"
AUTO_DAILY_ASSET_DIR = ASSETS_DIR / "daily"


def env_bool(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def env_int(name: str, default: int, minimum: int | None = None, maximum: int | None = None) -> int:
    try:
        value = int(os.getenv(name, str(default)) or str(default))
    except ValueError:
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


AI_THUMBNAIL_BACKFILL = env_bool("AI_THUMBNAIL_BACKFILL", True)
FORCE_AI_FOR_ALL_ARTICLE_THUMBNAILS = env_bool("FORCE_AI_FOR_ALL_ARTICLE_THUMBNAILS", True)
FORCE_AI_FOR_DAILY_STORIES = env_bool("FORCE_AI_FOR_DAILY_STORIES", True)
REPLACE_SVG_ARTICLE_THUMBNAILS = env_bool("REPLACE_SVG_ARTICLE_THUMBNAILS", True)
AI_REGENERATE_AI_THUMBNAILS = env_bool("AI_REGENERATE_AI_THUMBNAILS", False)
REMOVE_AI_GALLERIES = env_bool("REMOVE_AI_GALLERIES", True)

OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2")
OPENAI_IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1536x864")
OPENAI_IMAGE_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "high")
OPENAI_IMAGE_FORMAT = os.getenv("OPENAI_IMAGE_FORMAT", "jpeg").strip().lower() or "jpeg"
if OPENAI_IMAGE_FORMAT == "jpg":
    OPENAI_IMAGE_FORMAT = "jpeg"
OPENAI_IMAGE_COMPRESSION = env_int("OPENAI_IMAGE_COMPRESSION", 85, minimum=0, maximum=100)

# 0 means unlimited. Daily default is 15: one thumbnail for each new article.
AI_TOTAL_IMAGE_MAX_GENERATIONS = env_int(
    "AI_TOTAL_IMAGE_MAX_GENERATIONS",
    env_int("AI_THUMBNAIL_MAX_GENERATIONS", 15, minimum=0),
    minimum=0,
)
AI_ART_SCOPE = os.getenv("AI_ART_SCOPE", "current_issue").strip().lower() or "current_issue"
AI_ART_MAX_ARTICLES = env_int("AI_ART_MAX_ARTICLES", 15, minimum=0)
AI_UPDATE_LINKED_CARDS = env_bool("AI_UPDATE_LINKED_CARDS", True)
AI_CARD_UPDATE_SCOPE = os.getenv("AI_CARD_UPDATE_SCOPE", "front_pages").strip().lower() or "front_pages"

BANNED_VISUAL_TROPES = [
    "balancing scales",
    "red-versus-blue state maps",
    "U.S. map overlays",
    "floating state silhouettes",
    "generic server racks",
    "data-center exterior at sunset",
    "child-with-rash outbreak imagery",
    "vaccine vial on a map",
    "Supreme Court plus map collage",
    "space capsule splashdown beauty shot",
    "glowing AI brain",
    "hologram person sitting across from someone",
    "giant pencil drawing district lines",
]

VISUAL_CLICHE_REWRITES = {
    "balancing scales": "a close view of the actual decision setting, documents, tools, and people affected by the dispute",
    "red-versus-blue state maps": "a place-specific street, office, or public meeting scene that shows the local stakes without partisan color coding",
    "U.S. map overlays": "a grounded scene from the relevant institution, neighborhood, workplace, clinic, school, or infrastructure site",
    "floating state silhouettes": "a concrete local setting with one recognizable civic or material detail instead of a floating state outline",
    "generic server racks": "a human-scale operations scene with tagged fiber cables, cooling gauges, utility meters, and a technician's gloved hands",
    "data-center exterior at sunset": "a daylight infrastructure detail showing transformer equipment, cooling lines, power meters, or construction work tied to the story",
    "child-with-rash outbreak imagery": "a clinic intake desk, public-health lab bench, vaccine record folder, or waiting-room process scene",
    "vaccine vial on a map": "a clinic refrigerator tray, appointment clipboard, courier cooler, or public-health dashboard room with no readable text",
    "Supreme Court plus map collage": "a courthouse corridor, filing desk, hearing room door, or civic record archive tied to the legal stakes",
    "space capsule splashdown beauty shot": "a mission-control console, recovery-team process detail, lab sample tray, or engineering checklist with no readable text",
    "glowing AI brain": "a concrete human-computer work scene with screens, cables, notebooks, lab equipment, or workplace consequences",
    "hologram person sitting across from someone": "a phone or laptop on a kitchen table, clinic desk, classroom, or workplace showing mediated conversation without a fake person",
    "giant pencil drawing district lines": "a local election office table with paper precinct packets, rulers, laptops, and hands sorting map drafts without readable labels",
}


def parse_image_size(size: str) -> tuple[int, int]:
    match = re.match(r"^(\d+)x(\d+)$", size.strip().lower())
    if not match:
        return 1536, 864
    return int(match.group(1)), int(match.group(2))


IMAGE_WIDTH, IMAGE_HEIGHT = parse_image_size(OPENAI_IMAGE_SIZE)
IMAGE_EXTENSION = ".jpg" if OPENAI_IMAGE_FORMAT == "jpeg" else f".{OPENAI_IMAGE_FORMAT}"

SKIP_HTML_NAMES = {
    "404.html",
    "about.html",
    "ai-edition.html",
    "archive.html",
    "authors.html",
    "breaking-news.html",
    "contact.html",
    "corrections.html",
    "photo-workflow.html",
    "preview-homepage-fixes.html",
    "standards.html",
}

BAD_IMAGE_KEYWORDS = (
    "fallback",
    "placeholder",
    "no-image",
    "no_image",
    "image-unavailable",
    "image_unavailable",
    "unavailable",
    "blank",
)

IMAGE_KEYS = (
    "image",
    "image_url",
    "imageUrl",
    "thumbnail",
    "thumbnail_url",
    "thumbnailUrl",
    "thumbnail_local",
    "thumbnailLocal",
)


@dataclass
class ArticleThumbnailUpdate:
    page_path: Path
    page_url: str
    title: str
    dek: str
    section: str
    old_src: str
    new_src_for_page: str
    new_src_from_root: str
    new_abs_path: Path
    alt: str
    caption_html: str
    credit_plain: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def rel_from_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def rel_to_file(path: Path, from_file: Path) -> str:
    return os.path.relpath(path.resolve(), from_file.parent.resolve()).replace("\\", "/")


def slugify(text: str) -> str:
    value = text.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:90].strip("-") or "article"


def clean_text(value: str, max_len: int = 600) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def rewrite_visual_cliches_text(value: str) -> tuple[str, list[str]]:
    updated = value or ""
    rewrites: list[str] = []
    for banned, replacement in VISUAL_CLICHE_REWRITES.items():
        next_value = re.sub(re.escape(banned), replacement, updated, flags=re.I)
        if next_value != updated:
            rewrites.append(banned)
            updated = next_value
    return updated.strip(), rewrites


def path_from_img_src(src: str | None, html_path: Path) -> Path | None:
    if not src:
        return None
    parsed = urlparse(str(src))
    if parsed.scheme in {"http", "https", "data", "mailto"}:
        return None
    clean = unquote(parsed.path or str(src)).strip()
    if not clean:
        return None
    if clean.startswith("/"):
        return (ROOT / clean.lstrip("/")).resolve()
    return (html_path.parent / clean).resolve()


def is_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def is_auto_daily_asset(src: str | None, html_path: Path) -> bool:
    local_path = path_from_img_src(src, html_path)
    return bool(local_path and is_under(local_path, AUTO_DAILY_ASSET_DIR))


def is_ai_thumbnail_asset(src: str | None, html_path: Path) -> bool:
    local_path = path_from_img_src(src, html_path)
    return bool(local_path and is_under(local_path, AI_THUMBNAIL_DIR))


def is_svg_placeholder(path: Path) -> bool:
    if path.suffix.lower() != ".svg" or not path.exists():
        return False
    try:
        text = read_text(path).lower()
    except Exception:
        return True
    return any(word in text for word in BAD_IMAGE_KEYWORDS) or "image unavailable" in text


def is_bad_article_image(src: str | None, html_path: Path) -> bool:
    """Return True when the current image should be replaced with an AI thumbnail."""
    if not src or not str(src).strip():
        return True

    src_text = str(src).strip()
    lower = src_text.lower()

    if is_ai_thumbnail_asset(src_text, html_path):
        return AI_REGENERATE_AI_THUMBNAILS

    if lower.startswith("data:"):
        return False

    if any(word in lower for word in BAD_IMAGE_KEYWORDS):
        return True

    if FORCE_AI_FOR_DAILY_STORIES and is_auto_daily_asset(src_text, html_path):
        return True

    local_path = path_from_img_src(src_text, html_path)
    if local_path is None:
        # External image URLs are real images, but not AI-made. The force switch handles that.
        return False

    if not local_path.exists():
        return True

    if local_path.suffix.lower() == ".svg":
        if REPLACE_SVG_ARTICLE_THUMBNAILS:
            return True
        return is_svg_placeholder(local_path)

    if local_path.stat().st_size < 1024:
        return True

    return False


def should_replace_thumbnail(src: str | None, html_path: Path) -> bool:
    if is_ai_thumbnail_asset(src, html_path) and not AI_REGENERATE_AI_THUMBNAILS:
        return False
    if FORCE_AI_FOR_ALL_ARTICLE_THUMBNAILS:
        return True
    return is_bad_article_image(src, html_path)


def ordered_unique_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    output: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        output.append(path)
    return output


def repo_html_path_from_url(value: str) -> Path | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    parsed = urlparse(raw)
    path_text = parsed.path if parsed.scheme or parsed.netloc else raw
    path_text = path_text.split("#", 1)[0].split("?", 1)[0].strip()
    if path_text.startswith("/"):
        path_text = path_text.lstrip("/")
    if not path_text:
        return None
    if path_text.endswith("/"):
        path_text += "index.html"
    candidate = (ROOT / path_text).resolve()
    if candidate.suffix.lower() != ".html":
        return None
    return candidate


def load_daily_latest_article_paths() -> list[Path]:
    path = ROOT / "daily-latest.json"
    if not path.exists():
        print("daily-latest.json not found; current_issue thumbnail pass has no target articles", file=sys.stderr)
        return []
    try:
        data = json.loads(read_text(path))
    except Exception as exc:
        print(f"Could not read daily-latest.json: {exc}", file=sys.stderr)
        return []

    items: list[Any] = []
    if isinstance(data, dict):
        for key in ("articles", "stories", "items"):
            value = data.get(key)
            if isinstance(value, list):
                items.extend(value)
    elif isinstance(data, list):
        items = data

    paths: list[Path] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        for key in ("url", "href", "filename", "page_url", "pageUrl"):
            candidate = repo_html_path_from_url(str(item.get(key) or ""))
            if candidate:
                paths.append(candidate)
                break

    existing_paths = []
    for candidate in ordered_unique_paths(paths):
        if candidate.exists():
            existing_paths.append(candidate)
        else:
            print(f"Skipping missing article listed in daily-latest.json: {candidate}", file=sys.stderr)
    return existing_paths


def load_master_story_filenames() -> set[str]:
    path = ROOT / "master-edition.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(read_text(path))
    except Exception:
        return set()
    filenames: set[str] = set()
    for story in data.get("stories", []) if isinstance(data, dict) else []:
        filename = str(story.get("filename") or "").strip()
        if filename:
            filenames.add(filename)
    return filenames


def html_files() -> list[Path]:
    files = [p for p in ROOT.glob("*.html") if p.is_file()]
    if DAILY_DIR.exists():
        files.extend(p for p in DAILY_DIR.glob("*.html") if p.is_file())
    return sorted(files)


def looks_like_article_page(path: Path, soup: BeautifulSoup, master_filenames: set[str]) -> bool:
    if path.name in master_filenames:
        return True
    if path.parent == DAILY_DIR and path.suffix.lower() == ".html":
        return True
    if path.name in SKIP_HTML_NAMES or path.name.startswith("section-"):
        return False
    if soup.select_one("article.article-shell, main.article-layout, main.daily-story"):
        return True
    article = soup.find("article")
    if article and soup.find("h1"):
        return True
    return False


def load_article_paths() -> list[Path]:
    if AI_ART_SCOPE == "current_issue":
        paths = load_daily_latest_article_paths()
        if AI_ART_MAX_ARTICLES:
            paths = paths[:AI_ART_MAX_ARTICLES]
        return paths

    if AI_ART_SCOPE != "all":
        print(f"Unknown AI_ART_SCOPE={AI_ART_SCOPE!r}; using current_issue behavior", file=sys.stderr)
        paths = load_daily_latest_article_paths()
        if AI_ART_MAX_ARTICLES:
            paths = paths[:AI_ART_MAX_ARTICLES]
        return paths

    master_filenames = load_master_story_filenames()
    article_paths: list[Path] = []
    for path in html_files():
        soup = BeautifulSoup(read_text(path), "html.parser")
        if looks_like_article_page(path, soup, master_filenames):
            article_paths.append(path)
    if AI_ART_MAX_ARTICLES:
        article_paths = article_paths[:AI_ART_MAX_ARTICLES]
    return article_paths


def article_container(soup: BeautifulSoup) -> Any:
    return (
        soup.select_one("article.article-shell")
        or soup.select_one("main.daily-story")
        or soup.find("article")
        or soup.select_one("main.article-layout")
        or soup.body
        or soup
    )


def find_article_img(container: Any) -> Any | None:
    if not container:
        return None
    preferred = (
        container.select_one("figure.article-hero img")
        or container.select_one(".article-hero img")
        or container.select_one(".hero-image img")
    )
    if preferred:
        return preferred
    for img in container.select("img"):
        if img.find_parent(attrs={"data-ai-article-gallery": True}) or img.find_parent(class_="ai-article-gallery"):
            continue
        return img
    return None


def page_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        text = clean_text(h1.get_text(" ", strip=True), 180)
        if text:
            return text
    title_tag = soup.find("title")
    if title_tag:
        return clean_text(title_tag.get_text(" ", strip=True).replace("— The Press", ""), 180)
    return "The Press article"


def page_dek(soup: BeautifulSoup, container: Any) -> str:
    for selector in (".article-dek", ".dek", ".story-dek", ".lead", "meta[name='description']"):
        node = soup.select_one(selector)
        if not node:
            continue
        if node.name == "meta":
            text = str(node.get("content") or "")
        else:
            text = node.get_text(" ", strip=True)
        text = clean_text(text, 520)
        if text:
            return text
    first_p = container.find("p") if container else None
    if first_p:
        return clean_text(first_p.get_text(" ", strip=True), 520)
    return ""


def page_section(soup: BeautifulSoup) -> str:
    for selector in (".eyebrow", ".section-label", "[data-section]"):
        node = soup.select_one(selector)
        if not node:
            continue
        text = str(node.get("data-section") or node.get_text(" ", strip=True))
        text = clean_text(text, 100)
        if text:
            return text
    h1 = soup.find("h1")
    if h1:
        previous = h1.find_previous(string=True)
        if previous:
            text = clean_text(str(previous), 100)
            if text and text.lower() not in {"the press", "home", "daily issue"}:
                return text
    return "News"


def meta_content(soup: BeautifulSoup, name: str) -> str:
    node = soup.select_one(f'meta[name="{name}"]')
    if not node:
        return ""
    return clean_text(str(node.get("content") or ""), 1000)


def page_visual_archetype(soup: BeautifulSoup) -> str:
    return meta_content(soup, "press:visual-archetype")


def page_visual_brief(soup: BeautifulSoup) -> str:
    return meta_content(soup, "press:visual-brief")

def page_body_snippet(container: Any) -> str:
    body = (
        container.select_one(".article-body")
        or container.select_one("[data-article-body]")
        if container
        else None
    )
    node = body or container
    if not node:
        return ""
    clone = BeautifulSoup(str(node), "html.parser")
    for unwanted in clone.select("script, style, nav, footer, .ai-article-gallery, [data-ai-article-gallery]"):
        unwanted.decompose()
    return clean_text(clone.get_text(" ", strip=True), 3600)


def generation_budget_available(generated_count: int) -> bool:
    return not AI_TOTAL_IMAGE_MAX_GENERATIONS or generated_count < AI_TOTAL_IMAGE_MAX_GENERATIONS


def prompt_for_article(
    title: str,
    dek: str,
    section: str,
    body_snippet: str,
    visual_archetype: str,
    visual_brief: str,
) -> str:
    visual_brief, rewrites = rewrite_visual_cliches_text(visual_brief)
    if rewrites:
        print(f"WARNING: Rewrote banned thumbnail cliché(s) for {title}: {', '.join(rewrites)}")
    banned = "; ".join(BANNED_VISUAL_TROPES)
    return f"""
Create one premium 16:9 landscape GPT Image 2 thumbnail for a serious digital newspaper article.

Section: {section}
Title: {title}
Summary: {dek}
Article context: {body_snippet}
Assigned visual archetype: {visual_archetype or 'unique concrete editorial scene'}
Article-specific visual brief: {visual_brief or 'Choose a concrete visual moment from the reporting, with a fresh setting and one unmistakable subject.'}

Visual direction:
- Follow the assigned visual archetype and article-specific visual brief. Do not ignore them.
- Make the thumbnail clearly connected to this article, not a generic stock image or reusable news symbol.
- Favor concrete scenes: a specific room, street, workplace, clinic, court corridor, lab bench, classroom, kitchen table, market, field site, archive, machine, tool, document stack, weather condition, or human-scale object from the story.
- Use one strong central subject that reads instantly at homepage thumbnail size, with a distinctive composition that has not appeared in other cards.
- Choose either photorealistic documentary realism or polished editorial art, whichever best serves the story.
- Make it feel expensive, cinematic, original, and publishable for a modern newspaper.
- Avoid these repeated thumbnail tropes completely: {banned}.
- Only use a map when the article truly requires geography. Never make a red/blue political map, floating state silhouette, or state-outline collage.
- Only show a data center, server rack, courthouse, vaccine vial, space capsule, AI brain, or balancing metaphor if the exact article demands it; even then, choose a new angle, location, texture, or object-detail approach.

Safety and publishing requirements:
- No logos, watermarks, signatures, fake screenshots, fake documents, or readable text.
- Do not imitate a living artist, brand, copyrighted character, film still, or publication style.
- If the story involves a living/current real person, do not create a photorealistic likeness; use a non-photorealistic editorial portrait, silhouette, or symbolic representation instead.
- Avoid gore, graphic violence, shock imagery, or misleading visual claims.
""".strip()

def image_extension_from_bytes(data: bytes, default: str) -> str:
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"RIFF") and b"WEBP" in data[:16]:
        return ".webp"
    return default


def generate_ai_image(client: OpenAI, prompt: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    request: dict[str, Any] = {
        "model": OPENAI_IMAGE_MODEL,
        "prompt": prompt,
        "size": OPENAI_IMAGE_SIZE,
        "quality": OPENAI_IMAGE_QUALITY,
        "n": 1,
    }
    if OPENAI_IMAGE_FORMAT in {"jpeg", "png", "webp"}:
        request["output_format"] = OPENAI_IMAGE_FORMAT
    if OPENAI_IMAGE_FORMAT in {"jpeg", "webp"}:
        request["output_compression"] = OPENAI_IMAGE_COMPRESSION

    try:
        result = client.images.generate(**request)
    except Exception as exc:
        # Some accounts/models may reject output_format/output_compression. Retry once
        # without those optional knobs so thumbnail generation can still complete.
        message = str(exc).lower()
        if "output_format" not in message and "output_compression" not in message and "unsupported" not in message:
            raise
        request.pop("output_format", None)
        request.pop("output_compression", None)
        result = client.images.generate(**request)

    image_base64 = result.data[0].b64_json
    if not image_base64:
        raise RuntimeError("OpenAI image response did not include b64_json")

    data = base64.b64decode(image_base64)
    actual_ext = image_extension_from_bytes(data, output_path.suffix)
    if output_path.suffix.lower() != actual_ext:
        output_path = output_path.with_suffix(actual_ext)
    output_path.write_bytes(data)
    return output_path


def ensure_figure_and_img(soup: BeautifulSoup, container: Any, img: Any | None) -> Any:
    if img is not None:
        return img
    figure = soup.new_tag("figure")
    figure["class"] = "article-hero"
    new_img = soup.new_tag("img")
    new_img["loading"] = "eager"
    new_img["decoding"] = "async"
    figure.append(new_img)
    insert_after = (
        container.select_one(".button-row")
        or container.select_one(".article-meta")
        or container.select_one(".article-dek")
        or container.find("h1")
    )
    if insert_after:
        insert_after.insert_after(figure)
    elif container:
        container.insert(0, figure)
    else:
        soup.append(figure)
    return new_img


def set_or_replace_caption(soup: BeautifulSoup, img: Any, caption_html: str) -> None:
    figure = img.find_parent("figure")
    if not figure:
        return
    existing = figure.find("figcaption")
    caption_soup = BeautifulSoup(caption_html, "html.parser")
    if existing:
        existing.clear()
        for child in list(caption_soup.contents):
            existing.append(child)
        existing["class"] = existing.get("class") or ["article-hero__caption"]
        return
    figcaption = soup.new_tag("figcaption")
    figcaption["class"] = "article-hero__caption"
    for child in list(caption_soup.contents):
        figcaption.append(child)
    figure.append(figcaption)


def remove_ai_gallery_sections(soup: BeautifulSoup) -> bool:
    if not REMOVE_AI_GALLERIES:
        return False
    changed = False
    for gallery in soup.select("[data-ai-article-gallery], .ai-article-gallery"):
        gallery.decompose()
        changed = True
    return changed


def find_existing_thumbnail(slug: str) -> Path | None:
    for ext in (IMAGE_EXTENSION, ".jpg", ".jpeg", ".png", ".webp"):
        candidate = AI_THUMBNAIL_DIR / f"{slug}{ext}"
        if candidate.exists() and candidate.stat().st_size > 1024:
            return candidate
    return None


def update_article_page(client: OpenAI, path: Path, generated_count: int) -> tuple[ArticleThumbnailUpdate | None, int]:
    original = read_text(path)
    soup = BeautifulSoup(original, "html.parser")
    container = article_container(soup)
    title = page_title(soup)
    dek = page_dek(soup, container)
    section = page_section(soup)
    body_snippet = page_body_snippet(container)
    visual_archetype = page_visual_archetype(soup)
    visual_brief = page_visual_brief(soup)
    slug = slugify(path.stem or title)
    img = find_article_img(container)
    old_src = str(img.get("src") or "") if img else ""
    output_path = AI_THUMBNAIL_DIR / f"{slug}{IMAGE_EXTENSION}"
    changed = remove_ai_gallery_sections(soup)

    replace = should_replace_thumbnail(old_src, path)
    existing_ai_path = find_existing_thumbnail(slug)

    if not replace and existing_ai_path is None:
        if changed:
            write_text(path, str(soup))
        return None, generated_count

    if existing_ai_path and not AI_REGENERATE_AI_THUMBNAILS:
        output_path = existing_ai_path
        print(f"Reusing existing GPT Image 2 thumbnail for {rel_from_root(path)}")
    else:
        if not generation_budget_available(generated_count):
            print(f"Generation limit reached before {rel_from_root(path)}")
            if changed:
                write_text(path, str(soup))
            return None, generated_count
        print(f"Generating GPT Image 2 thumbnail for {rel_from_root(path)}")
        prompt = prompt_for_article(title, dek, section, body_snippet, visual_archetype, visual_brief)
        output_path = generate_ai_image(client, prompt, output_path)
        generated_count += 1
        time.sleep(1)

    img = ensure_figure_and_img(soup, container, img)
    alt = f"AI-generated editorial thumbnail for: {title}"
    caption_html = (
        f"{html.escape(alt)}. "
        f'<span class="figure-credit">AI-generated image by The Press.</span>'
    )
    credit_plain = f"{alt}. AI-generated image by The Press."

    img["src"] = rel_to_file(output_path, path)
    img["alt"] = alt
    img["loading"] = img.get("loading") or "eager"
    img["decoding"] = img.get("decoding") or "async"
    set_or_replace_caption(soup, img, caption_html)
    changed = True

    if changed:
        write_text(path, str(soup))

    page_url = rel_from_root(path)
    return (
        ArticleThumbnailUpdate(
            page_path=path,
            page_url=page_url,
            title=title,
            dek=dek,
            section=section,
            old_src=old_src,
            new_src_for_page=rel_to_file(output_path, path),
            new_src_from_root=rel_from_root(output_path),
            new_abs_path=output_path,
            alt=alt,
            caption_html=caption_html,
            credit_plain=credit_plain,
        ),
        generated_count,
    )


def front_page_files() -> list[Path]:
    files: list[Path] = []
    for name in ("index.html", "archive.html", "breaking-news.html", "ai-edition.html"):
        path = ROOT / name
        if path.exists():
            files.append(path)
    files.extend(sorted(ROOT.glob("section-*.html")))
    return ordered_unique_paths(files)


def card_update_files() -> list[Path]:
    if not AI_UPDATE_LINKED_CARDS:
        return []
    if AI_CARD_UPDATE_SCOPE == "all":
        return [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
    return front_page_files()


def update_cards_in_html_file(path: Path, updates: list[ArticleThumbnailUpdate]) -> bool:
    original = read_text(path)
    soup = BeautifulSoup(original, "html.parser")
    changed = False

    for update in updates:
        possible_hrefs = {
            update.page_url,
            "./" + update.page_url,
            "/" + update.page_url,
            update.page_path.name,
            "../" + update.page_url,
        }
        anchors = []
        for anchor in soup.find_all("a", href=True):
            href = str(anchor.get("href") or "").split("#", 1)[0]
            if href in possible_hrefs or href.endswith("/" + update.page_url):
                anchors.append(anchor)

        for anchor in anchors:
            card = anchor.find_parent(["article", "section", "li", "div"]) or anchor.parent
            if not card:
                continue
            img = card.find("img")
            if not img:
                continue
            current_src = str(img.get("src") or "")
            wanted_src = rel_to_file(update.new_abs_path, path)
            if current_src == wanted_src:
                continue
            if update.old_src and current_src == update.old_src:
                should_update = True
            elif FORCE_AI_FOR_ALL_ARTICLE_THUMBNAILS and not is_ai_thumbnail_asset(current_src, path):
                should_update = True
            else:
                should_update = is_bad_article_image(current_src, path)
            if should_update:
                img["src"] = wanted_src
                img["alt"] = update.alt
                changed = True

    if changed:
        write_text(path, str(soup))
    return changed


def update_master_edition(updates: list[ArticleThumbnailUpdate]) -> bool:
    path = ROOT / "master-edition.json"
    if not path.exists():
        return False
    try:
        data = json.loads(read_text(path))
    except Exception as exc:
        print(f"Could not read master-edition.json: {exc}")
        return False

    by_filename = {u.page_path.name: u for u in updates}
    changed = False
    if isinstance(data, dict):
        for story in data.get("stories", []):
            if not isinstance(story, dict):
                continue
            filename = str(story.get("filename") or "")
            update = by_filename.get(filename)
            if not update:
                continue
            story["image"] = update.new_src_from_root
            story["imageAlt"] = update.alt
            story["imageCaptionHtml"] = update.caption_html
            story["imageCreditPlain"] = update.credit_plain
            story["imageWidth"] = IMAGE_WIDTH
            story["imageHeight"] = IMAGE_HEIGHT
            if REMOVE_AI_GALLERIES and "galleryImages" in story:
                del story["galleryImages"]
            changed = True

    if changed:
        write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return changed


def recursively_update_json_images(obj: Any, updates_by_url: dict[str, ArticleThumbnailUpdate]) -> bool:
    changed = False
    if isinstance(obj, dict):
        url = str(obj.get("url") or obj.get("href") or obj.get("filename") or "")
        update = updates_by_url.get(url) or updates_by_url.get(url.lstrip("./"))
        if update:
            touched_image_key = False
            for key in IMAGE_KEYS:
                if key in obj:
                    obj[key] = update.new_src_from_root
                    touched_image_key = True
                    changed = True
            if not touched_image_key:
                obj["image"] = update.new_src_from_root
                changed = True
            obj["imageAlt"] = update.alt
            obj["imageCreditPlain"] = update.credit_plain
            if "image_credit" in obj:
                obj["image_credit"] = update.credit_plain
            if "thumbnail_alt" in obj:
                obj["thumbnail_alt"] = update.alt
            if REMOVE_AI_GALLERIES and "galleryImages" in obj:
                del obj["galleryImages"]
            changed = True
        for value in obj.values():
            if recursively_update_json_images(value, updates_by_url):
                changed = True
    elif isinstance(obj, list):
        for item in obj:
            if recursively_update_json_images(item, updates_by_url):
                changed = True
    return changed


def update_json_indexes(updates: list[ArticleThumbnailUpdate]) -> None:
    updates_by_url: dict[str, ArticleThumbnailUpdate] = {}
    for update in updates:
        updates_by_url[update.page_url] = update
        updates_by_url[update.page_path.name] = update
        updates_by_url["./" + update.page_url] = update

    for path in [
        ROOT / "daily-latest.json",
        ROOT / "archive-index.json",
        ROOT / "content-index.json",
        ROOT / "edition.json",
        ROOT / "live-index.json",
        ROOT / "search-index.json",
    ]:
        if not path.exists():
            continue
        try:
            data = json.loads(read_text(path))
        except Exception:
            continue
        if recursively_update_json_images(data, updates_by_url):
            write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            print(f"Updated {rel_from_root(path)}")


def main() -> int:
    if not AI_THUMBNAIL_BACKFILL:
        print("AI thumbnail generation disabled by AI_THUMBNAIL_BACKFILL")
        return 0

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is missing")

    client = OpenAI(api_key=api_key)
    AI_THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    article_paths = load_article_paths()
    print(
        f"Scanning {len(article_paths)} article page(s) for one GPT Image 2 thumbnail each "
        f"with scope={AI_ART_SCOPE!r} and cap={AI_TOTAL_IMAGE_MAX_GENERATIONS or 'unlimited'}"
    )

    updates: list[ArticleThumbnailUpdate] = []
    generated_count = 0
    for path in article_paths:
        try:
            update, generated_count = update_article_page(client, path, generated_count)
            if update:
                updates.append(update)
        except Exception as exc:
            print(f"AI thumbnail update failed for {rel_from_root(path)}: {exc}", file=sys.stderr)

    if updates:
        for path in card_update_files():
            if update_cards_in_html_file(path, updates):
                print(f"Updated linked cards in {rel_from_root(path)}")

        if update_master_edition(updates):
            print("Updated master-edition.json")
        update_json_indexes(updates)
    else:
        print("No article thumbnail updates were made")

    print(
        f"GPT Image 2 thumbnail pass complete: {len(updates)} article(s) checked/updated; "
        f"{generated_count} new thumbnail image(s) generated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

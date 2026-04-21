#!/usr/bin/env python3
"""
AI article-art backfill for The Press.

What this script does:
1. Scans article pages in the repo root and daily/*.html.
2. Makes every article thumbnail an AI-generated, article-specific image.
3. Adds a 6-10 image AI visual package to every article: photorealistic scenes,
   artistic illustrations, symbolic explainers, overhead/map-style visuals, and
   other article-relevant images.
4. Updates linked homepage/archive/section cards and common JSON indexes.

Run by GitHub Actions after the daily newsroom generator, or run manually.
"""
from __future__ import annotations

import base64
import html
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from openai import OpenAI

def find_repo_root(script_path: Path) -> Path:
    """Find the repository root whether this file is run from repo root or studio/automation."""
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
AI_ART_PACKAGE_BACKFILL = env_bool("AI_ART_PACKAGE_BACKFILL", True)
FORCE_AI_FOR_ALL_ARTICLE_THUMBNAILS = env_bool("FORCE_AI_FOR_ALL_ARTICLE_THUMBNAILS", True)
FORCE_AI_FOR_DAILY_STORIES = env_bool("FORCE_AI_FOR_DAILY_STORIES", True)
REPLACE_SVG_ARTICLE_THUMBNAILS = env_bool("REPLACE_SVG_ARTICLE_THUMBNAILS", True)
AI_REBUILD_ARTICLE_GALLERIES = env_bool("AI_REBUILD_ARTICLE_GALLERIES", False)

OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1.5")
OPENAI_IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1536x1024")
OPENAI_IMAGE_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "low")
OPENAI_ART_PROMPT_MODEL = os.getenv("AI_ART_PROMPT_MODEL", os.getenv("OPENAI_MODEL", "gpt-5.4-mini"))

AI_GALLERY_MIN_IMAGES = env_int("AI_GALLERY_MIN_IMAGES", 6, minimum=1, maximum=10)
AI_GALLERY_MAX_IMAGES = env_int("AI_GALLERY_MAX_IMAGES", 10, minimum=AI_GALLERY_MIN_IMAGES, maximum=10)
AI_GALLERY_IMAGES_PER_ARTICLE = env_int(
    "AI_GALLERY_IMAGES_PER_ARTICLE",
    8,
    minimum=AI_GALLERY_MIN_IMAGES,
    maximum=AI_GALLERY_MAX_IMAGES,
)

# 0 means unlimited. This counts new thumbnail + gallery generations together.
AI_TOTAL_IMAGE_MAX_GENERATIONS = env_int(
    "AI_TOTAL_IMAGE_MAX_GENERATIONS",
    env_int("AI_THUMBNAIL_MAX_GENERATIONS", 0, minimum=0),
    minimum=0,
)

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
class GalleryAsset:
    index: int
    role: str
    style: str
    title: str
    alt: str
    caption: str
    prompt: str
    src_for_page: str
    src_from_root: str
    abs_path: Path
    credit_plain: str = "AI-generated image by The Press."

    @property
    def caption_html(self) -> str:
        title = html.escape(self.title)
        caption = html.escape(self.caption)
        return (
            f"<strong>{title}</strong> {caption} "
            f'<span class="figure-credit">AI-generated image by The Press.</span>'
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "src": self.src_from_root,
            "alt": self.alt,
            "captionHtml": self.caption_html,
            "style": self.style,
            "role": self.role,
            "relevanceNote": self.caption,
            "creator": "The Press AI art workflow",
            "license": "AI-generated; review before reuse",
            "width": 1536,
            "height": 1024,
        }


@dataclass
class ArticleImageUpdate:
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
    gallery_assets: list[GalleryAsset] = field(default_factory=list)


def rel_from_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def rel_to_file(path: Path, from_file: Path) -> str:
    return os.path.relpath(path.resolve(), from_file.parent.resolve()).replace("\\", "/")


def slugify(text: str) -> str:
    value = text.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:90].strip("-") or "article"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


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


def is_ai_asset(src: str | None, html_path: Path) -> bool:
    local_path = path_from_img_src(src, html_path)
    if not local_path:
        return False
    return is_under(local_path, AI_THUMBNAIL_DIR) or is_under(local_path, AI_ART_DIR)


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

    if is_ai_asset(src_text, html_path):
        return False

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
    if is_ai_asset(src, html_path):
        return False
    if FORCE_AI_FOR_ALL_ARTICLE_THUMBNAILS:
        return True
    return is_bad_article_image(src, html_path)


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


def clean_text(value: str, max_len: int = 600) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


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
    return clean_text(clone.get_text(" ", strip=True), 4200)


def generation_budget_available(generated_count: int) -> bool:
    return not AI_TOTAL_IMAGE_MAX_GENERATIONS or generated_count < AI_TOTAL_IMAGE_MAX_GENERATIONS


def prompt_for_article(title: str, dek: str, section: str, body_snippet: str) -> str:
    return f"""
Create a 16:9 landscape AI-generated thumbnail for a serious digital newspaper article.

Section: {section}
Title: {title}
Summary: {dek}
Article context: {body_snippet}

Visual direction:
- Make the image clearly connected to the article topic, not a generic stock image.
- Choose either photorealistic documentary realism or polished editorial art, whichever best serves the article.
- Strong central subject, readable at small thumbnail size, cinematic newspaper composition.
- It can use symbolic objects, a relevant place, an institutional scene, a schematic overhead/map-like view, or an abstract editorial metaphor.

Safety and publishing requirements:
- No logos, no watermarks, no signatures, and no readable text.
- Do not imitate a living artist, brand, copyrighted character, or publication style.
- If the story involves a living/current real person, do not make a photorealistic likeness; use a non-photorealistic editorial portrait, silhouette, or symbolic representation instead.
- Avoid graphic violence, gore, or sensational imagery.
- The image should feel original, accurate to the article, and publishable as AI-generated art.
""".strip()


def extract_json(text: str) -> Any:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


def gallery_plan_prompt(title: str, dek: str, section: str, body_snippet: str, count: int) -> str:
    return f"""
You are the visual editor for The Press. Build an AI image plan for a serious digital newspaper article.

Article section: {section}
Article title: {title}
Article summary: {dek}
Article text excerpt: {body_snippet}

Return JSON only, no markdown fences. Use exactly this shape:
{{
  "images": [
    {{
      "role": "establishing scene | overhead map | data explainer | symbolic portrait | human impact | institutional scene | object detail | closing illustration",
      "style": "photorealistic | artistic",
      "title": "short display title",
      "alt": "plain-language alt text",
      "caption": "one sentence explaining how this visual connects to the article",
      "prompt": "detailed image-generation prompt"
    }}
  ]
}}

Create exactly {count} images. Every image must be tied to something specific in the article. Mix photorealistic and artistic images. Include at least:
- one establishing image for the core place, institution, or system;
- one overhead map or map-like schematic when geography, routes, neighborhoods, borders, supply chains, campuses, facilities, or regions matter;
- one explainer-style visual that expresses a key mechanism, tension, statistic, timeline, or cause-and-effect from the article without readable text;
- one human-scale scene showing who is affected;
- one symbolic or artistic image that captures the article's central argument.

Rules for prompts:
- No readable text, labels, logos, watermarks, signatures, or fake documents.
- Do not imitate a living artist, brand, copyrighted character, publication, or film still.
- Do not make a photorealistic likeness of a living/current real person. If a named current figure is relevant, use a non-photorealistic editorial portrait, silhouette, or symbolic stand-in.
- For maps, use unlabeled overhead geography, abstract routes, terrain, borders, pins, or diagrammatic shapes; no text.
- Avoid gore and sensational imagery. Keep it publishable for a general news audience.
- Prefer concrete article details over generic news clichés.
""".strip()


def fallback_gallery_specs(title: str, dek: str, section: str, body_snippet: str, count: int) -> list[dict[str, str]]:
    base = clean_text(f"{title}. {dek}. {body_snippet}", 1200)
    ideas = [
        (
            "establishing scene",
            "photorealistic",
            "Where the story begins",
            f"Photorealistic establishing scene that captures the main setting, institution, or public space implied by this {section} article: {base}",
        ),
        (
            "symbolic argument",
            "artistic",
            "The central tension",
            f"Artistic editorial illustration representing the central conflict, tradeoff, or argument in the article: {base}",
        ),
        (
            "overhead map",
            "artistic",
            "The geography of the issue",
            f"Unlabeled overhead map-like schematic showing relevant geography, routes, regions, supply chains, borders, campuses, or facilities connected to the article: {base}",
        ),
        (
            "data explainer",
            "artistic",
            "How the system works",
            f"Clean visual explainer without readable text showing the article's key mechanism, sequence, pressure point, or cause-and-effect: {base}",
        ),
        (
            "human impact",
            "photorealistic",
            "People inside the story",
            f"Photorealistic human-scale scene showing everyday people affected by the issue, with no identifiable real-person likenesses: {base}",
        ),
        (
            "object detail",
            "photorealistic",
            "The telling detail",
            f"Photorealistic close-up of an object, environment detail, tool, document-like shape without readable text, or material clue that symbolizes the article: {base}",
        ),
        (
            "institutional scene",
            "photorealistic",
            "The institution at work",
            f"Photorealistic scene of a relevant institution, facility, courtroom-like room, lab, school, market, newsroom, port, theater, clinic, or office setting tied to the article: {base}",
        ),
        (
            "closing illustration",
            "artistic",
            "What changes next",
            f"Artistic closing image that expresses what could change next or what uncertainty remains after the article's reporting: {base}",
        ),
        (
            "symbolic portrait",
            "artistic",
            "Power without a headshot",
            f"Non-photorealistic symbolic portrait or silhouette representing leadership, decision-making, or public pressure in the article without copying any living person's likeness: {base}",
        ),
        (
            "scene contrast",
            "artistic",
            "Two sides of the story",
            f"Artistic split-composition showing two forces, places, communities, or outcomes in tension in the article, with no readable text: {base}",
        ),
    ]
    specs: list[dict[str, str]] = []
    for role, style, display_title, prompt in ideas[:count]:
        specs.append(
            {
                "role": role,
                "style": style,
                "title": display_title,
                "alt": f"AI-generated {style} visual for {title}",
                "caption": f"This {style} visual connects to the article's {role.replace('-', ' ')}.",
                "prompt": prompt,
            }
        )
    return specs


def normalize_gallery_specs(raw: Any, title: str, dek: str, section: str, body_snippet: str, count: int) -> list[dict[str, str]]:
    if isinstance(raw, dict):
        raw_items = raw.get("images", [])
    elif isinstance(raw, list):
        raw_items = raw
    else:
        raw_items = []

    specs: list[dict[str, str]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        style = str(item.get("style") or "").strip().lower()
        if style not in {"photorealistic", "artistic"}:
            style = "photorealistic" if len(specs) % 2 == 0 else "artistic"
        role = clean_text(str(item.get("role") or "article visual"), 80)
        display_title = clean_text(str(item.get("title") or role.title()), 90)
        alt = clean_text(str(item.get("alt") or f"AI-generated {style} image for {title}"), 180)
        caption = clean_text(str(item.get("caption") or f"This visual connects to the article's {role}."), 220)
        prompt = clean_text(str(item.get("prompt") or ""), 1400)
        if not prompt:
            continue
        specs.append(
            {
                "role": role,
                "style": style,
                "title": display_title,
                "alt": alt,
                "caption": caption,
                "prompt": prompt,
            }
        )
        if len(specs) == count:
            break

    if len(specs) < count:
        fallback = fallback_gallery_specs(title, dek, section, body_snippet, count)
        specs.extend(fallback[len(specs) : count])

    return specs[:count]


def create_gallery_specs(client: OpenAI, title: str, dek: str, section: str, body_snippet: str, count: int) -> list[dict[str, str]]:
    prompt = gallery_plan_prompt(title, dek, section, body_snippet, count)
    try:
        response = client.responses.create(
            model=OPENAI_ART_PROMPT_MODEL,
            input=prompt,
            max_output_tokens=5000,
        )
        payload = extract_json(getattr(response, "output_text", "") or "")
        return normalize_gallery_specs(payload, title, dek, section, body_snippet, count)
    except Exception as exc:
        print(f"Gallery plan fallback for {title!r}: {exc}", file=sys.stderr)
        return fallback_gallery_specs(title, dek, section, body_snippet, count)


def compose_gallery_image_prompt(
    spec: dict[str, str],
    title: str,
    dek: str,
    section: str,
    body_snippet: str,
    index: int,
) -> str:
    style = spec.get("style", "artistic")
    return f"""
Create image {index} in a {AI_GALLERY_IMAGES_PER_ARTICLE}-image visual package for a serious digital newspaper article.

Article section: {section}
Article title: {title}
Article summary: {dek}
Relevant article context: {clean_text(body_snippet, 1600)}

Image role: {spec.get('role', 'article visual')}
Requested style: {style}
Specific brief: {spec.get('prompt', '')}
Caption/use: {spec.get('caption', '')}

Publishing requirements:
- 16:9 landscape composition, polished for a newspaper article.
- Make this image directly about the article content; avoid generic stock-photo imagery.
- For photorealistic images, use documentary realism with natural light and plausible settings.
- For artistic images, use original editorial illustration, symbolic composition, or clean explainer art.
- Maps or explainers may use unlabeled shapes, terrain, routes, arrows, dots, or diagram-like elements, but no readable text.
- No logos, watermarks, signatures, fake screenshots, fake documents, or readable text.
- Do not imitate a living artist, brand, copyrighted character, movie still, or publication style.
- If the brief involves a living/current real person, do not create a photorealistic likeness; use a non-photorealistic symbolic portrait, silhouette, or stand-in.
- Avoid gore, graphic violence, sensational imagery, and misleading visual claims.
""".strip()


def generate_ai_image(client: OpenAI, prompt: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = client.images.generate(
        model=OPENAI_IMAGE_MODEL,
        prompt=prompt,
        size=OPENAI_IMAGE_SIZE,
        quality=OPENAI_IMAGE_QUALITY,
        n=1,
    )
    image_base64 = result.data[0].b64_json
    if not image_base64:
        raise RuntimeError("OpenAI image response did not include b64_json")
    output_path.write_bytes(base64.b64decode(image_base64))


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


def existing_gallery_ready(soup: BeautifulSoup, path: Path) -> bool:
    if AI_REBUILD_ARTICLE_GALLERIES:
        return False
    gallery = soup.select_one("[data-ai-article-gallery], .ai-article-gallery")
    if not gallery:
        return False
    imgs = gallery.select("img[src]")
    if len(imgs) < AI_GALLERY_IMAGES_PER_ARTICLE:
        return False
    valid = 0
    for img in imgs:
        local = path_from_img_src(str(img.get("src") or ""), path)
        if local and local.exists() and is_under(local, AI_ART_DIR):
            valid += 1
    return valid >= AI_GALLERY_IMAGES_PER_ARTICLE


def render_gallery_section(soup: BeautifulSoup, assets: list[GalleryAsset]) -> Any:
    figures: list[str] = []
    for asset in assets:
        figures.append(
            f"""
<figure class="ai-article-gallery__item" data-ai-art-index="{asset.index}" data-ai-art-style="{html.escape(asset.style)}">
  <img src="{html.escape(asset.src_for_page)}" alt="{html.escape(asset.alt)}" loading="lazy" decoding="async" />
  <figcaption>{asset.caption_html}</figcaption>
</figure>
""".strip()
        )

    markup = f"""
<section class="ai-article-gallery" data-ai-article-gallery>
  <div class="ai-article-gallery__header">
    <p class="eyebrow eyebrow--tiny">AI visual brief</p>
    <h2>Scenes and explainers from this story</h2>
    <p>AI-generated visuals built from this article’s reporting, including documentary-style scenes, editorial illustrations, map-style context, and explainer images.</p>
  </div>
  <div class="ai-article-gallery__grid">
    {''.join(figures)}
  </div>
</section>
""".strip()
    return first_real_node(markup) or BeautifulSoup(markup, "html.parser")


def first_real_node(fragment: str) -> Any | None:
    soup = BeautifulSoup(fragment, "html.parser")
    for child in soup.contents:
        if getattr(child, "name", None):
            return child
    return None


def insert_or_replace_gallery(soup: BeautifulSoup, container: Any, assets: list[GalleryAsset]) -> bool:
    if not assets:
        return False
    new_section = render_gallery_section(soup, assets)
    existing = soup.select_one("[data-ai-article-gallery], .ai-article-gallery")
    if existing:
        if str(existing) == str(new_section):
            return False
        existing.replace_with(new_section)
        return True

    source_anchor = container.select_one(".article-sources, .source-notes, .sources, [data-source-notes]") if container else None
    body_anchor = container.select_one(".article-body, [data-article-body]") if container else None

    if source_anchor:
        source_anchor.insert_before(new_section)
    elif body_anchor:
        body_anchor.insert_after(new_section)
    elif container:
        container.append(new_section)
    elif soup.body:
        soup.body.append(new_section)
    else:
        soup.append(new_section)
    return True


def build_gallery_assets(
    client: OpenAI,
    path: Path,
    slug: str,
    title: str,
    dek: str,
    section: str,
    body_snippet: str,
    generated_count: int,
) -> tuple[list[GalleryAsset], int]:
    specs = create_gallery_specs(client, title, dek, section, body_snippet, AI_GALLERY_IMAGES_PER_ARTICLE)
    assets: list[GalleryAsset] = []
    article_art_dir = AI_ART_DIR / slug

    for idx, spec in enumerate(specs, start=1):
        style = str(spec.get("style") or ("photorealistic" if idx % 2 else "artistic")).lower()
        if style not in {"photorealistic", "artistic"}:
            style = "photorealistic" if idx % 2 else "artistic"
        output_path = article_art_dir / f"{slug}-{idx:02d}-{style}.png"
        prompt = compose_gallery_image_prompt(spec, title, dek, section, body_snippet, idx)

        if not output_path.exists():
            if not generation_budget_available(generated_count):
                print(f"Skipping gallery image {idx} for {rel_from_root(path)}; generation limit reached")
                continue
            print(f"Generating AI article image {idx}/{AI_GALLERY_IMAGES_PER_ARTICLE} for {rel_from_root(path)}")
            generate_ai_image(client, prompt, output_path)
            generated_count += 1
            time.sleep(1)
        else:
            print(f"Reusing AI article image {idx}/{AI_GALLERY_IMAGES_PER_ARTICLE} for {rel_from_root(path)}")

        if output_path.exists():
            caption = clean_text(str(spec.get("caption") or "AI-generated visual for this article."), 240)
            assets.append(
                GalleryAsset(
                    index=idx,
                    role=clean_text(str(spec.get("role") or "article visual"), 80),
                    style=style,
                    title=clean_text(str(spec.get("title") or f"AI visual {idx}"), 90),
                    alt=clean_text(str(spec.get("alt") or f"AI-generated {style} visual for {title}"), 180),
                    caption=caption,
                    prompt=prompt,
                    src_for_page=rel_to_file(output_path, path),
                    src_from_root=rel_from_root(output_path),
                    abs_path=output_path,
                )
            )

    if len(assets) < AI_GALLERY_MIN_IMAGES:
        print(
            f"WARNING: only {len(assets)} gallery image(s) available for {rel_from_root(path)}; "
            f"target is {AI_GALLERY_MIN_IMAGES}-{AI_GALLERY_MAX_IMAGES}",
            file=sys.stderr,
        )
    return assets, generated_count


def update_article_page(client: OpenAI, path: Path, generated_count: int) -> tuple[ArticleImageUpdate | None, int]:
    soup = BeautifulSoup(read_text(path), "html.parser")
    container = article_container(soup)
    img = find_article_img(container)
    old_src = str(img.get("src") or "") if img else ""

    title = page_title(soup)
    dek = page_dek(soup, container)
    section = page_section(soup)
    body_snippet = page_body_snippet(container)
    slug = slugify(path.stem if path.stem != "article" else title)
    output_path = AI_THUMBNAIL_DIR / f"{slug}-ai.png"
    changed = False

    if should_replace_thumbnail(old_src, path):
        if not output_path.exists():
            if not generation_budget_available(generated_count):
                print(f"Skipping thumbnail for {rel_from_root(path)}; generation limit reached")
                return None, generated_count
            prompt = prompt_for_article(title, dek, section, body_snippet)
            print(f"Generating AI thumbnail for {rel_from_root(path)}")
            generate_ai_image(client, prompt, output_path)
            generated_count += 1
            time.sleep(1)
        else:
            print(f"Reusing existing AI thumbnail for {rel_from_root(path)}")

        img = ensure_figure_and_img(soup, container, img)
        alt = f"AI-generated editorial image for: {title}"
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
    else:
        current_path = path_from_img_src(old_src, path)
        output_path = current_path if current_path and current_path.exists() else output_path
        alt = str(img.get("alt") or f"AI-generated editorial image for: {title}") if img else f"AI-generated editorial image for: {title}"
        caption_html = (
            f"{html.escape(alt)}. "
            f'<span class="figure-credit">AI-generated image by The Press.</span>'
        )
        credit_plain = f"{alt}. AI-generated image by The Press."

    gallery_assets: list[GalleryAsset] = []
    if AI_ART_PACKAGE_BACKFILL:
        if existing_gallery_ready(soup, path):
            print(f"Existing AI article gallery is complete for {rel_from_root(path)}")
        else:
            gallery_assets, generated_count = build_gallery_assets(
                client=client,
                path=path,
                slug=slug,
                title=title,
                dek=dek,
                section=section,
                body_snippet=body_snippet,
                generated_count=generated_count,
            )
            if gallery_assets:
                changed = insert_or_replace_gallery(soup, container, gallery_assets) or changed

    if changed:
        write_text(path, str(soup))

    if not output_path.exists():
        return None, generated_count

    page_url = rel_from_root(path)
    return (
        ArticleImageUpdate(
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
            gallery_assets=gallery_assets,
        ),
        generated_count,
    )


def html_files() -> list[Path]:
    files = [p for p in ROOT.glob("*.html") if p.is_file()]
    if DAILY_DIR.exists():
        files.extend(p for p in DAILY_DIR.glob("*.html") if p.is_file())
    return sorted(files)


def update_cards_in_html_file(path: Path, updates: list[ArticleImageUpdate]) -> bool:
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
            elif FORCE_AI_FOR_ALL_ARTICLE_THUMBNAILS and not is_ai_asset(current_src, path):
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


def gallery_records(update: ArticleImageUpdate) -> list[dict[str, Any]]:
    return [asset.to_record() for asset in update.gallery_assets]


def update_master_edition(updates: list[ArticleImageUpdate]) -> bool:
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
            story["imageWidth"] = 1536
            story["imageHeight"] = 1024
            if update.gallery_assets:
                story["galleryImages"] = gallery_records(update)
            changed = True

    if changed:
        write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return changed


def recursively_update_json_images(obj: Any, updates_by_url: dict[str, ArticleImageUpdate]) -> bool:
    changed = False
    if isinstance(obj, dict):
        url = str(obj.get("url") or obj.get("href") or obj.get("filename") or "")
        update = updates_by_url.get(url) or updates_by_url.get(url.lstrip("./"))
        if update:
            for key in IMAGE_KEYS:
                if key in obj:
                    obj[key] = update.new_src_from_root
                    changed = True
            if "image_credit" in obj:
                obj["image_credit"] = update.credit_plain
                changed = True
            if "imageCreditPlain" in obj:
                obj["imageCreditPlain"] = update.credit_plain
                changed = True
            if "imageAlt" in obj:
                obj["imageAlt"] = update.alt
                changed = True
            if "thumbnail_alt" in obj:
                obj["thumbnail_alt"] = update.alt
                changed = True
            if update.gallery_assets:
                obj["galleryImages"] = gallery_records(update)
                changed = True
        for value in obj.values():
            if recursively_update_json_images(value, updates_by_url):
                changed = True
    elif isinstance(obj, list):
        for item in obj:
            if recursively_update_json_images(item, updates_by_url):
                changed = True
    return changed


def update_json_indexes(updates: list[ArticleImageUpdate]) -> None:
    updates_by_url: dict[str, ArticleImageUpdate] = {}
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


def patch_styles() -> None:
    path = ROOT / "styles.css"
    existing = read_text(path) if path.exists() else ""
    start = "/* PRESS_AI_ART_PACKAGE_START */"
    end = "/* PRESS_AI_ART_PACKAGE_END */"
    patch = """
/* PRESS_AI_ART_PACKAGE_START */
.ai-article-gallery {
  margin: 3rem 0;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(40, 32, 25, 0.16);
}

.ai-article-gallery__header {
  max-width: 760px;
  margin-bottom: 1.25rem;
}

.ai-article-gallery__header h2 {
  margin: 0.2rem 0 0.45rem;
  font-size: clamp(1.45rem, 2vw, 2.1rem);
  line-height: 1.08;
}

.ai-article-gallery__header p:last-child {
  margin: 0;
  color: #5f574e;
  line-height: 1.55;
}

.ai-article-gallery__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.ai-article-gallery__item {
  margin: 0;
  background: #fffaf4;
  border: 1px solid rgba(40, 32, 25, 0.14);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 14px 34px rgba(32, 24, 16, 0.08);
}

.ai-article-gallery__item img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  display: block;
}

.ai-article-gallery__item figcaption {
  padding: 0.85rem 0.95rem 1rem;
  font-size: 0.94rem;
  line-height: 1.48;
  color: #4e463d;
}

.ai-article-gallery__item figcaption strong {
  color: #17120d;
  font-weight: 800;
}

.ai-article-gallery .figure-credit {
  color: #756b60;
}

@media (max-width: 680px) {
  .ai-article-gallery {
    margin: 2.25rem 0;
  }

  .ai-article-gallery__grid {
    grid-template-columns: 1fr;
  }
}
/* PRESS_AI_ART_PACKAGE_END */
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

    if updated != existing:
        write_text(path, updated)
        print("Updated styles.css for AI article galleries")


def main() -> int:
    if not AI_THUMBNAIL_BACKFILL:
        print("AI thumbnail backfill disabled by AI_THUMBNAIL_BACKFILL")
        return 0

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is missing")

    client = OpenAI(api_key=api_key)
    AI_THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
    AI_ART_DIR.mkdir(parents=True, exist_ok=True)

    master_filenames = load_master_story_filenames()
    article_paths: list[Path] = []
    for path in html_files():
        soup = BeautifulSoup(read_text(path), "html.parser")
        if looks_like_article_page(path, soup, master_filenames):
            article_paths.append(path)

    print(
        f"Scanning {len(article_paths)} article pages for AI thumbnails and "
        f"{AI_GALLERY_MIN_IMAGES}-{AI_GALLERY_MAX_IMAGES} image article-art packages"
    )

    updates: list[ArticleImageUpdate] = []
    generated_count = 0
    for path in article_paths:
        try:
            update, generated_count = update_article_page(client, path, generated_count)
            if update:
                updates.append(update)
        except Exception as exc:
            print(f"AI art update failed for {rel_from_root(path)}: {exc}", file=sys.stderr)

    if updates:
        all_html = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
        for path in all_html:
            if update_cards_in_html_file(path, updates):
                print(f"Updated linked cards in {rel_from_root(path)}")

        if update_master_edition(updates):
            print("Updated master-edition.json")
        update_json_indexes(updates)
    else:
        print("No article image updates were made")

    if AI_ART_PACKAGE_BACKFILL:
        patch_styles()

    print(
        f"AI article-art backfill complete: {len(updates)} article(s) checked/updated; "
        f"{generated_count} new image(s) generated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

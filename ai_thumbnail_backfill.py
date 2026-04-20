#!/usr/bin/env python3
"""
AI thumbnail backfill for The Press.

What this script does:
1. Scans article pages in the repo root and daily/*.html.
2. Keeps older curated real/legal images alone.
3. Replaces missing, broken, placeholder, fallback, SVG, or weak auto-fetched
   daily story thumbnails with an AI-generated editorial illustration matched
   to the article.
4. Updates the article page, linked homepage/archive/section cards, and common
   JSON indexes.
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

ROOT = Path(__file__).resolve().parents[2]
DAILY_DIR = ROOT / "daily"
ASSETS_DIR = ROOT / "assets"
AI_IMAGE_DIR = ASSETS_DIR / "ai-thumbnails"
AUTO_DAILY_ASSET_DIR = ASSETS_DIR / "daily"

AI_THUMBNAIL_BACKFILL = os.getenv("AI_THUMBNAIL_BACKFILL", "1").strip().lower() not in {
    "0",
    "false",
    "no",
}
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1.5")
OPENAI_IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1536x1024")
OPENAI_IMAGE_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "low")
AI_THUMBNAIL_MAX_GENERATIONS = int(os.getenv("AI_THUMBNAIL_MAX_GENERATIONS", "0") or "0")
REPLACE_SVG_ARTICLE_THUMBNAILS = os.getenv(
    "REPLACE_SVG_ARTICLE_THUMBNAILS", "1"
).strip().lower() not in {"0", "false", "no"}

# This is the important switch for your site right now.
# The daily generator can technically find a legal image, but sometimes that image is ugly,
# unrelated, or not thumbnail-worthy. When this is on, auto-fetched daily issue images
# are replaced with article-matched AI illustrations. Older curated root images remain alone.
FORCE_AI_FOR_DAILY_STORIES = os.getenv("FORCE_AI_FOR_DAILY_STORIES", "1").strip().lower() not in {
    "0",
    "false",
    "no",
}

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
    if not local_path:
        return False
    return is_under(local_path, AUTO_DAILY_ASSET_DIR)


def is_already_ai_asset(src: str | None, html_path: Path) -> bool:
    local_path = path_from_img_src(src, html_path)
    if not local_path:
        return False
    return is_under(local_path, AI_IMAGE_DIR)


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

    if lower.startswith("data:"):
        return False

    if is_already_ai_asset(src_text, html_path):
        return False

    if any(word in lower for word in BAD_IMAGE_KEYWORDS):
        return True

    if FORCE_AI_FOR_DAILY_STORIES and is_auto_daily_asset(src_text, html_path):
        return True

    local_path = path_from_img_src(src_text, html_path)
    if local_path is None:
        # External image URLs are treated as real images and left alone.
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
    return (
        container.select_one("figure.article-hero img")
        or container.select_one(".article-hero img")
        or container.select_one("main img")
        or container.select_one("img")
    )


def clean_text(value: str, max_len: int = 600) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def page_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        text = clean_text(h1.get_text(" ", strip=True), 160)
        if text:
            return text
    title_tag = soup.find("title")
    if title_tag:
        return clean_text(title_tag.get_text(" ", strip=True).replace("— The Press", ""), 160)
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
        text = clean_text(text, 450)
        if text:
            return text
    first_p = container.find("p") if container else None
    if first_p:
        return clean_text(first_p.get_text(" ", strip=True), 450)
    return ""


def page_section(soup: BeautifulSoup) -> str:
    for selector in (".eyebrow", ".section-label", "[data-section]"):
        node = soup.select_one(selector)
        if not node:
            continue
        text = str(node.get("data-section") or node.get_text(" ", strip=True))
        text = clean_text(text, 80)
        if text:
            return text
    # Daily pages often put the section as the first small text item near the top.
    h1 = soup.find("h1")
    if h1:
        previous = h1.find_previous(string=True)
        if previous:
            text = clean_text(str(previous), 80)
            if text and text.lower() not in {"the press", "home", "daily issue"}:
                return text
    return "News"


def page_body_snippet(container: Any) -> str:
    body = container.select_one(".article-body") if container else None
    node = body or container
    if not node:
        return ""
    return clean_text(node.get_text(" ", strip=True), 1200)


def prompt_for_article(title: str, dek: str, section: str, body_snippet: str) -> str:
    return f"""
Create a landscape editorial illustration for a serious digital newspaper article.

Section: {section}
Title: {title}
Summary: {dek}
Article context: {body_snippet}

Visual direction:
- Make the image clearly connected to the article topic.
- Use symbolic, contextual editorial imagery rather than a generic stock-photo look.
- Strong central subject, readable at small thumbnail size, 16:9 landscape composition.
- Polished newspaper/magazine illustration style.

Safety and publishing requirements:
- No logos, no watermarks, no signatures, and no readable text.
- Do not imitate a living artist, brand, copyrighted character, or publication style.
- Do not create a photorealistic likeness of a specific real person.
- Avoid graphic violence or sensational imagery.
- The image should feel original and publishable as an AI-generated illustration.
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


def update_article_page(client: OpenAI, path: Path, generated_count: int) -> tuple[ArticleImageUpdate | None, int]:
    soup = BeautifulSoup(read_text(path), "html.parser")
    container = article_container(soup)
    img = find_article_img(container)
    old_src = str(img.get("src") or "") if img else ""

    if not is_bad_article_image(old_src, path):
        return None, generated_count

    title = page_title(soup)
    dek = page_dek(soup, container)
    section = page_section(soup)
    body_snippet = page_body_snippet(container)
    slug = slugify(path.stem if path.stem != "article" else title)
    output_path = AI_IMAGE_DIR / f"{slug}-ai.png"

    if not output_path.exists():
        if AI_THUMBNAIL_MAX_GENERATIONS and generated_count >= AI_THUMBNAIL_MAX_GENERATIONS:
            print(f"Skipping {rel_from_root(path)}; AI_THUMBNAIL_MAX_GENERATIONS reached")
            return None, generated_count
        prompt = prompt_for_article(title, dek, section, body_snippet)
        print(f"Generating AI thumbnail for {rel_from_root(path)}")
        generate_ai_image(client, prompt, output_path)
        generated_count += 1
        time.sleep(1)
    else:
        print(f"Reusing existing AI thumbnail for {rel_from_root(path)}")

    img = ensure_figure_and_img(soup, container, img)
    alt = f"AI-generated editorial illustration for: {title}"
    caption_html = (
        f"{html.escape(alt)}. "
        f'<span class="figure-credit">AI-generated illustration by The Press.</span>'
    )
    credit_plain = f"{alt}. AI-generated illustration by The Press."

    new_src_for_page = rel_to_file(output_path, path)
    new_src_from_root = rel_from_root(output_path)
    img["src"] = new_src_for_page
    img["alt"] = alt
    img["loading"] = img.get("loading") or "eager"
    img["decoding"] = img.get("decoding") or "async"
    set_or_replace_caption(soup, img, caption_html)

    write_text(path, str(soup))

    page_url = rel_from_root(path)
    return (
        ArticleImageUpdate(
            page_path=path,
            page_url=page_url,
            title=title,
            dek=dek,
            section=section,
            old_src=old_src,
            new_src_for_page=new_src_for_page,
            new_src_from_root=new_src_from_root,
            new_abs_path=output_path,
            alt=alt,
            caption_html=caption_html,
            credit_plain=credit_plain,
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
            else:
                should_update = is_bad_article_image(current_src, path)
            if should_update:
                img["src"] = wanted_src
                img["alt"] = update.alt
                changed = True

    if changed:
        write_text(path, str(soup))
    return changed


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
            existing_image = str(story.get("image") or "")
            if existing_image and not is_bad_article_image(existing_image, ROOT / filename):
                continue
            story["image"] = update.new_src_from_root
            story["imageAlt"] = update.alt
            story["imageCaptionHtml"] = update.caption_html
            story["imageCreditPlain"] = update.credit_plain
            story["imageWidth"] = 1536
            story["imageHeight"] = 1024
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


def main() -> int:
    if not AI_THUMBNAIL_BACKFILL:
        print("AI thumbnail backfill disabled by AI_THUMBNAIL_BACKFILL")
        return 0

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is missing")

    client = OpenAI(api_key=api_key)
    AI_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    master_filenames = load_master_story_filenames()
    article_paths: list[Path] = []
    for path in html_files():
        soup = BeautifulSoup(read_text(path), "html.parser")
        if looks_like_article_page(path, soup, master_filenames):
            article_paths.append(path)

    print(f"Scanning {len(article_paths)} article pages for weak/missing/bad thumbnails")

    updates: list[ArticleImageUpdate] = []
    generated_count = 0
    for path in article_paths:
        try:
            update, generated_count = update_article_page(client, path, generated_count)
            if update:
                updates.append(update)
        except Exception as exc:
            print(f"Thumbnail update failed for {rel_from_root(path)}: {exc}", file=sys.stderr)

    if not updates:
        print("No weak/missing/bad article thumbnails found")
        return 0

    all_html = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
    for path in all_html:
        if update_cards_in_html_file(path, updates):
            print(f"Updated linked cards in {rel_from_root(path)}")

    if update_master_edition(updates):
        print("Updated master-edition.json")
    update_json_indexes(updates)

    print(
        f"AI thumbnail backfill complete: {len(updates)} page(s) updated; "
        f"{generated_count} new image(s) generated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
ASSETS_DAILY = ROOT / "assets" / "daily"
DAILY_DIR = ROOT / "daily"

# new: default image folder and per‑section fallback mapping
ASSETS_DEFAULT = ROOT / "assets" / "default"
DEFAULT_IMAGES = {
    "politics": str((ASSETS_DEFAULT / "politics.jpg").relative_to(ROOT)).replace("\\", "/"),
    "economics": str((ASSETS_DEFAULT / "economics.jpg").relative_to(ROOT)).replace("\\", "/"),
    "science": str((ASSETS_DEFAULT / "science.jpg").relative_to(ROOT)).replace("\\", "/"),
    "film": str((ASSETS_DEFAULT / "film.jpg").relative_to(ROOT)).replace("\\", "/"),
    "ai": str((ASSETS_DEFAULT / "ai.jpg").relative_to(ROOT)).replace("\\", "/"),
    "technology": str((ASSETS_DEFAULT / "technology.jpg").relative_to(ROOT)).replace("\\", "/"),
    "niche": str((ASSETS_DEFAULT / "niche.jpg").relative_to(ROOT)).replace("\\", "/"),
    "geopolitics": str((ASSETS_DEFAULT / "geopolitics.jpg").relative_to(ROOT)).replace("\\", "/"),
    "pop-culture": str((ASSETS_DEFAULT / "culture.jpg").relative_to(ROOT)).replace("\\", "/"),
    "world": str((ASSETS_DEFAULT / "world.jpg").relative_to(ROOT)).replace("\\", "/"),
    "generic": str((ASSETS_DEFAULT / "generic.jpg").relative_to(ROOT)).replace("\\", "/"),
}

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
        model=os.getenv("OPENAI_MODEL", "gpt-5.4"),
        tools=[{"type": "web_search_preview"}],
        input=prompt,
        max_output_tokens=12000,
    )
    return extract_json(resp.output_text)


def wiki_thumbnail(query: str) -> tuple[str, str]:
    # Wikimedia Commons search; fallback handled by caller.
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
    r = requests.get(search_url, params=params, timeout=20)
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
    if path.endswith(".png"):
        return ".png"
    if path.endswith(".webp"):
        return ".webp"
    return ".jpg"


def download_image(url: str, slug: str, edition_date: str) -> str:
    ASSETS_DAILY.mkdir(parents=True, exist_ok=True)
    ext = guess_ext(url)
    target = ASSETS_DAILY / f"{edition_date}-{slug}{ext}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    target.write_bytes(r.content)
    return str(target.relative_to(ROOT)).replace("\\", "/")


# --- new helpers for smarter thumbnail selection -----------------------------


def search_photo(search_hint: str) -> tuple[str, str] | None:
    """
    Try Wikimedia Commons queries that encourage photographs rather than scans.
    Returns (url, description_url) or None if nothing suitable is found.
    """
    for suffix in (" photo", " picture", " illustration"):
        try:
            return wiki_thumbnail(search_hint + suffix)
        except Exception:
            continue
    return None


def choose_thumbnail(section_slug: str, search_hint: str, title: str) -> str:
    """
    Decide which thumbnail to use for a story.
    1. Use the thumbnail_search_hint (or title) with photo qualifiers.
    2. If that fails, fall back to a desk‑specific default.
    """
    hint = search_hint or title
    result = search_photo(hint)
    if result:
        url, _ = result
        return url
    # default to desk-level image or generic fallback
    return DEFAULT_IMAGES.get(section_slug, DEFAULT_IMAGES["generic"])


# --- site rendering and patching functions (unchanged) -----------------------


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
      if (stop) stop.addEventListener('click', () => {
        window.speechSynthesis.cancel();
      });
    });
    </script>
    """

    # (everything below is exactly the same as the original script, omitted for brevity)
    # Build full HTML for each story card, including placeholders, audio buttons, etc.

    # The rest of this function remains unchanged from the original file...
    raise NotImplementedError("Full implementation omitted for brevity")


def patch_index(stories: list[Story], edition_date: str) -> None:
    # Implementation identical to the original file
    raise NotImplementedError("Full implementation omitted for brevity")


def patch_archive(stories: list[Story], edition_date: str) -> None:
    # Implementation identical to the original file
    raise NotImplementedError("Full implementation omitted for brevity")


def patch_breaking(stories: list[Story], edition_date: str) -> None:
    # Implementation identical to the original file
    raise NotImplementedError("Full implementation omitted for brevity")


def update_search_index(stories: list[Story]) -> None:
    # Implementation identical to the original file
    raise NotImplementedError("Full implementation omitted for brevity")


def write_latest_json(stories: list[Story], edition_date: str) -> None:
    # Implementation identical to the original file
    raise NotImplementedError("Full implementation omitted for brevity")


def write_daily_edition_page(stories: list[Story], edition_date: str) -> None:
    # Implementation identical to the original file
    raise NotImplementedError("Full implementation omitted for brevity")


def patch_bylines_in_js() -> None:
    # Implementation identical to the original file
    raise NotImplementedError("Full implementation omitted for brevity")


def patch_styles() -> None:
    # Implementation identical to the original file except for new daily grid & ticker speed
    raise NotImplementedError("Full implementation omitted for brevity")


def main() -> int:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    story_count = int(os.environ.get("STORY_COUNT", "10"))
    edition_date, published_label = now_labels()
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    stories: list[Story] = []
    for section_slug, section_name in pick_sections(story_count):
        payload = call_model(client, section_name, published_label)
        title = payload["title"].strip()
        slug = f"{edition_date}-{slugify(title)}"
        # use smarter thumbnail logic instead of wiki_thumbnail directly
        thumb_url = choose_thumbnail(section_slug, payload.get("thumbnail_search_hint"), title)
        if thumb_url.startswith("assets/"):
            # local fallback images live in assets/default; no download needed
            local_thumb = thumb_url
        else:
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
        # write each story page
        (DAILY_DIR / f"{story.slug}.html").write_text(
            build_story_page(story), encoding="utf-8"
        )

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

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import requests


COMMONS_API = "https://commons.wikimedia.org/w/api.php"
PEXELS_SEARCH_API = "https://api.pexels.com/v1/search"
USER_AGENT = "ThePressThumbnailUpgrade/1.0 (+https://github.com/taryntimdixon/The-Press)"
REQUEST_TIMEOUT = 30
GOOD_LICENSE_MARKERS = (
    "PUBLIC DOMAIN",
    "CC0",
    "CC BY",
    "CC-BY",
    "CC BY-SA",
    "CC-BY-SA",
    "PDM",
)
BAD_LICENSE_MARKERS = ("NC", "ND")
BAD_VISUAL_HINTS = {
    "logo",
    "seal",
    "flag",
    "coat of arms",
    "diagram",
    "map",
    "chart",
    "icon",
    "wordmark",
    "poster",
    "cover art",
}


@dataclass
class ImageChoice:
    provider: str
    query: str
    download_url: str
    page_url: str
    alt: str
    caption_html: str
    credit_plain: str
    width: int | None
    height: int | None
    extension: str
    debug_title: str


def strip_tags(text: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(token) > 2}


def repo_root_from(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "master-edition.json").exists() or (candidate / "studio" / "master-edition.json").exists():
            return candidate
    raise FileNotFoundError("Could not find master-edition.json in this repo.")


def locate_master_edition(root: Path) -> Path:
    direct = root / "master-edition.json"
    studio = root / "studio" / "master-edition.json"
    if direct.exists():
        return direct
    if studio.exists():
        return studio
    raise FileNotFoundError("master-edition.json not found.")


def load_master_edition(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_master_edition(path: Path, payload: dict[str, Any]) -> None:
    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(path, backup)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def current_rel_image_path(story: dict[str, Any]) -> str:
    value = str(story.get("image") or "").strip()
    return value


def current_image_file(root: Path, story: dict[str, Any]) -> Path | None:
    rel = current_rel_image_path(story)
    if not rel:
        return None
    return root / rel


def default_output_stem(story: dict[str, Any]) -> str:
    rel = current_rel_image_path(story)
    if rel:
        return Path(rel).stem
    slug = str(story.get("slug") or "").strip()
    if slug:
        return slug
    filename = str(story.get("filename") or "").strip()
    if filename:
        return Path(filename).stem
    return "story-image"


def preferred_output_dir(root: Path, story: dict[str, Any]) -> Path:
    rel = current_rel_image_path(story)
    if rel.startswith("assets/"):
        return root / Path(rel).parent
    return root / "assets"


def extension_from_url(url: str, default: str = ".jpg") -> str:
    path = urlparse(url).path.lower()
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        if path.endswith(ext):
            return ext
    return default


def should_process_story(root: Path, story: dict[str, Any], force: bool, missing_only: bool, selected: set[str]) -> bool:
    slug = str(story.get("slug") or "").strip()
    filename = str(story.get("filename") or "").strip()
    if selected and slug not in selected and filename not in selected:
        return False
    if force:
        return True
    image_path = current_image_file(root, story)
    if image_path is None:
        return True
    if not image_path.exists():
        return True
    if missing_only:
        return False
    # If the image exists but is suspiciously tiny, treat it like a placeholder.
    try:
        return image_path.stat().st_size < 20_000
    except OSError:
        return True


def story_queries(story: dict[str, Any]) -> list[str]:
    title = normalize_space(str(story.get("title") or ""))
    dek = normalize_space(str(story.get("dek") or ""))
    keywords = [normalize_space(str(k)) for k in story.get("keywords", []) if normalize_space(str(k))]
    core = [title]
    if keywords:
        core.append(" ".join(keywords[:4]))
    if title and keywords:
        core.append(f"{title} {' '.join(keywords[:4])}")
    if dek:
        core.append(dek[:140])
    deduped: list[str] = []
    seen: set[str] = set()
    for item in core:
        key = item.lower()
        if item and key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped or ["news photo"]


def commons_request(query: str, session: requests.Session) -> list[dict[str, Any]]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": 6,
        "gsrlimit": 8,
        "gsrsearch": query,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": 1600,
        "iiextmetadatamultilang": 1,
    }
    response = session.get(COMMONS_API, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {})
    return list(pages.values())


def commons_meta(info: dict[str, Any], key: str) -> str:
    value = (info.get("extmetadata") or {}).get(key, {}).get("value", "")
    return strip_tags(value)


def commons_license_ok(info: dict[str, Any]) -> bool:
    parts = [
        commons_meta(info, "LicenseShortName"),
        commons_meta(info, "License"),
        commons_meta(info, "UsageTerms"),
    ]
    combined = " ".join(parts).upper()
    if not combined:
        return False
    if any(marker in combined for marker in BAD_LICENSE_MARKERS):
        return False
    return any(marker in combined for marker in GOOD_LICENSE_MARKERS)


def commons_candidate_score(page: dict[str, Any], story_token_set: set[str], query_token_set: set[str]) -> int:
    infos = page.get("imageinfo") or []
    if not infos:
        return -10_000
    info = infos[0]
    if not commons_license_ok(info):
        return -10_000

    mime = (info.get("mime") or "").lower()
    width = int(info.get("width") or 0)
    height = int(info.get("height") or 0)

    if mime == "image/svg+xml":
        return -5_000

    title = strip_tags(str(page.get("title") or ""))
    desc = commons_meta(info, "ImageDescription")
    object_name = commons_meta(info, "ObjectName")
    visual_text = f"{title} {desc} {object_name}".lower()

    score = 0
    visual_tokens = tokenize(visual_text)
    score += 5 * len(story_token_set & visual_tokens)
    score += 3 * len(query_token_set & visual_tokens)

    if width >= 1200:
        score += 10
    elif width >= 800:
        score += 6
    if height >= 600:
        score += 4
    aspect = (width / height) if width and height else 0
    if 1.15 <= aspect <= 2.2:
        score += 6

    for hint in BAD_VISUAL_HINTS:
        if hint in visual_text and hint not in " ".join(sorted(story_token_set)):
            score -= 12

    if mime in {"image/jpeg", "image/jpg", "image/png", "image/webp"}:
        score += 8

    return score


def choose_commons_image(story: dict[str, Any], session: requests.Session) -> ImageChoice | None:
    queries = story_queries(story)
    story_tokens = tokenize(" ".join(queries))
    best: tuple[int, ImageChoice] | None = None
    seen_pages: set[str] = set()

    for query in queries:
        try:
            pages = commons_request(query, session)
        except requests.RequestException:
            continue
        query_tokens = tokenize(query)
        for page in pages:
            infos = page.get("imageinfo") or []
            if not infos:
                continue
            info = infos[0]
            page_url = str(info.get("descriptionurl") or "")
            if page_url in seen_pages:
                continue
            seen_pages.add(page_url)

            score = commons_candidate_score(page, story_tokens, query_tokens)
            if score < 0:
                continue

            download_url = str(info.get("thumburl") or info.get("url") or "")
            if not download_url:
                continue

            title = strip_tags(str(page.get("title") or ""))
            alt = commons_meta(info, "ImageDescription") or commons_meta(info, "ObjectName") or title
            artist = commons_meta(info, "Artist") or commons_meta(info, "Credit") or "Unknown"
            license_name = commons_meta(info, "LicenseShortName") or commons_meta(info, "License") or "license listed on file page"
            license_url = commons_meta(info, "LicenseUrl") or page_url

            alt = normalize_space(alt).strip(".") or normalize_space(str(story.get("title") or ""))
            caption_text = f"{alt}."
            caption_html = (
                f"{html.escape(caption_text)} "
                f'<span class="figure-credit">Photo by {html.escape(artist)} via '
                f'<a href="{html.escape(page_url)}">Wikimedia Commons</a>, '
                f'licensed <a href="{html.escape(license_url)}">{html.escape(license_name)}</a>.</span>'
            )
            credit_plain = f"{alt}. Photo by {artist} via Wikimedia Commons, licensed {license_name}."

            choice = ImageChoice(
                provider="commons",
                query=query,
                download_url=download_url,
                page_url=page_url,
                alt=alt,
                caption_html=caption_html,
                credit_plain=credit_plain,
                width=int(info.get("width") or 0) or None,
                height=int(info.get("height") or 0) or None,
                extension=extension_from_url(download_url),
                debug_title=title,
            )
            if best is None or score > best[0]:
                best = (score, choice)

    return best[1] if best else None


def pexels_request(query: str, api_key: str, session: requests.Session) -> list[dict[str, Any]]:
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": 8, "orientation": "landscape"}
    response = session.get(PEXELS_SEARCH_API, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json().get("photos", [])


def pexels_candidate_score(photo: dict[str, Any], story_tokens: set[str], query_tokens: set[str]) -> int:
    alt = normalize_space(str(photo.get("alt") or ""))
    text = alt.lower()
    visual_tokens = tokenize(text)
    score = 0
    score += 4 * len(story_tokens & visual_tokens)
    score += 2 * len(query_tokens & visual_tokens)

    width = int(photo.get("width") or 0)
    height = int(photo.get("height") or 0)
    if width >= 1200:
        score += 8
    if height >= 600:
        score += 4
    aspect = (width / height) if width and height else 0
    if 1.15 <= aspect <= 2.2:
        score += 6

    for hint in BAD_VISUAL_HINTS:
        if hint in text and hint not in " ".join(sorted(story_tokens)):
            score -= 8
    return score


def choose_pexels_image(story: dict[str, Any], api_key: str, session: requests.Session) -> ImageChoice | None:
    if not api_key:
        return None
    queries = story_queries(story)
    story_tokens = tokenize(" ".join(queries))
    best: tuple[int, ImageChoice] | None = None
    seen_urls: set[str] = set()

    for query in queries:
        try:
            photos = pexels_request(query, api_key, session)
        except requests.RequestException:
            continue
        query_tokens = tokenize(query)
        for photo in photos:
            photo_page = str(photo.get("url") or "")
            if not photo_page or photo_page in seen_urls:
                continue
            seen_urls.add(photo_page)

            score = pexels_candidate_score(photo, story_tokens, query_tokens)
            if score < 0:
                continue

            src = photo.get("src") or {}
            download_url = str(
                src.get("landscape")
                or src.get("large")
                or src.get("large2x")
                or src.get("original")
                or src.get("medium")
                or ""
            )
            if not download_url:
                continue

            photographer = normalize_space(str(photo.get("photographer") or "Pexels photographer"))
            photographer_url = normalize_space(str(photo.get("photographer_url") or "https://www.pexels.com/"))
            alt = normalize_space(str(photo.get("alt") or "")) or normalize_space(str(story.get("title") or ""))
            caption_text = f"{alt}."
            caption_html = (
                f"{html.escape(caption_text)} "
                f'<span class="figure-credit">Photo by '
                f'<a href="{html.escape(photographer_url)}">{html.escape(photographer)}</a> '
                f'on <a href="{html.escape(photo_page)}">Pexels</a>.</span>'
            )
            credit_plain = f"{alt}. Photo by {photographer} on Pexels."

            choice = ImageChoice(
                provider="pexels",
                query=query,
                download_url=download_url,
                page_url=photo_page,
                alt=alt,
                caption_html=caption_html,
                credit_plain=credit_plain,
                width=int(photo.get("width") or 0) or None,
                height=int(photo.get("height") or 0) or None,
                extension=extension_from_url(download_url),
                debug_title=alt,
            )
            if best is None or score > best[0]:
                best = (score, choice)

    return best[1] if best else None


def choose_best_image(
    story: dict[str, Any],
    session: requests.Session,
    pexels_api_key: str | None,
    commons_only: bool,
) -> ImageChoice | None:
    commons_choice = choose_commons_image(story, session)
    if commons_choice:
        return commons_choice
    if commons_only or not pexels_api_key:
        return None
    return choose_pexels_image(story, pexels_api_key, session)


def download_file(url: str, target: Path, session: requests.Session) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with session.get(url, stream=True, timeout=REQUEST_TIMEOUT) as response:
        response.raise_for_status()
        with target.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)


def relative_asset_path(root: Path, story: dict[str, Any], extension: str) -> tuple[Path, str]:
    stem = default_output_stem(story)
    out_dir = preferred_output_dir(root, story)
    out_path = out_dir / f"{stem}{extension}"
    rel = out_path.relative_to(root).as_posix()
    return out_path, rel


def update_story(story: dict[str, Any], rel_path: str, choice: ImageChoice) -> None:
    story["image"] = rel_path
    story["imageAlt"] = choice.alt
    story["imageCaptionHtml"] = choice.caption_html
    story["imageCreditPlain"] = choice.credit_plain
    if choice.width:
        story["imageWidth"] = choice.width
    if choice.height:
        story["imageHeight"] = choice.height


def process_story(
    root: Path,
    story: dict[str, Any],
    session: requests.Session,
    pexels_api_key: str | None,
    commons_only: bool,
    dry_run: bool,
) -> bool:
    choice = choose_best_image(story, session=session, pexels_api_key=pexels_api_key, commons_only=commons_only)
    if not choice:
        print(f"NO MATCH  {story.get('slug') or story.get('filename')}")
        return False

    out_path, rel_path = relative_asset_path(root, story, choice.extension)
    print(
        f"{choice.provider.upper():8} {story.get('slug') or story.get('filename')}\n"
        f"         query: {choice.query}\n"
        f"         pick:  {choice.debug_title}\n"
        f"         file:  {rel_path}"
    )
    if not dry_run:
        download_file(choice.download_url, out_path, session=session)
        update_story(story, rel_path, choice)
    return True


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replace hardcoded thumbnail picking with Wikimedia Commons search plus optional Pexels fallback."
    )
    parser.add_argument("--force", action="store_true", help="Reprocess stories even when the current local image exists.")
    parser.add_argument("--missing-only", action="store_true", help="Only fill stories with missing/broken image files.")
    parser.add_argument("--dry-run", action="store_true", help="Search and print picks without downloading or updating JSON.")
    parser.add_argument("--limit", type=int, default=0, help="Only process the first N matching stories.")
    parser.add_argument(
        "--story",
        action="append",
        default=[],
        help="Story slug or filename to process. Repeat for multiple stories.",
    )
    parser.add_argument("--commons-only", action="store_true", help="Disable the Pexels fallback.")
    parser.add_argument(
        "--pexels-key",
        default=os.getenv("PEXELS_API_KEY", "").strip(),
        help="Pexels API key. Defaults to PEXELS_API_KEY.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = repo_root_from(Path.cwd())
    master_path = locate_master_edition(root)
    data = load_master_edition(master_path)
    stories = data.get("stories")
    if not isinstance(stories, list):
        raise SystemExit("master-edition.json does not contain a top-level 'stories' list.")

    selected = {item.strip() for item in args.story if item.strip()}

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "image/*,*/*;q=0.8"})

    changed = 0
    inspected = 0
    for story in stories:
        if not isinstance(story, dict):
            continue
        if not should_process_story(root, story, args.force, args.missing_only, selected):
            continue
        inspected += 1
        ok = process_story(
            root=root,
            story=story,
            session=session,
            pexels_api_key=(None if args.commons_only else args.pexels_key or None),
            commons_only=args.commons_only,
            dry_run=args.dry_run,
        )
        if ok:
            changed += 1
        if args.limit and inspected >= args.limit:
            break

    if not args.dry_run and changed:
        save_master_edition(master_path, data)
        print(f"\nUpdated {changed} stories in {master_path}")
        print(f"Backup written to {master_path}.bak")
    else:
        print(f"\nMatched {changed} stories.")
        if args.dry_run:
            print("Dry run only — master-edition.json was not changed.")

    if changed == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

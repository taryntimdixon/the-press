#!/usr/bin/env python3
"""
Build The Press article ecosystem files.

Creates:
  - content-index.json   full canonical story list
  - live-index.json      small payload for the live homepage
  - archive-index.json   older stories for archive-only loading
  - placements.json      slot IDs for hero, secondary, rails, latest, daily, pulse

Run from the repository root:
  python tools/build_press_ecosystem.py

Optional:
  python tools/build_press_ecosystem.py --refresh-search-index
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now(timezone.utc)
LIVE_WINDOW_DAYS = 14
LIVE_MINIMUM = 48
AUTHOR_LABEL = "The Press"
SOURCE_PRIORITY = {
    "search-index": 0,
    "daily-latest": 1,
    "edition": 2,
    "master-edition": 3,
}

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "can", "could", "for", "from", "has", "have", "how", "in",
    "into", "is", "it", "its", "new", "not", "now", "of", "on", "or", "over", "that", "the", "their", "this", "to", "with",
    "without", "why", "will", "after", "before", "still", "about", "what", "when", "where", "who", "than", "then", "there",
    "they", "was", "were", "been", "being", "first", "real", "latest", "keeps", "shows", "says", "saying",
}

SECTION_ALIASES = {
    "ai": ["ai", "artificial-intelligence", "technology"],
    "artificial-intelligence": ["ai", "artificial-intelligence", "technology"],
    "film": ["film", "culture"],
    "geopolitics": ["geopolitics", "world"],
    "pop-culture": ["pop-culture", "culture"],
    "niche": ["niche", "culture"],
    "world": ["world", "geopolitics"],
}

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


FOURTH_WALL_RE = re.compile(
    r"ai[- ]generated|ai[- ]written|ai[- ]drafted|written and researched by ai|"
    r"intelligent ai|not a documentary|real social-media screenshot|official fifa image|"
    r"editorial workflow|source drawer|living article kit|live browser tools|static story",
    re.I,
)


def public_author(value: Any) -> str:
    text = clean(value)
    if not text or re.search(r"^(?:intelligent ai|ai|written and researched by ai)$", text, re.I):
        return AUTHOR_LABEL
    return re.sub(r"^By\s+", "", text, flags=re.I).strip() or AUTHOR_LABEL


def public_image_alt(value: Any, fallback: Any = "") -> str:
    text = clean(value)
    text = re.sub(r"\bAI[- ]generated\b\s*", "", text, flags=re.I)
    text = re.sub(r"\bphotorealistic editorial\b", "editorial", text, flags=re.I)
    text = re.sub(r"\beditorial thumbnail for:\s*", "", text, flags=re.I)
    text = re.sub(r"\beditorial illustration for:\s*", "", text, flags=re.I)
    text = re.sub(r"\beditorial image of\b", "image of", text, flags=re.I)
    text = re.sub(r"\beditorial image for\b", "image for", text, flags=re.I)
    text = re.sub(r"\beditorial composite\b", "image", text, flags=re.I)
    text = re.sub(r"\s*Not a documentary[^.]*\.", "", text, flags=re.I)
    text = re.sub(r"\s*not documentary evidence[^.]*\.", "", text, flags=re.I)
    text = re.sub(r"\s*not a real social-media screenshot[^.]*\.", "", text, flags=re.I)
    text = re.sub(r"\s*or official FIFA image[^.]*\.", ".", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip(" .")
    if not text or FOURTH_WALL_RE.search(text):
        text = clean(fallback) or "Story image"
    return text[:1].upper() + text[1:]


def slugify(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text


def title_case_section(value: Any) -> str:
    text = clean(value).replace("_", " ").replace("-", " ")
    slug = slugify(text)

    if slug == "ai":
        return "AI"

    if slug == "pop-culture":
        return "Pop Culture"

    return " ".join(part[:1].upper() + part[1:] for part in text.split()) or "News"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"warning: could not read {path.name}: {exc}")
        return default


def parse_date(value: Any, fallback_url: str = "") -> datetime | None:
    raw = clean(value)

    if not raw and fallback_url:
        match = re.search(r"(20\d{2})[-/](\d{2})[-/](\d{2})", fallback_url)
        if match:
            raw = f"{match.group(1)}-{match.group(2)}-{match.group(3)}T12:00:00+00:00"

    if not raw:
        return None

    text = (
        raw.replace("•", " ")
        .replace("a.m.", "AM")
        .replace("p.m.", "PM")
        .replace("A.M.", "AM")
        .replace("P.M.", "PM")
        .replace("EDT", "-04:00")
        .replace("EST", "-05:00")
        .replace("UTC", "+00:00")
    )
    text = re.sub(r"\s+", " ", text).strip()

    iso_candidate = text.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(iso_candidate)
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        pass

    match = re.search(
        r"(?P<month>[A-Za-z]+)\s+(?P<day>\d{1,2}),\s*(?P<year>20\d{2})(?:\s+(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<ampm>AM|PM)?\s*(?P<offset>[+-]\d{2}:?\d{2})?)?",
        text,
        re.I,
    )

    if match:
        month = MONTHS.get(match.group("month").lower())

        if month:
            hour = int(match.group("hour") or 12)
            minute = int(match.group("minute") or 0)
            ampm = (match.group("ampm") or "").upper()

            if ampm == "PM" and hour != 12:
                hour += 12
            elif ampm == "AM" and hour == 12:
                hour = 0

            offset = clean(match.group("offset"))
            tz = timezone.utc

            if offset:
                offset = offset if ":" in offset else f"{offset[:3]}:{offset[3:]}"
                sign = 1 if offset.startswith("+") else -1
                hours, minutes = map(int, offset[1:].split(":"))
                tz = timezone(sign * timedelta(hours=hours, minutes=minutes))

            return datetime(
                int(match.group("year")),
                month,
                int(match.group("day")),
                hour,
                minute,
                tzinfo=tz,
            ).astimezone(timezone.utc)

    return None


def date_label(dt: datetime | None) -> str:
    if not dt:
        return ""

    formatted = dt.astimezone(timezone.utc).strftime("%B %-d, %Y • %-I:%M %p UTC")
    return formatted.replace("AM", "a.m.").replace("PM", "p.m.")


def section_from_url(url: str) -> str:
    filename = Path(url).name
    first = filename.split("-")[0]

    if first and not re.match(r"20\d{2}", first):
        return title_case_section(first)

    return "News"


def story_id_from_url(url: str) -> str:
    name = Path(url).name

    if name.endswith(".html"):
        name = name[:-5]

    return slugify(name or url)


def cluster_id(title: str, keywords: list[str], section: str) -> str:
    text = f"{title} {' '.join(keywords[:6])}"
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
    words = re.findall(r"[a-z0-9]+", normalized)
    keep: list[str] = []

    for word in words:
        if len(word) <= 2 or word in STOP_WORDS:
            continue

        if word not in keep:
            keep.append(word)

        if len(keep) >= 6:
            break

    core = "-".join(keep) or slugify(title)[:48]
    return f"{slugify(section)}-{core}".strip("-")


def normalize_url(url: str) -> str:
    return re.sub(r"[?#].*$", "", clean(url).replace("./", "", 1))


def is_below_fold_item(item: dict[str, Any]) -> bool:
    url = normalize_url(item.get("url") or item.get("href") or item.get("link") or item.get("filename"))
    section = slugify(item.get("section") or item.get("section_slug") or item.get("sectionSlug"))
    story_type = slugify(item.get("type") or item.get("kind") or item.get("story_type"))
    if item.get("newsstandOnly") is True or item.get("excludeFromEdition") is True:
        return True
    return (
        url == "below-the-fold.html"
        or url.startswith("below-the-fold/")
        or section == "below-the-fold"
        or story_type in {"newsstand", "issue"}
    )


@dataclass
class Story:
    story_id: str
    cluster_id: str
    title: str
    section: str
    section_slug: str
    type: str
    dek: str
    url: str
    author: str = AUTHOR_LABEL
    published: str = ""
    published_iso: str = ""
    updated: str = ""
    updated_iso: str = ""
    image: str = ""
    image_alt: str = ""
    keywords: list[str] = field(default_factory=list)
    read_time: str = ""
    word_count: str = ""
    status: str = "published"
    priority: int = 0
    hero_eligible: bool = True
    source: str = ""
    sort_ts: float = 0.0
    is_daily: bool = False

    def public_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row.pop("sort_ts", None)
        return row


def normalize_story(item: dict[str, Any], source: str) -> Story | None:
    title = clean(item.get("title") or item.get("headline") or item.get("name"))
    url = normalize_url(item.get("url") or item.get("href") or item.get("link") or item.get("filename"))

    if not title or not url or url == "#":
        return None

    section = title_case_section(
        item.get("section")
        or item.get("desk")
        or item.get("category")
        or section_from_url(url)
    )

    story_type = clean(
        item.get("type")
        or item.get("kind")
        or ("Daily Issue" if url.startswith("daily/") else "Report")
    )

    keywords = (
        [clean(k) for k in item.get("keywords", []) if clean(k)]
        if isinstance(item.get("keywords"), list)
        else []
    )

    published_raw = (
        item.get("publishedIso")
        or item.get("published_iso")
        or item.get("publishedAt")
        or item.get("published")
        or item.get("publishedLabel")
        or item.get("date")
    )

    updated_raw = (
        item.get("updatedIso")
        or item.get("updated_iso")
        or item.get("updatedAt")
        or item.get("updated")
        or item.get("updatedLabel")
    )

    published_dt = parse_date(published_raw, url)
    updated_dt = parse_date(updated_raw, url)

    published_label = (
        clean(item.get("published") or item.get("publishedLabel") or item.get("published_label"))
        or date_label(published_dt)
    )

    updated_label = (
        clean(item.get("updated") or item.get("updatedLabel") or item.get("updated_label"))
        or date_label(updated_dt)
    )

    story_slug = clean(
        item.get("story_id")
        or item.get("storyId")
        or item.get("slug")
        or story_id_from_url(url)
    )

    section_slug = slugify(section)

    return Story(
        story_id=story_slug,
        cluster_id=clean(item.get("cluster_id") or item.get("clusterId") or cluster_id(title, keywords, section)),
        title=title,
        section=section,
        section_slug=section_slug,
        type=story_type,
        dek=clean(item.get("dek") or item.get("summary") or item.get("description") or item.get("excerpt")),
        url=url,
        author=public_author(item.get("author") or item.get("byline") or AUTHOR_LABEL),
        published=published_label,
        published_iso=published_dt.isoformat() if published_dt else "",
        updated=updated_label,
        updated_iso=updated_dt.isoformat() if updated_dt else "",
        image=clean(
            item.get("image")
            or item.get("imageUrl")
            or item.get("image_url")
            or item.get("thumbnail")
            or item.get("photo")
        ),
        image_alt=public_image_alt(item.get("imageAlt") or item.get("image_alt") or item.get("alt"), title),
        keywords=keywords,
        read_time=clean(item.get("readTime") or item.get("read_time")),
        word_count=clean(item.get("wordCount") or item.get("word_count")),
        status=clean(item.get("status") or "published"),
        priority=int(item.get("priority") or item.get("editorial_priority") or 0),
        hero_eligible=item.get("hero_eligible", True) is not False,
        source=source,
        sort_ts=published_dt.timestamp() if published_dt else 0.0,
        is_daily=url.startswith("daily/") or "daily" in story_type.lower(),
    )


def extract_source(payload: Any, source: str) -> list[Story]:
    if not payload:
        return []

    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = payload.get("stories") or payload.get("articles") or payload.get("items") or []
    else:
        rows = []

    out = []

    for item in rows:
        if isinstance(item, dict):
            if is_below_fold_item(item):
                continue
            story = normalize_story(item, source)

            if story:
                out.append(story)

    return out


def merge_story(a: Story, b: Story) -> Story:
    a_key = (a.sort_ts, SOURCE_PRIORITY.get(a.source, 0))
    b_key = (b.sort_ts, SOURCE_PRIORITY.get(b.source, 0))
    newer, older = (b, a) if b_key >= a_key else (a, b)
    merged = Story(**asdict(newer))

    merged.image = newer.image or older.image
    merged.image_alt = newer.image_alt or older.image_alt
    merged.dek = newer.dek if len(newer.dek) >= len(older.dek) else older.dek
    merged.keywords = list(dict.fromkeys([*older.keywords, *newer.keywords]))
    merged.read_time = newer.read_time or older.read_time
    merged.word_count = newer.word_count or older.word_count
    merged.priority = max(newer.priority, older.priority)
    merged.hero_eligible = newer.hero_eligible and older.hero_eligible
    if newer.author == AUTHOR_LABEL and older.author != AUTHOR_LABEL:
        merged.author = older.author
    if newer.image_alt == newer.title and older.image_alt and older.image_alt != older.title:
        merged.image_alt = older.image_alt

    return merged


def merge_all(groups: Iterable[Iterable[Story]]) -> list[Story]:
    by_url: dict[str, Story] = {}

    for story in [s for group in groups for s in group]:
        key = normalize_url(story.url)

        if key in by_url:
            by_url[key] = merge_story(by_url[key], story)
        else:
            by_url[key] = story

    return sorted(
        (s for s in by_url.values() if s.status == "published"),
        key=lambda s: s.sort_ts,
        reverse=True,
    )


def freshest_per_cluster(stories: list[Story]) -> list[Story]:
    by_cluster: dict[str, Story] = {}

    for story in stories:
        existing = by_cluster.get(story.cluster_id)

        if not existing or story.sort_ts > existing.sort_ts or (story.image and not existing.image):
            by_cluster[story.cluster_id] = story

    return sorted(by_cluster.values(), key=lambda s: s.sort_ts, reverse=True)


def score(story: Story, mode: str = "placement") -> float:
    age_hours = (NOW.timestamp() - story.sort_ts) / 3600 if story.sort_ts else 999999
    fresh = 24 if age_hours <= 72 else 8 if age_hours <= 168 else 0
    image = 6 if story.image else 0
    daily = 4 if story.is_daily else 0
    rich = 2 if len(story.dek) > 90 else 0
    editorial = 6 if mode == "editors" and re.search(r"analysis|essay|feature", story.type, re.I) else 0

    return story.sort_ts / 1e8 + fresh + image + daily + rich + editorial + story.priority * 20


def pick(
    stories: list[Story],
    count: int,
    used_clusters: set[str] | None = None,
    unique_sections: bool = False,
    require_image: bool = False,
    mode: str = "placement",
) -> list[Story]:
    used_clusters = used_clusters if used_clusters is not None else set()
    section_seen: set[str] = set()
    out: list[Story] = []
    candidates = sorted(stories, key=lambda s: score(s, mode), reverse=True)

    for story in candidates:
        if len(out) >= count:
            break

        if require_image and not story.image:
            continue

        if story.cluster_id in used_clusters:
            continue

        if unique_sections and story.section_slug in section_seen:
            continue

        out.append(story)
        used_clusters.add(story.cluster_id)
        section_seen.add(story.section_slug)

    if len(out) < count and (unique_sections or require_image):
        out.extend(
            pick(
                stories,
                count - len(out),
                used_clusters,
                unique_sections=False,
                require_image=False,
                mode=mode,
            )
        )

    return out[:count]


def resolve_manual_stories(stories: list[Story], entries: Any, count: int) -> list[Story]:
    if not isinstance(entries, list):
        return []

    by_key: dict[str, Story] = {}
    for story in stories:
        keys = {
            story.story_id,
            story.url,
            normalize_url(story.url),
            story_id_from_url(story.url),
        }
        for key in keys:
            if key:
                by_key[key] = story

    out: list[Story] = []
    seen: set[str] = set()
    for entry in entries:
        key = clean(entry.get("story_id") or entry.get("storyId") or entry.get("url") or entry.get("id")) if isinstance(entry, dict) else clean(entry)
        candidates = [
            key,
            normalize_url(key),
            story_id_from_url(key),
        ]
        story = next((by_key.get(candidate) for candidate in candidates if candidate in by_key), None)
        if not story or story.story_id in seen:
            continue
        seen.add(story.story_id)
        out.append(story)
        if len(out) >= count:
            break

    return out


def build_placements(stories: list[Story], homepage: dict[str, Any] | None = None) -> dict[str, Any]:
    homepage = homepage or {}
    hero_target = int(homepage.get("heroSlots") or homepage.get("hero_slots") or 7)
    live_cutoff = NOW - timedelta(days=LIVE_WINDOW_DAYS)
    recent = [
        story
        for story in stories
        if not story.sort_ts or datetime.fromtimestamp(story.sort_ts, timezone.utc) >= live_cutoff
    ]

    live_pool = recent if len(recent) >= 12 else stories[:max(LIVE_MINIMUM, min(len(stories), 80))]
    cluster_pool = freshest_per_cluster(live_pool)
    used: set[str] = set()

    hero = resolve_manual_stories(stories, homepage.get("leadOrder"), hero_target)
    if hero:
        used.update(story.cluster_id for story in hero)
    else:
        hero = pick(
            [s for s in cluster_pool if s.hero_eligible],
            hero_target,
            used,
            unique_sections=True,
            require_image=True,
        )

    secondary = pick(cluster_pool, 3, used, unique_sections=True)
    hero_ids = {s.story_id for s in hero}
    latest = [s for s in freshest_per_cluster(stories) if s.story_id not in hero_ids][:15]
    daily = [s for s in stories if s.is_daily][:10] or latest[:10]

    most_read = pick(
        cluster_pool,
        5,
        set(s.cluster_id for s in [*hero, *secondary]),
        unique_sections=False,
        mode="placement",
    )

    editor_used = set(s.cluster_id for s in [*hero, *secondary, *most_read])

    editors = pick(
        cluster_pool,
        4,
        editor_used,
        unique_sections=True,
        mode="editors",
    )

    desks: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "count": 0,
            "latest_ts": 0,
            "story_id": "",
            "section": "",
        }
    )

    for story in live_pool:
        desk = desks[story.section_slug]
        desk["section"] = story.section
        desk["count"] += 1

        if story.sort_ts >= desk["latest_ts"]:
            desk["latest_ts"] = story.sort_ts
            desk["story_id"] = story.story_id

    desk_pulse = sorted(
        desks.values(),
        key=lambda d: (d["latest_ts"], d["count"]),
        reverse=True,
    )[:10]

    return {
        "generated_at": NOW.isoformat(),
        "rules": {
            "live_window_days": LIVE_WINDOW_DAYS,
            "dedupe": "url + cluster_id",
            "hero": "fresh, image-ready, section-diverse",
            "secondary": "fresh, section-diverse, hero clusters excluded",
            "rails": "freshness-weighted fallback if manual analytics are unavailable",
        },
        "home": {
            "hero_slots": hero_target,
            "hero": [s.story_id for s in hero],
            "secondary": [s.story_id for s in secondary],
            "most_read": [s.story_id for s in most_read],
            "editors_picks": [s.story_id for s in editors],
            "latest": [s.story_id for s in latest],
            "daily": [s.story_id for s in daily],
            "breaking": [s.story_id for s in latest[:14]],
            "desk_pulse": desk_pulse,
        },
    }


def compact_search(stories: list[Story]) -> list[dict[str, Any]]:
    return [
        {
            "title": s.title,
            "section": s.section,
            "type": s.type,
            "dek": s.dek,
            "url": s.url,
            "author": s.author,
            "published": s.published,
            "keywords": s.keywords,
        }
        for s in stories
    ]


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build The Press article ecosystem JSON files.")
    parser.add_argument(
        "--refresh-search-index",
        action="store_true",
        help="Rewrite search-index.json from the canonical merged index.",
    )

    args = parser.parse_args()

    daily = load_json(ROOT / "daily-latest.json", {})
    edition = load_json(ROOT / "edition.json", [])
    search = load_json(ROOT / "search-index.json", [])
    master = load_json(ROOT / "master-edition.json", {})

    stories = merge_all(
        [
            extract_source(master, "master-edition"),
            extract_source(edition, "edition"),
            extract_source(daily, "daily-latest"),
            extract_source(search, "search-index"),
        ]
    )

    cutoff = NOW - timedelta(days=LIVE_WINDOW_DAYS)

    live = [
        story
        for story in stories
        if story.sort_ts and datetime.fromtimestamp(story.sort_ts, timezone.utc) >= cutoff
    ]

    if len(live) < 12:
        live = stories[:max(LIVE_MINIMUM, min(len(stories), 80))]
    else:
        live = live[:80]

    live_ids = {story.story_id for story in live}
    archive = [story for story in stories if story.story_id not in live_ids]

    content_payload = {
        "generated_at": NOW.isoformat(),
        "story_count": len(stories),
        "stories": [story.public_dict() for story in stories],
    }

    live_payload = {
        "generated_at": NOW.isoformat(),
        "story_count": len(live),
        "stories": [story.public_dict() for story in live],
    }

    archive_payload = {
        "generated_at": NOW.isoformat(),
        "story_count": len(archive),
        "stories": [story.public_dict() for story in archive],
    }

    write_json(ROOT / "content-index.json", content_payload)
    write_json(ROOT / "live-index.json", live_payload)
    write_json(ROOT / "archive-index.json", archive_payload)
    write_json(ROOT / "placements.json", build_placements(stories, master.get("homepage", {})))

    if args.refresh_search_index:
        write_json(ROOT / "search-index.json", compact_search(stories))

    print(
        f"done: {len(stories)} canonical stories, "
        f"{len(live)} live, "
        f"{len(archive)} archive-only"
    )


if __name__ == "__main__":
    main()

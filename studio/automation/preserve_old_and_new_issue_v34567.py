#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter

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

from topic_radar import (
    assignment_prompt_block,
    build_issue_plan,
    topic_radar_enabled,
)
ROOT = Path(__file__).resolve().parents[2]
ASSETS_DAILY = ROOT / "assets" / "daily"
DAILY_DIR = ROOT / "daily"

SECTIONS: list[tuple[str, str]] = [
    # Future issue assignment lanes (detoxed from legacy category rotation).
    ("front-page", "Front Page"),
    ("world", "World"),
    ("power", "Power"),
    ("money", "Money"),
    ("science", "Science"),
    ("life", "Life"),
    ("ideas", "Ideas"),
    ("culture", "Culture"),
    ("systems", "Systems"),
    ("the-weird-file", "The Weird File"),
]

SECTION_GUIDANCE: dict[str, str] = {
    "Front Page": "Choose one of the day's strongest, most consequential stories, regardless of old category habits.",
    "World": "Cover global developments, conflict, diplomacy, migration, climate stress, borders, alliances, humanitarian systems, and regional institutions.",
    "Power": "Cover courts, elections, public administration, law, corporate power, labor power, civic pressure, rights, enforcement, and public accountability.",
    "Money": "Cover prices, wages, housing, budgets, debt, markets, supply chains, business models, and household economic consequences.",
    "Science": "Cover research, medicine, climate, space, engineering, oceans, evidence, methods, uncertainty, and what would change the conclusion.",
    "Life": "Cover food, health, families, schools, consumer behavior, work, cities, rituals, routines, daily systems, and how policy reaches people.",
    "Ideas": "Run essays with a thesis, counterargument, evidence, ethical stakes, and concrete examples. Opinionated claims still need sourcing.",
    "Culture": "Cover entertainment, media, art, audience behavior, institutions, taste, sports as culture, creative labor, platform economics, and public meaning.",
    "Systems": "Cover infrastructure, technology, energy, security, logistics, platforms, software, data centers, grids, water, shipping, and machinery behind modern life.",
    "The Weird File": "Cover strange but real stories, odd institutions, subcultures, unusual data, weird markets, overlooked communities, and surprising human behavior without condescension.",
}


def env_int(name: str, default: int, minimum: int | None = None, maximum: int | None = None) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


def env_float(name: str, default: float, minimum: float | None = None, maximum: float | None = None) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except ValueError:
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


ARTICLE_TARGET_WORDS = env_int("ARTICLE_TARGET_WORDS", 2500, minimum=1200)
MIN_SOURCES = env_int("MIN_SOURCES", 20, minimum=6)
MAX_SOURCES = env_int("MAX_SOURCES", 30, minimum=MIN_SOURCES)
MAX_STORY_COUNT = env_int("MAX_STORY_COUNT", 30, minimum=1)
MIN_UNIQUE_SOURCE_DOMAINS = env_int("MIN_UNIQUE_SOURCE_DOMAINS", 8, minimum=1)
QUALITY_REPAIR_ATTEMPTS = env_int("QUALITY_REPAIR_ATTEMPTS", 2, minimum=0, maximum=3)
FACT_CHECK_PASSES = env_int("FACT_CHECK_PASSES", 1, minimum=0, maximum=3)
MAX_OUTPUT_TOKENS = env_int("MAX_OUTPUT_TOKENS", 24000, minimum=8000)
STRICT_QUALITY_GATE = env_bool("STRICT_QUALITY_GATE", False)
STRICT_EDITORIAL_GATES = env_bool("STRICT_EDITORIAL_GATES", False)
RECENT_TOPIC_LOOKBACK = env_int("RECENT_TOPIC_LOOKBACK", 120, minimum=0, maximum=500)
RECENT_TOPIC_SIMILARITY_LIMIT = env_float("RECENT_TOPIC_SIMILARITY_LIMIT", 0.34, minimum=0.1, maximum=0.9)
ISSUE_TOPIC_SIMILARITY_LIMIT = env_float(
    "ISSUE_TOPIC_SIMILARITY_LIMIT",
    max(0.24, RECENT_TOPIC_SIMILARITY_LIMIT - 0.08),
    minimum=0.1,
    maximum=0.9,
)
VISUAL_CONCEPT_SIMILARITY_LIMIT = env_float("VISUAL_CONCEPT_SIMILARITY_LIMIT", 0.32, minimum=0.1, maximum=0.9)
TITLE_RHYTHM_SIMILARITY_LIMIT = env_float("TITLE_RHYTHM_SIMILARITY_LIMIT", 0.64, minimum=0.1, maximum=1.0)
TITLE_STYLE_GATE = os.getenv("TITLE_STYLE_GATE", "1").strip().lower() not in {"0", "false", "no"}

SECTION_STATE_PATH = DAILY_DIR / "section-rotation.json"

VISUAL_ARCHETYPES = [
    "ground-level human scene with a specific setting and natural light",
    "object-detail still life built around a concrete artifact from the reporting",
    "institutional room or workplace scene with people, tools, and context",
    "wide environmental scene showing infrastructure, landscape, or atmosphere",
    "documentary street-level scene with motion and local texture",
    "macro material-detail scene where texture carries the story",
    "layered interior scene seen through glass, doorway, or reflection",
    "quiet aftermath scene that suggests stakes without melodrama",
    "hands-at-work scene focused on process, craft, or labor",
    "abstract physical installation using real-world objects, not maps or scales",
    "field-reporting scene with equipment, weather, terrain, or transit",
    "domestic-scale scene showing how a policy or system reaches daily life",
    "lab, archive, library, classroom, clinic, market, theater, or workshop scene",
    "architectural detail that reveals power, constraint, or neglect",
    "nonliteral atmospheric scene with color, depth, and one surprising focal object",
]

VISUAL_CLICHE_BANS = [
    "balancing scales",
    "red-versus-blue state maps",
    "U.S. map overlays",
    "state silhouette overlays",
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
    "state silhouette overlays": "a concrete local setting with one recognizable civic or material detail instead of a state outline",
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

TITLE_OPENERS_TO_AVOID = {
    "america",
    "america's",
    "americas",
    "brazil",
    "brazil's",
    "britain",
    "britain's",
    "canada",
    "canada's",
    "united states",
    "the united states",
    "u.s.",
    "us",
    "china",
    "china's",
    "france",
    "france's",
    "germany",
    "germany's",
    "india",
    "india's",
    "iran",
    "iran's",
    "israel",
    "israel's",
    "japan",
    "japan's",
    "mexico",
    "mexico's",
    "russia",
    "russia's",
    "europe",
    "europe's",
    "ukraine",
    "ukraine's",
    "washington",
}

BANNED_FORMULA_PATTERNS = [
    r"\bhas\s+become\b",
    r"\bhave\s+become\b",
    r"\bis\s+becoming\b",
    r"\bare\s+becoming\b",
    r"\bwas\s+becoming\b",
    r"\bwere\s+becoming\b",
    r"\bbecame\b",
    r"\bturns\s+into\b",
    r"\bturn\s+into\b",
    r"\bturns\s+on\b",
    r"\bturn\s+on\b",
    r"\bputs\s+into\s+focus\b",
    r"\bput\s+into\s+focus\b",
    r"\blands\s+inside\b",
    r"\bland\s+inside\b",
    r"\bwalks\s+onto\b",
    r"\bwalk\s+onto\b",
    r"\bis\s+not\s+just\b",
    r"\bare\s+not\s+just\b",
    r"\bhas\s+to\s+survive\b",
    r"\bhave\s+to\s+survive\b",
]

TITLE_CLICHE_PATTERNS = [
    r"^america(’s|'s)?\b",
    r"^why\b",
    r"^how\s+.+\s+is\s+reshaping\s+.+",
    r"^the\s+.+\s+that\s+.+",
    r"^what\s+.+\s+says\s+about\s+.+",
    r"^.+\s+is\s+reshaping\s+.+",
    r"^.+\s+tests\s+.+",
    r"^.+\s+shows\s+how\s+.+",
    *BANNED_FORMULA_PATTERNS,
]

HEADLINE_SHAPES = [
    "named actor + vivid verb + concrete stakes",
    "place + observed change + why it matters",
    "number or data point + human consequence",
    "institution + conflict + unresolved question",
    "object or detail + larger system",
    "short declarative headline under 9 words",
    "direct contrast using two clauses",
    "verb-led headline",
    "document or dataset-led headline",
    "person or community-led headline",
    "unexpected noun + precise verb",
    "scene-setting headline with no determiner opener",
    "rare question headline, only when genuinely sharper",
    "rare colon headline, only when genuinely sharper",
]

MAX_SAME_FIRST_WORD_PER_ISSUE = env_int("MAX_SAME_FIRST_WORD_PER_ISSUE", 2, minimum=1, maximum=5)
MAX_DETERMINER_OPENERS_PER_ISSUE = env_int("MAX_DETERMINER_OPENERS_PER_ISSUE", 2, minimum=0, maximum=5)
DETERMINER_OPENERS = {"a", "an", "the"}

HEADLINE_CERTAINTY_PATTERNS = [
    r"\bproves?\b",
    r"\bfinally\b",
    r"\bonce and for all\b",
    r"\bthe truth about\b",
    r"\bwhat everyone gets wrong\b",
    r"^the real reason\b",
    r"\beverything\b.*\bchanged\b",
    r"\bwill never\b",
    r"\bis doomed\b",
    r"\bhas already won\b",
    r"\bis over\b",
]
HEADLINE_CERTAINTY_GATE = env_bool("HEADLINE_CERTAINTY_GATE", True)
MAX_AVG_SENTENCE_WORDS = env_int("MAX_AVG_SENTENCE_WORDS", 24, minimum=14, maximum=40)
MAX_LONG_SENTENCE_SHARE = env_float("MAX_LONG_SENTENCE_SHARE", 0.22, minimum=0.05, maximum=0.80)
READER_VOICE_GUIDE = """
Write for curious people from age 10 to 99 without talking down to anyone.
Make the article fun to keep reading: vivid, concrete, occasionally surprising, and human-scale.
Be creative in structure, examples, scene-setting, and analogies — never creative with facts.
Stay unbiased: separate evidence from interpretation, include serious uncertainty, and avoid pretending one source or one explanation settles the whole story.
Explain specialized terms the first time they appear. Do not assume prior knowledge of politics, science, economics, AI, law, medicine, or any other field.
Use plain language first, then add depth. Short paragraphs are welcome. If a sentence needs three clauses, it probably needs a rewrite.
Headlines and deks should be concrete and curious, not smug or all-knowing. Avoid definitive frames like proving, finally explaining, revealing the real truth, or declaring that everything changed.
The article can be thought-provoking and substantive, but nobody should feel pushed out because the writing is showing off.
"""

STOPWORDS = {
    "about", "after", "again", "against", "america", "american", "americas", "among", "before", "behind",
    "being", "between", "could", "daily", "edition", "every", "fight", "from", "have", "into",
    "more", "over", "press", "return", "story", "that", "their", "there", "these", "they", "this",
    "through", "today", "under", "while", "would", "with", "without", "year", "years", "update",
}

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
    visual_brief: str = ""
    visual_archetype: str = ""


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


def read_section_cursor() -> int:
    if not SECTION_STATE_PATH.exists():
        return 0
    try:
        payload = json.loads(SECTION_STATE_PATH.read_text(encoding="utf-8"))
        return int(payload.get("next_index", 0)) % len(SECTIONS)
    except Exception:
        return 0


def save_section_cursor(stories_generated: int) -> None:
    SECTION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    next_index = (read_section_cursor() + max(0, stories_generated)) % len(SECTIONS)
    SECTION_STATE_PATH.write_text(
        json.dumps(
            {
                "next_index": next_index,
                "section_count": len(SECTIONS),
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def pick_sections(story_count: int) -> list[tuple[str, str]]:
    """Rotate through every desk instead of always favoring the first few."""
    capped = max(1, min(MAX_STORY_COUNT, story_count))
    start = read_section_cursor()
    return [SECTIONS[(start + i) % len(SECTIONS)] for i in range(capped)]




def visual_archetype_for(issue_index: int, section_name: str) -> str:
    seed = read_section_cursor() + issue_index + sum(ord(char) for char in section_name.lower())
    return VISUAL_ARCHETYPES[seed % len(VISUAL_ARCHETYPES)]


def strip_html_text(value: str) -> str:
    return BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)


def normalize_term(term: str) -> str:
    term = term.lower().strip("'’-.")
    for suffix in ("ization", "isation", "ments", "ment", "ingly", "edly", "ing", "ies", "ied", "ed", "es", "s"):
        if len(term) > len(suffix) + 4 and term.endswith(suffix):
            if suffix in {"ies", "ied"}:
                return term[: -len(suffix)] + "y"
            return term[: -len(suffix)]
    return term


def text_terms(*values: Any) -> set[str]:
    text = " ".join(strip_html_text(str(value or "")) for value in values)
    terms: set[str] = set()
    for raw in re.findall(r"[A-Za-z][A-Za-z'’.-]{2,}", text.lower()):
        token = raw.strip(".'’-")
        if len(token) < 4 or token in STOPWORDS:
            continue
        if token.endswith(".com") or token.endswith(".org"):
            continue
        terms.add(normalize_term(token))
    return terms


def item_terms(item: dict[str, Any]) -> set[str]:
    keywords = " ".join(str(k) for k in item.get("keywords", []) if k)
    return text_terms(item.get("title"), item.get("dek"), item.get("summary"), item.get("section"), keywords)


def visual_terms(item: dict[str, Any]) -> set[str]:
    return text_terms(
        item.get("visual_brief"),
        item.get("thumbnail_search_hint"),
        item.get("thumbnail_alt"),
        item.get("imageAlt"),
        item.get("image_alt"),
    )


def replace_case_insensitive(value: str, needle: str, replacement: str) -> tuple[str, bool]:
    updated = re.sub(re.escape(needle), replacement, value, flags=re.I)
    return updated, updated != value


def rewrite_visual_cliches(payload: dict[str, Any], visual_assignment: str) -> tuple[dict[str, Any], list[str]]:
    rewrites: list[str] = []
    for key in ("visual_brief", "thumbnail_search_hint", "thumbnail_alt"):
        value = str(payload.get(key) or "")
        updated = value
        for banned, replacement in VISUAL_CLICHE_REWRITES.items():
            updated, changed = replace_case_insensitive(updated, banned, replacement)
            if changed:
                rewrites.append(f"{key}: {banned} -> {replacement}")
        if updated != value:
            payload[key] = updated.strip()

    if rewrites:
        brief = str(payload.get("visual_brief") or "").strip()
        if not brief:
            brief = next(iter(VISUAL_CLICHE_REWRITES.values()))
        if visual_assignment and visual_assignment.lower() not in brief.lower():
            payload["visual_brief"] = f"Use the assigned visual archetype ({visual_assignment}) to show {brief}"
    return payload, rewrites


def title_rhythm_signature(title: str) -> set[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z'’.-]*", title.lower())
    if not tokens:
        return set()

    signature = {f"first:{tokens[0]}", f"length:{min(len(tokens) // 4, 4)}"}
    if len(tokens) > 1:
        signature.add(f"opener:{tokens[0]} {tokens[1]}")
    if "?" in title:
        signature.add("punct:question")
    if ":" in title:
        signature.add("punct:colon")
    if "—" in title or " - " in title:
        signature.add("punct:dash")
    if "," in title:
        signature.add("punct:comma")
    if tokens[0] in {"why", "how", "what", "when", "where"}:
        signature.add("question-led")
    if tokens[0] in {"as", "after", "before", "inside", "when"}:
        signature.add("scene-or-time-led")
    if re.search(r"\b(is|are|was|were)\s+reshaping\b", title.lower()):
        signature.add("formula:reshaping")
    if re.search(r"\btests?\b", title.lower()):
        signature.add("formula:tests")
    if re.search(r"\bshows?\s+how\b", title.lower()):
        signature.add("formula:shows-how")
    if re.search(r"\bsays?\s+about\b", title.lower()):
        signature.add("formula:says-about")
    if re.search(r"\bhas\s+become\b|\bhave\s+become\b|\bbecame\b", title.lower()):
        signature.add("formula:has-become")
    if re.search(r"\bis\s+becoming\b|\bare\s+becoming\b|\bwas\s+becoming\b|\bwere\s+becoming\b", title.lower()):
        signature.add("formula:becoming")
    if re.search(r"\bturns\s+into\b|\bturn\s+into\b", title.lower()):
        signature.add("formula:turns-into")
    if re.search(r"\bturns\s+on\b|\bturn\s+on\b", title.lower()):
        signature.add("formula:turns-on")
    if re.search(r"\bis\s+not\s+just\b|\bare\s+not\s+just\b", title.lower()):
        signature.add("formula:not-just")
    if re.search(r"\bputs\s+into\s+focus\b|\bput\s+into\s+focus\b", title.lower()):
        signature.add("formula:into-focus")
    if re.search(r"\blands\s+inside\b|\bland\s+inside\b", title.lower()):
        signature.add("formula:lands-inside")
    if re.search(r"\bwalks\s+onto\b|\bwalk\s+onto\b", title.lower()):
        signature.add("formula:walks-onto")
    if re.match(r"^[a-z][a-z.-]+['’]s\b", title.lower()):
        signature.add("possessive-opener")
    return signature


def first_word(title: str) -> str:
    normalized = title.lower().replace("’", "'")
    match = re.search(r"[a-z0-9][a-z0-9'.-]*", normalized)
    if not match:
        return ""
    return match.group(0).strip("'.-")


def issue_first_word_count(current_issue: list[dict[str, Any]], word: str) -> int:
    if not word:
        return 0
    return sum(1 for item in current_issue if first_word(str(item.get("title") or "")) == word)


def issue_determiner_opener_count(current_issue: list[dict[str, Any]]) -> int:
    return sum(1 for item in current_issue if first_word(str(item.get("title") or "")) in DETERMINER_OPENERS)


def headline_formula_families(title: str) -> set[str]:
    families: set[str] = set()
    lower = title.lower().replace("’", "'")
    if re.search(r"\bhas\s+become\b|\bhave\s+become\b|\bbecame\b", lower):
        families.add("formula:has-become")
    if re.search(r"\bis\s+becoming\b|\bare\s+becoming\b|\bwas\s+becoming\b|\bwere\s+becoming\b", lower):
        families.add("formula:becoming")
    if re.search(r"\bturns\s+into\b|\bturn\s+into\b", lower):
        families.add("formula:turns-into")
    if re.search(r"\bturns\s+on\b|\bturn\s+on\b", lower):
        families.add("formula:turns-on")
    if re.search(r"\bis\s+not\s+just\b|\bare\s+not\s+just\b", lower):
        families.add("formula:not-just")
    if re.search(r"\bputs\s+into\s+focus\b|\bput\s+into\s+focus\b", lower):
        families.add("formula:into-focus")
    if re.search(r"\blands\s+inside\b|\bland\s+inside\b", lower):
        families.add("formula:lands-inside")
    if re.search(r"\bwalks\s+onto\b|\bwalk\s+onto\b", lower):
        families.add("formula:walks-onto")
    return families


def headline_shape_for(issue_index: int) -> str:
    if not HEADLINE_SHAPES:
        return "named actor + vivid verb + concrete stakes"
    return HEADLINE_SHAPES[issue_index % len(HEADLINE_SHAPES)]


def required_payload_issues(payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    title = str(payload.get("title") or "").strip()
    dek = str(payload.get("dek") or "").strip()
    body_html = str(payload.get("body_html") or "")
    source_notes_html = str(payload.get("source_notes_html") or "")
    if not title:
        issues.append("missing required title")
    if not dek:
        issues.append("missing required dek")
    if not strip_html_text(body_html):
        issues.append("missing required body_html")
    if not extract_source_urls(source_notes_html):
        issues.append("missing required source_notes_html with at least one https source URL")
    return issues


def merge_story_memory_items(items: list[dict[str, Any]], seen: set[str], output: list[dict[str, Any]]) -> None:
    for item in items:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        if not title:
            continue
        key = (str(item.get("url") or item.get("href") or title)).strip().lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(
            {
                "title": title,
                "dek": str(item.get("dek") or item.get("summary") or "").strip(),
                "section": str(item.get("section") or "").strip(),
                "url": str(item.get("url") or item.get("href") or "").strip(),
                "keywords": item.get("keywords") if isinstance(item.get("keywords"), list) else [],
                "visual_archetype": str(item.get("visual_archetype") or "").strip(),
                "visual_brief": str(item.get("visual_brief") or "").strip(),
                "thumbnail_search_hint": str(item.get("thumbnail_search_hint") or "").strip(),
                "thumbnail_alt": str(item.get("thumbnail_alt") or item.get("imageAlt") or item.get("image_alt") or "").strip(),
            }
        )


def load_recent_story_memory(limit: int = RECENT_TOPIC_LOOKBACK) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in (ROOT / "daily-latest.json", ROOT / "search-index.json", ROOT / "archive-index.json"):
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict):
            items: list[Any] = []
            for key in ("articles", "stories", "items"):
                value = data.get(key)
                if isinstance(value, list):
                    items.extend(value)
            merge_story_memory_items([item for item in items if isinstance(item, dict)], seen, output)
        elif isinstance(data, list):
            merge_story_memory_items([item for item in data if isinstance(item, dict)], seen, output)
        if len(output) >= limit:
            break
    return output[:limit]


def brief_recent_context(recent: list[dict[str, Any]], section_name: str, current_issue: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    if current_issue:
        lines.append("Already selected for this same issue — do not choose overlapping topics or image concepts:")
        for item in current_issue[-10:]:
            lines.append(f"- {item.get('section', 'News')}: {item.get('title', '')} — {item.get('dek', '')}")
    section_matches = [item for item in recent if item.get("section") == section_name]
    mixed_recent = section_matches[:10] + [item for item in recent if item.get("section") != section_name][:14]
    if mixed_recent:
        lines.append("Recent archive memory — avoid same subject, same framing, and same title rhythm unless there is a major new development:")
        for item in mixed_recent[:24]:
            visual = item.get("visual_archetype") or item.get("visual_brief") or ""
            extra = f" | recent visual: {visual}" if visual else ""
            lines.append(f"- {item.get('section', 'News')}: {item.get('title', '')} — {item.get('dek', '')}{extra}")
    if not lines:
        lines.append("No recent archive memory is available; still seek range across geography, institutions, people affected, and story type.")
    return "\n".join(lines)


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))


def title_opener(title: str, words: int = 2) -> str:
    tokens = re.findall(r"[A-Za-z][A-Za-z'’.-]*", title.lower())
    return " ".join(tokens[:words])


def editorial_quality_issues(
    payload: dict[str, Any],
    recent: list[dict[str, Any]],
    current_issue: list[dict[str, Any]],
    visual_assignment: str,
) -> tuple[list[str], dict[str, Any]]:
    title = str(payload.get("title") or "").strip()
    dek = str(payload.get("dek") or "").strip()
    body_html = str(payload.get("body_html") or "")
    keywords = payload.get("keywords") if isinstance(payload.get("keywords"), list) else []
    payload_terms = text_terms(title, dek, " ".join(str(k) for k in keywords))
    payload_visual_terms = visual_terms(payload)
    payload_title_rhythm = title_rhythm_signature(title)
    issues: list[str] = []
    title_lower = title.lower().replace("’", "'")
    opener = first_word(title)
    if HEADLINE_CERTAINTY_GATE:
        for pattern in HEADLINE_CERTAINTY_PATTERNS:
            if re.search(pattern, title_lower):
                issues.append("headline sounds too definitive/all-knowing; rewrite with curiosity, concrete evidence, and room for uncertainty")
                break

    body_text = strip_html_text(body_html)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", body_text) if len(s.split()) >= 6]
    if sentences:
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_words = sum(sentence_lengths) / max(1, len(sentence_lengths))
        long_sentence_share = sum(1 for count in sentence_lengths if count > 34) / max(1, len(sentence_lengths))
        if avg_sentence_words > MAX_AVG_SENTENCE_WORDS or long_sentence_share > MAX_LONG_SENTENCE_SHARE:
            issues.append("article voice is getting too dense; split long sentences, explain terms plainly, and make the story easier for non-specialists to keep reading")


    if TITLE_STYLE_GATE:
        opener_one = title_opener(title, 1)
        opener_two = title_opener(title, 2)
        opener_three = title_opener(title, 3)
        if (
            opener_one in TITLE_OPENERS_TO_AVOID
            or opener_two in TITLE_OPENERS_TO_AVOID
            or opener_three in TITLE_OPENERS_TO_AVOID
        ):
            issues.append(
                "title starts with an overused country/institution opener; rewrite with a sharper concrete subject unless that exact actor is essential"
            )
        for pattern in TITLE_CLICHE_PATTERNS:
            if re.search(pattern, title_lower):
                issues.append(f"title matches an overused Press headline pattern: {pattern}")
                break

    if TITLE_STYLE_GATE and opener in DETERMINER_OPENERS:
        determiner_count = issue_determiner_opener_count(current_issue)
        if determiner_count >= MAX_DETERMINER_OPENERS_PER_ISSUE:
            issues.append(
                "title starts with A/An/The but this issue already hit the determiner-opener cap; rewrite with a sharper subject"
            )

    if TITLE_STYLE_GATE and opener:
        first_word_count = issue_first_word_count(current_issue, opener)
        if first_word_count >= MAX_SAME_FIRST_WORD_PER_ISSUE:
            issues.append(
                f"title repeats first-word opener '{opener}' beyond allowed issue cap ({MAX_SAME_FIRST_WORD_PER_ISSUE})"
            )

    if TITLE_STYLE_GATE:
        current_families: set[str] = set()
        for item in current_issue:
            current_families |= headline_formula_families(str(item.get("title") or ""))
        repeated_families = headline_formula_families(title) & current_families
        if repeated_families:
            issues.append(
                "title repeats formulaic syntax already used in this issue: " + ", ".join(sorted(repeated_families))
            )

    def best_term_match(items: list[dict[str, Any]], base_terms: set[str], term_fn: Any) -> tuple[float, str]:
        best_score = 0.0
        best_title = ""
        for item in items:
            score = jaccard(base_terms, term_fn(item))
            if score > best_score:
                best_score = score
                best_title = str(item.get("title") or "")
        return best_score, best_title

    def best_title_rhythm_match(items: list[dict[str, Any]]) -> tuple[float, str]:
        best_score = 0.0
        best_title = ""
        for item in items:
            other_title = str(item.get("title") or "")
            score = jaccard(payload_title_rhythm, title_rhythm_signature(other_title))
            if score > best_score:
                best_score = score
                best_title = other_title
        return best_score, best_title

    recent_score, recent_title = best_term_match(recent, payload_terms, item_terms)
    issue_score, issue_title = best_term_match(current_issue, payload_terms, item_terms)
    if recent_score >= RECENT_TOPIC_SIMILARITY_LIMIT:
        issues.append(
            f"topic is too close to recent archive story '{recent_title}' (similarity {recent_score:.2f}); choose a different subject or materially new angle"
        )
    if issue_score >= ISSUE_TOPIC_SIMILARITY_LIMIT:
        issues.append(
            f"topic overlaps another story in this issue '{issue_title}' (similarity {issue_score:.2f}); choose a different story"
        )

    recent_visual_score, recent_visual_title = best_term_match(recent, payload_visual_terms, visual_terms)
    issue_visual_score, issue_visual_title = best_term_match(current_issue, payload_visual_terms, visual_terms)
    visual_similarity_limit = VISUAL_CONCEPT_SIMILARITY_LIMIT
    if payload_visual_terms and recent_visual_score >= visual_similarity_limit:
        issues.append(
            f"visual concept is too close to recent archive story '{recent_visual_title}' (similarity {recent_visual_score:.2f}); choose a fresher image scene"
        )
    if payload_visual_terms and issue_visual_score >= max(0.22, visual_similarity_limit - 0.08):
        issues.append(
            f"visual concept overlaps another story in this issue '{issue_visual_title}' (similarity {issue_visual_score:.2f}); choose a distinct thumbnail scene"
        )

    recent_rhythm_score, recent_rhythm_title = best_title_rhythm_match(recent)
    issue_rhythm_score, issue_rhythm_title = best_title_rhythm_match(current_issue)
    if TITLE_STYLE_GATE and recent_rhythm_score >= TITLE_RHYTHM_SIMILARITY_LIMIT:
        issues.append(
            f"headline rhythm is too close to recent archive title '{recent_rhythm_title}' (similarity {recent_rhythm_score:.2f}); change the sentence shape"
        )
    if TITLE_STYLE_GATE and issue_rhythm_score >= TITLE_RHYTHM_SIMILARITY_LIMIT:
        issues.append(
            f"headline rhythm repeats another story in this issue '{issue_rhythm_title}' (similarity {issue_rhythm_score:.2f}); change the sentence shape"
        )

    visual_brief = str(payload.get("visual_brief") or "").strip().lower()
    thumbnail_hint = str(payload.get("thumbnail_search_hint") or "").strip().lower()
    visual_text = f"{payload.get('visual_archetype') or ''} {visual_brief} {thumbnail_hint}"
    for banned in VISUAL_CLICHE_BANS:
        if banned.lower() in visual_text:
            issues.append(f"visual plan repeats a banned thumbnail cliché: {banned}")
            break
    if visual_assignment and visual_assignment.lower() not in visual_text:
        issues.append(f"visual_brief must clearly use the assigned visual archetype: {visual_assignment}")

    metrics = {
        "recent_similarity": round(recent_score, 3),
        "recent_match": recent_title,
        "issue_similarity": round(issue_score, 3),
        "issue_match": issue_title,
        "recent_visual_similarity": round(recent_visual_score, 3),
        "recent_visual_match": recent_visual_title,
        "issue_visual_similarity": round(issue_visual_score, 3),
        "issue_visual_match": issue_visual_title,
        "recent_title_rhythm_similarity": round(recent_rhythm_score, 3),
        "recent_title_rhythm_match": recent_rhythm_title,
        "issue_title_rhythm_similarity": round(issue_rhythm_score, 3),
        "issue_title_rhythm_match": issue_rhythm_title,
        "term_count": len(payload_terms),
        "visual_assignment": visual_assignment,
    }
    return issues, metrics


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


def source_domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def extract_source_urls(fragment: str) -> list[str]:
    soup = BeautifulSoup(fragment or "", "html.parser")
    urls: list[str] = []
    for anchor in soup.find_all("a"):
        href = str(anchor.get("href") or "").strip()
        if href.startswith("https://"):
            urls.append(href)
    return list(dict.fromkeys(urls))


def payload_quality_issues(payload: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    body_html = str(payload.get("body_html") or "")
    source_notes_html = str(payload.get("source_notes_html") or "")
    words = story_word_count(body_html)
    urls = extract_source_urls(source_notes_html)
    domains = [source_domain(url) for url in urls if source_domain(url)]
    domain_counts = Counter(domains)

    issues: list[str] = []
    if words < ARTICLE_TARGET_WORDS:
        issues.append(f"body_html has {words} words; minimum is {ARTICLE_TARGET_WORDS}")
    if len(urls) < MIN_SOURCES:
        issues.append(f"source_notes_html has {len(urls)} distinct https source URLs; minimum is {MIN_SOURCES}")
    # Keep the real hard gates focused on what matters most:
    # enough words and enough distinct https source URLs.
    # Extra source abundance and domain mix are tracked in metrics, not used
    # to kill the whole daily issue after the article has already been researched.
    metrics = {
        "words": words,
        "source_urls": len(urls),
        "source_domains": len(set(domains)),
        "top_domains": domain_counts.most_common(5),
    }
    return issues, metrics


def request_payload(client: OpenAI, prompt: str) -> dict[str, Any]:
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
                    model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
                    tools=[{"type": tool_type}],
                    input=prompt,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                )
                return extract_json(getattr(response, "output_text", "") or "")
            except Exception as exc:  # pragma: no cover - runtime retry path
                last_error = exc
                if attempt == 1:
                    break
                time.sleep(2 * (attempt + 1))

    assert last_error is not None
    raise last_error



def generation_prompt(
    section_name: str,
    date_label: str,
    recent_context: str,
    visual_assignment: str,
    headline_shape: str,
    current_issue: list[dict[str, Any]],
    assignment: dict[str, Any] | None = None,
) -> str:
    guidance = SECTION_GUIDANCE.get(section_name, f"Cover {section_name} with depth, humility, and strong sourcing.")
    banned_visuals = "; ".join(VISUAL_CLICHE_BANS)
    title_openers = ", ".join(sorted(TITLE_OPENERS_TO_AVOID))
    reader_voice = READER_VOICE_GUIDE.strip()
    topic_requirement = (
        "- You are assigned the Topic Radar story above. Stay on this assignment unless live reporting proves it is false, stale, unsafe, or impossible to source."
        if assignment
        else ("- Choose a genuinely current, newsworthy topic for the " + section_name + " desk.")
    )
    determiner_count = issue_determiner_opener_count(current_issue)
    determiner_note = (
        f"- Do not start with A, An, or The because this issue already has {determiner_count} determiner-led headlines."
        if determiner_count >= MAX_DETERMINER_OPENERS_PER_ISSUE
        else f"- Keep determiner-led headlines rare; the per-issue cap is {MAX_DETERMINER_OPENERS_PER_ISSUE}."
    )
    return f"""
You are the newsroom engine for The Press.

Desk: {section_name}
Desk mandate: {guidance}
Date context: {date_label}

Editorial variety brief:
{recent_context}

Assigned visual archetype for this article:
{visual_assignment}

Required headline shape for this article:
{headline_shape}

Research widely, then write. Gather a broad source map before drafting: primary documents, official datasets, credible news reports, local reporting where useful, academic or technical sources when relevant, explainers from authoritative institutions, and at least a few sources that complicate or challenge the main thesis.

Return JSON only. No markdown fences. Use exactly this shape:
{{
  "title": "string",
  "dek": "string",
  "keywords": ["string", "string", "string"],
  "visual_archetype": "{visual_assignment}",
  "visual_brief": "string",
  "thumbnail_search_hint": "string",
  "thumbnail_alt": "string",
  "body_html": "<p>...</p><h2>...</h2>...",
  "source_notes_html": "<ol><li><a href='https://example.com'>Source label</a> — one short note about what it supports</li></ol>"
}}

Reader voice and headline stance:
{reader_voice}

Hard requirements:
{topic_requirement}
- Do not choose any topic too close to the recent archive memory or another story in this same issue. If a same broad event is unavoidable, the article must have a materially new factual peg, a different institution/geography/human group, and a different thesis.
- Make the mix feel like a real newspaper, not a playlist of the same four news obsessions. Seek range across local/global, institutional/human, data/culture, science/policy, money/labor, courts/communities, and daily-life consequences.
- Give the headline a concrete subject and fresh syntax. Avoid starting titles with these overused openers unless absolutely essential: {title_openers}.
- Do not reuse the same headline syntax as another story in this issue; vary sentence construction and rhythm.
- Avoid these headline formulas: has become, have become, is becoming, are becoming, was becoming, were becoming, became, turns into, turn into, turns on, turn on, puts into focus, put into focus, lands inside, land inside, walks onto, walk onto, is not just, are not just, has to survive, have to survive.
- Use a named actor, place, institution, document, dataset, number, event, or concrete object when possible.
- Never use the assignment or fallback title as the final headline.
- Required headline shape: {headline_shape}.
{determiner_note}
- Avoid stock headline formulas: "Why X is...", "What X says about...", "X is reshaping Y", "X tests Y", "X shows how Y", and other seminar-room titles. No corny portentous headers.
- Prefer titles with a precise noun, vivid verb, and clear stakes. The title should sound edited by a sharp human editor, not templated.
- body_html must be at least {ARTICLE_TARGET_WORDS} words. Do not pad; add reporting depth, context, counterevidence, implications, and uncertainty.
- source_notes_html should contain at least {MIN_SOURCES} distinct live https source URLs. {MAX_SOURCES} is a soft target, not a hard ceiling; prefer broad, independent source diversity when possible.
- Use clean HTML with paragraphs and clear h2 subheads. Do not use markdown inside body_html.
- Do not mention being an AI, being prompted, model behavior, tools, workflows, PRs, or backend systems.
- Do not invent sources, titles, dates, data, quotes, organizations, or URLs.
- Do not copy source text. Write in original synthesized prose. Direct quotes should be rare, short, and clearly attributed.
- Fact-check hard claims: dates, numbers, names, laws, studies, medical claims, scientific claims, market claims, and geopolitical claims.
- Triangulate major claims across independent sources. Mark uncertainty where sources disagree.
- Source notes should make it obvious what each source contributed.
- Use concise source labels, not raw naked URLs.
- visual_archetype must exactly equal: {visual_assignment}
- visual_brief must be a specific, image-generation-ready plan that follows the assigned visual archetype and describes a unique scene, not a generic symbol.
- Do not use these repeated visual tropes in thumbnail_search_hint, thumbnail_alt, or visual_brief: {banned_visuals}.
- Only use maps when the story truly requires geography, and never default to red/blue political maps or floating state silhouettes.
- Only use data centers, server racks, scales, court buildings, vaccines, rockets, capsules, or glowing AI brains when they are unavoidable and visually handled in a fresh, concrete way.
- thumbnail_search_hint should be a short Wikimedia Commons-friendly search phrase for a literal fallback image, not a cliché.
- For the Ideas lane, write an argument with a clear point of view, keep factual scaffolding sourced, and include a strong counterargument.
""".strip()

def verification_prompt(payload: dict[str, Any], section_name: str, date_label: str, recent_context: str, visual_assignment: str) -> str:
    banned_visuals = "; ".join(VISUAL_CLICHE_BANS)
    return f"""
You are the verification editor for The Press.

Desk: {section_name}
Date context: {date_label}
Assigned visual archetype: {visual_assignment}

Editorial variety brief:
{recent_context}

Use live web research to fact-check the draft below. Fix unsupported or stale claims, remove claims that cannot be verified, add missing context, strengthen source diversity, and keep the prose original. The final article must still be at least {ARTICLE_TARGET_WORDS} words and must list at least {MIN_SOURCES} distinct live https source URLs in source_notes_html. {MAX_SOURCES} is a soft target, not a hard ceiling.

Also preserve the variety standards: do not drift back to the same recent topic, do not use a templated country-first headline, and do not use banned thumbnail clichés. The visual_archetype field must exactly equal "{visual_assignment}". The visual_brief must be specific and must avoid: {banned_visuals}.

Keep the headline concrete, sourced, and curious rather than sweeping or all-knowing.

Return the same JSON shape only. No markdown fences.

Draft JSON:
{json.dumps(payload, ensure_ascii=False)}
""".strip()

def repair_prompt(
    payload: dict[str, Any],
    section_name: str,
    date_label: str,
    issues: list[str],
    metrics: dict[str, Any],
    recent_context: str,
    visual_assignment: str,
    headline_shape: str,
    current_issue: list[dict[str, Any]],
) -> str:
    banned_visuals = "; ".join(VISUAL_CLICHE_BANS)
    determiner_count = issue_determiner_opener_count(current_issue)
    return f"""
The Press quality gate rejected this {section_name} draft.

Issues:
{chr(10).join(f"- {issue}" for issue in issues)}

Current metrics:
{json.dumps(metrics, ensure_ascii=False)}

Editorial variety brief:
{recent_context}

Repair the article by doing more live research, expanding the analysis, improving fact-checking, changing the topic or framing when required, and fixing the source list. Do not merely add links; each source must directly support claims in the story. Keep the writing original, polished, concrete, and less templated.

Required final standards:
- At least {ARTICLE_TARGET_WORDS} words in body_html.
- At least {MIN_SOURCES} distinct live https source URLs in source_notes_html. {MAX_SOURCES} is a soft target, not a hard ceiling.
- At least {MIN_UNIQUE_SOURCE_DOMAINS} unique source domains.
- No unsupported facts.
- A fresh topic or materially new angle compared with the recent archive memory and this same issue.
- A stronger, less formulaic title that is concrete, sourced, and does not open with the usual country/institution template unless essential.
- Required headline shape for this story: {headline_shape}.
- Do not reuse the same headline syntax as another story in this issue.
- Avoid these headline formulas: has become, have become, is becoming, are becoming, was becoming, were becoming, became, turns into, turn into, turns on, turn on, puts into focus, put into focus, lands inside, land inside, walks onto, walk onto, is not just, are not just, has to survive, have to survive.
- Never use the assignment or fallback title as the final headline.
- Use a named actor, place, institution, document, dataset, number, event, or concrete object when possible.
- Do not start with A, An, or The if {MAX_DETERMINER_OPENERS_PER_ISSUE} current-issue headlines already do. Current count: {determiner_count}.
- visual_archetype exactly equals: {visual_assignment}
- visual_brief follows that archetype and avoids these visual clichés: {banned_visuals}
- Return the exact JSON shape only. No markdown fences.

Date context: {date_label}

Rejected draft JSON:
{json.dumps(payload, ensure_ascii=False)}
""".strip()

def call_model(
    client: OpenAI,
    section_name: str,
    date_label: str,
    recent_memory: list[dict[str, Any]] | None = None,
    current_issue: list[dict[str, Any]] | None = None,
    issue_index: int = 0,
    assignment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    recent_memory = recent_memory or []
    current_issue = current_issue or []

    visual_assignment = visual_archetype_for(issue_index, section_name)
    headline_shape = headline_shape_for(issue_index)
    recent_context = brief_recent_context(recent_memory, section_name, current_issue)

    if assignment:
        recent_context = f"{assignment_prompt_block(assignment)}\n\n{recent_context}"
    def lock_visual(payload: dict[str, Any]) -> dict[str, Any]:
        payload["visual_archetype"] = visual_assignment

        if not str(payload.get("visual_brief") or "").strip():
            payload[
                "visual_brief"
            ] = f"Use the assigned visual archetype: {visual_assignment}. Build a concrete, non-cliché scene specific to the article."

        payload, rewrites = rewrite_visual_cliches(payload, visual_assignment)

        if rewrites:
            print(
                f"WARNING: Rewrote banned visual cliché(s) for {section_name}: "
                + "; ".join(rewrites)
            )

        return payload

    def split_quality_issues(
        payload: dict[str, Any],
    ) -> tuple[list[str], list[str], list[str], dict[str, Any]]:
        required_issues = required_payload_issues(payload)
        base_issues, metrics = payload_quality_issues(payload)

        editorial_issues, editorial_metrics = editorial_quality_issues(
            payload=payload,
            recent=recent_memory,
            current_issue=current_issue,
            visual_assignment=visual_assignment,
        )

        merged_metrics = {**metrics, **editorial_metrics}
        return required_issues, base_issues, editorial_issues, merged_metrics

    payload = lock_visual(
        request_payload(
            client,
            generation_prompt(
                section_name,
                date_label,
                recent_context,
                visual_assignment,
                headline_shape,
                current_issue,
                assignment,
                ),
        )
    )

    for _ in range(FACT_CHECK_PASSES):
        payload = lock_visual(
            request_payload(
                client,
                verification_prompt(
                    payload,
                    section_name,
                    date_label,
                    recent_context,
                    visual_assignment,
                ),
            )
        )

    for _ in range(QUALITY_REPAIR_ATTEMPTS):
        required_issues, base_issues, editorial_issues, metrics = split_quality_issues(
            payload
        )

        reader_voice_issues = [

            issue

            for issue in editorial_issues

            if issue.startswith("headline sounds too definitive")

            or issue.startswith("article voice is getting too dense")

        ]

        hard_repair_issues = required_issues + base_issues + reader_voice_issues

        remaining_editorial_issues = [issue for issue in editorial_issues if issue not in reader_voice_issues]

        blocking_editorial_issues = remaining_editorial_issues if STRICT_EDITORIAL_GATES else []
        repair_issues = hard_repair_issues + blocking_editorial_issues

        if not repair_issues:
            if editorial_issues:
                print(
                    f"WARNING: {section_name} article has editorial variety warnings "
                    f"but no repair-triggering quality issues: {editorial_issues}; metrics={metrics}"
                )
            return payload

        prompt_issues = list(repair_issues)

        if editorial_issues and not STRICT_EDITORIAL_GATES:
            prompt_issues.append(
                "Non-blocking editorial warnings to improve while repairing hard quality issues: "
                + "; ".join(editorial_issues)
            )

        print(f"Quality repair needed for {section_name}: {repair_issues}")

        payload = lock_visual(
            request_payload(
                client,
                repair_prompt(
                    payload,
                    section_name,
                    date_label,
                    prompt_issues,
                    metrics,
                    recent_context,
                    visual_assignment,
                    headline_shape,
                    current_issue,
                ),
            )
        )

    required_issues, base_issues, editorial_issues, metrics = split_quality_issues(
        payload
    )

    if required_issues:
        raise RuntimeError(
            f"{section_name} article is missing required fields after repairs: "
            f"{required_issues}; metrics={metrics}"
        )

    if base_issues:
        message = (
            f"{section_name} article still has quality warnings after repairs: "
            f"{base_issues}; metrics={metrics}"
        )

        if STRICT_QUALITY_GATE:
            raise RuntimeError(message)

        print("WARNING: " + message)

    if editorial_issues:
        message = (
            f"{section_name} article still has editorial variety warnings after repairs: "
            f"{editorial_issues}; metrics={metrics}"
        )

        if STRICT_EDITORIAL_GATES:
            raise RuntimeError(message)

        print("WARNING: " + message)

    return payload


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


def issue_headline_audit_failures(headlines: list[str]) -> list[str]:
    failures: list[str] = []
    normalized = [title.strip() for title in headlines if str(title or "").strip()]

    determiner_titles = [title for title in normalized if first_word(title) in DETERMINER_OPENERS]
    if len(determiner_titles) > MAX_DETERMINER_OPENERS_PER_ISSUE:
        failures.append(
            "determiner opener cap exceeded "
            f"({len(determiner_titles)} > {MAX_DETERMINER_OPENERS_PER_ISSUE}): "
            + " | ".join(determiner_titles)
        )

    first_word_counts: Counter[str] = Counter()
    for title in normalized:
        word = first_word(title)
        if word:
            first_word_counts[word] += 1
    repeated = [f"{word}={count}" for word, count in sorted(first_word_counts.items()) if count > MAX_SAME_FIRST_WORD_PER_ISSUE]
    if repeated:
        failures.append(
            "first-word opener cap exceeded "
            f"(max {MAX_SAME_FIRST_WORD_PER_ISSUE}): " + ", ".join(repeated)
        )

    family_counts: Counter[str] = Counter()
    banned_titles: list[str] = []
    for title in normalized:
        families = headline_formula_families(title)
        lower = title.lower().replace("’", "'")
        matched_patterns = [pattern for pattern in BANNED_FORMULA_PATTERNS if re.search(pattern, lower)]
        if families or matched_patterns:
            details = sorted(set(families) | set(matched_patterns))
            banned_titles.append(f"{title} -> {', '.join(details)}")
        for family in families:
            family_counts[family] += 1

    if banned_titles:
        failures.append("banned headline formulas detected: " + " | ".join(banned_titles))

    repeated_families = [f"{family}={count}" for family, count in sorted(family_counts.items()) if count > 1]
    if repeated_families:
        failures.append("same banned formula family repeated across issue: " + ", ".join(repeated_families))

    return failures


def audit_issue_headlines(stories: list[Story]) -> None:
    failures = issue_headline_audit_failures([story.title for story in stories])
    if not failures:
        return

    message = "Final issue headline audit failed:\n- " + "\n- ".join(failures)
    if STRICT_EDITORIAL_GATES:
        raise RuntimeError(message)
    print("WARNING: " + message)


def enforce_issue_headline_audit(stories: list[Story]) -> None:
    """Backward-compatible alias for older call sites."""
    audit_issue_headlines(stories)


def run_headline_audit_self_test() -> None:
    sample = [
        "A city budget has become a housing trap",
        "An agency is becoming the loudest voice",
        "The council lands inside a transit crisis",
        "Markets is not just a scoreboard anymore",
        "Markets reprice the weekly grocery run",
    ]
    failures = issue_headline_audit_failures(sample)
    checks = {
        "determiner opener cap": any("determiner opener cap exceeded" in failure for failure in failures),
        "first-word opener cap": any("first-word opener cap exceeded" in failure for failure in failures),
        "has become": any("formula:has-become" in failure for failure in failures),
        "is becoming": any("formula:becoming" in failure for failure in failures),
        "lands inside": any("formula:lands-inside" in failure for failure in failures),
        "is not just": any("formula:not-just" in failure for failure in failures),
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError("Headline audit self-test failed: missing checks for " + ", ".join(missing))



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
    visual_brief = html.escape(story.visual_brief, quote=True)
    visual_archetype = html.escape(story.visual_archetype, quote=True)
    meta = html.escape(f"Written by Intelligent AI • {story.published_label} • {story_word_count(story.body_html)} words")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title} — The Press</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="{dek}" />
  <meta name="press:visual-archetype" content="{visual_archetype}" />
  <meta name="press:visual-brief" content="{visual_brief}" />
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
    visual_archetype = html.escape(story.visual_archetype, quote=True)
    meta = html.escape(f"Written by Intelligent AI • {story.published_label}")

    return f"""
<article class="story-card story-card--daily" data-section="{section}" data-visual-archetype="{visual_archetype}">
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


def patch_section_pages(stories: list[Story], edition_date: str) -> None:
    by_section: dict[str, list[Story]] = {}
    for story in stories:
        by_section.setdefault(story.section_slug, []).append(story)

    for section_slug, section_name in SECTIONS:
        section_stories = by_section.get(section_slug, [])
        if not section_stories:
            continue

        path = ROOT / f"section-{section_slug}.html"
        soup = load_or_minimal_html(path, f"{section_name} — The Press")
        cards = "\n".join(daily_card(story) for story in section_stories)
        html_fragment = f"""
<section id="daily-section-feed" class="daily-section-feed daily-home-section">
  <div class="section-heading-row">
    <h2 class="section-heading">Latest in {html.escape(section_name)} — {html.escape(edition_date)}</h2>
    <a class="section-link" href="archive.html">Open archive</a>
  </div>
  <p class="section-standfirst">New long-form work for this desk, built from broad source gathering, verification, and original synthesis.</p>
  <div class="cards-grid cards-grid--daily">
    {cards}
  </div>
</section>
""".strip()
        upsert_section(
            soup,
            "daily-section-feed",
            html_fragment,
            after_selector=".section-hero, .desk-hero, header",
        )
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
            "thumbnail_alt": story.thumbnail_alt,
            "visual_archetype": story.visual_archetype,
            "visual_brief": story.visual_brief,
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
                "keywords": story.keywords,
                "thumbnail_alt": story.thumbnail_alt,
                "visual_archetype": story.visual_archetype,
                "visual_brief": story.visual_brief,
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
      <p class="article-dek">Today’s full set of new long-form stories across the desks included in the daily workflow.</p>
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
    visual_archetype = str(payload.get("visual_archetype") or "").strip()
    visual_brief = str(payload.get("visual_brief") or "").strip()
    thumb_query = str(payload.get("thumbnail_search_hint") or visual_brief or title).strip()
    thumb_alt = str(payload.get("thumbnail_alt") or title).strip()

    # NEWS_FLOW_UI_IMPROVEMENT: skip database thumbnails; GPT Image backfill supplies article art.

    thumbnail_url = None

    thumbnail_caption_html = ""

    thumbnail_credit_plain = ""

    thumbnail_local = download_image(None, page_slug)

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
        visual_brief=visual_brief,
        visual_archetype=visual_archetype,
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
    run_headline_audit_self_test()

    stories: list[Story] = []
    selected_sections = pick_sections(story_count)
    recent_memory = load_recent_story_memory()
    story_goal = len(selected_sections)
    topic_plan: list[dict[str, Any]] = []
    if topic_radar_enabled():
        topic_plan = build_issue_plan(
            client=client,
            story_count=story_goal,
            date_label=published_label,
            edition_date=edition_date,
            recent_memory=recent_memory,
            allowed_sections=SECTIONS,
            root=ROOT,
        )

    if topic_plan:
        selected_assignments = topic_plan
    else:
        selected_assignments = [
            {
                "section_slug": section_slug,
                "section_name": section_name,
                "title": "",
                "bucket": "SECTION_ROTATION",
                "why_now": "",
                "core_question": "",
                "angle": "",
                "source_urls": [],
            }
            for section_slug, section_name in selected_sections
        ]

    current_issue_memory: list[dict[str, Any]] = []

    for issue_index, assignment in enumerate(selected_assignments):
        fallback_section_slug, fallback_section_name = selected_sections[issue_index % len(selected_sections)]
        section_slug = str(assignment.get("section_slug") or fallback_section_slug)
        section_name = str(assignment.get("section_name") or fallback_section_name)
        assignment_for_prompt = assignment if topic_plan else None
        payload = call_model(
            client,
            section_name,
            published_label,
            recent_memory=recent_memory,
            current_issue=current_issue_memory,
            issue_index=issue_index,
            assignment=assignment_for_prompt,
        )
        story = build_story_from_payload(
            payload=payload,
            section_slug=section_slug,
            section_name=section_name,
            edition_date=edition_date,
            published_label=published_label,
        )
        stories.append(story)
        current_issue_memory.append(
            {
                "title": story.title,
                "dek": story.dek,
                "section": story.section_name,
                "url": f"daily/{story.slug}.html",
                "keywords": story.keywords,
                "visual_archetype": story.visual_archetype,
                "visual_brief": story.visual_brief,
                "thumbnail_alt": story.thumbnail_alt,
            }
        )

    if not stories:
        raise RuntimeError("No articles generated; preserving existing site files")

    audit_issue_headlines(stories)

    for story in stories:
        page_path = DAILY_DIR / f"{story.slug}.html"
        page_path.write_text(build_story_page(story), encoding="utf-8")
        print(f"Wrote {page_path.relative_to(ROOT)}")

    patch_index(stories, edition_date)
    patch_archive(stories, edition_date)
    patch_breaking(stories, edition_date)
    patch_section_pages(stories, edition_date)
    update_search_index(stories)
    write_latest_json(stories, edition_date)
    write_daily_edition_page(stories, edition_date)
    patch_bylines_in_js()
    patch_styles()
    save_section_cursor(len(selected_assignments))

    print(f"Generated {len(stories)} stories for {edition_date}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

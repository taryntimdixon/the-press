#!/usr/bin/env python3
"""Topic Radar for The Press daily newsroom.

This module moves topic selection upstream of article generation. It uses the
OpenAI Responses API with web search to build a scored, varied daily assignment
plan, then hands concrete story assignments to the existing long-form generator.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import json
import os
import re
import time


# These are editorial *buckets*, not necessarily public site sections. Buckets
# let the issue mix notice interesting things without forcing the navigation to
# grow every time the newsroom gets curious.
TOPIC_BUCKETS: dict[str, str] = {
    "WORLD_HEAT": "major global news, wars, coups, sanctions, diplomacy, repression, regional crises, institutions under stress",
    "PUBLIC_UPRISING": "protests, strikes, youth movements, labor actions, civil unrest, anti-corruption movements, mass civic pressure",
    "AI_FRONTIER": "model releases, AI agents, chips, compute, data centers, frontier labs, regulation, labor impacts, education impacts",
    "SCIENCE_FEAT": "space, medicine, climate science, physics, archaeology, oceans, engineering milestones, peer-reviewed discoveries",
    "FOOD_CULTURE_LIFE": "food culture, restaurants, groceries, agriculture, taste, migration cuisines, public health, school food, supermarket politics",
    "CULTURE_PLATFORM": "film, music, fandom, creators, streaming, games, celebrity as industry signal, platform economics, audience behavior",
    "MONEY_SYSTEM": "housing, labor, inflation, debt, wages, budgets, supply chains, markets, business models, daily-life economics",
    "WEIRD_BUT_REAL": "odd institutions, subcultures, niche communities, strange datasets, surprising inventions, internet-native phenomena",
    "LOCAL_TO_GLOBAL": "one place, city, school, market, court, lab, factory, farm, or neighborhood that reveals a bigger system",

    # New interest buckets added for broader, more varied daily issues.
    "CLIMATE_EXTREMES": "heat, floods, storms, drought, wildfires, adaptation, disaster insurance, climate migration, grid stress",
    "CYBER_SECURITY": "cyberattacks, ransomware, surveillance, data leaks, digital infrastructure, scams, election security, spyware abuse",
    "MIGRATION_BORDERS": "migration routes, asylum systems, border politics, diaspora communities, remittances, refugee crises, deportations",
    "CITIES_HOUSING_TRANSIT": "cities, rent, homelessness, transit, roads, zoning, architecture, urban policy, infrastructure people actually use",
    "SPORTS_POWER": "sports as money, politics, labor, media rights, stadiums, gambling pressure, athlete power, fan cultures",
    "RELIGION_IDENTITY": "religion, belief, secularization, identity, ritual, institutions, moral conflict, law, education, community life",
    "JUSTICE_PUBLIC_SAFETY": "courts, prisons, policing, crime trends, public safety, civil rights, surveillance, local justice systems",
    "ENERGY_INFRASTRUCTURE": "power grids, oil, gas, nuclear, renewables, mining, transmission lines, water systems, shipping, logistics",
    "CONSUMER_LIFE": "what people buy, use, repair, eat, watch, subscribe to, return, save for, or quietly abandon",
    "HEALTH_SYSTEM_SHOCK": "disease outbreaks, hospitals, insurance, drugs, mental health, health labor, medical evidence, public-health capacity",
    "EDUCATION_YOUTH": "schools, colleges, youth culture, attendance, debt, campus politics, teachers, learning technology, family pressure",
    "SPACE_OCEAN_FRONTIER": "spaceflight, satellites, astronomy, oceans, polar science, deep-sea mining, frontier exploration and risk",
    "NATURE_ANIMALS": "wildlife, invasive species, biodiversity, animal welfare, conservation, urban animals, ecosystems in motion",
}

# Map buckets to the closest existing site section. This keeps the public nav
# stable while the assignment mix gets much more alive.
BUCKET_SECTION_DEFAULTS: dict[str, tuple[str, str]] = {
    "WORLD_HEAT": ("world", "World"),
    "PUBLIC_UPRISING": ("power", "Power"),
    "AI_FRONTIER": ("systems", "Systems"),
    "SCIENCE_FEAT": ("science", "Science"),
    "FOOD_CULTURE_LIFE": ("life", "Life"),
    "CULTURE_PLATFORM": ("culture", "Culture"),
    "MONEY_SYSTEM": ("money", "Money"),
    "WEIRD_BUT_REAL": ("the-weird-file", "The Weird File"),
    "LOCAL_TO_GLOBAL": ("front-page", "Front Page"),
    "CLIMATE_EXTREMES": ("science", "Science"),
    "CYBER_SECURITY": ("systems", "Systems"),
    "MIGRATION_BORDERS": ("world", "World"),
    "CITIES_HOUSING_TRANSIT": ("life", "Life"),
    "SPORTS_POWER": ("culture", "Culture"),
    "RELIGION_IDENTITY": ("ideas", "Ideas"),
    "JUSTICE_PUBLIC_SAFETY": ("power", "Power"),
    "ENERGY_INFRASTRUCTURE": ("systems", "Systems"),
    "CONSUMER_LIFE": ("life", "Life"),
    "HEALTH_SYSTEM_SHOCK": ("life", "Life"),
    "EDUCATION_YOUTH": ("life", "Life"),
    "SPACE_OCEAN_FRONTIER": ("science", "Science"),
    "NATURE_ANIMALS": ("science", "Science"),
}

WORLD_HEAT_BUCKETS = {"WORLD_HEAT", "PUBLIC_UPRISING", "MIGRATION_BORDERS"}
AI_OR_SCIENCE_BUCKETS = {"AI_FRONTIER", "SCIENCE_FEAT", "CLIMATE_EXTREMES", "SPACE_OCEAN_FRONTIER", "NATURE_ANIMALS"}
WEIRD_BUCKETS = {"WEIRD_BUT_REAL", "LOCAL_TO_GLOBAL", "CONSUMER_LIFE"}

HIGH_TRUST_SOURCE_HINTS = [
    "Reuters", "Associated Press", "BBC", "Al Jazeera", "France 24", "Deutsche Welle",
    "NPR", "Financial Times", "The Guardian", "New York Times", "Washington Post",
    "NASA", "NOAA", "WHO", "CDC", "FDA", "UN", "World Bank", "IMF", "OECD",
    "Nature", "Science", "arXiv", "PLOS", "The Lancet", "JAMA", "NEJM",
    "Eater", "Bon Appétit", "Food & Wine", "Civil Eats", "Rest of World", "404 Media",
]


@dataclass
class TopicAssignment:
    title: str
    bucket: str
    section_slug: str
    section_name: str
    why_now: str
    core_question: str
    angle: str
    source_urls: list[str] = field(default_factory=list)
    country_or_region: str = ""
    tags: list[str] = field(default_factory=list)
    trend_heat: float = 0.0
    global_news_heat: float = 0.0
    impact: float = 0.0
    freshness: float = 0.0
    source_quality: float = 0.0
    surprise: float = 0.0
    press_fit: float = 0.0
    repetition_penalty: float = 0.0
    low_source_penalty: float = 0.0
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["score"] = round(float(self.score or self.computed_score()), 3)
        return payload

    def computed_score(self) -> float:
        return (
            self.trend_heat * 0.24
            + self.global_news_heat * 0.22
            + self.impact * 0.18
            + self.freshness * 0.12
            + self.source_quality * 0.10
            + self.surprise * 0.08
            + self.press_fit * 0.06
            - self.repetition_penalty
            - self.low_source_penalty
        )


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


def topic_radar_enabled() -> bool:
    mode = os.getenv("TOPIC_SELECTION_MODE", "radar").strip().lower()
    return mode not in {"", "0", "false", "off", "section", "sections", "rotation", "old"}


def topic_radar_required() -> bool:
    mode = os.getenv("TOPIC_SELECTION_MODE", "radar").strip().lower()
    default_required = mode == "radar"
    return env_bool("TOPIC_RADAR_REQUIRED", default_required)


def clean_text(value: Any, max_len: int = 260) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:max_len].rstrip()


def source_domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return ""
    return host[4:] if host.startswith("www.") else host


def extract_json(text: str, repair_attempt: bool = False) -> dict[str, Any]:
    """Extract JSON from model response, fixing common formatting issues.
    
    Args:
        text: Raw model response that may contain JSON with formatting issues.
        repair_attempt: If True, this is a repair retry and we should be stricter.
        
    Returns:
        Parsed JSON object as dict.
        
    Raises:
        json.JSONDecodeError: If JSON cannot be parsed after cleanup attempts.
        ValueError: If no JSON object found or other structural issues.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("Response is empty")
    
    # Remove markdown code fences if present
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()
    
    # Find the outermost JSON object boundaries
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object ('{' ... '}') found in response")
    
    # Extract just the JSON object
    cleaned = cleaned[start : end + 1]
    
    # Remove trailing commas before closing braces/brackets
    # This regex handles: ,"};  ,"]:  ,}  ,]  etc.
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        # Provide context for debugging without exposing raw response
        error_msg = f"JSON parse error at position {exc.pos}: {exc.msg}"
        if len(cleaned) > 500:
            snippet = f"...{cleaned[max(0, exc.pos-100):min(len(cleaned), exc.pos+100)]}..."
        else:
            snippet = cleaned
        raise json.JSONDecodeError(
            f"{error_msg}\nSnippet: {snippet}",
            exc.doc,
            exc.pos
        ) from exc


def topic_terms(*values: Any) -> set[str]:
    stopwords = {
        "about", "after", "again", "against", "america", "american", "between", "could",
        "daily", "edition", "every", "from", "have", "more", "over", "press", "story",
        "that", "their", "there", "these", "they", "this", "through", "today", "under",
        "while", "would", "with", "without", "year", "years", "update",
    }
    text = " ".join(str(value or "") for value in values)
    output: set[str] = set()
    for raw in re.findall(r"[A-Za-z][A-Za-z'’.-]{2,}", text.lower()):
        token = raw.strip(".'’-")
        if len(token) < 4 or token in stopwords:
            continue
        output.add(token)
    return output


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))


def brief_recent_for_prompt(recent_memory: list[dict[str, Any]], limit: int = 40) -> str:
    if not recent_memory:
        return "No recent archive memory was available. Still avoid obvious generic topics and samey headline rhythms."
    lines = []
    for item in recent_memory[:limit]:
        title = clean_text(item.get("title"), 160)
        section = clean_text(item.get("section"), 40)
        dek = clean_text(item.get("dek") or item.get("summary"), 180)
        if title:
            lines.append(f"- {section}: {title} — {dek}")
    return "\n".join(lines) or "No usable recent archive memory was available."


def section_lookup(allowed_sections: list[tuple[str, str]]) -> dict[str, tuple[str, str]]:
    lookup: dict[str, tuple[str, str]] = {}
    for slug, name in allowed_sections:
        lookup[slug.lower()] = (slug, name)
        lookup[name.lower()] = (slug, name)
    return lookup


def normalize_assignment(raw: dict[str, Any], allowed_sections: list[tuple[str, str]]) -> TopicAssignment | None:
    if not isinstance(raw, dict):
        return None
    title = clean_text(raw.get("title"), 220)
    if not title:
        return None

    bucket = clean_text(raw.get("bucket"), 80).upper().replace(" ", "_").replace("-", "_")
    if bucket not in TOPIC_BUCKETS:
        bucket = "WEIRD_BUT_REAL"

    lookup = section_lookup(allowed_sections)
    default_slug, default_name = BUCKET_SECTION_DEFAULTS.get(bucket, allowed_sections[0])
    raw_slug = clean_text(raw.get("section_slug"), 80).lower()
    raw_name = clean_text(raw.get("section_name"), 80).lower()
    section_slug, section_name = lookup.get(raw_slug) or lookup.get(raw_name) or lookup.get(default_slug) or allowed_sections[0]

    source_urls: list[str] = []
    for item in raw.get("source_urls") or raw.get("starter_sources") or []:
        url = str(item or "").strip()
        if url.startswith("https://") and source_domain(url):
            source_urls.append(url)
    source_urls = list(dict.fromkeys(source_urls))[:12]

    tags = [clean_text(tag, 40) for tag in raw.get("tags", []) if clean_text(tag, 40)][:10]

    def num(name: str) -> float:
        try:
            return float(raw.get(name, 0.0) or 0.0)
        except (TypeError, ValueError):
            return 0.0

    assignment = TopicAssignment(
        title=title,
        bucket=bucket,
        section_slug=section_slug,
        section_name=section_name,
        why_now=clean_text(raw.get("why_now"), 500),
        core_question=clean_text(raw.get("core_question"), 260),
        angle=clean_text(raw.get("angle"), 500),
        source_urls=source_urls,
        country_or_region=clean_text(raw.get("country_or_region"), 100),
        tags=tags,
        trend_heat=num("trend_heat"),
        global_news_heat=num("global_news_heat"),
        impact=num("impact"),
        freshness=num("freshness"),
        source_quality=num("source_quality"),
        surprise=num("surprise"),
        press_fit=num("press_fit"),
        repetition_penalty=num("repetition_penalty"),
        low_source_penalty=num("low_source_penalty"),
        score=num("score"),
    )
    if not assignment.score:
        assignment.score = assignment.computed_score()
    return assignment


def pad_with_section_rotation(
    assignments: list[TopicAssignment],
    story_count: int,
    allowed_sections: list[tuple[str, str]],
) -> list[TopicAssignment]:
    if len(assignments) >= story_count:
        return assignments[:story_count]
    existing_terms = [topic_terms(item.title, item.angle, item.why_now) for item in assignments]
    for idx in range(story_count - len(assignments)):
        slug, name = allowed_sections[(len(assignments) + idx) % len(allowed_sections)]
        fallback = TopicAssignment(
            title=(
                f"{name} fallback assignment: choose a current story with a named actor, "
                "place, document, dataset, or event"
            ),
            bucket="LOCAL_TO_GLOBAL",
            section_slug=slug,
            section_name=name,
            why_now="Fallback assignment used because the radar returned fewer stories than requested.",
            core_question=(
                f"What current {name.lower()} story has the clearest named actor, place, document, "
                "dataset, institution, event, or object anchor with real stakes?"
            ),
            angle=(
                "Do not use this fallback assignment as the final headline. Avoid headlines that start "
                "with A, An, or The unless no sharper subject exists. Choose a current, sourced, "
                "concrete story with real stakes and anchor the headline in a named actor, place, "
                "document, dataset, institution, event, or object."
            ),
            source_urls=[],
            press_fit=5.0,
            freshness=5.0,
            score=3.0,
        )
        terms = topic_terms(fallback.title, fallback.angle)
        if all(jaccard(terms, existing) < 0.30 for existing in existing_terms):
            assignments.append(fallback)
            existing_terms.append(terms)
    return assignments[:story_count]


def normalize_plan(
    payload: dict[str, Any],
    story_count: int,
    allowed_sections: list[tuple[str, str]],
) -> tuple[list[dict[str, Any]], list[TopicAssignment], int]:
    raw_candidates = payload.get("candidates") if isinstance(payload, dict) else []
    raw_assignments = payload.get("assignments") if isinstance(payload, dict) else []
    if not isinstance(raw_candidates, list):
        raw_candidates = []
    if not isinstance(raw_assignments, list):
        raw_assignments = []

    normalized_candidates: list[dict[str, Any]] = []
    for raw in raw_candidates:
        item = normalize_assignment(raw, allowed_sections) if isinstance(raw, dict) else None
        if item:
            normalized_candidates.append(item.to_dict())

    assignments: list[TopicAssignment] = []
    seen: list[set[str]] = []
    for raw in raw_assignments or raw_candidates:
        item = normalize_assignment(raw, allowed_sections) if isinstance(raw, dict) else None
        if not item:
            continue
        terms = topic_terms(item.title, item.angle, item.why_now, " ".join(item.tags))
        if any(jaccard(terms, other) >= 0.35 for other in seen):
            continue
        assignments.append(item)
        seen.append(terms)
        if len(assignments) >= story_count:
            break

    usable_assignment_count = len(assignments)
    assignments = pad_with_section_rotation(assignments, story_count, allowed_sections)
    return normalized_candidates, assignments, usable_assignment_count


def issue_mix_rules(story_count: int) -> dict[str, Any]:
    return {
        "story_count": story_count,
        "candidate_count_target": max(story_count * env_int("TOPIC_RADAR_CANDIDATE_MULTIPLIER", 3, minimum=2, maximum=6), story_count + 8),
        "min_world_heat": min(story_count, env_int("MIN_WORLD_HEAT_STORIES", 3, minimum=0)),
        "min_ai_or_science": min(story_count, env_int("MIN_AI_OR_SCIENCE_STORIES", 2, minimum=0)),
        "min_food_culture_life": min(story_count, env_int("MIN_FOOD_CULTURE_LIFE_STORIES", 1, minimum=0)),
        "min_weird_or_niche": min(story_count, env_int("MIN_WEIRD_OR_NICHE_STORIES", 1, minimum=0)),
        "min_non_us": min(story_count, env_int("MIN_NON_US_STORIES", 4, minimum=0)),
        "max_us_institutional_process": env_int("MAX_US_INSTITUTIONAL_PROCESS_STORIES", 2, minimum=0),
        "max_same_country": env_int("MAX_SAME_COUNTRY_STORIES", 2, minimum=1),
        "max_same_bucket": env_int("MAX_SAME_BUCKET_STORIES", 3, minimum=1),
        "wildcard_rate": env_float("WILDCARD_RATE", 0.20, minimum=0.0, maximum=1.0),
        "trend_lookback_hours": env_int("TREND_LOOKBACK_HOURS", 48, minimum=4, maximum=168),
    }


def build_topic_radar_prompt(
    *,
    story_count: int,
    date_label: str,
    recent_memory: list[dict[str, Any]],
    allowed_sections: list[tuple[str, str]],
) -> str:
    bucket_lines = "\n".join(f"- {key}: {value}" for key, value in TOPIC_BUCKETS.items())
    section_lines = "\n".join(f"- {slug}: {name}" for slug, name in allowed_sections)
    rules = issue_mix_rules(story_count)
    source_hints = ", ".join(HIGH_TRUST_SOURCE_HINTS)
    recent = brief_recent_for_prompt(recent_memory)
    return f"""
You are the assignment editor for The Press. Build today's topic radar before article generation.

Date context: {date_label}
Requested final assignments: {story_count}

Allowed public site sections. Every assignment must choose one of these section_slug/section_name pairs:
{section_lines}

Editorial buckets to watch. Buckets are broader than site sections:
{bucket_lines}

Issue mix rules:
{json.dumps(rules, indent=2)}

Recent archive memory — avoid repeating the same subject, same country-only framing, same headline rhythm, or same visual idea:
{recent}

Source standards:
- Use live web search and favor high-trust reporting, primary documents, official datasets, scientific institutions, and strong local reporting.
- Useful source families include: {source_hints}.
- Each candidate should include 3 to 8 starter https URLs when possible. Do not invent URLs.
- The later article generator will still do deeper research; your job is to assign the right stories.

Selection taste:
- Think like a sharp front-page editor, not a category rotator.
- Assignment framing should be concrete, curious, and humble, not all-knowing. Avoid this-proves-everything or real-truth language.
- Include huge global developments, AI/science/technology shocks, uprisings and civic pressure, climate/energy/infrastructure, food/life/culture, and one or two strange but real stories.
- Do not overfit to any examples. The point is range, surprise, consequence, and sourceability.
- Avoid a stale run of generic U.S. institutional-process stories unless one is genuinely enormous.
- Prefer concrete factual pegs from the last {rules['trend_lookback_hours']} hours, but allow slower-moving stories when the stakes are large and the angle is fresh.
- Assignment titles are planning labels only, not final headlines.

Return JSON only with this exact shape:
{{
  "candidates": [
    {{
      "title": "specific assignment title, not final headline; concrete, curious, and not over-definitive",
      "bucket": "ONE_BUCKET_KEY_FROM_ABOVE",
      "section_slug": "one allowed slug",
      "section_name": "one allowed section name",
      "why_now": "fresh factual peg and why it matters today",
      "core_question": "the question the article should answer",
      "angle": "the reporting angle, with what to avoid",
      "country_or_region": "place or global",
      "tags": ["short", "tags"],
      "source_urls": ["https://..."],
      "trend_heat": 0-10,
      "global_news_heat": 0-10,
      "impact": 0-10,
      "freshness": 0-10,
      "source_quality": 0-10,
      "surprise": 0-10,
      "press_fit": 0-10,
      "repetition_penalty": 0-10,
      "low_source_penalty": 0-10,
      "score": 0-10
    }}
  ],
  "assignments": [
    "select exactly {story_count} candidate objects here, revised if needed for variety"
  ]
}}
""".strip()


def request_topic_payload(client: Any, prompt: str) -> dict[str, Any]:
    """Request and parse topic radar JSON payload from the model.
    
    Attempts to parse the response with the improved extract_json() function.
    If JSON parsing fails, makes a repair request asking the model to return
    valid JSON only, then retries parsing.
    
    Args:
        client: OpenAI client with responses API.
        prompt: The editorial assignment prompt.
        
    Returns:
        Parsed Topic Radar JSON payload as dict.
        
    Raises:
        Exception: If all attempts fail (API errors or unfixable JSON).
    """
    tool_candidates = [
        os.getenv("OPENAI_WEB_SEARCH_TOOL", "").strip(),
        "web_search",
        "web_search_preview",
    ]
    ordered_tools: list[str] = []
    for tool in tool_candidates:
        if tool and tool not in ordered_tools:
            ordered_tools.append(tool)

    model = os.getenv("TOPIC_RADAR_MODEL") or os.getenv("OPENAI_MODEL", "gpt-5.5")
    max_tokens = env_int("TOPIC_RADAR_MAX_OUTPUT_TOKENS", 9000, minimum=3000, maximum=24000)
    last_response_text = ""
    last_error: Exception | None = None

    # Try to get a valid response from the model
    for tool_type in ordered_tools:
        for attempt in range(2):
            try:
                response = client.responses.create(
                    model=model,
                    tools=[{"type": tool_type}],
                    input=prompt,
                    max_output_tokens=max_tokens,
                )
                last_response_text = getattr(response, "output_text", "") or ""
                return extract_json(last_response_text)
            except (json.JSONDecodeError, ValueError) as json_exc:
                # JSON parsing error: save it but try repair
                last_error = json_exc
                break  # Don't retry network, go straight to repair
            except Exception as exc:  # pragma: no cover - API/network error
                last_error = exc
                if attempt == 1:
                    break
                time.sleep(2 * (attempt + 1))

    # Last chance without the explicit web-search tool
    if not last_response_text:
        try:
            response = client.responses.create(
                model=model,
                input=prompt,
                max_output_tokens=max_tokens,
            )
            last_response_text = getattr(response, "output_text", "") or ""
            return extract_json(last_response_text)
        except (json.JSONDecodeError, ValueError) as json_exc:
            last_error = json_exc
        except Exception as exc:  # pragma: no cover - runtime fallback path
            last_error = exc

    # If we got a response but it had JSON issues, try repair
    if last_response_text and isinstance(last_error, (json.JSONDecodeError, ValueError)):
        repair_prompt = f"""Your previous response had JSON formatting issues. 
Please return ONLY valid JSON, with no markdown code fences, no commentary, and no extra text.
Preserve all the original fields and meaning.

Previous response (for context):
{last_response_text[:1500]}

Now return ONLY the corrected JSON:"""
        
        try:
            repair_response = client.responses.create(
                model=model,
                input=repair_prompt,
                max_output_tokens=max_tokens,
            )
            repair_text = getattr(repair_response, "output_text", "") or ""
            return extract_json(repair_text, repair_attempt=True)
        except Exception as repair_exc:  # pragma: no cover - repair attempt failed
            # If repair also fails, raise the original JSON error with context
            raise last_error from repair_exc

    # No response received and no repair opportunity
    assert last_error is not None
    raise last_error


def write_topic_plan_files(
    *,
    root: Path,
    edition_date: str,
    payload: dict[str, Any],
    candidates: list[dict[str, Any]],
    assignments: list[TopicAssignment],
) -> None:
    daily_dir = root / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    output = {
        "edition_date": edition_date,
        "mode": os.getenv("TOPIC_SELECTION_MODE", "radar"),
        "mix_rules": issue_mix_rules(len(assignments)),
        "candidates": candidates,
        "assignments": [item.to_dict() for item in assignments],
        "raw_payload_keys": sorted(payload.keys()) if isinstance(payload, dict) else [],
    }
    dated = daily_dir / f"topic-candidates-{edition_date}.json"
    latest = daily_dir / "topic-plan-latest.json"
    dated.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    latest.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Topic radar wrote {dated.relative_to(root)} and {latest.relative_to(root)}")


def build_issue_plan(
    *,
    client: Any,
    story_count: int,
    date_label: str,
    edition_date: str,
    recent_memory: list[dict[str, Any]],
    allowed_sections: list[tuple[str, str]],
    root: Path,
) -> list[dict[str, Any]]:
    if not topic_radar_enabled():
        return []

    story_count = max(1, story_count)
    prompt = build_topic_radar_prompt(
        story_count=story_count,
        date_label=date_label,
        recent_memory=recent_memory,
        allowed_sections=allowed_sections,
    )
    required = topic_radar_required()
    try:
        payload = request_topic_payload(client, prompt)
        if not isinstance(payload, dict):
            raise RuntimeError("Topic radar returned a non-object payload")
        if isinstance(payload, dict) and payload.get("error"):
            raise RuntimeError(f"Topic radar returned error payload: {clean_text(payload.get('error'), 300)}")

        raw_assignments = payload.get("assignments")
        if not isinstance(raw_assignments, list) or not raw_assignments:
            raise RuntimeError("Topic radar returned empty assignments")

        candidates, assignments, usable_assignment_count = normalize_plan(payload, story_count, allowed_sections)
        if not candidates:
            raise RuntimeError("Topic radar returned empty candidates")
        if not assignments or usable_assignment_count <= 0:
            raise RuntimeError("Topic radar returned an unusable plan")
        if usable_assignment_count < story_count:
            raise RuntimeError(
                f"Topic radar returned only {usable_assignment_count} usable assignments for requested {story_count}"
            )

        write_topic_plan_files(
            root=root,
            edition_date=edition_date,
            payload=payload,
            candidates=candidates,
            assignments=assignments,
        )
        return [item.to_dict() for item in assignments]
    except Exception as exc:  # pragma: no cover - runtime fallback path
        if required:
            raise RuntimeError(f"Topic radar is required and failed: {exc}") from exc

        print(f"WARNING: Topic radar failed; using emergency lane rotation fallback: {exc}")
        fallback_payload = {"error": str(exc), "candidates": [], "assignments": []}
        _, assignments, _ = normalize_plan(fallback_payload, story_count, allowed_sections)
        write_topic_plan_files(
            root=root,
            edition_date=edition_date,
            payload=fallback_payload,
            candidates=[],
            assignments=assignments,
        )
        return [item.to_dict() for item in assignments]


def assignment_prompt_block(assignment: dict[str, Any] | None) -> str:
    if not assignment:
        return ""
    title = clean_text(assignment.get("title"), 240)
    bucket = clean_text(assignment.get("bucket"), 80)
    why_now = clean_text(assignment.get("why_now"), 700)
    core_question = clean_text(assignment.get("core_question"), 300)
    angle = clean_text(assignment.get("angle"), 700)
    source_urls = assignment.get("source_urls") if isinstance(assignment.get("source_urls"), list) else []
    sources = "\n".join(f"  - {url}" for url in source_urls[:10] if str(url).startswith("https://"))
    if not sources:
        sources = "  - No starter URLs supplied; perform live research before drafting."
    return f"""
Story assignment locked by Topic Radar:
- Topic: {title}
- Bucket: {bucket}
- Why now: {why_now}
- Core question: {core_question}
- Required angle: {angle}
- Starter sources:
{sources}

Stay on this assignment unless live research proves it is false, stale, unsafe, or impossible to source. If the assignment fails, pivot only to a nearby story in the same bucket and show that pivot through sourcing, not meta language.

Voice reminder: the final article should be fun, clear, humane, substantive, and unbiased. Make room for uncertainty. Explain specialized terms the first time they appear. Keep headlines concrete, sourced, and curious. Do not make the headline or thesis sound like the newsroom has solved the whole subject.
""".strip()

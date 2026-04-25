#!/usr/bin/env python3
"""
Apply visible, user-facing fixes to The Press site.

This patch is intentionally aimed at the files visitors actually load:
- index.html homepage lead panels and top cards
- app.js page transition / double-flash behavior
- styles.css flash and lead-image spacing overrides
- HTML cache-busting for app.js/styles.css
- thumbnail workflow force settings for the current issue backfill

Run from the repository root:
    python3 apply_actual_visible_site_fix.py
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import time
from pathlib import Path
from typing import Any

TOKEN = "newsflow-visible-fix-20260425"
BACKUP_DIR_NAME = ".bak-actual-visible-site-fix"


def find_repo_root() -> Path:
    here = Path.cwd().resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "index.html").exists() and (candidate / "styles.css").exists() and (candidate / "app.js").exists():
            return candidate
    raise SystemExit("Run this from the repo root — the folder with index.html, app.js, and styles.css.")


ROOT = find_repo_root()
BACKUP_DIR = ROOT / BACKUP_DIR_NAME / time.strftime("%Y%m%d-%H%M%S")
CHANGED: list[str] = []


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_if_changed(path: Path, text: str) -> bool:
    old = read(path) if path.exists() else ""
    if old == text:
        return False
    backup(path)
    path.write_text(text, encoding="utf-8")
    CHANGED.append(rel(path))
    return True


def backup(path: Path) -> None:
    if not path.exists():
        return
    dest = BACKUP_DIR / path.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(path, dest)


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def h(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def section_href(section: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(section or "").lower()).strip("-")
    return f"section-{slug}.html" if slug else "archive.html"


def load_current_articles() -> list[dict[str, Any]]:
    path = ROOT / "daily-latest.json"
    if not path.exists():
        raise SystemExit("daily-latest.json is missing, so I cannot promote the current issue onto the homepage.")
    data = json.loads(read(path))
    if isinstance(data, dict):
        items = data.get("articles") or data.get("stories") or data.get("items") or []
    elif isinstance(data, list):
        items = data
    else:
        items = []
    articles = [item for item in items if isinstance(item, dict) and item.get("title") and item.get("url")]
    if len(articles) < 4:
        raise SystemExit("daily-latest.json needs at least 4 current articles to rebuild the homepage lead area.")
    return articles


def image_for(article: dict[str, Any]) -> str:
    return str(
        article.get("image")
        or article.get("thumbnail")
        or article.get("photo")
        or "assets/fallback-news.svg"
    ).strip()


def alt_for(article: dict[str, Any]) -> str:
    return str(
        article.get("imageAlt")
        or article.get("thumbnail_alt")
        or article.get("alt")
        or article.get("title")
        or "The Press story image"
    ).strip()


def summary_for(article: dict[str, Any], limit: int = 430) -> str:
    text = re.sub(r"\s+", " ", str(article.get("summary") or article.get("dek") or article.get("description") or "")).strip()
    if len(text) <= limit:
        return text
    clipped = text[: limit - 1]
    last_space = clipped.rfind(" ")
    if last_space > 120:
        clipped = clipped[:last_space]
    return clipped.rstrip() + "…"


def render_lead_panel(article: dict[str, Any], idx: int) -> str:
    active = " is-active" if idx == 0 else ""
    title = str(article.get("title") or "Untitled")
    section = str(article.get("section") or "News")
    url = str(article.get("url") or "#")
    image = image_for(article)
    alt = alt_for(article)
    published = str(article.get("published") or article.get("publishedLabel") or "")
    meta = "Written by Intelligent AI" + (f" • {published}" if published else "")
    note = str(article.get("image_credit") or article.get("imageCreditPlain") or article.get("imageCredit") or "AI-generated editorial thumbnail by The Press.")
    return f'''<div class="lead-panel{active}" data-lead-panel="" id="lead-{idx}">
  <div class="lead-panel__media">
    <img alt="{h(alt)}" decoding="async" loading="{'eager' if idx == 0 else 'lazy'}" src="{h(image)}" />
    <div class="lead-panel__media-note"><p class="eyebrow eyebrow--tiny">AI thumbnail</p><p class="lead-panel__media-copy">{h(note)}</p><p class="lead-panel__media-source">Current issue • AI-generated story art</p></div>
  </div>
  <div class="lead-panel__body">
    <div>
      <p class="eyebrow">Front Page • {h(section)} • Daily Issue</p>
      <h2><a href="{h(url)}">{h(title)}</a></h2>
      <p class="lead-panel__dek">{h(summary_for(article))}</p>
      <p class="lead-panel__meta">{h(meta)}</p>
    </div>
    <div class="button-row">
      <a class="button" href="{h(url)}">Read story</a>
      <a class="button button--ghost" href="{h(section_href(section))}">More {h(section.lower())}</a>
    </div>
  </div>
</div>'''


def render_lead_button(article: dict[str, Any], idx: int) -> str:
    active = " is-active" if idx == 0 else ""
    pressed = "true" if idx == 0 else "false"
    return (
        f'<button aria-pressed="{pressed}" class="lead-nav__button{active}" data-lead-button="" '
        f'data-target="lead-{idx}" type="button"><span>{h(article.get("section") or "News")}</span>'
        f'<strong>{h(article.get("title") or "Untitled")}</strong></button>'
    )


def render_card(article: dict[str, Any]) -> str:
    title = str(article.get("title") or "Untitled")
    section = str(article.get("section") or "News")
    url = str(article.get("url") or "#")
    image = image_for(article)
    alt = alt_for(article)
    published = str(article.get("published") or article.get("publishedLabel") or "")
    meta = "Written by Intelligent AI" + (f" • {published}" if published else "")
    return f'''<article class="story-card" data-section="{h(section)}" data-type="Daily Issue">
  <a class="story-card__image" href="{h(url)}">
    <img alt="{h(alt)}" decoding="async" loading="lazy" src="{h(image)}" />
  </a>
  <div class="story-card__body">
    <p class="eyebrow eyebrow--compact">{h(section)} • Daily Issue</p>
    <h3 class="story-card__title"><a href="{h(url)}">{h(title)}</a></h3>
    <p class="story-card__dek">{h(summary_for(article, 260))}</p>
    <p class="story-card__meta">{h(meta)}</p>
  </div>
</article>'''


IMMEDIATE_ROTATION_SCRIPT = '''<script>
(function () {
  try {
    var panels = Array.prototype.slice.call(document.querySelectorAll('[data-lead-panel]'));
    var buttons = Array.prototype.slice.call(document.querySelectorAll('[data-lead-button]'));
    if (!panels.length || !buttons.length) return;
    var previous = Number(sessionStorage.getItem('press-visible-lead-index') || '-1');
    var chosen = Math.floor(Math.random() * panels.length);
    if (panels.length > 1 && chosen === previous) chosen = (chosen + 1) % panels.length;
    sessionStorage.setItem('press-visible-lead-index', String(chosen));
    panels.forEach(function (panel, index) { panel.classList.toggle('is-active', index === chosen); });
    buttons.forEach(function (button, index) {
      button.classList.toggle('is-active', index === chosen);
      button.setAttribute('aria-pressed', String(index === chosen));
    });
  } catch (_) {}
})();
</script>'''


def patch_index() -> None:
    path = ROOT / "index.html"
    text = read(path)
    articles = load_current_articles()
    lead_articles = articles[:4]
    card_articles = articles[4:7] if len(articles) >= 7 else articles[1:4]

    lead_block = (
        '<div class="lead-switcher__panels">\n'
        + "\n".join(render_lead_panel(article, idx) for idx, article in enumerate(lead_articles))
        + '\n</div>\n\n<div aria-label="Lead story switcher" class="lead-nav">\n'
        + "\n".join(render_lead_button(article, idx) for idx, article in enumerate(lead_articles))
        + "\n</div>\n"
        + IMMEDIATE_ROTATION_SCRIPT
    )

    lead_pattern = re.compile(
        r'<div class="lead-switcher__panels">.*?<div aria-label="Lead story switcher" class="lead-nav">.*?</div>',
        re.S,
    )
    text, lead_count = lead_pattern.subn(lead_block, text, count=1)
    if lead_count != 1:
        raise SystemExit("Could not find the homepage lead switcher block in index.html.")

    card_block = '<div class="cards-grid cards-grid--three">\n' + "\n".join(render_card(article) for article in card_articles) + "\n"
    cards_pattern = re.compile(
        r'<div class="cards-grid cards-grid--three">.*?(?=</div>\s*</div>\s*<aside class="home-grid__aside">)',
        re.S,
    )
    text, cards_count = cards_pattern.subn(card_block, text, count=1)
    if cards_count != 1:
        print("Warning: could not replace the More from the edition card grid; lead area was still updated.")

    first = lead_articles[0]
    abs_image = "https://thepress.live/" + image_for(first).lstrip("/")
    title = str(first.get("title") or "The Press — Front Page")
    desc = summary_for(first, 220)
    text = re.sub(r'(<meta content=")[^"]*(" property="og:title"/>)', rf'\1{h(title)} — The Press\2', text, count=1)
    text = re.sub(r'(<meta content=")[^"]*(" name="twitter:title"/>)', rf'\1{h(title)} — The Press\2', text, count=1)
    text = re.sub(r'(<meta content=")[^"]*(" property="og:description"/>)', rf'\1{h(desc)}\2', text, count=1)
    text = re.sub(r'(<meta content=")[^"]*(" name="twitter:description"/>)', rf'\1{h(desc)}\2', text, count=1)
    text = re.sub(r'(<meta content=")[^"]*(" property="og:image"/>)', rf'\1{h(abs_image)}\2', text, count=1)
    text = re.sub(r'(<meta content=")[^"]*(" name="twitter:image"/>)', rf'\1{h(abs_image)}\2', text, count=1)

    write_if_changed(path, text)


def patch_cache_busting() -> None:
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts or BACKUP_DIR_NAME in path.parts:
            continue
        text = read(path)
        new = re.sub(r'href="styles\.css(?:\?[^\"]*)?"', f'href="styles.css?v={TOKEN}"', text)
        new = re.sub(r'src="app\.js(?:\?[^\"]*)?"', f'src="app.js?v={TOKEN}"', new)
        write_if_changed(path, new)


def replace_function(text: str, name: str, new_function: str) -> tuple[str, int]:
    needle = f"function {name}"
    start = text.find(needle)
    if start < 0:
        return text, 0
    brace = text.find("{", start)
    if brace < 0:
        return text, 0
    depth = 0
    for index in range(brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[:start] + new_function + text[index + 1 :], 1
    return text, 0


def patch_app_js() -> None:
    path = ROOT / "app.js"
    text = read(path)
    new_function = """function setupSmoothNavigation() {
    // Disabled by visible news-flow fix: instant navigation prevents the refresh/click double-flash.
  }"""
    text, count = replace_function(text, "setupSmoothNavigation", new_function)
    if count != 1:
        print("Warning: setupSmoothNavigation() was not found in app.js; CSS flash fixes still apply.")

    # Make the built-in lead picker avoid deterministic same-day behavior when it runs.
    old = """const weightedOrder = [0, 0, 0, 1, 1, 2, 3]; const key = new Date().toISOString().slice(0, 10).split('-').join(''); let hash = 0; for (const char of key) hash = ((hash * 31) + char.charCodeAt(0)) >>> 0; const chosen = weightedOrder[hash % weightedOrder.length]; const chosenButton = leadButtons[chosen]; if (chosenButton) setLead(chosenButton.dataset.target);"""
    new = """const previous = Number(sessionStorage.getItem('press-last-lead-index') ?? -1); let chosen = Math.floor(Math.random() * leadButtons.length); if (leadButtons.length > 1 && chosen === previous) { chosen = (chosen + 1) % leadButtons.length; } sessionStorage.setItem('press-last-lead-index', String(chosen)); const chosenButton = leadButtons[chosen]; if (chosenButton) setLead(chosenButton.dataset.target);"""
    text = text.replace(old, new)

    write_if_changed(path, text)


def patch_styles() -> None:
    path = ROOT / "styles.css"
    text = read(path)
    block = """

/* PRESS_ACTUAL_VISIBLE_SITE_FIX_START
   No transition flash, no delayed internal navigation feel, tighter lead-image geometry.
*/
html.press-dynamic-page body,
html.press-page-ready body,
html.press-page-leaving body,
body.press-page-leaving {
  animation: none !important;
  opacity: 1 !important;
  transform: none !important;
  filter: none !important;
}
html.press-dynamic-page [data-press-reveal],
html.press-page-ready [data-press-reveal],
html.press-page-leaving [data-press-reveal],
.page-home [data-press-reveal],
.page-archive [data-press-reveal],
.page-section [data-press-reveal] {
  opacity: 1 !important;
  transform: none !important;
  transition: none !important;
  filter: none !important;
}
.press-ink-ripple {
  display: none !important;
}
.lead-switcher,
.lead-panel {
  min-height: 0 !important;
}
.lead-panel__media {
  min-height: 0 !important;
  margin: 0 !important;
}
.lead-panel__media img,
.lead-panel img {
  display: block !important;
  width: 100% !important;
  height: auto !important;
  aspect-ratio: 16 / 9 !important;
  max-height: min(58vh, 560px) !important;
  object-fit: cover !important;
}
.lead-panel__media-note {
  margin-top: 0.65rem !important;
}
@media (max-width: 760px) {
  .lead-panel__media img,
  .lead-panel img {
    max-height: 42vh !important;
  }
}
/* PRESS_ACTUAL_VISIBLE_SITE_FIX_END */
"""
    if "PRESS_ACTUAL_VISIBLE_SITE_FIX_START" not in text:
        text = text.rstrip() + block
    write_if_changed(path, text)


def patch_thumbnail_workflow() -> None:
    # For the one-click backfill workflow, force missing/non-AI current issue art to become AI art.
    for rel_path in [
        ".github/workflows/ai-thumbnail-backfill.yml",
        "ai-thumbnail-backfill.yml",
    ]:
        path = ROOT / rel_path
        if not path.exists():
            continue
        text = read(path)
        text = re.sub(r'AI_REGENERATE_AI_THUMBNAILS:\s*"0"', 'AI_REGENERATE_AI_THUMBNAILS: "1"', text)
        text = text.replace('AI_REGENERATE_AI_THUMBNAILS: "false"', 'AI_REGENERATE_AI_THUMBNAILS: "1"')
        write_if_changed(path, text)


def main() -> int:
    print(f"Applying actual visible site fix in {ROOT}")
    patch_index()
    patch_app_js()
    patch_styles()
    patch_cache_busting()
    patch_thumbnail_workflow()

    if CHANGED:
        print("\nChanged files:")
        for item in CHANGED:
            print(f"  - {item}")
        print(f"\nBackups are in: {rel(BACKUP_DIR)}")
    else:
        print("No changes were needed.")

    print("\nNext: git status --short, then commit and push.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

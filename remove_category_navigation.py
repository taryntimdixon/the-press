#!/usr/bin/env python3
"""Remove category navigation surfaces from The Press generated pages.

Run from the repository root, or directly from tools/:

    python3 tools/remove_category_navigation.py

What it does:
- Converts the malformed escaped Open Graph marker into a real HTML comment.
- Removes the top category nav bar and its mobile Menu button.
- Removes the homepage desk/category directory.
- Removes the footer Sections list while keeping Archive/Newsroom links.
- Repoints old section-page anchor links to archive.html so readers stay in the archive flow.
"""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

OPEN_GRAPH_REPLACEMENTS = {
    "&lt;\\!-- Open Graph --&gt;": "<!-- Open Graph -->",
    "&lt;!-- Open Graph --&gt;": "<!-- Open Graph -->",
    "<\\!-- Open Graph -->": "<!-- Open Graph -->",
    "<\\!-- Open Graph --&gt;": "<!-- Open Graph -->",
}

MENU_BUTTON_RE = re.compile(
    r"\s*<button\b(?=[^>]*\bdata-menu-toggle\b)[\s\S]*?</button>",
    re.IGNORECASE,
)

SECTION_NAV_RE = re.compile(
    r"\s*<nav\b(?=[^>]*\bclass=[\"'][^\"']*\bsection-nav\b[^\"']*[\"'])(?=[^>]*\bid=[\"']site-sections[\"'])[\s\S]*?</nav>",
    re.IGNORECASE,
)

FOOTER_SECTIONS_RE = re.compile(
    r"\s*<section>\s*<h2\b[^>]*\bclass=[\"'][^\"']*\bfooter-heading\b[^\"']*[\"'][^>]*>\s*Sections\s*</h2>\s*<ul\b[^>]*\bclass=[\"'][^\"']*\bfooter-list\b[^\"']*[\"'][^>]*>[\s\S]*?</ul>\s*</section>",
    re.IGNORECASE,
)

DESK_DIRECTORY_RE = re.compile(
    r"\s*<section\b(?=[^>]*\bclass=[\"'][^\"']*\bdesk-directory\b[^\"']*[\"'])[\s\S]*?</section>",
    re.IGNORECASE,
)

SECTION_ANCHOR_RE = re.compile(
    r"(<a\b[^>]*\bhref=[\"'])section-[^\"']+\.html([\"'])",
    re.IGNORECASE,
)

MORE_SECTION_LABEL_RE = re.compile(
    r">\s*More\s+[A-Za-z][^<]*</a>",
    re.IGNORECASE,
)

EXCESS_BLANK_LINES_RE = re.compile(r"\n{3,}")


def clean_html(text: str) -> str:
    original = text
    for bad, good in OPEN_GRAPH_REPLACEMENTS.items():
        text = text.replace(bad, good)
    text = MENU_BUTTON_RE.sub("", text)
    text = SECTION_NAV_RE.sub("", text)
    text = FOOTER_SECTIONS_RE.sub("", text)
    text = DESK_DIRECTORY_RE.sub("", text)
    text = SECTION_ANCHOR_RE.sub(r"\1archive.html\2", text)
    text = MORE_SECTION_LABEL_RE.sub(">Open archive</a>", text)
    text = EXCESS_BLANK_LINES_RE.sub("\n\n", text)
    return text if text != original else original


def html_files() -> list[Path]:
    files = list(ROOT.glob("*.html"))
    daily_dir = ROOT / "daily"
    if daily_dir.exists():
        files.extend(daily_dir.rglob("*.html"))
    return sorted({path.resolve() for path in files})


def main() -> int:
    changed: list[Path] = []
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        cleaned = clean_html(text)
        if cleaned != text:
            path.write_text(cleaned, encoding="utf-8")
            changed.append(path)
    if changed:
        print(f"Category navigation removed from {len(changed)} HTML file(s):")
        for path in changed:
            print(f"  - {path.relative_to(ROOT)}")
    else:
        print("No category navigation markup found. HTML already looks clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

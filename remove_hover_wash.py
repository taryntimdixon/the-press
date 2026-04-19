#!/usr/bin/env python3
"""Remove article-text hover highlights and card color washes from The Press.

Run from the repository root:
    python3 tools/remove_hover_wash.py

The script is idempotent: running it multiple times will not duplicate CSS.
"""
from __future__ import annotations

import re
from pathlib import Path

GUARD_START = "/* PRESS_NO_HOVER_WASH_START */"
GUARD_END = "/* PRESS_NO_HOVER_WASH_END */"

NO_HOVER_WASH_CSS = f"""
{GUARD_START}
/* Keep article text calm on hover: no colored paragraph wash or card tint. */
@media (hover:hover) and (pointer:fine) {{
  .article-body p:hover,
  .generated-story .article-body p:hover,
  .article-body li:hover,
  .generated-story .article-body li:hover {{
    background: transparent !important;
    box-shadow: none !important;
  }}
}}

.article-body p,
.generated-story .article-body p {{
  transition: color .18s ease;
}}

.press-micro-card::before,
.press-micro-card:hover::before {{
  background: transparent !important;
  opacity: 0 !important;
}}

.article-body a:hover,
.generated-story .article-body a:hover,
.story-card__title a:hover,
.archive-card h3 a:hover,
.lead-panel h2 a:hover,
.link-list__item a:hover {{
  background: transparent !important;
}}
{GUARD_END}
""".strip()


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [Path.cwd(), *Path.cwd().parents, here.parent.parent, *here.parents]:
        if (candidate / "styles.css").exists():
            return candidate
    raise SystemExit("Could not find styles.css. Run this from The Press repository root.")


def remove_existing_guard(css: str) -> str:
    return re.sub(
        rf"\n?\s*{re.escape(GUARD_START)}.*?{re.escape(GUARD_END)}\s*",
        "\n",
        css,
        flags=re.DOTALL,
    )


def remove_original_article_hover(css: str) -> tuple[str, int]:
    """Remove the paragraph-hover highlight block when it exists.

    Handles both the formatted stylesheet and the currently-minified GitHub output.
    The final guard is still appended afterward as a belt-and-suspenders override.
    """
    patterns = [
        re.compile(
            r"\s*\.article-body\s+p\s*,\s*\.generated-story\s+\.article-body\s+p\s*\{\s*"
            r"transition\s*:\s*background-color\s*\.2s\s*ease\s*,\s*box-shadow\s*\.2s\s*ease\s*;\s*\}\s*"
            r"@media\s*\(hover:hover\)\s*and\s*\(pointer:fine\)\s*\{\s*"
            r"\.article-body\s+p:hover\s*,\s*\.generated-story\s+\.article-body\s+p:hover\s*\{\s*"
            r"background\s*:[^;{}]+;\s*box-shadow\s*:[^;{}]+;\s*\}\s*\}",
            flags=re.DOTALL,
        ),
        re.compile(
            r"\s*@media\s*\(hover:hover\)\s*and\s*\(pointer:fine\)\s*\{\s*"
            r"\.article-body\s+p:hover\s*,\s*\.generated-story\s+\.article-body\s+p:hover\s*\{\s*"
            r"background\s*:[^;{}]+;\s*box-shadow\s*:[^;{}]+;\s*\}\s*\}",
            flags=re.DOTALL,
        ),
    ]

    replacements = 0
    for pattern in patterns:
        css, count = pattern.subn("\n", css)
        replacements += count
    return css, replacements


def main() -> None:
    repo_root = find_repo_root()
    styles_path = repo_root / "styles.css"
    css = styles_path.read_text(encoding="utf-8")

    original = css
    css = remove_existing_guard(css)
    css, removed_hover_blocks = remove_original_article_hover(css)
    css = css.rstrip() + "\n\n" + NO_HOVER_WASH_CSS + "\n"

    if css != original:
        styles_path.write_text(css, encoding="utf-8")
        print(f"Updated {styles_path.relative_to(repo_root)}")
        if removed_hover_blocks:
            print(f"Removed {removed_hover_blocks} old article hover highlight block(s).")
        print("Disabled colored hover backgrounds on article text and article cards.")
    else:
        print("No changes needed.")


if __name__ == "__main__":
    main()

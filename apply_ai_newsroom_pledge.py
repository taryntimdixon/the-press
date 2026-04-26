#!/usr/bin/env python3
"""
Install the logo-safe AI Newsroom pledge page for The Press.

This script:
  - backs up authors.html, styles.css, and build.py when present
  - replaces only the <main> content in authors.html so existing header/logo/footer stay intact
  - appends or replaces the scoped pledge CSS block in styles.css
  - updates build.py render_authors() so future builds keep the pledge page
  - preserves existing logo markup instead of replacing it with text
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import shutil
import sys

START_MARKER = "/* PRESS_AI_NEWSROOM_PLEDGE_START"
END_MARKER = "/* PRESS_AI_NEWSROOM_PLEDGE_END */"
PAGE_TITLE = "AI Newsroom Pledge — The Press"
PAGE_DESCRIPTION = (
    "The Press AI Newsroom pledge: AI-generated articles, human editorial review, "
    "heavy sourcing, public corrections, and reader skepticism."
)

HEADER_LOGO = '<a class="masthead masthead-with-logo" href="index.html" aria-label="The Press home"><img class="masthead-logo" src="assets/the-press-logo.svg" alt="The Press logo" decoding="async" /></a>'
FOOTER_LOGO = '<a class="masthead masthead--footer masthead-with-logo" href="index.html" aria-label="The Press home"><img class="masthead-logo" src="assets/the-press-logo.svg" alt="The Press logo" decoding="async" /></a>'


def repo_root_from_args() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).expanduser().resolve()
    return Path.cwd().resolve()


def require_repo(root: Path) -> None:
    required = ["styles.css", "authors.html"]
    missing = [name for name in required if not (root / name).exists()]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(
            f"Could not find {joined} in {root}. Run this from the repo root, "
            "or pass the repo path as the first argument."
        )


def backup_files(root: Path, paths: list[Path]) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = root / f".pledge-backup-{stamp}"
    backup_dir.mkdir(exist_ok=False)
    for path in paths:
        if path.exists():
            shutil.copy2(path, backup_dir / path.name)
    return backup_dir


def replace_marked_block(text: str, block: str) -> str:
    start = text.find(START_MARKER)
    if start == -1:
        return text.rstrip() + "\n\n" + block.rstrip() + "\n"

    end = text.find(END_MARKER, start)
    if end == -1:
        raise SystemExit("Found the pledge CSS start marker but not the end marker. Refusing to guess.")
    end += len(END_MARKER)
    return text[:start].rstrip() + "\n\n" + block.rstrip() + "\n\n" + text[end:].lstrip()


def add_body_class(html: str, class_name: str) -> str:
    body_match = re.search(r"<body\b([^>]*)>", html, flags=re.I)
    if not body_match:
        raise SystemExit("Could not find a <body> tag in authors.html.")

    body_tag = body_match.group(0)
    class_match = re.search(r'class=("|\')([^"\']*)("|\')', body_tag, flags=re.I)
    if class_match:
        classes = class_match.group(2).split()
        if class_name not in classes:
            classes.append(class_name)
        quote = class_match.group(1)
        new_class_attr = f"class={quote}{' '.join(classes)}{quote}"
        new_body_tag = body_tag[:class_match.start()] + new_class_attr + body_tag[class_match.end():]
    else:
        new_body_tag = body_tag[:-1] + f' class="{class_name}">'

    return html[:body_match.start()] + new_body_tag + html[body_match.end():]


def replace_or_add_meta_description(html: str, description: str) -> str:
    escaped = description.replace('"', '&quot;')
    pattern = re.compile(r'<meta\s+[^>]*name=("|\')description\1[^>]*>', flags=re.I)
    replacement = f'<meta name="description" content="{escaped}"/>'
    if pattern.search(html):
        return pattern.sub(replacement, html, count=1)

    head_match = re.search(r"</head>", html, flags=re.I)
    if not head_match:
        return html
    return html[:head_match.start()] + replacement + "\n" + html[head_match.start():]


def replace_or_add_open_graph_descriptions(html: str) -> str:
    replacements = {
        "og:title": PAGE_TITLE,
        "twitter:title": PAGE_TITLE,
        "og:description": "How The Press uses Intelligent AI, human editorial review, heavy sourcing, corrections, and reader skepticism.",
        "twitter:description": "How The Press uses Intelligent AI, human editorial review, heavy sourcing, corrections, and reader skepticism.",
    }
    for prop, value in replacements.items():
        attr = "property" if prop.startswith("og:") else "name"
        pattern = re.compile(rf'<meta\s+{attr}=("|\'){re.escape(prop)}\1\s+content=("|\')[^"\']*("|\')\s*/?>', flags=re.I)
        replacement = f'<meta {attr}="{prop}" content="{value}"/>'
        html = pattern.sub(replacement, html, count=1)
    return html


def update_authors_html(root: Path, main_html: str) -> None:
    authors_path = root / "authors.html"
    html = authors_path.read_text(encoding="utf-8")

    html = html.replace("<\\!--", "<!--")
    html = re.sub(r"<title>.*?</title>", f"<title>{PAGE_TITLE}</title>", html, count=1, flags=re.I | re.S)
    html = replace_or_add_meta_description(html, PAGE_DESCRIPTION)
    html = replace_or_add_open_graph_descriptions(html)
    html = add_body_class(html, "page-pledge")

    main_pattern = re.compile(r"<main\b[^>]*>.*?</main>", flags=re.I | re.S)
    html, count = main_pattern.subn(main_html.strip(), html, count=1)
    if count != 1:
        raise SystemExit("Could not replace the <main> block in authors.html. No partial page update was written.")

    authors_path.write_text(html, encoding="utf-8")


def preserve_logo_markup(text: str, root: Path) -> str:
    """Keep the existing SVG logo in generated pages when the asset exists."""
    logo_path = root / "assets" / "the-press-logo.svg"
    if not logo_path.exists():
        return text

    replacements = {
        '<a class="masthead" href="index.html">{h(SITE[\'name\'])}</a>': HEADER_LOGO,
        '<a class="masthead" href="index.html">{h(SITE["name"])}</a>': HEADER_LOGO,
        '<a class="masthead masthead--footer" href="index.html">{h(SITE[\'name\'])}</a>': FOOTER_LOGO,
        '<a class="masthead masthead--footer" href="index.html">{h(SITE["name"])}</a>': FOOTER_LOGO,
        '<a class="masthead masthead--footer" href="index.html">The Press</a>': FOOTER_LOGO,
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def patch_build_py(root: Path, build_path: Path, replacement_function: str) -> bool:
    if not build_path.exists():
        return False

    text = build_path.read_text(encoding="utf-8")
    original = text

    pattern = re.compile(
        r"def render_authors\(\) -> str:\n.*?\n(?=def render_story\(story: dict\) -> str:)",
        re.S,
    )
    text, count = pattern.subn(replacement_function.rstrip() + "\n\n", text, count=1)
    if count != 1:
        raise SystemExit("Could not locate render_authors() in build.py. No partial build.py patch was written.")

    text = text.replace(
        '<li><a href="authors.html">Authors</a></li>',
        '<li><a href="authors.html">AI Newsroom</a></li>',
    )
    text = preserve_logo_markup(text, root)

    if text != original:
        build_path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    root = repo_root_from_args()
    bundle_dir = Path(__file__).resolve().parent

    require_repo(root)

    main_path = bundle_dir / "authors-main.html"
    css_path = bundle_dir / "ai-newsroom-pledge.css"
    replacement_path = bundle_dir / "build-render_authors.replacement.py"
    for needed in (main_path, css_path, replacement_path):
        if not needed.exists():
            raise SystemExit(f"Missing bundle file: {needed.name}")

    targets = [root / "authors.html", root / "styles.css", root / "build.py"]
    backup_dir = backup_files(root, targets)

    update_authors_html(root, main_path.read_text(encoding="utf-8"))

    styles_path = root / "styles.css"
    styles_text = styles_path.read_text(encoding="utf-8")
    css_block = css_path.read_text(encoding="utf-8")
    styles_path.write_text(replace_marked_block(styles_text, css_block), encoding="utf-8")

    build_changed = patch_build_py(root, root / "build.py", replacement_path.read_text(encoding="utf-8"))

    print(f"Backed up originals to: {backup_dir}")
    print("Updated: authors.html main content only. Existing header/logo/footer markup was preserved.")
    print("Updated: styles.css with a body.page-pledge-scoped CSS block using existing site colors.")
    if build_changed:
        print("Updated: build.py render_authors() and preserved existing logo markup.")
    else:
        print("Skipped: build.py was not found")
    print("No logo/image assets were deleted, renamed, moved, recolored, or overwritten.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

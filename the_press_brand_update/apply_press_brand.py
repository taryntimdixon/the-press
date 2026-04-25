#!/usr/bin/env python3
"""
Apply the clean The Press brand update.

Run from the root of the The-Press repository:
    python apply_press_brand.py

What it does:
- Sets the visible tagline to "AI Powered News".
- Adds brand-friendly masthead/tagline CSS.
- Adds SVG logo assets under assets/.
- Updates common generated HTML text immediately, so the site can look right before a rebuild.
"""

from __future__ import annotations

from pathlib import Path
import shutil

TAGLINE = "AI Powered News"
DESCRIPTION = (
    "AI powered news across politics, culture, technology, economics, education, "
    "health, philosophy, science, world, and opinion."
)
NEWSLETTER_COPY = (
    "A calm digest of AI powered reporting from every desk, with visible dates, "
    "clear bylines, and transparent source notes."
)
FOOTER_NOTE = "Visible AI use, visible standards, visible source notes."

OLD_TAGLINES = [
    "AI Powered News",
]

OLD_DESCRIPTIONS = [
    "AI powered news across politics, culture, technology, economics, education, health, philosophy, science, world, and opinion.",
    "AI powered news across politics, culture, technology, economics, education, health, philosophy, science, world, and opinion.",
    "AI powered news across politics, culture, technology, economics, education, health, philosophy, science, world, and opinion.",
]

OLD_NEWSLETTER_COPY = [
    "A calm digest of AI powered reporting from every desk, with visible dates, clear bylines, and transparent source notes.",
]

OLD_FOOTER_NOTES = [
    "Visible AI use, visible standards, visible source notes.",
]

BRAND_CSS = r'''

/* The Press brand lockup — AI Powered News */
.site-header{
  background:color-mix(in srgb, var(--bg) 94%, transparent);
  border-bottom:1px solid color-mix(in srgb, var(--ink) 10%, transparent);
}

.masthead-row{
  align-items:center;
}

.masthead-wrap{
  align-items:center;
  gap:.8rem 1rem;
}

.masthead{
  text-transform:uppercase;
  letter-spacing:.018em;
  font-weight:800;
  text-shadow:none;
}

.masthead-tagline{
  display:inline-flex;
  align-items:center;
  gap:.45rem;
  width:max-content;
  min-height:2.05rem;
  margin:0;
  padding:.34rem .72rem .31rem;
  border:1px solid color-mix(in srgb, var(--accent) 38%, var(--line));
  border-radius:999px;
  background:color-mix(in srgb, var(--accent-soft) 58%, transparent);
  color:var(--accent);
  font-family:var(--sans);
  font-size:clamp(.66rem,.8vw,.78rem);
  font-weight:800;
  line-height:1.1;
  letter-spacing:.16em;
  text-transform:uppercase;
  white-space:nowrap;
}

.masthead-tagline::before{
  content:"";
  width:.45rem;
  height:.45rem;
  border-radius:999px;
  background:currentColor;
  box-shadow:0 0 0 .22rem color-mix(in srgb, currentColor 15%, transparent);
}

.footer-brand .masthead--footer{
  display:inline-block;
  text-transform:uppercase;
  letter-spacing:.018em;
  font-weight:800;
}

.footer-brand .footer-copy:first-of-type{
  display:inline-flex;
  align-items:center;
  width:max-content;
  margin-top:.55rem;
  padding:.32rem .68rem;
  border:1px solid color-mix(in srgb, var(--accent) 38%, var(--line));
  border-radius:999px;
  background:color-mix(in srgb, var(--accent-soft) 58%, transparent);
  color:var(--accent);
  font-size:.74rem;
  font-weight:800;
  letter-spacing:.14em;
  line-height:1.1;
  text-transform:uppercase;
}

@media (max-width: 700px){
  .masthead-row{
    align-items:start;
  }

  .masthead-wrap{
    flex-direction:column;
    align-items:flex-start;
    gap:.45rem;
  }

  .masthead-tagline{
    min-height:0;
    padding:.32rem .58rem;
    font-size:.64rem;
    letter-spacing:.13em;
  }
}
'''.strip()

LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="180" viewBox="0 0 760 180" role="img" aria-labelledby="title desc">
  <title id="title">The Press logo</title>
  <desc id="desc">The Press wordmark with the tagline AI Powered News.</desc>
  <defs>
    <style>
      .wordmark{font-family:'Playfair Display', Georgia, 'Times New Roman', serif;font-weight:800;letter-spacing:.045em;fill:#1f1f1b;}
      .tag{font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;font-weight:800;letter-spacing:.18em;fill:#9d3a2d;text-transform:uppercase;}
      .rule{stroke:#9d3a2d;stroke-width:2.4;stroke-linecap:round;opacity:.88;}
      .tagbox{fill:#f1e0dc;stroke:#9d3a2d;stroke-width:1.5;opacity:.92;}
    </style>
  </defs>
  <g transform="translate(28 28)">
    <text class="wordmark" x="0" y="72" font-size="76">THE PRESS</text>
    <line class="rule" x1="4" y1="103" x2="230" y2="103" />
    <rect class="tagbox" x="248" y="86" width="260" height="38" rx="19" />
    <text class="tag" x="272" y="111" font-size="18">AI Powered News</text>
    <line class="rule" x1="528" y1="103" x2="704" y2="103" />
  </g>
</svg>'''

LOGO_REVERSE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="180" viewBox="0 0 760 180" role="img" aria-labelledby="title desc">
  <title id="title">The Press reverse logo</title>
  <desc id="desc">Light version of The Press wordmark with the tagline AI Powered News.</desc>
  <defs>
    <style>
      .wordmark{font-family:'Playfair Display', Georgia, 'Times New Roman', serif;font-weight:800;letter-spacing:.045em;fill:#f0ebe0;}
      .tag{font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;font-weight:800;letter-spacing:.18em;fill:#f6d3cd;text-transform:uppercase;}
      .rule{stroke:#e06b5b;stroke-width:2.4;stroke-linecap:round;opacity:.9;}
      .tagbox{fill:#3a1e1a;stroke:#e06b5b;stroke-width:1.5;opacity:.95;}
    </style>
  </defs>
  <g transform="translate(28 28)">
    <text class="wordmark" x="0" y="72" font-size="76">THE PRESS</text>
    <line class="rule" x1="4" y1="103" x2="230" y2="103" />
    <rect class="tagbox" x="248" y="86" width="260" height="38" rx="19" />
    <text class="tag" x="272" y="111" font-size="18">AI Powered News</text>
    <line class="rule" x1="528" y1="103" x2="704" y2="103" />
  </g>
</svg>'''

MARK_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-labelledby="title desc">
  <title id="title">The Press TP mark</title>
  <desc id="desc">A compact TP monogram for The Press.</desc>
  <rect x="36" y="36" width="440" height="440" rx="74" fill="#1f1f1b"/>
  <rect x="56" y="56" width="400" height="400" rx="58" fill="none" stroke="#f4f0e8" stroke-width="12" opacity=".78"/>
  <text x="256" y="311" text-anchor="middle" font-family="'Playfair Display', Georgia, 'Times New Roman', serif" font-size="188" font-weight="800" letter-spacing="-18" fill="#f4f0e8">TP</text>
  <line x1="151" y1="353" x2="361" y2="353" stroke="#9d3a2d" stroke-width="14" stroke-linecap="round"/>
</svg>'''

FAVICON_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" role="img" aria-label="The Press">
  <rect x="5" y="5" width="54" height="54" rx="10" fill="#1f1f1b"/>
  <rect x="9" y="9" width="46" height="46" rx="7" fill="none" stroke="#f4f0e8" stroke-width="2" opacity=".85"/>
  <text x="32" y="39" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="24" font-weight="700" letter-spacing="-2" fill="#f4f0e8">TP</text>
  <line x1="19" y1="45" x2="45" y2="45" stroke="#9d3a2d" stroke-width="2.5" stroke-linecap="round"/>
</svg>'''


def replace_all(text: str, replacements: dict[str, str]) -> tuple[str, int]:
    count = 0
    for old, new in replacements.items():
        if old in text:
            occurrences = text.count(old)
            text = text.replace(old, new)
            count += occurrences
    return text, count


def update_text_file(path: Path, replacements: dict[str, str]) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return 0
    new_text, count = replace_all(text, replacements)
    if count:
        path.write_text(new_text, encoding="utf-8")
    return count


def append_css(root: Path) -> bool:
    css_path = root / "styles.css"
    if not css_path.exists():
        print("styles.css not found; skipping CSS append")
        return False
    text = css_path.read_text(encoding="utf-8")
    if "The Press brand lockup — AI Powered News" in text:
        return False
    css_path.write_text(text.rstrip() + "\n\n" + BRAND_CSS + "\n", encoding="utf-8")
    return True


def write_assets(root: Path) -> list[Path]:
    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    files = {
        assets / "the-press-logo.svg": LOGO_SVG,
        assets / "the-press-logo-reverse.svg": LOGO_REVERSE_SVG,
        assets / "the-press-mark.svg": MARK_SVG,
        assets / "favicon.svg": FAVICON_SVG,
    }
    # Some current files reference root/favicon.svg in addition to assets/favicon.svg.
    if (root / "favicon.svg").exists():
        files[root / "favicon.svg"] = FAVICON_SVG
    written = []
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def main() -> None:
    root = Path.cwd()

    replacements: dict[str, str] = {}
    for old in OLD_TAGLINES:
        replacements[old] = TAGLINE
    for old in OLD_DESCRIPTIONS:
        replacements[old] = DESCRIPTION
    for old in OLD_NEWSLETTER_COPY:
        replacements[old] = NEWSLETTER_COPY
    for old in OLD_FOOTER_NOTES:
        replacements[old] = FOOTER_NOTE

    files_to_scan = []
    for pattern in ("*.html", "*.json", "*.py", "*.xml"):
        files_to_scan.extend(root.rglob(pattern))

    changed_files = []
    total_replacements = 0
    for path in files_to_scan:
        if ".git" in path.parts:
            continue
        count = update_text_file(path, replacements)
        if count:
            changed_files.append(path.relative_to(root))
            total_replacements += count

    css_added = append_css(root)
    assets_written = write_assets(root)

    print("Brand update complete.")
    print(f"Tagline set to: {TAGLINE}")
    print(f"Text replacements: {total_replacements}")
    if changed_files:
        print("Updated text in:")
        for file in changed_files[:80]:
            print(f"  - {file}")
        if len(changed_files) > 80:
            print(f"  ...and {len(changed_files) - 80} more files")
    print("CSS block appended to styles.css" if css_added else "CSS block already present or skipped")
    print("Assets written:")
    for path in assets_written:
        print(f"  - {path.relative_to(root)}")
    print("\nNext: open index.html locally, then commit and push the changes.")


if __name__ == "__main__":
    main()

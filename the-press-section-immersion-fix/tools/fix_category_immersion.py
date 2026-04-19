#!/usr/bin/env python3
"""Clean section pages after the daily/category build.

This keeps category pages immersive by repairing accidentally escaped Open Graph
comments before deployment. It is safe to run repeatedly from the repo root:

    python3 tools/fix_category_immersion.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION_GLOB = "section-*.html"

REPLACEMENTS = {
    "&lt;\\!-- Open Graph --&gt;": "<!-- Open Graph -->",
    "&lt;!-- Open Graph --&gt;": "<!-- Open Graph -->",
    "&lt;\\!-- Open Graph / social sharing --&gt;": "<!-- Open Graph / social sharing -->",
    "&lt;!-- Open Graph / social sharing --&gt;": "<!-- Open Graph / social sharing -->",
}


def clean_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    cleaned = original

    for bad, good in REPLACEMENTS.items():
        cleaned = cleaned.replace(bad, good)

    # Belt-and-suspenders cleanup for any visible ghost that was moved into body.
    cleaned = cleaned.replace("<\\!-- Open Graph -->", "<!-- Open Graph -->")
    cleaned = cleaned.replace("<\\!-- Open Graph / social sharing -->", "<!-- Open Graph / social sharing -->")

    if cleaned == original:
        return False

    path.write_text(cleaned, encoding="utf-8")
    return True


def main() -> None:
    changed = [path for path in sorted(ROOT.glob(SECTION_GLOB)) if clean_file(path)]
    if changed:
        print("Cleaned section Open Graph comments:")
        for path in changed:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("Section Open Graph comments already clean.")


if __name__ == "__main__":
    main()

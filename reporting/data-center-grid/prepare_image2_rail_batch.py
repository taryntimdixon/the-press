#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "reporting" / "data-center-grid" / "source-stack.json"


def main() -> None:
    raise SystemExit(
        "The gpt-image-2/API rail-image batch path is disabled for this article. "
        "Use the built-in imagegen sheet workflow instead: "
        "python reporting/data-center-grid/prepare_imagegen_sheet_plan.py, "
        "create the sheet images in assets/data-center-grid/rail-imagegen-sheets/, "
        "then run python reporting/data-center-grid/finalize_imagegen_sheet_rail_images.py."
    )


if __name__ == "__main__":
    main()

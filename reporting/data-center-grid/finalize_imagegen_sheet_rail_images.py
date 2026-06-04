#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "reporting" / "data-center-grid" / "imagegen-sheet-plan.json"
OUT_DIR = ROOT / "assets" / "data-center-grid" / "rail"
MANIFEST_PATH = ROOT / "reporting" / "data-center-grid" / "rail-image-manifest.json"

W, H = 800, 520


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cover_crop(img: Image.Image) -> Image.Image:
    img = ImageOps.exif_transpose(img.convert("RGB"))
    scale = max(W / img.width, H / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - W) // 2)
    top = max(0, (resized.height - H) // 2)
    return resized.crop((left, top, left + W, top + H))


def panel_boxes(width: int, height: int, layout: str, count: int) -> list[tuple[int, int, int, int]]:
    inset_x = round(width * 0.018)
    inset_y = round(height * 0.018)
    if layout == "quad":
        half_w = width // 2
        half_h = height // 2
        boxes = [
            (0, 0, half_w, half_h),
            (half_w, 0, width, half_h),
            (0, half_h, half_w, height),
            (half_w, half_h, width, height),
        ]
    else:
        half_w = width // 2
        boxes = [(0, 0, half_w, height), (half_w, 0, width, height)]
    return [
        (x1 + inset_x, y1 + inset_y, x2 - inset_x, y2 - inset_y)
        for x1, y1, x2, y2 in boxes[:count]
    ]


def main() -> None:
    sheets = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    missing = [sheet["image"] for sheet in sheets if not (ROOT / sheet["image"]).exists()]
    if missing:
        raise SystemExit("Missing generated sheet images:\n" + "\n".join(missing))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("source-*.jpg"):
        old.unlink()

    manifest = []
    for sheet in sheets:
        sheet_path = ROOT / sheet["image"]
        with Image.open(sheet_path) as raw_sheet:
            source_items = sheet["sources"]
            boxes = panel_boxes(raw_sheet.width, raw_sheet.height, sheet["layout"], len(source_items))
            for source, box in zip(source_items, boxes):
                panel = raw_sheet.crop(box)
                final = OUT_DIR / f"source-{source['number']:03d}.jpg"
                cover_crop(panel).save(final, quality=88, optimize=True, progressive=True)
                manifest.append(
                    {
                        "source": source["number"],
                        "category": source["category"],
                        "outlet": source["outlet"],
                        "title": source["title"],
                        "rail_image": str(final.relative_to(ROOT)),
                        "sheet_image": str(sheet_path.relative_to(ROOT)),
                        "generation_model": "built-in-imagegen",
                        "sheet": sheet["sheet"],
                        "layout": sheet["layout"],
                        "sheet_sha256": digest(sheet_path),
                        "final_sha256": digest(final),
                    }
                )

    if len(manifest) != 110:
        raise SystemExit(f"Expected 110 final rail images, got {len(manifest)}")
    final_hashes = [item["final_sha256"] for item in manifest]
    if len(set(final_hashes)) != len(final_hashes):
        raise SystemExit("Final rail images are not unique by file hash")

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Finalized {len(manifest)} rail images")
    print(f"Wrote {MANIFEST_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

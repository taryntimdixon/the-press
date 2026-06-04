#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
from collections import Counter
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "reporting" / "data-center-grid" / "imagegen-sheet-plan.json"
AUDIT_DIR = ROOT / "reporting" / "data-center-grid" / "audit-rail-crops"
AUDIT_PATH = ROOT / "reporting" / "data-center-grid" / "rail-uniqueness-audit.json"

W, H = 800, 520

STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "create",
    "data",
    "do",
    "from",
    "in",
    "it",
    "light",
    "no",
    "of",
    "on",
    "or",
    "source",
    "text",
    "the",
    "to",
    "under",
    "use",
    "with",
}


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


def ahash(img: Image.Image, size: int = 16) -> str:
    small = ImageOps.grayscale(img).resize((size, size), Image.Resampling.LANCZOS)
    pixels = list(small.getdata())
    avg = sum(pixels) / len(pixels)
    return "".join("1" if pixel >= avg else "0" for pixel in pixels)


def dhash(img: Image.Image, width: int = 17, height: int = 16) -> str:
    small = ImageOps.grayscale(img).resize((width, height), Image.Resampling.LANCZOS)
    pixels = list(small.getdata())
    bits = []
    for y in range(height):
        row = pixels[y * width : (y + 1) * width]
        bits.extend("1" if row[x] > row[x + 1] else "0" for x in range(width - 1))
    return "".join(bits)


def hamming(a: str, b: str) -> int:
    return sum(x != y for x, y in zip(a, b))


def color_vector(img: Image.Image) -> list[float]:
    small = img.resize((160, 104), Image.Resampling.LANCZOS).convert("RGB")
    hist = small.histogram()
    total = sum(hist) or 1
    return [value / total for value in hist]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if not mag_a or not mag_b:
        return 0.0
    return dot / (mag_a * mag_b)


def scene_for(sheet: dict, source_number: int) -> str:
    prompt = sheet["prompt"]
    match = re.search(
        rf"Source {source_number:03d}, .*? Create (.*?)\. Connect it visually",
        prompt,
        flags=re.S,
    )
    if match:
        return " ".join(match.group(1).split())
    return ""


def scene_tokens(scene: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z][a-z-]{2,}", scene.lower())
        if token not in STOPWORDS
    }


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def crop_available(plan: list[dict]) -> list[dict]:
    if AUDIT_DIR.exists():
        shutil.rmtree(AUDIT_DIR)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for sheet in plan:
        sheet_path = ROOT / sheet["image"]
        if not sheet_path.exists():
            continue
        with Image.open(sheet_path) as raw_sheet:
            boxes = panel_boxes(raw_sheet.width, raw_sheet.height, sheet["layout"], len(sheet["sources"]))
            for source, box in zip(sheet["sources"], boxes):
                source_number = source["number"]
                final = AUDIT_DIR / f"source-{source_number:03d}.jpg"
                panel = raw_sheet.crop(box)
                cropped = cover_crop(panel)
                cropped.save(final, quality=88, optimize=True)
                rows.append(
                    {
                        "source": source_number,
                        "category": source["category"],
                        "title": source["title"],
                        "scene": scene_for(sheet, source_number),
                        "path": str(final.relative_to(ROOT)),
                        "sha256": hashlib.sha256(final.read_bytes()).hexdigest(),
                        "ahash": ahash(cropped),
                        "dhash": dhash(cropped),
                        "color": color_vector(cropped),
                    }
                )
    return sorted(rows, key=lambda row: row["source"])


def compare(row: dict, other: dict) -> dict:
    return {
        "source": row["source"],
        "other": other["source"],
        "ahash_distance": hamming(row["ahash"], other["ahash"]),
        "dhash_distance": hamming(row["dhash"], other["dhash"]),
        "color_cosine": round(cosine(row["color"], other["color"]), 4),
        "scene_overlap": round(jaccard(scene_tokens(row["scene"]), scene_tokens(other["scene"])), 4),
        "scene": row["scene"],
        "other_scene": other["scene"],
    }


def is_flagged(pair: dict) -> bool:
    visually_close = pair["ahash_distance"] <= 30 and pair["dhash_distance"] <= 45
    same_palette = pair["color_cosine"] >= 0.965
    same_scene = pair["scene_overlap"] >= 0.36
    return (visually_close and same_palette) or same_scene


def audit(rows: list[dict], latest_group: int | None = None) -> dict:
    complete_groups = len(rows) // 5
    if latest_group is None:
        group_numbers = range(1, complete_groups + 1)
    else:
        if latest_group < 1 or latest_group > complete_groups:
            raise SystemExit(f"Group {latest_group} is not available; {len(rows)} crops only cover {complete_groups} complete groups")
        group_numbers = (latest_group,)

    groups = []
    for group_number in group_numbers:
        start = (group_number - 1) * 5
        current = rows[start : start + 5]
        previous = rows[:start]
        within = []
        prior = []
        for index, row in enumerate(current):
            for other in current[index + 1 :]:
                pair = compare(row, other)
                if is_flagged(pair):
                    within.append(pair)
            for other in previous:
                pair = compare(row, other)
                if is_flagged(pair):
                    prior.append(pair)
        scene_word_counts = Counter(
            token
            for row in current
            for token in scene_tokens(row["scene"])
            if token not in {"data-center", "utility", "power", "industrial"}
        )
        groups.append(
            {
                "group": group_number,
                "sources": [row["source"] for row in current],
                "scenes": {f"{row['source']:03d}": row["scene"] for row in current},
                "repeated_scene_tokens": [
                    {"token": token, "count": count}
                    for token, count in scene_word_counts.most_common()
                    if count >= 3
                ],
                "within_group_flags": within,
                "prior_group_flags": prior,
                "passed": not within and not prior,
            }
        )
    return {"available_crops": len(rows), "complete_groups": complete_groups, "groups": groups}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=int, help="Audit one five-photo group number, e.g. 2 for sources 006-010")
    args = parser.parse_args()

    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    rows = crop_available(plan)
    report = audit(rows, args.group)
    for group in report["groups"]:
        status = "PASS" if group["passed"] else "CHECK"
        print(f"group {group['group']:02d} sources {group['sources'][0]:03d}-{group['sources'][-1]:03d}: {status}")
        if group["repeated_scene_tokens"]:
            print("  repeated scene tokens:", group["repeated_scene_tokens"][:6])
        if group["within_group_flags"]:
            print(f"  within-group flags: {len(group['within_group_flags'])}")
        if group["prior_group_flags"]:
            print(f"  prior-group flags: {len(group['prior_group_flags'])}")
    AUDIT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {AUDIT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

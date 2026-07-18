#!/usr/bin/env python3
"""Compare generated carousel headers with one image-generated master-frame."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


HEADER_HEIGHT = 140
# Measure header glyphs only.  The divider belongs to the invariant background
# and must not expand a glyph bbox in the master while disappearing from a
# candidate bbox because of antialiasing.
LEFT_ZONE = (45, 20, 700, 90)
RIGHT_ZONE = (735, 20, 1035, 90)
TEXT_THRESHOLD = 170
MIN_CORAL_PIXELS = 300


def dark_bbox(image: Image.Image, zone: tuple[int, int, int, int]) -> tuple[int, int, int, int] | None:
    grey = image.convert("L").crop(zone)
    mask = grey.point(lambda value: 255 if value < TEXT_THRESHOLD else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return None
    return (bbox[0] + zone[0], bbox[1] + zone[1], bbox[2] + zone[0], bbox[3] + zone[1])


def geometry(image: Image.Image) -> dict:
    left = dark_bbox(image, LEFT_ZONE)
    right = dark_bbox(image, RIGHT_ZONE)
    return {
        "left_bbox": list(left) if left else None,
        "right_bbox": list(right) if right else None,
        "left_anchor_x": left[0] if left else None,
        "left_center_y": round((left[1] + left[3]) / 2, 2) if left else None,
        "right_anchor_x": right[2] if right else None,
        "right_center_y": round((right[1] + right[3]) / 2, 2) if right else None,
    }


def coral_pixel_count(image: Image.Image) -> int:
    """Count pixels matching the approved muted-coral header accent."""
    crop = image.convert("RGB").crop(LEFT_ZONE)
    pixels = crop.get_flattened_data() if hasattr(crop, "get_flattened_data") else crop.getdata()
    return sum(
        1
        for red, green, blue in pixels
        if red > 150 and red - green > 45 and red - blue > 45
    )


def background_mae(master: Image.Image, candidate: Image.Image) -> float:
    """Compare invariant header background after masking both text regions."""
    master_crop = master.convert("RGB").crop((0, 0, 1080, HEADER_HEIGHT))
    candidate_crop = candidate.convert("RGB").crop((0, 0, 1080, HEADER_HEIGHT))
    mask = Image.new("L", master_crop.size, 255)
    for zone in (LEFT_ZONE, RIGHT_ZONE):
        Image.Image.paste(mask, 0, zone)
    diff = ImageChops.difference(master_crop, candidate_crop)
    stats = ImageStat.Stat(diff, mask=mask)
    return round(sum(stats.mean) / 3, 3)


def compare(master: Image.Image, candidate: Image.Image, vertical: int = 8, horizontal: int = 14) -> dict:
    master_geometry = geometry(master)
    candidate_geometry = geometry(candidate)
    errors = []
    for side in ("left", "right"):
        if candidate_geometry[f"{side}_bbox"] is None:
            errors.append(f"{side} header text missing")
    if not errors:
        if abs(candidate_geometry["left_anchor_x"] - master_geometry["left_anchor_x"]) > horizontal:
            errors.append("left header anchor drift")
        if abs(candidate_geometry["right_anchor_x"] - master_geometry["right_anchor_x"]) > horizontal:
            errors.append("pagination right anchor drift")
        for side in ("left", "right"):
            if abs(candidate_geometry[f"{side}_center_y"] - master_geometry[f"{side}_center_y"]) > vertical:
                errors.append(f"{side} header baseline drift")
    mae = background_mae(master, candidate)
    if mae > 18:
        errors.append(f"header background/grid drift: mae={mae}")
    master_coral = coral_pixel_count(master)
    candidate_coral = coral_pixel_count(candidate)
    if master_coral >= MIN_CORAL_PIXELS and candidate_coral < MIN_CORAL_PIXELS:
        errors.append(f"left header lost muted-coral accent: pixels={candidate_coral}")
    return {
        "ok": not errors,
        "errors": errors,
        "master_geometry": master_geometry,
        "candidate_geometry": candidate_geometry,
        "background_mae": mae,
        "master_coral_pixels": master_coral,
        "candidate_coral_pixels": candidate_coral,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("master", type=Path)
    parser.add_argument("slides", nargs="+", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    with Image.open(args.master) as source:
        master = source.convert("RGB")
    results = []
    for path in args.slides:
        with Image.open(path) as source:
            candidate = source.convert("RGB")
        results.append({"path": path.as_posix(), **compare(master, candidate)})
    report = {"ok": all(item["ok"] for item in results), "master": args.master.as_posix(), "results": results}
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

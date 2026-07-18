#!/usr/bin/env python3
"""Measure palette isolation and vertical use of a 1080×1350 carousel slide."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


CANVAS = (1080, 1350)
CONTENT_SCAN_START = 130
TITLE_RANGES = {
    1: (210, 330),
    2: (150, 240),
    3: (150, 240),
    4: (150, 240),
    5: (150, 240),
    6: (200, 330),
}
END_RANGE = (1160, 1290)
TITLE_TOLERANCE = 12
BLUE_PIXEL_LIMIT = 50
MIN_FILL = {1: 0.72, 2: 0.72, 3: 0.78, 4: 0.78, 5: 0.78, 6: 0.72}
MAX_CORAL_RATIO = {1: 0.25, 2: 0.15, 3: 0.15, 4: 0.15, 5: 0.15, 6: 0.25}


def pixels(image: Image.Image):
    data = image.convert("RGB")
    return data.get_flattened_data() if hasattr(data, "get_flattened_data") else data.getdata()


def color_counts(image: Image.Image) -> tuple[int, int]:
    blue = 0
    coral = 0
    for red, green, value_blue in pixels(image):
        if value_blue >= 120 and value_blue - red >= 45 and value_blue - green >= 25:
            blue += 1
        if red >= 150 and red - green >= 45 and red - value_blue >= 45:
            coral += 1
    return blue, coral


def active_rows(image: Image.Image) -> list[int]:
    rgb = image.convert("RGB")
    rows = []
    for y in range(CONTENT_SCAN_START, rgb.height):
        active = 0
        for x in range(rgb.width):
            red, green, blue = rgb.getpixel((x, y))
            dark = (red + green + blue) / 3 < 112
            coral = red >= 150 and red - green >= 45 and red - blue >= 45
            if dark or coral:
                active += 1
        if active > 24:
            rows.append(y)
    return rows


def sustained_edge(rows: list[int], from_end: bool = False) -> int | None:
    if not rows:
        return None
    row_set = set(rows)
    iterable = reversed(rows) if from_end else rows
    for y in iterable:
        offsets = range(-11, 1) if from_end else range(12)
        if sum(1 for offset in offsets if y + offset in row_set) >= 8:
            return y
    return rows[-1] if from_end else rows[0]


def analyze(image: Image.Image, index: int) -> dict:
    errors = []
    if image.size != CANVAS:
        errors.append(f"wrong canvas: {image.size}")
    rows = active_rows(image)
    start = sustained_edge(rows)
    end = sustained_edge(rows, from_end=True)
    low, high = TITLE_RANGES[index]
    if start is None or not low <= start <= high + TITLE_TOLERANCE:
        errors.append(f"title starts at {start}, expected {low}..{high}")
    if end is None or not END_RANGE[0] <= end <= END_RANGE[1]:
        errors.append(f"content ends at {end}, expected {END_RANGE[0]}..{END_RANGE[1]}")
    fill = round((end - start) / (END_RANGE[1] - low), 3) if start is not None and end is not None else 0.0
    if fill < MIN_FILL[index]:
        errors.append(f"vertical fill too low: {fill} < {MIN_FILL[index]}")
    blue, coral = color_counts(image)
    ratio = round(coral / (image.width * image.height), 5)
    if blue > BLUE_PIXEL_LIMIT:
        errors.append(f"forbidden electric-blue pixels: {blue}")
    if ratio > MAX_CORAL_RATIO[index]:
        errors.append(f"coral coverage too high: {ratio} > {MAX_CORAL_RATIO[index]}")
    return {
        "ok": not errors,
        "errors": errors,
        "content_start_y": start,
        "content_end_y": end,
        "vertical_fill": fill,
        "blue_pixels": blue,
        "coral_pixels": coral,
        "coral_ratio": ratio,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slides", nargs="+", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    results = []
    for index, path in enumerate(args.slides, 1):
        with Image.open(path) as opened:
            results.append({"slide": index, "path": path.as_posix(), **analyze(opened.convert("RGB"), index)})
    report = {"ok": all(item["ok"] for item in results), "results": results}
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

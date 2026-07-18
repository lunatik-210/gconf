#!/usr/bin/env python3
"""Apply one deterministic GCONF header system to six normalized slides."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


FONT_ALLOWLIST = (
    Path("/System/Library/Fonts/Supplemental/PTMono.ttc"),
    Path("/System/Library/Fonts/SFNSMono.ttf"),
    Path("/System/Library/Fonts/Menlo.ttc"),
)
LEFT_LABELS = (
    "[ gconf ]",
    "[ gconf ]  за 3 недели",
    "[ gconf ]  программа",
    "[ gconf ]  запросы",
    "[ gconf ]  результат",
    "[ gconf ]  старт",
)
FORMAT_SPECS = {
    "9:16": {
        "canvas": (1080, 1920),
        "band_height": 210,
        "left_x": 88,
        "baseline_y": 118,
        "right_x": 992,
        "divider_y": 208,
        "font_size": 25,
        "tracking": 0,
    },
    "4:5": {
        "canvas": (1080, 1350),
        "band_height": 150,
        "left_x": 88,
        "baseline_y": 96,
        "right_x": 992,
        "divider_y": 148,
        "font_size": 25,
        "tracking": 0,
    },
}
PAPER = "#F7F4EE"
GRAPHITE = "#171513"
GRID = "#E1DCD4"
GREY = "#77716C"


def choose_font() -> Path:
    for path in FONT_ALLOWLIST:
        if path.exists():
            return path
    raise FileNotFoundError("no approved monospaced font found")


def layout_for(format_name: str = "9:16") -> dict:
    return FORMAT_SPECS[format_name]


def apply_header(image: Image.Image, index: int, font_path: Path, format_name: str = "9:16") -> Image.Image:
    layout = layout_for(format_name)
    image.load()
    canvas = image.convert("RGB").copy()
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1080, layout["band_height"]), fill=PAPER)
    for x in range(0, 1081, 36):
        draw.line((x, 0, x, layout["divider_y"]), fill=GRID, width=1)
    for y in range(0, layout["divider_y"] + 1, 36):
        draw.line((0, y, 1080, y), fill=GRID, width=1)
    draw.rectangle((0, 0, 1080, layout["band_height"]), outline=None)
    font = ImageFont.truetype(str(font_path), layout["font_size"])
    left = LEFT_LABELS[index - 1]
    page = f"{index:02d} / 06"
    draw.text((layout["left_x"], layout["baseline_y"]), left, font=font, fill=GRAPHITE, anchor="lm")
    draw.text((layout["right_x"], layout["baseline_y"]), page, font=font, fill=GREY, anchor="rm")
    draw.line((0, layout["divider_y"], 1080, layout["divider_y"]), fill=GRAPHITE, width=2)
    return canvas


def header_pixels_sha256(image: Image.Image, format_name: str = "9:16") -> str:
    layout = layout_for(format_name)
    crop = image.convert("RGB").crop((0, 0, 1080, layout["band_height"] + 1))
    return hashlib.sha256(crop.tobytes()).hexdigest()


def expected_header_sha256(index: int, font_path: Path, format_name: str = "9:16") -> str:
    blank = Image.new("RGB", layout_for(format_name)["canvas"], PAPER)
    return header_pixels_sha256(apply_header(blank, index, font_path, format_name), format_name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs=6, type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--format", choices=tuple(FORMAT_SPECS), default="9:16")
    parser.add_argument("--template-out", type=Path)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    font_path = choose_font()
    layout = layout_for(args.format)
    if args.template_out:
        args.template_out.parent.mkdir(parents=True, exist_ok=True)
        blank = Image.new("RGB", layout["canvas"], PAPER)
        apply_header(blank, 1, font_path, args.format).save(args.template_out, optimize=True)
    outputs = []
    for index, source in enumerate(args.inputs, 1):
        with Image.open(source) as image:
            if image.size != tuple(layout["canvas"]):
                raise SystemExit(f"normalized input must be {layout['canvas'][0]}x{layout['canvas'][1]}: {source}")
            output = args.out_dir / f"slide-{index:02d}.png"
            apply_header(image, index, font_path, args.format).save(output, optimize=True)
            outputs.append(output.as_posix())
    report = {
        "header_applied": True,
        "format": args.format,
        "layout": layout,
        "font_path": font_path.as_posix(),
        "font_sha256": hashlib.sha256(font_path.read_bytes()).hexdigest(),
        "page_labels": [f"{index:02d} / 06" for index in range(1, 7)],
        "left_labels": list(LEFT_LABELS),
        "header_pixel_sha256": [expected_header_sha256(index, font_path, args.format) for index in range(1, 7)],
        "template_path": args.template_out.as_posix() if args.template_out else None,
        "template_sha256": hashlib.sha256(args.template_out.read_bytes()).hexdigest() if args.template_out else None,
        "outputs": outputs,
    }
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

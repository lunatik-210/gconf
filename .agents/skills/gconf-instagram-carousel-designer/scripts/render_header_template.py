#!/usr/bin/env python3
"""Render the deterministic blank master-template used as an image reference."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

import apply_shared_header


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--format", choices=tuple(apply_shared_header.FORMAT_SPECS), default="9:16")
    args = parser.parse_args()
    layout = apply_shared_header.layout_for(args.format)
    font = apply_shared_header.choose_font()
    blank = Image.new("RGB", layout["canvas"], apply_shared_header.PAPER)
    rendered = apply_shared_header.apply_header(blank, 1, font, args.format)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rendered.save(args.output, optimize=True)
    print(json.dumps({
        "path": args.output.as_posix(),
        "format": args.format,
        "size": list(layout["canvas"]),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "font_path": font.as_posix(),
        "font_sha256": hashlib.sha256(font.read_bytes()).hexdigest(),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

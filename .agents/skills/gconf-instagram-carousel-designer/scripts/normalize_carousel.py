#!/usr/bin/env python3
"""Normalize generated carousel sources to one fixed Instagram canvas."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


CANVAS = (1080, 1350)


def normalize_exact(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Fix the canvas without deleting any model-generated edge.

    Image edits occasionally return a canvas a few percent away from 4:5 even
    when both the prompt and edit target are exact. A cover crop would delete
    the generated header. An exact resize preserves all four edges and keeps
    the header part of the generated image, not a later overlay.
    """
    return image.resize(size, Image.Resampling.LANCZOS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--start-index", type=int, default=1)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for index, path in enumerate(args.inputs, args.start_index):
        with Image.open(path) as image:
            image = image.convert("RGB")
            normalize_exact(image, CANVAS).save(
                args.out_dir / f"slide-{index:02d}.png", optimize=True
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

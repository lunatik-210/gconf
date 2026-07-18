#!/usr/bin/env python3
"""Create grayscale structural references while preserving source provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def derive(source: Path, output: Path) -> dict:
    before = sha(source)
    with Image.open(source) as opened:
        rgb = opened.convert("RGB")
        grayscale = ImageOps.grayscale(rgb).convert("RGB")
        dimensions = list(rgb.size)
    output.parent.mkdir(parents=True, exist_ok=True)
    grayscale.save(output, optimize=True)
    after = sha(source)
    if before != after:
        raise RuntimeError(f"source reference changed while deriving: {source}")
    return {
        "source": source.as_posix(),
        "source_sha256": before,
        "derived": output.as_posix(),
        "derived_sha256": sha(output),
        "dimensions": dimensions,
        "transform": "grayscale_rgb_no_resize",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    slides = sorted(args.references_dir.glob("IMG_*.jpg"))
    feed = args.references_dir / "инстаграмм аккаунт gconf.PNG"
    if len(slides) != 6 or not feed.is_file():
        raise SystemExit("expected feed screenshot and exactly six IMG_*.jpg references")
    records = [derive(feed, args.out_dir / "feed.png")]
    records.extend(
        derive(source, args.out_dir / f"slide-{index:02d}.png")
        for index, source in enumerate(slides, 1)
    )
    report = {"ok": True, "reference_mode": "grayscale_structure_only", "records": records}
    report_path = args.report or args.out_dir / "structure-provenance.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

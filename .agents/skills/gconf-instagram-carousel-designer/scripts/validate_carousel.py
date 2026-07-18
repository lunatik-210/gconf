#!/usr/bin/env python3
"""Validate a completed master-frame GCONF Instagram carousel run."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

import analyze_header_geometry
import analyze_visual_style


PROJECT_ROOT = Path(__file__).resolve().parents[4]
REQUIRED = (
    "design-brief.json", "prompts.json", "manifest.json", "qa.md",
    "master-report.json", "header-geometry-report.json", "visual-style-report.json",
    "structure-provenance.json",
)
EXPECTED_SIZE = (1080, 1350)
REQUIRED_TITLES = (
    "Vibe Coding", "За 3 недели вы", "Программа потока",
    "С чем приходят", "С чем уходят участники GCONF", "Vibe Coding · AI Ops",
)
EXPECTED_HEADERS = (
    ("[ gconf ]", "01 / 06"),
    ("[ 02 ] за 3 недели", "02 / 06"),
    ("[ 03 ] программа", "03 / 06"),
    ("[ 04 ] запросы", "04 / 06"),
    ("[ 05 ] результат", "05 / 06"),
    ("[ 06 ] старт · gconf", "06 / 06"),
)


def first_content_row(image: Image.Image, start: int = 175) -> int | None:
    grey = image.convert("L")
    active = []
    for y in range(start, grey.height):
        dark = sum(1 for x in range(grey.width) if grey.getpixel((x, y)) < 105)
        if dark > 30:
            active.append(y)
    active_set = set(active)
    for y in active:
        if sum(1 for offset in range(12) if y + offset in active_set) >= 8:
            return y
    return None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(run: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED:
        if not (run / name).exists():
            errors.append(f"missing: {name}")
    master_path = run / "master" / "slide-00-master.png"
    if not master_path.exists():
        errors.append("missing generated master-frame")
    sources = sorted((run / "source").glob("slide-*.png"))
    finals = sorted((run / "generated").glob("slide-*.png"))
    if len(sources) != 6:
        errors.append(f"expected six source edits, found {len(sources)}")
    if len(finals) != 6:
        errors.append(f"expected six final PNGs, found {len(finals)}")
    manifest = {}
    prompts = []
    try:
        if (run / "manifest.json").exists():
            manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        if (run / "prompts.json").exists():
            prompts = json.loads((run / "prompts.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON: {exc}")
    format_name = manifest.get("format", "4:5")
    expected_size = EXPECTED_SIZE
    if format_name != "4:5":
        errors.append(f"format must be 4:5, found: {format_name}")
    sizes = set()
    if master_path.exists():
        with Image.open(master_path) as master_image:
            if master_image.size != expected_size:
                errors.append(f"wrong master size: {master_image.size}")
            master = master_image.convert("RGB")
        for index, path in enumerate(finals, 1):
            with Image.open(path) as opened:
                sizes.add(opened.size)
                if opened.size != expected_size:
                    errors.append(f"wrong size {opened.size}: {path.name}")
                image = opened.convert("RGB")
            comparison = analyze_header_geometry.compare(master, image)
            for issue in comparison["errors"]:
                errors.append(f"slide {index}: {issue}")
            style = analyze_visual_style.analyze(image, index)
            for issue in style["errors"]:
                errors.append(f"slide {index}: {issue}")
    if len(sizes) > 1:
        errors.append(f"mixed final dimensions: {sorted(sizes)}")
    if len(prompts) != 6:
        errors.append("prompts.json must contain six prompts")
    for index, item in enumerate(prompts, 1):
        prompt = re.sub(r"\s+", " ", item.get("prompt", "")).strip()
        required = item.get("required_text", [])
        for unit in required:
            if re.sub(r"\s+", " ", unit).strip() not in prompt:
                errors.append(f"slide {index}: required text missing from prompt: {unit[:60]}")
        if REQUIRED_TITLES[index - 1] not in prompt:
            errors.append(f"slide {index}: required large title missing")
        left, right = EXPECTED_HEADERS[index - 1]
        if left not in prompt or right not in prompt:
            errors.append(f"slide {index}: expected header text missing from prompt")
        roles = [ref.get("role") for ref in item.get("references", [])]
        if roles != ["master_edit_target", "grayscale_structure_density_geometry"]:
            errors.append(f"slide {index}: references must be master then matching grayscale structure only")
        if item.get("legacy_reference_policy") != "forbid_all_readable_legacy_copy":
            errors.append(f"slide {index}: legacy reference copy policy missing")
    prompt_blob = " ".join(item.get("prompt", "") for item in prompts)
    if "НУЖНО ПОДТВЕРДИТЬ" in prompt_blob:
        errors.append("confirmation placeholder remains in prompts")
    if "27 октября 2026" not in prompt_blob:
        errors.append("approved proposed date is missing")
    confirmed_cta = "«vibe» в комменты — скинем детали"
    if confirmed_cta not in prompt_blob:
        errors.append("confirmed CTA is missing from prompts")
    if "[CTA — НУЖНО ПОДТВЕРДИТЬ]" in prompt_blob:
        errors.append("CTA placeholder remains in prompts")
    if prompts:
        cover_required = prompts[0].get("required_text", [])
        if sum(unit.lower().count("vibe coding") for unit in cover_required) != 1:
            errors.append("cover must contain Vibe Coding exactly once")
    if manifest:
        if manifest.get("generation_mode") != "built-in image_gen":
            errors.append("generation_mode must be built-in image_gen")
        if manifest.get("workflow_mode") != "master-frame-generation":
            errors.append("workflow_mode must be master-frame-generation")
        if manifest.get("header_overlay_applied") is not False:
            errors.append("header_overlay_applied must be false")
        if "shared_header" in manifest:
            errors.append("legacy shared_header must not appear in v6 manifest")
        if manifest.get("date", {}).get("value") != "2026-10-27" or manifest.get("date", {}).get("status") != "proposal_user_authorized":
            errors.append("date must be 2026-10-27 with proposal_user_authorized status")
        copy_source = manifest.get("copy_source", {})
        source_value = copy_source.get("path")
        path = PROJECT_ROOT / source_value if source_value else None
        if not path or not path.is_file() or copy_source.get("sha256") != sha(path):
            errors.append("copy source path/SHA invalid")
        master_ref = manifest.get("master_frame", {})
        if master_path.exists() and master_ref.get("sha256") != sha(master_path):
            errors.append("master-frame SHA invalid")
        refs = manifest.get("references", {})
        if refs.get("reference_mode") != "grayscale_structure_only":
            errors.append("reference_mode must be grayscale_structure_only")
        historical_refs = refs.get("historical_slides", [])
        if len(historical_refs) != 6:
            errors.append("manifest must contain six historical reference pairs")
        for index, ref in enumerate(historical_refs, 1):
            source = PROJECT_ROOT / ref.get("source", "")
            derived = PROJECT_ROOT / ref.get("derived", "")
            if ref.get("slide") != index or not source.is_file() or ref.get("source_sha256") != sha(source):
                errors.append(f"historical source reference {index} path/SHA invalid")
            if not derived.is_file() or ref.get("derived_sha256") != sha(derived):
                errors.append(f"grayscale reference {index} path/SHA invalid")
            if index <= len(prompts):
                prompt_refs = prompts[index - 1].get("references", [])
                if len(prompt_refs) != 2 or prompt_refs[1].get("path") != ref.get("derived"):
                    errors.append(f"slide {index}: prompt does not use recorded grayscale derivative")
        slide_records = manifest.get("slides", [])
        if len(slide_records) != 6:
            errors.append("manifest must contain six slide records")
        for index, record in enumerate(slide_records, 1):
            source_path = PROJECT_ROOT / record.get("source", "")
            final_path = PROJECT_ROOT / record.get("final", "")
            if record.get("slide") != index:
                errors.append(f"slide record {index} has wrong index")
            if not source_path.is_file() or record.get("source_sha256") != sha(source_path):
                errors.append(f"slide record {index} source path/SHA invalid")
            if not final_path.is_file() or record.get("final_sha256") != sha(final_path):
                errors.append(f"slide record {index} final path/SHA invalid")
            if final_path.is_file():
                with Image.open(final_path) as opened:
                    style = analyze_visual_style.analyze(opened.convert("RGB"), index)
                if record.get("content_start_y") != style["content_start_y"]:
                    errors.append(f"slide record {index} content_start_y is stale")
                if record.get("content_end_y") != style["content_end_y"]:
                    errors.append(f"slide record {index} content_end_y is stale")
                if record.get("vertical_fill") != style["vertical_fill"]:
                    errors.append(f"slide record {index} vertical_fill is stale")
                if record.get("blue_pixels") != style["blue_pixels"]:
                    errors.append(f"slide record {index} blue pixel count is stale")
        inventory = manifest.get("copy_inventory", {})
        for key, value in {"outcomes": 5, "program_blocks": 6, "audience_requests": 6, "case_cards": 6, "condition_tags": 4}.items():
            if inventory.get(key) != value:
                errors.append(f"copy inventory {key} must equal {value}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    errors = validate(args.run.resolve())
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

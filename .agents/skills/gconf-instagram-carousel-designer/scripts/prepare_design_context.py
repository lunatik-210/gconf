#!/usr/bin/env python3
"""Validate and summarize announcement copy and local references without writes."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path


def root() -> Path:
    return Path(__file__).resolve().parents[4]


def resolve_copy_decision(project: Path, decision_id: str, run_ref: str) -> dict:
    path = project / ".agents/skills/gconf-editorial-gates/scripts/editorial_gates.py"
    spec = importlib.util.spec_from_file_location("gconf_editorial_gates", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Editorial gate dependency is missing: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.resolve(
        project,
        argparse.Namespace(
            decision_id=decision_id,
            workflow="announcement",
            gate_type="announcement_copy_approval",
            upstream_ref=run_ref,
            selected_ref=[],
        ),
    )
    return result["decision"]


def resolve_permission_decision(project: Path, decision_id: str, run_ref: str) -> dict:
    path = project / ".agents/skills/gconf-editorial-gates/scripts/editorial_gates.py"
    spec = importlib.util.spec_from_file_location("gconf_editorial_permissions", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Editorial gate dependency is missing: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.resolve(
        project,
        argparse.Namespace(
            decision_id=decision_id, workflow="announcement",
            gate_type="publication_permission", upstream_ref=run_ref,
            selected_ref=[],
        ),
    )["decision"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--announcement-run", type=Path, required=True)
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--permission-decision-id", required=True)
    parser.add_argument("--carousel-file", default="instagram-carousel.md")
    parser.add_argument("--references-dir", type=Path, required=True)
    args = parser.parse_args()
    project = root()
    run = args.announcement_run if args.announcement_run.is_absolute() else project / args.announcement_run
    refs = args.references_dir if args.references_dir.is_absolute() else project / args.references_dir
    carousel = (run / args.carousel_file).resolve()
    if run.resolve() not in carousel.parents:
        raise SystemExit("--carousel-file must resolve inside --announcement-run")
    manifest_path = run / "manifest.json"
    errors: list[str] = []
    if not carousel.exists() or not manifest_path.exists():
        errors.append(f"announcement run lacks {args.carousel_file} or manifest.json")
    old_slides = sorted(refs.glob("IMG_*.jpg"))
    feed = refs / "инстаграмм аккаунт gconf.PNG"
    if len(old_slides) != 6:
        errors.append(f"expected six old slides, found {len(old_slides)}")
    if not feed.exists():
        errors.append("feed screenshot is missing")
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    run_ref = run.resolve().relative_to(project.resolve()).as_posix()
    carousel_ref = carousel.relative_to(project).as_posix()
    try:
        decision = resolve_copy_decision(project, args.decision_id, run_ref)
        resolve_permission_decision(project, args.permission_decision_id, run_ref)
    except Exception as exc:
        print(json.dumps({"ok": False, "errors": [f"copy approval gate failed: {exc}"]}, ensure_ascii=False, indent=2))
        return 1
    if carousel_ref not in decision.get("selected_refs", []):
        print(json.dumps({"ok": False, "errors": ["approved copy does not include the selected carousel file"]}, ensure_ascii=False, indent=2))
        return 1
    copy = carousel.read_text(encoding="utf-8")
    headings = re.findall(r"^## Слайд (\d) — (.+)$", copy, flags=re.MULTILINE)
    if len(headings) != 6:
        print(json.dumps({"ok": False, "errors": ["carousel copy must have six slide headings"]}, ensure_ascii=False, indent=2))
        return 1
    source_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sections = re.split(r"^## Слайд \d — .+$", copy, flags=re.MULTILINE)[1:]
    required_text = []
    for index, section in enumerate(sections, 1):
        units = []
        for block in re.split(r"\n\s*\n", section.strip()):
            normalized = re.sub(r"\s+", " ", block.replace("**", "")).strip()
            if normalized:
                units.append(normalized)
        required_text.append({"index": index, "units": units})
    inventory = {
        "slide_count": 6,
        "outcomes": 5,
        "program_blocks": 6,
        "audience_requests": 6,
        "case_cards": 6,
        "condition_tags": 4,
    }
    files = [feed, *old_slides]
    result = {
        "schema_version": "2.0",
        "ok": True,
        "read_only": True,
        "decision_refs": [args.decision_id, args.permission_decision_id],
        "workflow_status": "approved",
        "publication_status": "not_ready",
        "format": "4:5",
        "canvas": [1080, 1350],
        "announcement_run": run_ref,
        "carousel_file": carousel.name,
        "carousel_path": carousel.relative_to(project).as_posix(),
        "carousel_sha256": hashlib.sha256(copy.encode("utf-8")).hexdigest(),
        "copy_inventory": inventory,
        "required_text": required_text,
        "product_name": source_manifest.get("product_name"),
        "direction_id": source_manifest.get("direction_id"),
        "slides": [{"index": int(index), "job": job} for index, job in headings],
        "placeholders": sorted(set(re.findall(r"\[[^\]]*НУЖНО ПОДТВЕРДИТЬ[^\]]*\]", copy))),
        "references": {
            "feed": {
                "role": "brand_grammar",
                "path": feed.relative_to(project).as_posix(),
                "sha256": hashlib.sha256(feed.read_bytes()).hexdigest(),
                "bytes": feed.stat().st_size,
            },
            "blue_slides": [
                {
                    "slide": index,
                    "role": "structure_density_geometry",
                    "path": path.relative_to(project).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "bytes": path.stat().st_size,
                }
                for index, path in enumerate(old_slides, 1)
            ],
            "master_frame_required": True,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Resolve copy approval before formatting selected GCONF Telegram posts."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--writer-run", type=Path, required=True)
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--permission-decision-id", required=True)
    parser.add_argument("--freshness-decision-id")
    parser.add_argument("--workflow", choices=("news", "announcement"), required=True)
    parser.add_argument("--source", action="append", required=True, type=Path)
    args = parser.parse_args()
    root = project_root()
    run = args.writer_run if args.writer_run.is_absolute() else root / args.writer_run
    try:
        run_ref = run.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        print(json.dumps({"ok": False, "error": "writer run is outside project"}))
        return 1
    gate_type = "news_copy_approval" if args.workflow == "news" else "announcement_copy_approval"
    path = root / ".agents/skills/gconf-editorial-gates/scripts/editorial_gates.py"
    spec = importlib.util.spec_from_file_location("gconf_editorial_gates", path)
    if not spec or not spec.loader:
        print(json.dumps({"ok": False, "error": f"gate dependency missing: {path}"}))
        return 1
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        manifest_path = run / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
        result = module.resolve(
            root,
            argparse.Namespace(
                decision_id=args.decision_id,
                workflow=args.workflow,
                gate_type=gate_type,
                upstream_ref=run_ref,
                selected_ref=[],
            ),
        )
        decision = result["decision"]
        permission = module.resolve(
            root,
            argparse.Namespace(
                decision_id=args.permission_decision_id,
                workflow=args.workflow,
                gate_type="publication_permission",
                upstream_ref=run_ref,
                selected_ref=[],
            ),
        )["decision"]
        material_limitations = manifest.get("unresolved_items") or []
        freshness_decision = None
        if args.workflow == "news" and material_limitations:
            if not args.freshness_decision_id:
                raise module.GateError(
                    "material news limitations require --freshness-decision-id"
                )
            freshness_decision = module.resolve(
                root,
                argparse.Namespace(
                    decision_id=args.freshness_decision_id,
                    workflow="news",
                    gate_type="freshness_acceptance",
                    upstream_ref=run_ref,
                    selected_ref=[],
                ),
            )["decision"]
        sources = []
        for value in args.source:
            source = value if value.is_absolute() else root / value
            source_ref = source.resolve().relative_to(root.resolve()).as_posix()
            if run.resolve() not in source.resolve().parents:
                raise module.GateError(f"source is outside writer run: {source_ref}")
            if source_ref not in decision["selected_refs"]:
                raise module.GateError(f"source is not approved: {source_ref}")
            sources.append(source_ref)
    except (module.GateError, OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    decision_refs = [args.decision_id, args.permission_decision_id]
    if args.freshness_decision_id:
        decision_refs.append(args.freshness_decision_id)
    print(json.dumps({
        "ok": True,
        "read_only": True,
        "workflow": args.workflow,
        "gate_type": gate_type,
        "decision_refs": decision_refs,
        "writer_run": run_ref,
        "approved_sources": sources,
        "material_limitations": material_limitations,
        "publication_status": "not_ready",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

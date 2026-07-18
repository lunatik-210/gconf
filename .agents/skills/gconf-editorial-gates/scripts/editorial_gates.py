#!/usr/bin/env python3
"""Record and validate append-only GCONF editorial decisions."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKFLOWS = {"semantic", "news", "announcement", "design", "publication"}
GATES = {
    "semantic_evidence_review": "semantic",
    "news_topic_selection": "news",
    "news_copy_approval": "news",
    "freshness_acceptance": None,
    "announcement_direction_selection": "announcement",
    "offer_fact_and_cta_allowlist": "announcement",
    "publication_permission": None,
    "announcement_copy_approval": "announcement",
    "carousel_visual_approval": "design",
    "publication_confirmation": "publication",
}
SOURCES = {"human_explicit", "agent_choice_authorized", "inferred_backfill"}
STATUSES = {"confirmed", "declined", "needs_confirmation"}
REQUIRED = {
    "type", "schema_version", "decision_id", "workflow", "gate_type",
    "upstream_ref", "selected_refs", "artifact_refs", "decision_source",
    "recorded_by", "instruction_excerpt", "decided_at", "status",
    "supersedes", "downstream_ref",
}
RUN_LANES = {
    "research/news_analysis/runs": "news_analysis",
    "research/news_drafts/runs": "news_draft",
    "research/announcement_analysis/runs": "announcement_analysis",
    "research/announcement_drafts/runs": "announcement_draft",
    "research/instagram_carousels/runs": "carousel",
}


class GateError(RuntimeError):
    pass


def default_root() -> Path:
    return Path(__file__).resolve().parents[4]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def rel(root: Path, value: str | Path) -> str:
    path = Path(value)
    resolved = path.resolve() if path.is_absolute() else (root / path).resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise GateError(f"Path is outside project root: {value}") from exc


def yaml_scalar(value: Any) -> str:
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if value is None:
        value = ""
    return json.dumps(str(value), ensure_ascii=False)


def render_card(card: dict[str, Any]) -> str:
    ordered = [
        "type", "schema_version", "decision_id", "workflow", "gate_type",
        "upstream_ref", "selected_refs", "artifact_refs", "decision_source",
        "recorded_by", "instruction_excerpt", "decided_at", "status",
        "supersedes", "downstream_ref",
    ]
    frontmatter = "\n".join(f"{key}: {yaml_scalar(card.get(key))}" for key in ordered)
    selections = "\n".join(f"- `{item}`" for item in card["selected_refs"]) or "- none"
    return (
        f"---\n{frontmatter}\n---\n\n"
        f"# {card['gate_type']}\n\n"
        f"Human decision recorded by an agent. Canonical upstream: "
        f"`{card['upstream_ref']}`.\n\n## Selected refs\n\n{selections}\n"
    )


def parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw.strip('"')


def read_card(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, flags=re.DOTALL)
    if not match:
        raise GateError(f"Decision card lacks YAML frontmatter: {path}")
    card: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        card[key.strip()] = parse_scalar(value)
    return card


def decisions_dir(root: Path) -> Path:
    return root / "knowledge/editorial/decisions"


def load_decisions(root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    items: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for path in sorted(decisions_dir(root).glob("*.md")):
        try:
            card = read_card(path)
        except (OSError, GateError) as exc:
            errors.append(str(exc))
            continue
        decision_id = str(card.get("decision_id") or "")
        if not decision_id:
            errors.append(f"Decision id is missing: {path}")
        elif decision_id in items:
            errors.append(f"Duplicate decision id: {decision_id}")
        else:
            card["_path"] = path
            items[decision_id] = card
    return items, errors


def load_manifest(root: Path, upstream_ref: str) -> tuple[Path, dict[str, Any]]:
    upstream = root / rel(root, upstream_ref)
    path = upstream / "manifest.json" if upstream.is_dir() else upstream
    if not path.is_file():
        raise GateError(f"Upstream manifest is missing: {path}")
    try:
        return upstream, json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GateError(f"Invalid upstream manifest: {path}: {exc}") from exc


def validate_selected_refs(
    root: Path, gate_type: str, upstream_ref: str, selected_refs: list[str]
) -> list[str]:
    if not selected_refs:
        return ["selected_refs must not be empty"]
    if len(selected_refs) != len(set(selected_refs)):
        return ["selected_refs must be unique"]
    errors: list[str] = []
    if gate_type == "semantic_evidence_review":
        for item in selected_refs:
            if not semantic_path(root, item):
                errors.append(f"Semantic card is missing: {item}")
    elif gate_type == "news_topic_selection":
        _, manifest = load_manifest(root, upstream_ref)
        known = {
            str(item.get("topic_id"))
            for item in manifest.get("candidates", []) + manifest.get("rejected_signals", [])
        }
        unknown = sorted(set(selected_refs) - known)
        if unknown:
            errors.append(f"Unknown topic IDs: {unknown}")
    elif gate_type == "announcement_direction_selection":
        _, manifest = load_manifest(root, upstream_ref)
        known = {str(item.get("id")) for item in manifest.get("directions", [])}
        unknown = sorted(set(selected_refs) - known)
        if unknown:
            errors.append(f"Unknown direction IDs: {unknown}")
    elif gate_type == "offer_fact_and_cta_allowlist":
        for item in selected_refs:
            if item == "allowlist:none":
                continue
            path = root / rel(root, item)
            if not path.is_file() or path.suffix.lower() != ".json":
                errors.append(f"Confirmed-facts allowlist is missing or not JSON: {item}")
    elif gate_type in {"news_copy_approval", "announcement_copy_approval", "carousel_visual_approval", "publication_confirmation"}:
        upstream = root / rel(root, upstream_ref)
        for item in selected_refs:
            path = root / rel(root, item)
            if not path.is_file():
                errors.append(f"Selected artifact is missing: {item}")
            elif upstream.is_dir() and upstream.resolve() not in path.resolve().parents and gate_type != "publication_confirmation":
                errors.append(f"Selected artifact is outside upstream run: {item}")
        if gate_type == "carousel_visual_approval" and len(selected_refs) != 6:
            errors.append("carousel_visual_approval requires exactly six images")
    return errors


def semantic_path(root: Path, value: str) -> Path | None:
    direct = root / value
    if direct.is_file() and direct.suffix == ".md" and direct.parent.parent == root / "knowledge":
        return direct
    for folder in ("actors", "labs", "cohorts", "pains", "cases", "trends", "technologies", "claims"):
        candidate = root / "knowledge" / folder / f"{value}.md"
        if candidate.is_file():
            return candidate
    return None


def artifact_refs(root: Path, selected_refs: list[str], gate_type: str) -> list[str]:
    if gate_type not in {
        "news_copy_approval", "announcement_copy_approval",
        "carousel_visual_approval", "publication_confirmation",
        "offer_fact_and_cta_allowlist",
    }:
        return []
    result = []
    for item in selected_refs:
        if item == "allowlist:none":
            continue
        path = root / rel(root, item)
        if path.is_file():
            result.append(f"{rel(root, path)}#sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
    return result


def record(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    if args.workflow not in WORKFLOWS:
        raise GateError(f"Unknown workflow: {args.workflow}")
    if args.gate_type not in GATES:
        raise GateError(f"Unknown gate type: {args.gate_type}")
    expected = GATES[args.gate_type]
    if expected and expected != args.workflow:
        raise GateError(f"{args.gate_type} requires workflow {expected}")
    if args.decision_source not in SOURCES or args.status not in STATUSES:
        raise GateError("Invalid decision source or status")
    if args.decision_source == "inferred_backfill" and args.status != "needs_confirmation":
        raise GateError("inferred_backfill must use needs_confirmation")
    if args.decision_source != "inferred_backfill" and args.status == "needs_confirmation":
        raise GateError("needs_confirmation is reserved for inferred_backfill")
    upstream_ref = rel(root, args.upstream_ref)
    errors = validate_selected_refs(root, args.gate_type, upstream_ref, args.selected_ref)
    if errors:
        raise GateError("; ".join(errors))
    existing, load_errors = load_decisions(root)
    if load_errors:
        raise GateError("; ".join(load_errors))
    if args.supersedes and args.supersedes not in existing:
        raise GateError(f"Superseded decision does not exist: {args.supersedes}")
    now = utc_now()
    slug = args.gate_type.replace("_", "-")
    decision_id = args.decision_id or f"decision-{now.strftime('%Y%m%dT%H%M%S%fZ')}-{slug}"
    if decision_id in existing:
        raise GateError(f"Decision already exists: {decision_id}")
    card = {
        "type": "editorial_decision",
        "schema_version": "1.0",
        "decision_id": decision_id,
        "workflow": args.workflow,
        "gate_type": args.gate_type,
        "upstream_ref": upstream_ref,
        "selected_refs": list(args.selected_ref),
        "artifact_refs": artifact_refs(root, args.selected_ref, args.gate_type),
        "decision_source": args.decision_source,
        "recorded_by": "agent",
        "instruction_excerpt": args.instruction_excerpt.strip(),
        "decided_at": args.decided_at or now.isoformat().replace("+00:00", "Z"),
        "status": args.status,
        "supersedes": args.supersedes or "",
        "downstream_ref": rel(root, args.downstream_ref) if args.downstream_ref else "",
    }
    directory = decisions_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{decision_id}.md"
    path.write_text(render_card(card), encoding="utf-8")
    return {"ok": True, "decision_id": decision_id, "path": rel(root, path), "decision": card}


def verify_artifacts(root: Path, refs: list[str]) -> list[str]:
    errors = []
    for ref in refs:
        if "#sha256=" not in ref:
            errors.append(f"Invalid artifact ref: {ref}")
            continue
        path_text, expected = ref.rsplit("#sha256=", 1)
        path = root / rel(root, path_text)
        if not path.is_file():
            errors.append(f"Approved artifact is missing: {path_text}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"Approved artifact changed: {path_text}")
    return errors


def resolve(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    decisions, errors = load_decisions(root)
    if errors:
        raise GateError("; ".join(errors))
    card = decisions.get(args.decision_id)
    if not card:
        raise GateError(f"Decision not found: {args.decision_id}")
    if card.get("status") != "confirmed":
        raise GateError(f"Decision is not confirmed: {card.get('status')}")
    for item in decisions.values():
        if item.get("supersedes") == args.decision_id and item.get("status") == "confirmed":
            raise GateError(f"Decision is superseded by {item.get('decision_id')}")
    expected = {
        "workflow": args.workflow,
        "gate_type": args.gate_type,
        "upstream_ref": rel(root, args.upstream_ref),
    }
    for key, value in expected.items():
        if card.get(key) != value:
            raise GateError(f"Decision {key} mismatch: {card.get(key)!r} != {value!r}")
    if args.selected_ref and card.get("selected_refs") != args.selected_ref:
        raise GateError("Decision selected_refs mismatch")
    selection_errors = validate_selected_refs(
        root, str(card["gate_type"]), str(card["upstream_ref"]), list(card["selected_refs"])
    )
    artifact_errors = verify_artifacts(root, list(card.get("artifact_refs") or []))
    if selection_errors or artifact_errors:
        raise GateError("; ".join(selection_errors + artifact_errors))
    clean = {key: value for key, value in card.items() if not key.startswith("_")}
    return {"ok": True, "decision": clean}


def backfill(root: Path) -> dict[str, Any]:
    existing, errors = load_decisions(root)
    if errors:
        raise GateError("; ".join(errors))
    signatures = {
        (card.get("gate_type"), card.get("upstream_ref"), tuple(card.get("selected_refs") or []), card.get("downstream_ref"))
        for card in existing.values()
    }
    created = []
    specs = [
        (root / "research/news_drafts/runs", "news", "news_topic_selection", "radar_run", "selected_topic_ids"),
        (root / "research/announcement_drafts/runs", "announcement", "announcement_direction_selection", "analysis_run", "direction_id"),
    ]
    for base, workflow, gate_type, upstream_key, selected_key in specs:
        for manifest_path in sorted(base.glob("*/manifest.json")):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            upstream = manifest.get(upstream_key)
            raw_selected = manifest.get(selected_key)
            selected = raw_selected if isinstance(raw_selected, list) else ([raw_selected] if raw_selected else [])
            if not upstream or not selected:
                continue
            downstream = rel(root, manifest_path.parent)
            signature = (gate_type, rel(root, upstream), tuple(selected), downstream)
            if signature in signatures:
                continue
            run_id = manifest.get("run_id") or manifest_path.parent.name
            decision_id = f"decision-backfill-{run_id}-{gate_type.replace('_', '-')}"
            namespace = argparse.Namespace(
                workflow=workflow, gate_type=gate_type, upstream_ref=upstream,
                selected_ref=selected, decision_source="inferred_backfill",
                instruction_excerpt=f"Recovered from downstream manifest {downstream}",
                status="needs_confirmation", supersedes=None, downstream_ref=downstream,
                decision_id=decision_id, decided_at=manifest.get("generated_at"),
            )
            created.append(record(root, namespace))
            signatures.add(signature)
    return {"ok": True, "created": len(created), "decisions": [item["decision_id"] for item in created]}


def run_status(root: Path) -> dict[str, Any]:
    decisions, errors = load_decisions(root)
    counts: dict[str, int] = {}
    pending = []
    for card in decisions.values():
        status = str(card.get("status"))
        counts[status] = counts.get(status, 0) + 1
        if status != "confirmed":
            pending.append(card.get("decision_id"))
    return {"ok": not errors, "counts": counts, "pending": pending, "errors": errors}


def apply_semantic_review(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    decisions, errors = load_decisions(root)
    if errors:
        raise GateError("; ".join(errors))
    card = decisions.get(args.decision_id)
    if not card:
        raise GateError(f"Decision not found: {args.decision_id}")
    if card.get("workflow") != "semantic" or card.get("gate_type") != "semantic_evidence_review":
        raise GateError("Decision is not a semantic evidence review")
    if card.get("status") != "confirmed":
        raise GateError("Semantic review decision is not confirmed")
    if any(
        item.get("supersedes") == args.decision_id and item.get("status") == "confirmed"
        for item in decisions.values()
    ):
        raise GateError("Semantic review decision was superseded")
    changed = []
    for item in card.get("selected_refs") or []:
        path = semantic_path(root, item)
        if not path:
            raise GateError(f"Semantic card is missing: {item}")
        text = path.read_text(encoding="utf-8")
        updated, count = re.subn(
            r'(?m)^review_status:\s*(?:"[^"]*"|\S+)\s*$',
            f'review_status: "{args.review_status}"',
            text,
            count=1,
        )
        if count != 1:
            raise GateError(f"Semantic card lacks one review_status: {rel(root, path)}")
        path.write_text(updated, encoding="utf-8")
        changed.append(rel(root, path))
    return {"ok": True, "decision_id": args.decision_id, "review_status": args.review_status, "changed": changed}


def write_control_files(root: Path) -> None:
    editorial = root / "knowledge/editorial"
    (editorial / "runs").mkdir(parents=True, exist_ok=True)
    (editorial / "views").mkdir(parents=True, exist_ok=True)
    dashboard = """# Editorial Control Plane\n\n- [[views/Editorial Decisions.base|All decisions]]\n- [[views/Pending Gates.base|Pending human gates]]\n- [[views/Editorial Runs.base|Editorial runs]]\n- [[../views/Review Inbox.base|Semantic Review Inbox]]\n\nFull run artifacts remain immutable under `research/`.\n"""
    (editorial / "Editorial Control Plane.md").write_text(dashboard, encoding="utf-8")
    decisions_base = """filters:\n  and:\n    - type == \"editorial_decision\"\nviews:\n  - type: table\n    name: Editorial Decisions\n    order:\n      - file.name\n      - workflow\n      - gate_type\n      - status\n      - decision_source\n      - upstream_ref\n      - decided_at\n"""
    pending_base = """filters:\n  and:\n    - type == \"editorial_decision\"\n    - status != \"confirmed\"\nviews:\n  - type: table\n    name: Pending Human Gates\n    order:\n      - file.name\n      - workflow\n      - gate_type\n      - status\n      - selected_refs\n      - upstream_ref\n"""
    runs_base = """filters:\n  and:\n    - type == \"editorial_run\"\nviews:\n  - type: table\n    name: Editorial Runs\n    order:\n      - file.name\n      - workflow\n      - run_kind\n      - workflow_status\n      - publication_status\n      - generated_at\n"""
    (editorial / "views/Editorial Decisions.base").write_text(decisions_base, encoding="utf-8")
    (editorial / "views/Pending Gates.base").write_text(pending_base, encoding="utf-8")
    (editorial / "views/Editorial Runs.base").write_text(runs_base, encoding="utf-8")


def sync(root: Path) -> dict[str, Any]:
    write_control_files(root)
    output = root / "knowledge/editorial/runs"
    decisions, _ = load_decisions(root)
    created = 0
    for lane, kind in RUN_LANES.items():
        for manifest_path in sorted((root / lane).glob("*/manifest.json")):
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            run_id = str(manifest.get("run_id") or manifest_path.parent.name)
            run_ref = rel(root, manifest_path.parent)
            workflow = "news" if kind.startswith("news") else ("design" if kind == "carousel" else "announcement")
            if kind.endswith("analysis"):
                workflow_status = "awaiting_human_selection"
            elif kind in {"news_draft", "announcement_draft"}:
                workflow_status = "awaiting_copy_approval"
            else:
                workflow_status = "awaiting_visual_approval"
            publication_status = "ready_for_manual_handoff" if manifest.get("publication_ready") is True else "not_ready"
            linked_decisions = list(manifest.get("decision_refs") or [])
            linked_decisions.extend(
                decision_id
                for decision_id, decision in decisions.items()
                if decision.get("upstream_ref") == run_ref
                or decision.get("downstream_ref") == run_ref
            )
            linked_decisions = list(dict.fromkeys(linked_decisions))
            card = {
                "type": "editorial_run", "schema_version": "1.0", "run_id": run_id,
                "workflow": workflow, "run_kind": kind,
                "run_ref": run_ref,
                "generated_at": manifest.get("generated_at") or "",
                "workflow_status": manifest.get("workflow_status") or workflow_status,
                "publication_status": manifest.get("publication_status") or publication_status,
                "decision_refs": linked_decisions,
                "generated": "true",
            }
            fm = "\n".join(f"{key}: {yaml_scalar(value)}" for key, value in card.items())
            text = f"---\n{fm}\n---\n\n# {kind}: {run_id}\n\nCanonical run: `{card['run_ref']}`.\n"
            (output / f"{kind}-{run_id}.md").write_text(text, encoding="utf-8")
            created += 1
    return {"ok": True, "run_cards": created}


def validate(root: Path) -> dict[str, Any]:
    decisions, errors = load_decisions(root)
    for decision_id, card in decisions.items():
        missing = REQUIRED - set(card)
        if missing:
            errors.append(f"{decision_id}: missing fields {sorted(missing)}")
            continue
        if card.get("type") != "editorial_decision" or card.get("schema_version") != "1.0":
            errors.append(f"{decision_id}: invalid type or schema")
        if card.get("workflow") not in WORKFLOWS or card.get("gate_type") not in GATES:
            errors.append(f"{decision_id}: invalid workflow or gate")
        if card.get("decision_source") not in SOURCES or card.get("status") not in STATUSES:
            errors.append(f"{decision_id}: invalid source or status")
        if card.get("decision_source") == "inferred_backfill" and card.get("status") != "needs_confirmation":
            errors.append(f"{decision_id}: inferred backfill is not pending")
        supersedes = card.get("supersedes")
        if supersedes and supersedes not in decisions:
            errors.append(f"{decision_id}: missing superseded decision {supersedes}")
        try:
            errors.extend(
                f"{decision_id}: {error}"
                for error in validate_selected_refs(root, card["gate_type"], card["upstream_ref"], card["selected_refs"])
            )
            errors.extend(f"{decision_id}: {error}" for error in verify_artifacts(root, card.get("artifact_refs") or []))
        except GateError as exc:
            errors.append(f"{decision_id}: {exc}")
        seen = {decision_id}
        target = supersedes
        while target:
            if target in seen:
                errors.append(f"{decision_id}: supersede cycle")
                break
            seen.add(target)
            target = decisions.get(target, {}).get("supersedes")
    return {"ok": not errors, "decision_count": len(decisions), "errors": errors}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=default_root())
    sub = result.add_subparsers(dest="command", required=True)
    record_parser = sub.add_parser("record")
    record_parser.add_argument("--workflow", required=True, choices=sorted(WORKFLOWS))
    record_parser.add_argument("--gate-type", required=True, choices=sorted(GATES))
    record_parser.add_argument("--upstream-ref", required=True)
    record_parser.add_argument("--selected-ref", action="append", default=[], required=True)
    record_parser.add_argument("--decision-source", required=True, choices=sorted(SOURCES))
    record_parser.add_argument("--instruction-excerpt", required=True)
    record_parser.add_argument("--status", choices=sorted(STATUSES), default="confirmed")
    record_parser.add_argument("--supersedes")
    record_parser.add_argument("--downstream-ref")
    record_parser.add_argument("--decision-id")
    record_parser.add_argument("--decided-at")
    resolve_parser = sub.add_parser("resolve")
    resolve_parser.add_argument("--decision-id", required=True)
    resolve_parser.add_argument("--workflow", required=True, choices=sorted(WORKFLOWS))
    resolve_parser.add_argument("--gate-type", required=True, choices=sorted(GATES))
    resolve_parser.add_argument("--upstream-ref", required=True)
    resolve_parser.add_argument("--selected-ref", action="append", default=[])
    sub.add_parser("backfill")
    sub.add_parser("sync")
    sub.add_parser("status")
    sub.add_parser("validate")
    review_parser = sub.add_parser("apply-semantic-review")
    review_parser.add_argument("--decision-id", required=True)
    review_parser.add_argument("--review-status", required=True, choices=("approved", "rejected", "superseded"))
    return result


def main() -> int:
    args = parser().parse_args()
    root = args.root.resolve()
    try:
        if args.command == "record":
            result = record(root, args)
        elif args.command == "resolve":
            result = resolve(root, args)
        elif args.command == "backfill":
            result = backfill(root)
        elif args.command == "sync":
            result = sync(root)
        elif args.command == "status":
            result = run_status(root)
        elif args.command == "apply-semantic-review":
            result = apply_semantic_review(root, args)
        else:
            result = validate(root)
    except (GateError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

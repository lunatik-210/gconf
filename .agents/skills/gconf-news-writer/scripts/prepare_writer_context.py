#!/usr/bin/env python3
"""Prepare selected radar topics for GCONF news writing without mutating inputs."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ContextError(RuntimeError):
    """Raised when writer preconditions are not met."""


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def load_radar_modules(root: Path):
    scripts = root / ".agents/skills/gconf-news-radar/scripts"

    def load(name: str):
        path = scripts / f"{name}.py"
        if not path.exists():
            raise ContextError(f"Radar dependency is missing: {path}")
        spec = importlib.util.spec_from_file_location(f"gconf_radar_{name}", path)
        if not spec or not spec.loader:
            raise ContextError(f"Cannot load radar dependency: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    return load("prepare_radar_context"), load("validate_radar_run")


def resolve_selection_decision(
    root: Path, decision_id: str, radar_run: str
) -> dict[str, Any]:
    path = root / ".agents/skills/gconf-editorial-gates/scripts/editorial_gates.py"
    spec = importlib.util.spec_from_file_location("gconf_editorial_gates", path)
    if not spec or not spec.loader:
        raise ContextError(f"Editorial gate dependency is missing: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        result = module.resolve(
            root,
            argparse.Namespace(
                decision_id=decision_id,
                workflow="news",
                gate_type="news_topic_selection",
                upstream_ref=radar_run,
                selected_ref=[],
            ),
        )
    except module.GateError as exc:
        raise ContextError(f"News topic selection gate failed: {exc}") from exc
    return result["decision"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_run(root: Path, value: Path) -> Path:
    run = value if value.is_absolute() else root / value
    run = run.resolve()
    allowed = (root / "research/news_analysis/runs").resolve()
    if allowed not in run.parents:
        raise ContextError(f"Radar run must be inside {allowed}")
    return run


def select_topics(
    manifest: dict[str, Any], topic_ids: list[str], allow_rejected: bool
) -> list[dict[str, Any]]:
    if not topic_ids:
        raise ContextError("At least one explicit --topic-id is required")
    if len(topic_ids) != len(set(topic_ids)):
        raise ContextError("Topic IDs must be unique")
    items = {
        item.get("topic_id"): item
        for item in manifest.get("candidates", []) + manifest.get("rejected_signals", [])
    }
    missing = [topic_id for topic_id in topic_ids if topic_id not in items]
    if missing:
        raise ContextError(f"Unknown topic IDs: {missing}")
    selected = []
    for topic_id in topic_ids:
        item = items[topic_id]
        score = item.get("score", {}).get("priority_score", -1)
        rejected = item.get("status") == "reject" or score < 65
        if rejected and not allow_rejected:
            raise ContextError(
                f"Topic {topic_id} was rejected or scored below 65; explicit --allow-rejected is required"
            )
        selected.append(item)
    return selected


def resolve_parent_locator(connection, locator: str) -> str | None:
    current = locator
    visited: set[str] = set()
    for _ in range(6):
        row = connection.execute(
            "SELECT target_locator FROM edges WHERE source_locator = ? AND relation = 'replies_to'",
            (current,),
        ).fetchone()
        if not row or row["target_locator"] in visited:
            return None
        current = row["target_locator"]
        visited.add(current)
        document = connection.execute(
            "SELECT kind FROM documents WHERE locator = ?", (current,)
        ).fetchone()
        if document and document["kind"] not in {"youtube_comment", "instagram_comment"}:
            return current
    return None


def resolve_locator(connection, root: Path, item: dict[str, Any]) -> dict[str, Any]:
    locator = str(item.get("locator") or "")
    document = connection.execute(
        """
        SELECT d.locator, d.kind, d.title, d.author, d.published_at, d.url,
               d.body, d.source_path, d.visibility, s.name AS source_name
        FROM documents d JOIN sources s ON s.id = d.source_id
        WHERE d.locator = ?
        """,
        (locator,),
    ).fetchone()
    chunk = None
    if not document:
        chunk = connection.execute(
            """
            SELECT c.locator, 'youtube_transcript_chunk' AS kind, d.title,
                   d.author, d.published_at, d.url, c.body, d.source_path,
                   d.visibility, s.name AS source_name, d.locator AS parent_locator,
                   c.start_seconds, c.end_seconds
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            JOIN sources s ON s.id = d.source_id
            WHERE c.locator = ?
            """,
            (locator,),
        ).fetchone()
    row = document or chunk
    resolved: dict[str, Any] = {
        "evidence_id": item.get("id"),
        "locator": locator,
        "resolved": bool(row),
        "record": dict(row) if row else None,
        "parent": None,
    }
    parent_locator = item.get("parent_locator")
    if not parent_locator and document and document["kind"] in {
        "youtube_comment",
        "instagram_comment",
    }:
        parent_locator = resolve_parent_locator(connection, locator)
    if not parent_locator and chunk:
        parent_locator = chunk["parent_locator"]
    if parent_locator:
        parent = connection.execute(
            """
            SELECT locator, kind, title, author, published_at, url, body,
                   source_path, visibility
            FROM documents WHERE locator = ?
            """,
            (parent_locator,),
        ).fetchone()
        if parent:
            resolved["parent"] = dict(parent)
    local_source = item.get("local_source")
    if not row and local_source:
        path = (root / str(local_source)).resolve()
        if root.resolve() in path.parents and path.is_file():
            resolved["resolved"] = True
            resolved["record"] = {
                "locator": locator,
                "kind": "local_semantic_card",
                "title": item.get("title"),
                "body": path.read_text(encoding="utf-8")[:6000],
                "source_path": path.relative_to(root).as_posix(),
                "visibility": item.get("visibility", "public"),
            }
    return resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radar-run", type=Path, required=True)
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--topic-id", action="append", default=[])
    parser.add_argument("--voice-mode", choices=("GCONF", "Dima"), default="GCONF")
    parser.add_argument("--address", choices=("vy", "ty"), default="vy")
    parser.add_argument("--cta-mode", choices=("editorial", "commercial"), default="editorial")
    parser.add_argument("--cta-text")
    parser.add_argument("--angle-note")
    parser.add_argument("--allow-rejected", action="store_true")
    return parser.parse_args()


def prepare(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    if args.cta_mode == "commercial" and not args.cta_text:
        raise ContextError("A commercial CTA requires --cta-text")
    radar_prepare, radar_validate = load_radar_modules(root)
    run = resolve_run(root, args.radar_run)
    validation_errors = radar_validate.validate(run)
    if validation_errors:
        raise ContextError(f"Radar run is invalid: {validation_errors}")
    manifest_path = run / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    radar_ref = run.relative_to(root).as_posix()
    decision = resolve_selection_decision(root, args.decision_id, radar_ref)
    decision_topics = list(decision["selected_refs"])
    if args.topic_id and args.topic_id != decision_topics:
        raise ContextError("--topic-id values do not match the confirmed decision")
    selected = select_topics(manifest, decision_topics, args.allow_rejected)
    evidence_ids = {
        ref for topic in selected for ref in topic.get("evidence_refs", [])
    }
    evidence = [
        item for item in manifest.get("evidence_index", []) if item.get("id") in evidence_ids
    ]
    coverage_ids = {
        ref for topic in selected for ref in topic.get("closest_coverage_refs", [])
    }
    coverage = [
        item for item in manifest.get("coverage_index", []) if item.get("id") in coverage_ids
    ]
    now = datetime.now(timezone.utc)
    generated_at = manifest.get("generated_at")
    radar_age_days = None
    if generated_at:
        try:
            generated = datetime.fromisoformat(str(generated_at).replace("Z", "+00:00"))
            if generated.tzinfo is None:
                generated = generated.replace(tzinfo=timezone.utc)
            radar_age_days = max(0, (now - generated.astimezone(timezone.utc)).days)
        except ValueError:
            pass
    database = root / "knowledge/_index/gconf.sqlite"
    with closing(radar_prepare.readonly_connection(database)) as connection:
        live_coverage = {
            topic["topic_id"]: radar_prepare.coverage_matches(
                connection,
                f"{topic.get('working_title', '')} {topic.get('focus', '')}",
                limit=8,
            )
            for topic in selected
        }
        resolved_local_evidence = [
            resolve_locator(connection, root, item) for item in evidence
        ]
    permission_blockers = [
        {
            "evidence_id": item.get("id"),
            "visibility": item.get("visibility"),
            "permission_status": item.get("permission_status"),
        }
        for item in evidence
        if item.get("permission_status") in {"required", "unknown"}
    ]
    local_resolution_blockers = [
        item["evidence_id"]
        for item in resolved_local_evidence
        if not item["resolved"]
        and next(
            (source.get("local_source") for source in evidence if source.get("id") == item["evidence_id"]),
            None,
        )
    ]
    return {
        "schema_version": "2.0",
        "prepared_at": now.isoformat(),
        "read_only": True,
        "human_selection": True,
        "decision_refs": [args.decision_id],
        "workflow_status": "selected",
        "publication_status": "not_ready",
        "radar_run": radar_ref,
        "radar_run_sha256": {
            name: digest(run / name) for name in ("backlog.md", "manifest.json", "audit.md")
        },
        "radar_generated_at": generated_at,
        "radar_age_days": radar_age_days,
        "radar_stale": radar_age_days is None or radar_age_days > 14,
        "selected_topic_ids": decision_topics,
        "selected_topics": selected,
        "evidence": evidence,
        "radar_coverage": coverage,
        "live_local_coverage_check": live_coverage,
        "resolved_local_evidence": resolved_local_evidence,
        "permission_blockers": permission_blockers,
        "publication_permission_blocked": bool(permission_blockers),
        "local_resolution_blockers": local_resolution_blockers,
        "writing_settings": {
            "voice_mode": args.voice_mode,
            "address": args.address,
            "cta_mode": args.cta_mode,
            "cta_text": args.cta_text,
            "angle_note": args.angle_note,
            "allow_rejected": args.allow_rejected,
        },
        "required_live_revalidation": [
            {
                "evidence_id": item.get("id"),
                "url": item.get("url"),
                "published_at": item.get("published_at"),
                "claim_supported": item.get("claim_supported"),
            }
            for item in evidence
            if item.get("url")
        ],
        "stop_condition": (
            "Stop without drafting when the central fact or selected focus is no longer supported; "
            "never substitute another topic. Permission-required or unresolved local evidence keeps "
            "publication_ready false."
        ),
    }


def main() -> int:
    args = parse_args()
    try:
        result = prepare(args, project_root())
    except (ContextError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

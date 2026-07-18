#!/usr/bin/env python3
"""Prepare read-only, paginated context for GCONF news discovery."""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import math
import re
import sqlite3
from collections import Counter
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


LANES = (
    "official_release",
    "protagonist",
    "gconf_case",
    "audience_reaction",
    "ecosystem_posts",
    "semantic_context",
)
DEFAULT_LOCAL_WINDOW_DAYS = 30
MAX_LOCAL_WINDOW_DAYS = 60


class ContextError(RuntimeError):
    """Raised when the local evidence packet cannot be prepared safely."""


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clip(value: Any, limit: int = 600) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def freshness(value: Any, now: datetime) -> dict[str, Any]:
    if not value:
        return {"freshness_days": None, "freshness_band": "unknown"}
    try:
        observed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        try:
            observed = datetime.strptime(str(value), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return {"freshness_days": None, "freshness_band": "unknown"}
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=timezone.utc)
    days = max(0, (now - observed.astimezone(timezone.utc)).days)
    if days <= 14:
        band = "live"
    elif days <= 45:
        band = "fresh"
    elif days <= 90:
        band = "recent"
    else:
        band = "historical"
    return {"freshness_days": days, "freshness_band": band}


def readonly_connection(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise ContextError(f"Knowledge database is missing: {path}")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def load_lane_config(root: Path) -> dict[str, Any]:
    path = root / ".agents/skills/gconf-news-radar/references/source-lanes.json"
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise ContextError(f"Invalid source-lane registry: {path}") from exc
    required = {"protagonists", "gconf_owned_coverage", "gconf_internal_discovery"}
    if required - set(config):
        raise ContextError("Source-lane registry is missing required keys")
    return config


def protagonist_registry(config: dict[str, Any]) -> tuple[set[str], dict[str, str]]:
    source_ids: set[str] = set()
    actor_by_source: dict[str, str] = {}
    for actor_id, values in config.get("protagonists", {}).items():
        for source_id in values:
            if source_id in actor_by_source:
                raise ContextError(f"Protagonist source is assigned twice: {source_id}")
            source_ids.add(source_id)
            actor_by_source[source_id] = actor_id
    return source_ids, actor_by_source


def load_card_helper(root: Path):
    helper_path = root / ".agents/skills/gconf-announcement-analysis/scripts/prepare_context.py"
    if not helper_path.exists():
        raise ContextError(f"Semantic-card helper is missing: {helper_path}")
    spec = importlib.util.spec_from_file_location("gconf_announcement_context", helper_path)
    if not spec or not spec.loader:
        raise ContextError(f"Cannot load semantic-card helper: {helper_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collect_cards(root: Path, now: datetime) -> list[dict[str, Any]]:
    helper = load_card_helper(root)
    cards = []
    for card in helper.collect_cards(root, now):
        evidence = []
        for item in card.get("evidence_quotes", [])[:6]:
            evidence.append(
                {
                    "locator": item.get("locator"),
                    "role": item.get("role"),
                    "author": item.get("author"),
                    "source_date": item.get("source_date"),
                    "visibility": item.get("visibility"),
                    "supports": item.get("supports"),
                    "source_url": item.get("source_url"),
                    "local_source": item.get("local_source"),
                    "exact_quote": clip(item.get("exact_quote"), 320),
                }
            )
        cards.append(
            {
                "id": card.get("id"),
                "type": card.get("type"),
                "label": card.get("label"),
                "status": card.get("status"),
                "review_status": card.get("review_status"),
                "source_wave": card.get("source_wave"),
                "first_seen": card.get("first_seen"),
                "last_seen": card.get("last_seen"),
                "freshness": freshness(card.get("last_seen"), now),
                "abstract": clip(card.get("abstract"), 450),
                "path": card.get("path"),
                "evidence": evidence,
            }
        )
    cards.sort(
        key=lambda item: (
            item.get("review_status") != "approved",
            item.get("freshness", {}).get("freshness_days")
            if isinstance(item.get("freshness", {}).get("freshness_days"), int)
            else 10**9,
            str(item.get("id")),
        )
    )
    return cards


def latest_announcement(root: Path) -> dict[str, Any]:
    base = root / "research/announcement_drafts/runs"
    for run in sorted((path for path in base.glob("*") if path.is_dir()), reverse=True):
        carousel = run / "instagram-carousel-v3.md"
        manifest_path = run / "manifest.json"
        if not carousel.exists() or not manifest_path.exists():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ContextError(f"Invalid announcement manifest: {manifest_path}") from exc
        files = {}
        for name in ("brief.md", "telegram.md", "instagram-carousel-v3.md", "audit.md"):
            path = run / name
            if path.exists():
                files[name] = clip(path.read_text(encoding="utf-8"), 6000)
        return {"run": run.relative_to(root).as_posix(), "manifest": manifest, "files": files}
    raise ContextError("No announcement run containing instagram-carousel-v3.md was found")


def iso_cutoff(now: datetime, days: int) -> str:
    return (now - timedelta(days=days)).date().isoformat()


def meaningful_text(value: Any) -> tuple[bool, str | None]:
    text = str(value or "").strip()
    if not text:
        return False, "empty"
    if not re.search(r"[\w\d]", text, flags=re.UNICODE):
        return False, "emoji_or_punctuation_only"
    return True, None


def document_rows(
    connection: sqlite3.Connection,
    since: str,
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT d.id, d.source_id, d.platform, d.kind, d.title, d.author,
               d.published_at, d.url, d.locator, d.body, d.source_path,
               d.visibility, d.metadata_json, d.checksum,
               s.name AS source_name, s.source_type
        FROM documents d JOIN sources s ON s.id = d.source_id
        WHERE d.published_at >= ?
        """,
        (since,),
    ).fetchall()
    return [dict(row) for row in rows]


def chunk_rows(connection: sqlite3.Connection, since: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT c.id, d.source_id, d.platform, 'youtube_transcript_chunk' AS kind,
               d.title, d.author, d.published_at, d.url, c.locator, c.body,
               d.source_path, d.visibility, c.metadata_json, c.checksum,
               s.name AS source_name, s.source_type, d.locator AS parent_locator,
               c.start_seconds, c.end_seconds
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        JOIN sources s ON s.id = d.source_id
        WHERE d.published_at >= ?
        """,
        (since,),
    ).fetchall()
    return [dict(row) for row in rows]


def parent_indexes(
    connection: sqlite3.Connection,
) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    edges = {
        row["source_locator"]: row["target_locator"]
        for row in connection.execute(
            "SELECT source_locator, target_locator FROM edges WHERE relation = 'replies_to'"
        ).fetchall()
    }
    documents = {
        row["locator"]: dict(row)
        for row in connection.execute(
            "SELECT locator, kind, title, author, published_at, url, body FROM documents"
        ).fetchall()
    }
    return edges, documents


def root_parent(
    locator: str,
    edges: dict[str, str],
    documents: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    current = locator
    visited: set[str] = set()
    for _ in range(6):
        target = edges.get(current)
        if not target or target in visited:
            return None
        current = target
        visited.add(current)
        parent = documents.get(current)
        if parent and parent["kind"] not in {"youtube_comment", "instagram_comment"}:
            return {
                "locator": parent["locator"],
                "kind": parent["kind"],
                "title": parent["title"],
                "author": parent["author"],
                "published_at": parent["published_at"],
                "url": parent["url"],
                "excerpt": clip(parent["body"], 500),
            }
    return None


def card_item(card: dict[str, Any]) -> dict[str, Any]:
    visibilities = {item.get("visibility") for item in card.get("evidence", []) if item.get("visibility")}
    visibility = "internal" if visibilities == {"internal"} else "public"
    return {
        "record_type": "semantic_card",
        "source_id": "knowledge:semantic",
        "platform": "knowledge",
        "kind": card.get("type"),
        "title": card.get("label"),
        "author": None,
        "published_at": card.get("last_seen"),
        "url": None,
        "locator": f"knowledge:{card.get('id')}",
        "excerpt": card.get("abstract"),
        "local_source": card.get("path"),
        "visibility": visibility,
        "permission_status": "required" if visibility == "internal" else "not_required",
        "metadata": {
            "status": card.get("status"),
            "review_status": card.get("review_status"),
            "source_wave": card.get("source_wave"),
            "evidence": card.get("evidence"),
        },
        "checksum": hashlib.sha256(json.dumps(card, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
    }


def normalize_item(row: dict[str, Any], actor_by_source: dict[str, str]) -> dict[str, Any]:
    try:
        metadata = json.loads(row.get("metadata_json") or "{}")
    except json.JSONDecodeError:
        metadata = {}
    internal = row.get("visibility") == "internal"
    item = {
        "record_type": "transcript_chunk" if row.get("kind") == "youtube_transcript_chunk" else "document",
        "source_id": row.get("source_id"),
        "source_name": row.get("source_name"),
        "source_type": row.get("source_type"),
        "platform": row.get("platform"),
        "kind": row.get("kind"),
        "title": row.get("title") or clip(row.get("body"), 140),
        "author": row.get("author"),
        "published_at": row.get("published_at"),
        "url": row.get("url"),
        "locator": row.get("locator"),
        "excerpt": clip(row.get("body"), 700),
        "local_source": row.get("source_path"),
        "visibility": row.get("visibility"),
        "permission_status": "required" if internal else "not_required",
        "protagonist_id": actor_by_source.get(str(row.get("source_id"))),
        "metadata": metadata,
        "checksum": row.get("checksum"),
    }
    if row.get("parent_locator"):
        item["parent_locator"] = row.get("parent_locator")
    if row.get("start_seconds") is not None:
        item["start_seconds"] = row.get("start_seconds")
        item["end_seconds"] = row.get("end_seconds")
    return item


def lane_items(
    connection: sqlite3.Connection,
    root: Path,
    config: dict[str, Any],
    cards: list[dict[str, Any]],
    lane: str,
    now: datetime,
    window_days: int,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    if lane not in LANES:
        raise ContextError(f"Unknown lane: {lane}")
    since = iso_cutoff(now, window_days)
    protagonist_ids, actor_by_source = protagonist_registry(config)
    internal_ids = set(config.get("gconf_internal_discovery", []))
    rows = document_rows(connection, since)
    chunks = chunk_rows(connection, since)
    selected: list[dict[str, Any]] = []

    if lane == "official_release":
        selected = [normalize_item(row, actor_by_source) for row in rows if row["kind"] == "official_lab_article"]
    elif lane == "protagonist":
        allowed_kinds = {"telegram_message", "instagram_post", "youtube_video"}
        selected = [
            normalize_item(row, actor_by_source)
            for row in rows
            if row["source_id"] in protagonist_ids and row["kind"] in allowed_kinds
        ]
        selected.extend(
            normalize_item(row, actor_by_source) for row in chunks if row["source_id"] in protagonist_ids
        )
    elif lane == "gconf_case":
        selected = [
            normalize_item(row, actor_by_source)
            for row in rows
            if row["source_id"] in internal_ids and row["kind"] == "telegram_message"
        ]
        selected.extend(
            card_item(card)
            for card in cards
            if card.get("type") == "case"
            and isinstance(card.get("freshness", {}).get("freshness_days"), int)
            and card["freshness"]["freshness_days"] <= window_days
        )
    elif lane == "audience_reaction":
        comment_kinds = {"youtube_comment", "instagram_comment"}
        selected = [normalize_item(row, actor_by_source) for row in rows if row["kind"] in comment_kinds]
        edges, documents = parent_indexes(connection)
        for item in selected:
            parent = root_parent(str(item["locator"]), edges, documents)
            if parent:
                item["parent_locator"] = parent["locator"]
                item["parent_context"] = parent
    elif lane == "ecosystem_posts":
        public_kinds = {"telegram_message", "instagram_post", "youtube_video"}
        selected = [
            normalize_item(row, actor_by_source)
            for row in rows
            if row["visibility"] == "public"
            and row["kind"] in public_kinds
            and row["source_id"] not in protagonist_ids
        ]
        selected.extend(
            normalize_item(row, actor_by_source) for row in chunks if row["source_id"] not in protagonist_ids
        )
    else:
        selected = [
            card_item(card)
            for card in cards
            if isinstance(card.get("freshness", {}).get("freshness_days"), int)
            and card["freshness"]["freshness_days"] <= window_days
        ]

    noise: Counter[str] = Counter()
    meaningful: list[dict[str, Any]] = []
    for item in selected:
        ok, reason = meaningful_text(item.get("excerpt") or item.get("title"))
        if not ok:
            noise[reason or "technical_noise"] += 1
            continue
        meaningful.append(item)
    meaningful.sort(key=lambda item: str(item.get("locator", "")))
    meaningful.sort(key=lambda item: str(item.get("published_at") or ""), reverse=True)
    return meaningful, noise


def items_fingerprint(items: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for item in items:
        digest.update(
            json.dumps(
                [item.get("record_type"), item.get("locator"), item.get("checksum")],
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode()
        )
    return digest.hexdigest()


def encode_cursor(offset: int, fingerprint: str) -> str:
    raw = json.dumps({"offset": offset, "fingerprint": fingerprint}, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(value: str) -> dict[str, Any]:
    try:
        padded = value + "=" * (-len(value) % 4)
        result = json.loads(base64.urlsafe_b64decode(padded).decode())
    except (ValueError, json.JSONDecodeError) as exc:
        raise ContextError("Invalid cursor") from exc
    if not isinstance(result.get("offset"), int) or not result.get("fingerprint"):
        raise ContextError("Invalid cursor payload")
    return result


def lane_summary(
    connection: sqlite3.Connection,
    root: Path,
    config: dict[str, Any],
    cards: list[dict[str, Any]],
    lane: str,
    now: datetime,
    window_days: int,
    page_size: int,
) -> dict[str, Any]:
    items, noise = lane_items(connection, root, config, cards, lane, now, window_days)
    dates = [str(item["published_at"]) for item in items if item.get("published_at")]
    return {
        "window_days": window_days,
        "available_items": len(items) + sum(noise.values()),
        "meaningful_items": len(items),
        "noise_excluded": sum(noise.values()),
        "noise_reasons": dict(sorted(noise.items())),
        "pages_expected": math.ceil(len(items) / page_size),
        "pages_reviewed": 0,
        "complete": False,
        "freshest_published_at": max(dates) if dates else None,
        "oldest_published_at": min(dates) if dates else None,
        "fingerprint": items_fingerprint(items),
        "signals_found": 0,
        "passing_candidates": 0,
    }


def lane_page(
    connection: sqlite3.Connection,
    root: Path,
    config: dict[str, Any],
    cards: list[dict[str, Any]],
    lane: str,
    now: datetime,
    window_days: int,
    page_size: int,
    cursor: str | None,
    expansion_reason: str | None,
) -> dict[str, Any]:
    items, noise = lane_items(connection, root, config, cards, lane, now, window_days)
    fingerprint = items_fingerprint(items)
    offset = 0
    if cursor:
        decoded = decode_cursor(cursor)
        if decoded["fingerprint"] != fingerprint:
            raise ContextError("Cursor snapshot no longer matches the local corpus")
        offset = decoded["offset"]
    page = items[offset : offset + page_size]
    next_offset = offset + len(page)
    return {
        "schema_version": "1.1",
        "prepared_at": now.isoformat(),
        "read_only": True,
        "lane": lane,
        "window_days": window_days,
        "window_expansion_reason": expansion_reason,
        "snapshot_fingerprint": fingerprint,
        "total_meaningful_items": len(items),
        "noise_excluded": sum(noise.values()),
        "noise_reasons": dict(sorted(noise.items())),
        "page_size": page_size,
        "offset": offset,
        "items": page,
        "next_cursor": encode_cursor(next_offset, fingerprint) if next_offset < len(items) else None,
        "complete": next_offset >= len(items),
    }


def published_coverage(connection: sqlite3.Connection, source_ids: list[str], limit: int) -> list[dict[str, Any]]:
    placeholders = ",".join("?" for _ in source_ids)
    rows = connection.execute(
        f"""
        SELECT d.id, d.external_id, d.platform, d.published_at, d.locator, d.url,
               d.title, d.body, d.metadata_json, s.name AS source_name
        FROM documents d JOIN sources s ON s.id = d.source_id
        WHERE d.source_id IN ({placeholders})
          AND d.kind IN ('telegram_message', 'instagram_post')
          AND trim(d.body) != ''
        ORDER BY d.published_at DESC LIMIT ?
        """,
        (*source_ids, limit),
    ).fetchall()
    result = []
    for row in rows:
        try:
            metadata = json.loads(row["metadata_json"] or "{}")
        except json.JSONDecodeError:
            metadata = {}
        result.append(
            {
                "id": row["id"],
                "external_id": row["external_id"],
                "platform": row["platform"],
                "source_name": row["source_name"],
                "published_at": row["published_at"],
                "locator": row["locator"],
                "url": row["url"],
                "title": row["title"] or clip(row["body"], 140),
                "excerpt": clip(row["body"]),
                "reactions": metadata.get("reactions", metadata.get("metrics", {})),
            }
        )
    return result


def safe_fts_query(value: str) -> str:
    tokens = re.findall(r"[\w-]+", value, flags=re.UNICODE)
    if not tokens:
        raise ContextError(f"Coverage query has no searchable tokens: {value!r}")
    return " OR ".join(f'"{token.replace(chr(34), "")}"' for token in tokens[:12])


def coverage_matches(
    connection: sqlite3.Connection,
    query: str,
    limit: int = 8,
    source_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    source_ids = source_ids or load_lane_config(project_root())["gconf_owned_coverage"]
    placeholders = ",".join("?" for _ in source_ids)
    rows = connection.execute(
        f"""
        SELECT d.id, d.external_id, d.platform, d.published_at, d.locator, d.url,
               d.title, d.body, s.name AS source_name, bm25(documents_fts) AS rank
        FROM documents_fts
        JOIN documents d ON d.id = documents_fts.document_id
        JOIN sources s ON s.id = d.source_id
        WHERE documents_fts MATCH ? AND d.source_id IN ({placeholders})
          AND d.kind IN ('telegram_message', 'instagram_post')
        ORDER BY rank, d.published_at DESC LIMIT ?
        """,
        (safe_fts_query(query), *source_ids, limit),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "external_id": row["external_id"],
            "platform": row["platform"],
            "source_name": row["source_name"],
            "published_at": row["published_at"],
            "locator": row["locator"],
            "url": row["url"],
            "title": row["title"] or clip(row["body"], 140),
            "excerpt": clip(row["body"]),
            "rank": row["rank"],
        }
        for row in rows
    ]


def previous_runs(root: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for run_type, base in (
        ("radar", root / "research/news_analysis/runs"),
        ("writer", root / "research/news_drafts/runs"),
    ):
        for path in sorted(base.glob("*/manifest.json"), reverse=True)[:50]:
            try:
                manifest = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            item = {
                "run_type": run_type,
                "run": path.parent.relative_to(root).as_posix(),
                "generated_at": manifest.get("generated_at"),
                "candidate_topics": [
                    {
                        "topic_id": candidate.get("topic_id"),
                        "working_title": candidate.get("working_title"),
                        "focus": candidate.get("focus"),
                        "coverage_delta": candidate.get("coverage_delta"),
                        "status": candidate.get("status"),
                    }
                    for candidate in manifest.get("candidates", [])
                ],
                "selected_topic_ids": manifest.get("selected_topic_ids", []),
            }
            if run_type == "writer":
                item["posts"] = [
                    {"file": news_path.name, "excerpt": clip(news_path.read_text(encoding="utf-8"))}
                    for news_path in sorted(path.parent.glob("news-*.md"))
                ]
            result.append(item)
    return result


def source_snapshot(connection: sqlite3.Connection, root: Path, config: dict[str, Any]) -> dict[str, Any]:
    rows = connection.execute(
        """
        SELECT s.id, s.name, s.platform, s.source_type, s.visibility,
               count(d.id) AS document_count, min(d.published_at) AS first,
               max(d.published_at) AS last
        FROM sources s LEFT JOIN documents d ON d.source_id = s.id
        GROUP BY s.id ORDER BY s.platform, s.name
        """
    ).fetchall()
    database = root / "knowledge/_index/gconf.sqlite"
    required = [root / "AGENTS.md", root / "editorial/gconf-tone-of-voice.md", database]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise ContextError(f"Required local inputs are missing: {missing}")
    protagonist_ids, _ = protagonist_registry(config)
    known_ids = protagonist_ids | set(config["gconf_owned_coverage"]) | set(config["gconf_internal_discovery"])
    return {
        "database": {
            "path": database.relative_to(root).as_posix(),
            "sha256": sha256(database),
            "bytes": database.stat().st_size,
        },
        "sources": [dict(row) for row in rows],
        "unassigned_sources": [
            row["id"]
            for row in rows
            if row["id"] not in known_ids and row["source_type"] == "youtube_channel"
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window-days", type=int, default=14, help="Live-web discovery window")
    parser.add_argument("--local-window-days", type=int, default=DEFAULT_LOCAL_WINDOW_DAYS)
    parser.add_argument("--local-max-days", type=int, default=MAX_LOCAL_WINDOW_DAYS)
    parser.add_argument("--use-extended-window", action="store_true")
    parser.add_argument("--window-expansion-reason")
    parser.add_argument("--max-candidates", type=int, default=10)
    parser.add_argument("--coverage-limit", type=int, default=100)
    parser.add_argument("--coverage-query", action="append", default=[])
    parser.add_argument("--lane", choices=LANES)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--cursor")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if not 1 <= args.window_days <= 45:
        raise ContextError("--window-days must be between 1 and 45")
    if not 1 <= args.local_window_days <= args.local_max_days <= MAX_LOCAL_WINDOW_DAYS:
        raise ContextError("Local windows must satisfy 1 <= primary <= maximum <= 60")
    if not 1 <= args.max_candidates <= 10:
        raise ContextError("--max-candidates must be between 1 and 10")
    if not 1 <= args.coverage_limit <= 500:
        raise ContextError("--coverage-limit must be between 1 and 500")
    if not 1 <= args.page_size <= 200:
        raise ContextError("--page-size must be between 1 and 200")
    if args.use_extended_window and not str(args.window_expansion_reason or "").strip():
        raise ContextError("The extended local window requires --window-expansion-reason")
    if args.cursor and not args.lane:
        raise ContextError("--cursor requires --lane")


def prepare(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    validate_args(args)
    now = datetime.now(timezone.utc)
    config = load_lane_config(root)
    cards = collect_cards(root, now)
    database = root / "knowledge/_index/gconf.sqlite"
    window_days = args.local_max_days if args.use_extended_window else args.local_window_days
    with closing(readonly_connection(database)) as connection:
        if args.lane:
            return lane_page(
                connection,
                root,
                config,
                cards,
                args.lane,
                now,
                window_days,
                args.page_size,
                args.cursor,
                args.window_expansion_reason,
            )
        source_review = {
            lane: lane_summary(
                connection, root, config, cards, lane, now, args.local_window_days, args.page_size
            )
            for lane in LANES
        }
        for lane in LANES:
            extended, extended_noise = lane_items(
                connection, root, config, cards, lane, now, args.local_max_days
            )
            source_review[lane]["extended_meaningful_items"] = len(extended)
            source_review[lane]["extended_available_items"] = len(extended) + sum(
                extended_noise.values()
            )
        queries = {
            query: coverage_matches(connection, query, source_ids=config["gconf_owned_coverage"])
            for query in args.coverage_query
        }
        snapshot = source_snapshot(connection, root, config)
        published = published_coverage(connection, config["gconf_owned_coverage"], args.coverage_limit)
    semantic_cards = [
        card
        for card in cards
        if isinstance(card.get("freshness", {}).get("freshness_days"), int)
        and card["freshness"]["freshness_days"] <= args.local_max_days
    ]
    return {
        "schema_version": "1.1",
        "prepared_at": now.isoformat(),
        "read_only": True,
        "parameters": {
            "default_window_days": args.window_days,
            "expanded_window_days": 45,
            "local_window_days": args.local_window_days,
            "local_max_days": args.local_max_days,
            "max_candidates": args.max_candidates,
            "minimum_score": 65,
            "reserved_lanes": ["protagonist", "gconf_case", "audience_reaction"],
            "page_size": args.page_size,
        },
        "source_snapshot": snapshot,
        "source_review": source_review,
        "source_lane_registry": config,
        "announcement_v3_baseline": latest_announcement(root),
        "semantic_cards": semantic_cards,
        "semantic_card_type_counts": dict(sorted(Counter(card.get("type") for card in semantic_cards).items())),
        "published_gconf_coverage": published,
        "previous_news_runs": previous_runs(root),
        "coverage_query_results": queries,
        "live_research_requirements": {
            "product_release": "one official primary source minimum",
            "broad_trend": "two independent publishers minimum",
            "publisher_benchmarks": "label as publisher claims",
            "comments": "audience reaction only; never product proof",
            "internal": "discovery only until public corroboration or permission",
            "unindexed_live_source": "record as unindexed_observation and queue only",
        },
    }


def main() -> int:
    args = parse_args()
    try:
        packet = prepare(args, project_root())
    except (ContextError, sqlite3.Error) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

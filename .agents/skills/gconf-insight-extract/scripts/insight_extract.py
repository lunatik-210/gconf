#!/usr/bin/env python3
"""Prepare, fingerprint, and validate GCONF semantic extraction batches."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[4]
KNOWLEDGE_ROOT = PROJECT_ROOT / "knowledge"
DB_PATH = KNOWLEDGE_ROOT / "_index" / "gconf.sqlite"
PROCESSING_ROOT = KNOWLEDGE_ROOT / "processing"
RUNS_ROOT = KNOWLEDGE_ROOT / "runs" / "insight-extract"
REVIEW_VIEW = KNOWLEDGE_ROOT / "views" / "Review Inbox.base"

SEMANTIC_FOLDERS = {
    "actor": "actors",
    "lab": "labs",
    "cohort": "cohorts",
    "pain": "pains",
    "case": "cases",
    "trend": "trends",
    "technology": "technologies",
    "claim": "claims",
}
ALLOWED_STATUSES = {"fact", "inference", "proposal"}
ALLOWED_REVIEW_STATUSES = {"candidate", "approved", "rejected", "superseded"}
ALLOWED_SOURCE_WAVES = {"internal", "external", "mixed"}
ALLOWED_EVENT_PHASES = {"before", "during", "after", "unknown"}
ALLOWED_ATTRIBUTIONS = {"explicit", "inferred_by_time", "unattributed"}
ALLOWED_EVIDENCE_ROLES = {"primary", "corroborating", "context", "counterevidence"}
ALLOWED_CASE_ORIGINS = {
    "gconf_participant",
    "gconf_community",
    "gconf_protagonist",
    "external",
}
ALLOWED_REPORTING_MODES = {
    "direct_self_report",
    "organizer_report",
    "protagonist_report",
    "third_party_report",
}
ALLOWED_PROOF_LEVELS = {
    "claim_only",
    "described_result",
    "working_artifact",
    "linked_artifact",
    "independently_verified",
}
ALLOWED_ARTIFACT_STATUSES = {"idea", "prototype", "working", "deployed", "unknown"}
ALLOWED_TECHNOLOGY_LIFECYCLES = {
    "announced",
    "available",
    "mature",
    "deprecated",
    "retired",
    "unknown",
}
EVIDENCE_START = "<!-- evidence:start -->"
EVIDENCE_END = "<!-- evidence:end -->"
MAX_UNIT_RECORDS = 100
MAX_UNIT_CHARS = 80_000
MAX_EVIDENCE_QUOTE_CHARS = 1200


def now_utc() -> str:
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        handle.write(text)
        temporary = handle.name
    os.replace(temporary, path)


def atomic_json(path: Path, payload: Any) -> None:
    atomic_write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def project_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def normalize_published_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if re.fullmatch(r"\d{8}", text):
        try:
            return dt.datetime.strptime(text, "%Y%m%d").date().isoformat()
        except ValueError:
            return None
    if re.match(r"^\d{4}-\d{2}-\d{2}", text):
        try:
            return dt.date.fromisoformat(text[:10]).isoformat()
        except ValueError:
            return None
    return None


def parse_scalar(value: str) -> Any:
    text = value.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        if text in {"null", "~"}:
            return None
        if text.lower() in {"true", "false"}:
            return text.lower() == "true"
        return text.strip('"\'')


def parse_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"missing YAML frontmatter: {project_relative(path)}")
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError(f"unterminated YAML frontmatter: {project_relative(path)}") from exc
    source = lines[1:end]
    data: dict[str, Any] = {}
    index = 0
    while index < len(source):
        raw = source[index]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or raw[:1].isspace() or ":" not in raw:
            index += 1
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            data[key] = parse_scalar(value)
            index += 1
            continue
        values: list[Any] = []
        index += 1
        while index < len(source):
            item_raw = source[index]
            if item_raw and not item_raw[:1].isspace():
                break
            item_stripped = item_raw.strip()
            if not item_stripped or item_stripped.startswith("#"):
                index += 1
                continue
            if not item_raw.startswith("  -"):
                index += 1
                continue
            item_text = item_stripped[1:].strip()
            if not re.match(r"^[^:]+:(?:\s|$)", item_text):
                values.append(parse_scalar(item_text))
                index += 1
                continue
            item: dict[str, Any] = {}
            item_key, item_value = item_text.split(":", 1)
            item[item_key.strip()] = parse_scalar(item_value)
            index += 1
            while index < len(source):
                field_raw = source[index]
                if field_raw.startswith("  -") or (field_raw and not field_raw[:1].isspace()):
                    break
                field_stripped = field_raw.strip()
                if not field_stripped or field_stripped.startswith("#"):
                    index += 1
                    continue
                if not field_raw.startswith("    ") or ":" not in field_stripped:
                    index += 1
                    continue
                field_key, field_value = field_stripped.split(":", 1)
                field_value = field_value.strip()
                if field_value in {"|", "|-", ">", ">-"}:
                    index += 1
                    block: list[str] = []
                    while index < len(source):
                        block_raw = source[index]
                        if block_raw.startswith("      ") or not block_raw.strip():
                            block.append(block_raw[6:] if block_raw.startswith("      ") else "")
                            index += 1
                            continue
                        break
                    item[field_key.strip()] = "\n".join(block).rstrip("\n")
                else:
                    item[field_key.strip()] = parse_scalar(field_value)
                    index += 1
            values.append(item)
        data[key] = values
    return data


def connect() -> sqlite3.Connection:
    if not DB_PATH.is_file():
        raise RuntimeError(f"missing database: {project_relative(DB_PATH)}; run knowledge ingest")
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def scope_path(scope: str) -> Path:
    candidate = Path(scope).expanduser()
    if candidate.is_file():
        return candidate.resolve()
    if not candidate.is_absolute():
        project_candidate = PROJECT_ROOT / candidate
        if project_candidate.is_file():
            return project_candidate.resolve()
    return PROCESSING_ROOT / scope / "scope.json"


def load_scope(scope: str) -> tuple[Path, dict[str, Any]]:
    path = scope_path(scope)
    if not path.is_file():
        raise RuntimeError(f"missing scope: {project_relative(path)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {"schema_version", "id", "profile_version", "event_ids", "batches"}
    missing = sorted(required - set(payload))
    if missing or not isinstance(payload.get("batches"), list):
        raise RuntimeError(f"invalid scope {project_relative(path)}; missing {missing}")
    batch_ids = [item.get("id") for item in payload["batches"] if isinstance(item, dict)]
    if len(batch_ids) != len(set(batch_ids)) or any(not value for value in batch_ids):
        raise RuntimeError(f"scope has missing or duplicate batch IDs: {project_relative(path)}")
    event_ids = payload.get("event_ids")
    if not isinstance(event_ids, list) or len(event_ids) != len(set(event_ids)):
        raise RuntimeError(f"scope has missing or duplicate event IDs: {project_relative(path)}")
    return path, payload


def get_batch(scope: dict[str, Any], batch_id: str) -> dict[str, Any]:
    for batch in scope["batches"]:
        if batch.get("id") == batch_id:
            return batch
    raise RuntimeError(f"unknown batch {batch_id!r} in scope {scope['id']!r}")


def date_in_window(value: Any, start: str, end: str) -> bool:
    normalized = normalize_published_date(value)
    return bool(normalized and start <= normalized <= end)


def _query_documents(
    connection: sqlite3.Connection, source_ids: list[str], kinds: list[str]
) -> list[sqlite3.Row]:
    clauses: list[str] = []
    parameters: list[str] = []
    if source_ids:
        clauses.append("d.source_id IN (" + ",".join("?" for _ in source_ids) + ")")
        parameters.extend(source_ids)
    if kinds:
        clauses.append("d.kind IN (" + ",".join("?" for _ in kinds) + ")")
        parameters.extend(kinds)
    if not clauses:
        raise RuntimeError("a selector must include source_ids or kinds")
    return connection.execute(
        f"""
        SELECT d.*, s.name AS source_name, s.visibility AS source_visibility
        FROM documents d JOIN sources s ON s.id = d.source_id
        WHERE {' AND '.join(clauses)}
        ORDER BY d.published_at, d.locator
        """,
        parameters,
    ).fetchall()


def telegram_relation_context(
    connection: sqlite3.Connection, source_ids: list[str]
) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    if not source_ids:
        return {}, {}
    rows = connection.execute(
        f"SELECT * FROM documents WHERE source_id IN ({','.join('?' for _ in source_ids)})",
        source_ids,
    ).fetchall()
    documents = {str(row["locator"]): dict(row) for row in rows}
    locators = set(documents)
    parents = {
        str(row["source_locator"]): str(row["target_locator"])
        for row in connection.execute("SELECT source_locator, target_locator FROM edges WHERE relation = 'replies_to'")
        if str(row["source_locator"]) in locators
    }
    roots: dict[str, str] = {}
    for locator in locators:
        current = locator
        visited: set[str] = set()
        while current in parents and current not in visited:
            visited.add(current)
            current = parents[current]
        roots[locator] = current
    return parents, {locator: {**item, "thread_root_locator": roots[locator]} for locator, item in documents.items()}


def selector_topic_locators(selector: dict[str, Any], source_ids: list[str], key: str) -> set[str]:
    values = {str(value) for value in selector.get(key) or []}
    result = {value for value in values if value.startswith("telegram:")}
    numeric = values - result
    for source_id in source_ids:
        if source_id.startswith("telegram:chat:"):
            chat_id = source_id.rsplit(":", 1)[-1]
            result.update(f"telegram:{chat_id}:{value}" for value in numeric)
    return result


def select_batch_records(
    connection: sqlite3.Connection, batch: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selectors = batch.get("selectors")
    if not isinstance(selectors, list) or not selectors:
        raise RuntimeError(f"batch {batch.get('id')} has no selectors")
    documents: dict[str, dict[str, Any]] = {}
    chunk_document_ids: set[str] = set()
    for selector in selectors:
        source_ids = [str(value) for value in selector.get("source_ids") or []]
        kinds = [str(value) for value in selector.get("kinds") or []]
        start = str(selector.get("window_start") or batch.get("window_start") or "")
        end = str(selector.get("window_end") or batch.get("window_end") or "")
        if not start or not end:
            raise RuntimeError(f"batch {batch.get('id')} selector has no date window")
        parents, telegram_documents = telegram_relation_context(connection, source_ids)
        include_topics = selector_topic_locators(selector, source_ids, "topic_root_ids")
        exclude_topics = selector_topic_locators(selector, source_ids, "exclude_topic_root_ids")
        for row in _query_documents(connection, source_ids, kinds):
            if not date_in_window(row["published_at"], start, end):
                continue
            item = dict(row)
            relation = telegram_documents.get(str(item["locator"]))
            if relation:
                thread_root = str(relation["thread_root_locator"])
                if include_topics and thread_root not in include_topics:
                    continue
                if exclude_topics and thread_root in exclude_topics:
                    continue
                item["thread_root_locator"] = thread_root
                root = telegram_documents.get(thread_root)
                if root:
                    item["thread_title"] = root.get("title") or root.get("body")
                parent_locator = parents.get(str(item["locator"]))
                if parent_locator:
                    item["reply_to_locator"] = parent_locator
                    parent = telegram_documents.get(parent_locator)
                    if parent:
                        item["reply_context"] = {
                            "locator": parent_locator,
                            "author": parent.get("author"),
                            "published_at": parent.get("published_at"),
                            "body": str(parent.get("body") or "")[:2000],
                        }
            item["record_type"] = "document"
            item["published_date"] = normalize_published_date(row["published_at"])
            if item.get("kind") == "youtube_video" and selector.get("include_chunks"):
                item["body"] = str(item.get("body") or "")[:6000]
                item["body_truncated_for_chunks"] = True
                chunk_document_ids.add(str(item["id"]))
            documents[str(item["locator"])] = item
    chunks: dict[str, dict[str, Any]] = {}
    if chunk_document_ids:
        ids = sorted(chunk_document_ids)
        rows = connection.execute(
            f"""
            SELECT c.*, d.title, d.author, d.published_at, d.source_id,
                   s.name AS source_name, s.visibility AS source_visibility
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            JOIN sources s ON s.id = d.source_id
            WHERE c.document_id IN ({','.join('?' for _ in ids)})
            ORDER BY c.document_id, c.ordinal
            """,
            ids,
        ).fetchall()
        for row in rows:
            item = dict(row)
            item["record_type"] = "chunk"
            item["published_date"] = normalize_published_date(row["published_at"])
            chunks[str(item["locator"])] = item
    return (
        sorted(documents.values(), key=lambda item: (item.get("published_date") or "", item["locator"])),
        sorted(chunks.values(), key=lambda item: (item.get("published_date") or "", item["locator"])),
    )


def input_fingerprint(documents: Iterable[dict[str, Any]], chunks: Iterable[dict[str, Any]]) -> str:
    lines = [f"{item['locator']}\0{item['checksum']}" for item in [*documents, *chunks]]
    return hashlib.sha256("\n".join(sorted(lines)).encode("utf-8")).hexdigest()


def _record_for_work_unit(item: dict[str, Any]) -> dict[str, Any]:
    keep = {
        "record_type",
        "locator",
        "kind",
        "title",
        "author",
        "published_at",
        "published_date",
        "source_id",
        "source_name",
        "source_visibility",
        "start_seconds",
        "end_seconds",
        "body",
        "body_truncated_for_chunks",
        "thread_root_locator",
        "thread_title",
        "reply_to_locator",
        "reply_context",
    }
    return {key: item.get(key) for key in keep if item.get(key) is not None}


def split_large_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    body = str(record.get("body") or "")
    if len(body) <= MAX_UNIT_CHARS:
        return [record]
    parts: list[dict[str, Any]] = []
    for index, start in enumerate(range(0, len(body), MAX_UNIT_CHARS), 1):
        part = dict(record)
        part["body"] = body[start : start + MAX_UNIT_CHARS]
        part["work_part"] = index
        part["evidence_locator"] = record["locator"]
        parts.append(part)
    return parts


def pack_work_units(
    records: list[dict[str, Any]], group_by_thread: bool = False
) -> list[list[dict[str, Any]]]:
    if group_by_thread:
        groups: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            key = str(record.get("thread_root_locator") or record.get("locator") or "unknown")
            groups.setdefault(key, []).append(record)
        units: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        current_chars = 0
        for key in sorted(groups):
            thread_units = pack_work_units(groups[key], group_by_thread=False)
            for thread_unit in thread_units:
                thread_chars = sum(len(canonical_json(record)) for record in thread_unit)
                if current and (
                    len(current) + len(thread_unit) > MAX_UNIT_RECORDS
                    or current_chars + thread_chars > MAX_UNIT_CHARS
                ):
                    units.append(current)
                    current = []
                    current_chars = 0
                current.extend(thread_unit)
                current_chars += thread_chars
        if current:
            units.append(current)
        return units
    units: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_chars = 0
    expanded: list[dict[str, Any]] = []
    for item in records:
        expanded.extend(split_large_record(_record_for_work_unit(item)))
    for record in expanded:
        size = len(canonical_json(record))
        if current and (len(current) >= MAX_UNIT_RECORDS or current_chars + size > MAX_UNIT_CHARS):
            units.append(current)
            current = []
            current_chars = 0
        current.append(record)
        current_chars += size
    if current:
        units.append(current)
    return units


def processing_card_path(scope_id: str, batch_id: str) -> Path:
    return PROCESSING_ROOT / scope_id / f"{batch_id}.md"


def batch_status(connection: sqlite3.Connection, scope: dict[str, Any], batch: dict[str, Any]) -> dict[str, Any]:
    documents, chunks = select_batch_records(connection, batch)
    fingerprint = input_fingerprint(documents, chunks)
    path = processing_card_path(str(scope["id"]), str(batch["id"]))
    stored: dict[str, Any] = {}
    state = "pending"
    if path.is_file():
        stored = parse_frontmatter(path)
        state = (
            "complete"
            if stored.get("processing_status") == "complete"
            and stored.get("input_fingerprint") == fingerprint
            and stored.get("profile_version") == scope.get("profile_version")
            else "stale"
        )
    return {
        "id": batch["id"],
        "label": batch.get("label"),
        "state": state,
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "fingerprint": fingerprint,
        "stored_fingerprint": stored.get("input_fingerprint"),
        "profile_version": scope.get("profile_version"),
        "stored_profile_version": stored.get("profile_version"),
        "processing_card": project_relative(path),
    }


def status_report(scope_name: str) -> dict[str, Any]:
    path, scope = load_scope(scope_name)
    connection = connect()
    try:
        batches = [batch_status(connection, scope, batch) for batch in scope["batches"]]
    finally:
        connection.close()
    counts = {state: sum(item["state"] == state for item in batches) for state in ("pending", "complete", "stale")}
    return {
        "ok": True,
        "scope": scope["id"],
        "scope_path": project_relative(path),
        "counts": counts,
        "batches": batches,
    }


def prepare_report(scope_name: str, batch_id: str) -> dict[str, Any]:
    _, scope = load_scope(scope_name)
    batch = get_batch(scope, batch_id)
    connection = connect()
    try:
        documents, chunks = select_batch_records(connection, batch)
    finally:
        connection.close()
    fingerprint = input_fingerprint(documents, chunks)
    units = pack_work_units(
        [*documents, *chunks], group_by_thread=bool(batch.get("group_by_thread"))
    )
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = RUNS_ROOT / f"{run_id}-{scope['id']}-{batch_id}"
    unit_paths: list[str] = []
    for index, records in enumerate(units, 1):
        path = run_dir / f"unit-{index:03d}.json"
        atomic_json(
            path,
            {
                "schema_version": "1.0",
                "scope_id": scope["id"],
                "batch_id": batch_id,
                "unit": index,
                "unit_count": len(units),
                "records": records,
            },
        )
        unit_paths.append(project_relative(path))
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "prepared_at": now_utc(),
        "scope_id": scope["id"],
        "batch_id": batch_id,
        "profile_version": scope["profile_version"],
        "input_fingerprint": fingerprint,
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "work_unit_count": len(units),
        "work_units": unit_paths,
    }
    manifest_path = run_dir / "manifest.json"
    atomic_json(manifest_path, manifest)
    return {"ok": True, **manifest, "manifest": project_relative(manifest_path)}


def semantic_card_index() -> dict[str, tuple[Path, dict[str, Any]]]:
    cards: dict[str, tuple[Path, dict[str, Any]]] = {}
    for folder in SEMANTIC_FOLDERS.values():
        root = KNOWLEDGE_ROOT / folder
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.md")):
            data = parse_frontmatter(path)
            card_id = data.get("id")
            if isinstance(card_id, str):
                if card_id in cards:
                    raise ValueError(f"duplicate semantic card id: {card_id}")
                cards[card_id] = (path, data)
    return cards


def locator_set(connection: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in connection.execute("SELECT locator FROM documents UNION SELECT locator FROM chunks")
    }


def evidence_record_map(connection: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for row in connection.execute(
        """
        SELECT d.locator, d.kind, d.title, d.author, d.published_at, d.url,
               d.body, d.source_path, d.visibility, d.source_id,
               s.name AS source_name, s.url AS source_url
        FROM documents d JOIN sources s ON s.id = d.source_id
        """
    ):
        item = dict(row)
        item["record_type"] = "document"
        item["published_date"] = normalize_published_date(item.get("published_at"))
        records[str(item["locator"])] = item
    for row in connection.execute(
        """
        SELECT c.locator, c.body, c.start_seconds, c.end_seconds,
               d.kind, d.title, d.author, d.published_at, d.url,
               d.source_path, d.visibility, d.source_id,
               s.name AS source_name, s.url AS source_url
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        JOIN sources s ON s.id = d.source_id
        """
    ):
        item = dict(row)
        item["record_type"] = "chunk"
        item["published_date"] = normalize_published_date(item.get("published_at"))
        records[str(item["locator"])] = item
    return records


def normalized_quote(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def evidence_source_link(locator: str, record: dict[str, Any]) -> str | None:
    if record.get("url"):
        url = str(record["url"])
        if record.get("record_type") == "chunk" and record.get("start_seconds") is not None:
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}t={int(float(record['start_seconds']))}s"
        if ":comment:" in locator and "youtube.com/watch" in url:
            return f"{url}&lc={locator.split(':comment:', 1)[1]}"
        return url
    if locator.startswith("youtube:"):
        video_id = locator.split(":", 2)[1]
        base = f"https://www.youtube.com/watch?v={video_id}"
        if ":comment:" in locator:
            return f"{base}&lc={locator.split(':comment:', 1)[1]}"
        if record.get("start_seconds") is not None:
            return f"{base}&t={int(float(record['start_seconds']))}s"
        return base
    return None


def validate_semantic_card(
    path: Path,
    data: dict[str, Any],
    records: dict[str, dict[str, Any]] | set[str],
    allowed_event_ids: set[str] | None = None,
    require_rendered: bool = True,
) -> list[str]:
    errors: list[str] = []
    record_map = records if isinstance(records, dict) else {locator: {} for locator in records}
    required = {
        "type",
        "id",
        "label",
        "status",
        "review_status",
        "first_seen",
        "last_seen",
        "source_wave",
        "evidence",
        "evidence_quotes",
        "related",
        "event_context",
    }
    missing = sorted(required - set(data))
    if missing:
        errors.append(f"{project_relative(path)} missing fields: {', '.join(missing)}")
        return errors
    card_type = data.get("type")
    expected_folder = SEMANTIC_FOLDERS.get(str(card_type))
    if expected_folder is None:
        errors.append(f"{project_relative(path)} invalid type: {card_type}")
    elif path.parent.name != expected_folder:
        errors.append(f"{project_relative(path)} must be in knowledge/{expected_folder}")
    if data.get("status") not in ALLOWED_STATUSES:
        errors.append(f"{project_relative(path)} invalid status")
    if data.get("review_status") not in ALLOWED_REVIEW_STATUSES:
        errors.append(f"{project_relative(path)} invalid review_status")
    if data.get("source_wave") not in ALLOWED_SOURCE_WAVES:
        errors.append(f"{project_relative(path)} invalid source_wave")
    evidence = data.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{project_relative(path)} evidence must be a non-empty list")
    else:
        missing_locators = sorted(str(item) for item in evidence if str(item) not in record_map)
        if missing_locators:
            errors.append(
                f"{project_relative(path)} unresolved evidence: {', '.join(missing_locators)}"
            )
    evidence_quotes = data.get("evidence_quotes")
    quote_locators: set[str] = set()
    if not isinstance(evidence_quotes, list) or not evidence_quotes:
        errors.append(f"{project_relative(path)} evidence_quotes must be a non-empty list")
    else:
        for item in evidence_quotes:
            if not isinstance(item, dict):
                errors.append(f"{project_relative(path)} invalid evidence quote item")
                continue
            locator = str(item.get("locator") or "")
            quote = str(item.get("quote") or "")
            quote_locators.add(locator)
            if locator not in set(map(str, evidence or [])):
                errors.append(f"{project_relative(path)} quote locator is not in evidence: {locator}")
            if item.get("role") not in ALLOWED_EVIDENCE_ROLES:
                errors.append(f"{project_relative(path)} invalid evidence role: {locator}")
            if not str(item.get("supports") or "").strip():
                errors.append(f"{project_relative(path)} evidence quote missing supports: {locator}")
            if not quote.strip() or len(quote) > MAX_EVIDENCE_QUOTE_CHARS:
                errors.append(f"{project_relative(path)} invalid evidence quote length: {locator}")
            record = record_map.get(locator)
            if record and normalized_quote(quote) not in normalized_quote(record.get("body")):
                errors.append(f"{project_relative(path)} quote not found in evidence: {locator}")
        uncovered = sorted(set(map(str, evidence or [])) - quote_locators)
        if uncovered:
            errors.append(f"{project_relative(path)} evidence without quotes: {', '.join(uncovered)}")
    dated = [
        record_map[str(locator)].get("published_date")
        for locator in evidence or []
        if str(locator) in record_map and record_map[str(locator)].get("published_date")
    ]
    if dated:
        if data.get("first_seen") != min(dated):
            errors.append(f"{project_relative(path)} first_seen does not match evidence dates")
        if data.get("last_seen") != max(dated):
            errors.append(f"{project_relative(path)} last_seen does not match evidence dates")
    related = data.get("related")
    if not isinstance(related, list):
        errors.append(f"{project_relative(path)} related must be a list")
    context = data.get("event_context")
    if not isinstance(context, list):
        errors.append(f"{project_relative(path)} event_context must be a list")
    else:
        for item in context:
            if not isinstance(item, dict):
                errors.append(f"{project_relative(path)} invalid event_context item")
                continue
            if item.get("phase") not in ALLOWED_EVENT_PHASES:
                errors.append(f"{project_relative(path)} invalid event phase")
            if item.get("attribution") not in ALLOWED_ATTRIBUTIONS:
                errors.append(f"{project_relative(path)} invalid event attribution")
            if not item.get("event_id"):
                errors.append(f"{project_relative(path)} event context missing event_id")
            elif allowed_event_ids is not None and item.get("event_id") not in allowed_event_ids:
                errors.append(f"{project_relative(path)} event is outside configured scope")
    if data.get("review_status") == "candidate" and path.stem != data.get("id"):
        errors.append(f"{project_relative(path)} candidate filename must equal card id")
    if card_type == "case":
        if data.get("case_origin") not in ALLOWED_CASE_ORIGINS:
            errors.append(f"{project_relative(path)} invalid case_origin")
        if data.get("reporting_mode") not in ALLOWED_REPORTING_MODES:
            errors.append(f"{project_relative(path)} invalid reporting_mode")
        if data.get("proof_level") not in ALLOWED_PROOF_LEVELS:
            errors.append(f"{project_relative(path)} invalid proof_level")
        if data.get("artifact_status") not in ALLOWED_ARTIFACT_STATUSES:
            errors.append(f"{project_relative(path)} invalid artifact_status")
    if card_type == "lab":
        if data.get("organization_type") != "ai_lab":
            errors.append(f"{project_relative(path)} lab organization_type must be ai_lab")
        domains = data.get("official_domains")
        if not isinstance(domains, list) or not domains:
            errors.append(f"{project_relative(path)} lab official_domains must be non-empty")
        source_ids = data.get("source_ids")
        if not isinstance(source_ids, list) or not source_ids:
            errors.append(f"{project_relative(path)} lab source_ids must be non-empty")
    if card_type == "technology" and data.get("lifecycle_status") is not None:
        if data.get("lifecycle_status") not in ALLOWED_TECHNOLOGY_LIFECYCLES:
            errors.append(f"{project_relative(path)} invalid technology lifecycle_status")
    if require_rendered:
        body = path.read_text(encoding="utf-8")
        if EVIDENCE_START not in body or EVIDENCE_END not in body:
            errors.append(f"{project_relative(path)} missing rendered Evidence block")
    return errors


def card_write_action(existing: dict[str, Any] | None) -> str:
    if not existing:
        return "create_candidate"
    if existing.get("review_status") == "approved":
        return "create_update_candidate"
    return "merge_candidate"


def latest_prepare_manifest(scope_id: str, batch_id: str) -> dict[str, Any] | None:
    matches: list[tuple[str, dict[str, Any]]] = []
    if not RUNS_ROOT.is_dir():
        return None
    for path in RUNS_ROOT.glob("*/manifest.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if payload.get("scope_id") == scope_id and payload.get("batch_id") == batch_id:
            matches.append((str(payload.get("prepared_at") or ""), payload))
    return max(matches, key=lambda item: item[0])[1] if matches else None


def yaml_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def render_evidence_block(data: dict[str, Any], records: dict[str, dict[str, Any]]) -> str:
    lines = [EVIDENCE_START, "## Evidence", ""]
    for index, item in enumerate(data.get("evidence_quotes") or [], 1):
        locator = str(item["locator"])
        record = records[locator]
        date = record.get("published_date") or "unknown date"
        source = record.get("source_name") or record.get("source_id") or "Unknown source"
        platform = locator.split(":", 1)[0].title()
        lines.extend(
            [
                f"### {index}. {source} · {platform} · {date}",
                "",
                f"- **Автор:** {record.get('author') or 'не указан'}",
                f"- **Роль:** `{item['role']}`",
                f"- **Подтверждает:** {item['supports']}",
                f"- **Visibility:** `{record.get('visibility') or 'unknown'}`",
                "",
            ]
        )
        lines.extend(f"> {line}" if line else ">" for line in str(item["quote"]).splitlines())
        lines.extend(["", f"- Locator: `{locator}`"])
        link = evidence_source_link(locator, record)
        if link:
            lines.append(f"- [Открыть источник]({link})")
        if record.get("source_path"):
            lines.append(f"- Local source: `{record['source_path']}`")
        lines.append("")
    lines.append(EVIDENCE_END)
    return "\n".join(lines)


def render_evidence_card(
    path: Path, data: dict[str, Any], records: dict[str, dict[str, Any]]
) -> None:
    block = render_evidence_block(data, records)
    text = path.read_text(encoding="utf-8")
    if EVIDENCE_START in text and EVIDENCE_END in text:
        start = text.index(EVIDENCE_START)
        end = text.index(EVIDENCE_END, start) + len(EVIDENCE_END)
        updated = text[:start].rstrip() + "\n\n" + block + text[end:].rstrip() + "\n"
    else:
        updated = text.rstrip() + "\n\n" + block + "\n"
    atomic_write(path, updated)


def render_evidence_report(card_ids: list[str]) -> dict[str, Any]:
    cards = semantic_card_index()
    targets = sorted(set(card_ids)) if card_ids else sorted(cards)
    connection = connect()
    try:
        records = evidence_record_map(connection)
    finally:
        connection.close()
    errors: list[str] = []
    rendered: list[str] = []
    for card_id in targets:
        if card_id not in cards:
            errors.append(f"missing semantic card: {card_id}")
            continue
        path, data = cards[card_id]
        card_errors = validate_semantic_card(path, data, records, require_rendered=False)
        if card_errors:
            errors.extend(card_errors)
            continue
        render_evidence_card(path, data, records)
        rendered.append(card_id)
    return {"ok": not errors, "errors": errors, "rendered": rendered}


def show_evidence_report(locator: str) -> dict[str, Any]:
    connection = connect()
    try:
        records = evidence_record_map(connection)
        record = records.get(locator)
        if not record:
            return {"ok": False, "error": f"unknown evidence locator: {locator}"}
        parent = connection.execute(
            "SELECT target_locator FROM edges WHERE source_locator = ? AND relation = 'replies_to'",
            (locator,),
        ).fetchone()
        parent_record = records.get(str(parent[0])) if parent else None
    finally:
        connection.close()
    return {
        "ok": True,
        "locator": locator,
        "source": record,
        "source_link": evidence_source_link(locator, record),
        "reply_parent": parent_record,
    }


def finalize_report(scope_name: str, batch_id: str, outputs: list[str]) -> dict[str, Any]:
    _, scope = load_scope(scope_name)
    batch = get_batch(scope, batch_id)
    prepared = latest_prepare_manifest(str(scope["id"]), batch_id)
    if not prepared:
        raise RuntimeError(f"batch {batch_id} has not been prepared")
    connection = connect()
    try:
        documents, chunks = select_batch_records(connection, batch)
        current_fingerprint = input_fingerprint(documents, chunks)
        records = evidence_record_map(connection)
    finally:
        connection.close()
    if prepared.get("input_fingerprint") != current_fingerprint:
        raise RuntimeError(f"batch {batch_id} changed after prepare; prepare it again")
    batch_locators = {
        str(item["locator"]) for item in [*documents, *chunks] if item.get("locator")
    }
    normalized_outputs: list[str] = []
    for value in outputs:
        normalized_outputs.extend(item for item in value.split(",") if item)
    normalized_outputs = sorted(set(normalized_outputs))
    cards = semantic_card_index()
    errors: list[str] = []
    for card_id in normalized_outputs:
        if card_id not in cards:
            errors.append(f"missing output card: {card_id}")
            continue
        path, data = cards[card_id]
        card_errors = validate_semantic_card(
            path,
            data,
            records,
            set(scope.get("event_ids") or []),
            require_rendered=False,
        )
        errors.extend(card_errors)
        evidence = data.get("evidence")
        if isinstance(evidence, list) and not batch_locators.intersection(map(str, evidence)):
            errors.append(f"output card has no evidence in batch {batch_id}: {card_id}")
    if errors:
        return {"ok": False, "errors": errors}
    for card_id in normalized_outputs:
        card_path, card_data = cards[card_id]
        render_evidence_card(card_path, card_data, records)
        errors.extend(
            validate_semantic_card(
                card_path,
                card_data,
                records,
                set(scope.get("event_ids") or []),
                require_rendered=True,
            )
        )
    if errors:
        return {"ok": False, "errors": errors}
    path = processing_card_path(str(scope["id"]), batch_id)
    window_start = str(batch.get("window_start") or "")
    window_end = str(batch.get("window_end") or "")
    frontmatter = {
        "type": "insight_processing",
        "scope_id": scope["id"],
        "batch_id": batch_id,
        "processing_status": "complete",
        "profile_version": scope["profile_version"],
        "window_start": window_start,
        "window_end": window_end,
        "input_fingerprint": current_fingerprint,
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "processed_at": now_utc(),
        "outputs": normalized_outputs,
    }
    lines = ["---", *(f"{key}: {yaml_value(value)}" for key, value in frontmatter.items()), "---", "", f"# {batch.get('label') or batch_id}", ""]
    if normalized_outputs:
        lines.extend(["## Outputs", "", *(f"- [[{card_id}]]" for card_id in normalized_outputs), ""])
    else:
        lines.extend(["Весь пакет просмотрен; переиспользуемых смысловых карточек не найдено.", ""])
    atomic_write(path, "\n".join(lines))
    return {
        "ok": True,
        "scope": scope["id"],
        "batch": batch_id,
        "fingerprint": current_fingerprint,
        "processing_card": project_relative(path),
        "outputs": normalized_outputs,
    }


def doctor_report() -> dict[str, Any]:
    scopes = sorted(PROCESSING_ROOT.glob("*/scope.json")) if PROCESSING_ROOT.is_dir() else []
    return {
        "ok": DB_PATH.is_file() and bool(scopes),
        "python": sys.version.split()[0],
        "sqlite": sqlite3.sqlite_version,
        "database": {"path": project_relative(DB_PATH), "exists": DB_PATH.is_file()},
        "scopes": [project_relative(path) for path in scopes],
        "network_required": False,
        "external_dependencies": [],
    }


def validate_report() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    loaded_scopes = [load_scope(str(path))[1] for path in sorted(PROCESSING_ROOT.glob("*/scope.json"))]
    allowed_event_ids = {
        str(event_id) for scope in loaded_scopes for event_id in scope.get("event_ids") or []
    }
    connection = connect()
    try:
        records = evidence_record_map(connection)
        cards = semantic_card_index()
        for path, data in cards.values():
            errors.extend(validate_semantic_card(path, data, records, allowed_event_ids))
    finally:
        connection.close()
    if REVIEW_VIEW.is_file():
        view_text = REVIEW_VIEW.read_text(encoding="utf-8")
        if "review_status" not in view_text or 'file.inFolder("_inbox")' in view_text:
            errors.append("Review Inbox view must select candidate cards across typed folders")
    else:
        errors.append(f"missing review view: {project_relative(REVIEW_VIEW)}")
    scope_reports: list[dict[str, Any]] = []
    for scope_file in sorted(PROCESSING_ROOT.glob("*/scope.json")):
        report = status_report(str(scope_file))
        scope_reports.append(report)
        warnings.extend(
            f"{report['scope']}:{item['id']} is {item['state']}"
            for item in report["batches"]
            if item["state"] != "complete"
        )
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "semantic_cards": len(cards),
        "scopes": scope_reports,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract traceable GCONF insight batches")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor")
    status_parser = commands.add_parser("status")
    status_parser.add_argument("--scope", required=True)
    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--scope", required=True)
    prepare_parser.add_argument("--batch", required=True)
    finalize_parser = commands.add_parser("finalize")
    finalize_parser.add_argument("--scope", required=True)
    finalize_parser.add_argument("--batch", required=True)
    finalize_parser.add_argument("--outputs", nargs="*", default=[])
    evidence_parser = commands.add_parser("show-evidence")
    evidence_parser.add_argument("locator")
    render_parser = commands.add_parser("render-evidence")
    render_parser.add_argument("--card", nargs="*", default=[])
    commands.add_parser("validate")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            report = doctor_report()
        elif args.command == "status":
            report = status_report(args.scope)
        elif args.command == "prepare":
            report = prepare_report(args.scope, args.batch)
        elif args.command == "finalize":
            report = finalize_report(args.scope, args.batch, args.outputs)
        elif args.command == "show-evidence":
            report = show_evidence_report(args.locator)
        elif args.command == "render-evidence":
            report = render_evidence_report(args.card)
        elif args.command == "validate":
            report = validate_report()
        else:
            return 1
    except (RuntimeError, ValueError, OSError, sqlite3.Error, json.JSONDecodeError) as exc:
        report = {"ok": False, "error": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

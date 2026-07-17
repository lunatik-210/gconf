#!/usr/bin/env python3
"""Build a local SQLite and Obsidian index from collected GCONF artifacts."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
import unicodedata
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[4]
KNOWLEDGE_ROOT = PROJECT_ROOT / "knowledge"
DB_PATH = KNOWLEDGE_ROOT / "_index" / "gconf.sqlite"
RUNS_ROOT = KNOWLEDGE_ROOT / "runs"
SOURCE_CARDS_ROOT = KNOWLEDGE_ROOT / "sources"
SCHEMA_VERSION = "1.0"

SOURCE_ROOTS = {
    "youtube": PROJECT_ROOT / "YouTube",
    "telegram": PROJECT_ROOT / "telegram",
    "instagram": PROJECT_ROOT / "Instagram",
    "research": PROJECT_ROOT / "research",
    "web_articles": PROJECT_ROOT / "Web Articles",
}


@dataclass
class Counters:
    sources_inserted: int = 0
    sources_updated: int = 0
    sources_unchanged: int = 0
    documents_inserted: int = 0
    documents_updated: int = 0
    documents_unchanged: int = 0
    chunks_written: int = 0
    edges_written: int = 0
    files_processed: int = 0
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            key: value
            for key, value in vars(self).items()
        }


def now_utc() -> str:
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


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
    return text


def project_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def checksum_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def checksum_value(value: Any) -> str:
    return checksum_text(canonical_json(value))


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        handle.write(text)
        temp_name = handle.name
    os.replace(temp_name, path)


def atomic_json(path: Path, payload: Any) -> None:
    atomic_write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        return ""
    parts: list[str] = []
    for item in value:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict):
            text = str(item.get("text") or "")
            href = item.get("href")
            parts.append(f"{text} [{href}]" if href else text)
    return "".join(parts)


def slugify(value: str, limit: int = 100) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    if not slug:
        slug = checksum_text(value)[:12]
    return slug[:limit].rstrip("-")


def yaml_string(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def ensure_knowledge_layout() -> None:
    for relative in (
        "_inbox",
        "_index",
        "actors",
        "labs",
        "cohorts",
        "pains",
        "cases",
        "trends",
        "technologies",
        "claims",
        "sources",
        "views",
        "runs",
    ):
        (KNOWLEDGE_ROOT / relative).mkdir(parents=True, exist_ok=True)

    home = KNOWLEDGE_ROOT / "GCONF Knowledge.md"
    if not home.exists():
        atomic_write(
            home,
            "# GCONF Knowledge\n\n"
            "Локальная база источников, доказательств и проверяемых смысловых карточек.\n\n"
            "- [[views/Sources.base|Sources]]\n"
            "- [[views/Review Inbox.base|Review Inbox]]\n"
            "- [[views/Semantic Knowledge.base|Semantic Knowledge]]\n\n"
            "Сырые Telegram, Instagram, YouTube и Web Articles остаются вне vault и не "
            "изменяются importer-ом.\n",
        )
    inbox = KNOWLEDGE_ROOT / "_inbox" / "Inbox Guide.md"
    if not inbox.exists():
        atomic_write(
            inbox,
            "---\n"
            "type: guide\n"
            "generated: true\n"
            "---\n\n"
            "# Review inbox\n\n"
            "AI-кандидаты на лаборатории, технологии, боли, кейсы, тренды и claims появляются здесь. "
            "Переносить их в typed folders можно только после человеческой проверки.\n",
        )
    bases = {
        "Sources.base": (
            'filters:\n  and:\n    - file.inFolder("sources")\n'
            "views:\n  - type: table\n    name: Sources\n"
            "    order:\n      - file.name\n      - platform\n      - visibility\n"
            "      - document_count\n"
        ),
        "Review Inbox.base": (
            'filters:\n  and:\n    - file.inFolder("_inbox")\n'
            "views:\n  - type: table\n    name: Review Inbox\n"
            "    order:\n      - file.name\n      - type\n      - status\n"
            "      - review_status\n"
        ),
        "Semantic Knowledge.base": (
            "filters:\n  and:\n"
            '    - \'list("actor", "lab", "cohort", "pain", "case", "trend", "technology", "claim").contains(type)\'\n'
            "views:\n  - type: table\n    name: Semantic Knowledge\n"
            "    order:\n      - file.name\n      - type\n      - status\n"
            "      - review_status\n      - first_seen\n      - last_seen\n"
        ),
    }
    for name, content in bases.items():
        path = KNOWLEDGE_ROOT / "views" / name
        if not path.exists():
            atomic_write(path, content)


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    visibility TEXT NOT NULL,
    path TEXT,
    url TEXT,
    collected_at TEXT,
    metadata_json TEXT NOT NULL,
    checksum TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(id),
    platform TEXT NOT NULL,
    external_id TEXT,
    kind TEXT NOT NULL,
    title TEXT,
    author TEXT,
    published_at TEXT,
    url TEXT,
    locator TEXT NOT NULL UNIQUE,
    body TEXT NOT NULL,
    source_path TEXT,
    visibility TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    checksum TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS documents_source_idx ON documents(source_id);
CREATE INDEX IF NOT EXISTS documents_published_idx ON documents(published_at);
CREATE INDEX IF NOT EXISTS documents_kind_idx ON documents(kind);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    locator TEXT NOT NULL UNIQUE,
    start_seconds REAL,
    end_seconds REAL,
    body TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    checksum TEXT NOT NULL,
    UNIQUE(document_id, ordinal)
);

CREATE INDEX IF NOT EXISTS chunks_document_idx ON chunks(document_id);

CREATE TABLE IF NOT EXISTS edges (
    id TEXT PRIMARY KEY,
    source_locator TEXT NOT NULL,
    target_locator TEXT NOT NULL,
    relation TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    UNIQUE(source_locator, target_locator, relation)
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    command TEXT NOT NULL,
    status TEXT NOT NULL,
    report_json TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    document_id UNINDEXED,
    locator UNINDEXED,
    title,
    body,
    author,
    tokenize = 'unicode61'
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    chunk_id UNINDEXED,
    document_id UNINDEXED,
    locator UNINDEXED,
    body,
    tokenize = 'unicode61'
);
"""


def connect() -> sqlite3.Connection:
    ensure_knowledge_layout()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA_SQL)
    return connection


def upsert_source(
    connection: sqlite3.Connection,
    counters: Counters,
    *,
    source_id: str,
    platform: str,
    name: str,
    source_type: str,
    visibility: str,
    path: str | None,
    url: str | None,
    collected_at: str | None,
    metadata: dict[str, Any],
) -> None:
    payload_checksum = checksum_value(
        {
            "platform": platform,
            "name": name,
            "source_type": source_type,
            "visibility": visibility,
            "path": path,
            "url": url,
            "collected_at": collected_at,
            "metadata": metadata,
        }
    )
    row = connection.execute(
        "SELECT checksum FROM sources WHERE id = ?", (source_id,)
    ).fetchone()
    if row is None:
        counters.sources_inserted += 1
    elif row["checksum"] == payload_checksum:
        counters.sources_unchanged += 1
        return
    else:
        counters.sources_updated += 1
    connection.execute(
        """
        INSERT INTO sources (
            id, platform, name, source_type, visibility, path, url,
            collected_at, metadata_json, checksum, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            platform=excluded.platform,
            name=excluded.name,
            source_type=excluded.source_type,
            visibility=excluded.visibility,
            path=excluded.path,
            url=excluded.url,
            collected_at=excluded.collected_at,
            metadata_json=excluded.metadata_json,
            checksum=excluded.checksum,
            updated_at=excluded.updated_at
        """,
        (
            source_id,
            platform,
            name,
            source_type,
            visibility,
            path,
            url,
            collected_at,
            canonical_json(metadata),
            payload_checksum,
            now_utc(),
        ),
    )


def upsert_document(
    connection: sqlite3.Connection,
    counters: Counters,
    *,
    document_id: str,
    source_id: str,
    platform: str,
    external_id: str | None,
    kind: str,
    title: str | None,
    author: str | None,
    published_at: str | None,
    url: str | None,
    locator: str,
    body: str,
    source_path: str | None,
    visibility: str,
    metadata: dict[str, Any],
    chunks: list[dict[str, Any]] | None = None,
) -> None:
    payload_checksum = checksum_value(
        {
            "source_id": source_id,
            "kind": kind,
            "title": title,
            "author": author,
            "published_at": published_at,
            "url": url,
            "locator": locator,
            "body": body,
            "visibility": visibility,
            "metadata": metadata,
            "chunks": chunks or [],
        }
    )
    row = connection.execute(
        "SELECT checksum FROM documents WHERE id = ?", (document_id,)
    ).fetchone()
    if row is None:
        counters.documents_inserted += 1
    elif row["checksum"] == payload_checksum:
        counters.documents_unchanged += 1
        return
    else:
        counters.documents_updated += 1
    connection.execute(
        """
        INSERT INTO documents (
            id, source_id, platform, external_id, kind, title, author,
            published_at, url, locator, body, source_path, visibility,
            metadata_json, checksum, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            source_id=excluded.source_id,
            platform=excluded.platform,
            external_id=excluded.external_id,
            kind=excluded.kind,
            title=excluded.title,
            author=excluded.author,
            published_at=excluded.published_at,
            url=excluded.url,
            locator=excluded.locator,
            body=excluded.body,
            source_path=excluded.source_path,
            visibility=excluded.visibility,
            metadata_json=excluded.metadata_json,
            checksum=excluded.checksum,
            updated_at=excluded.updated_at
        """,
        (
            document_id,
            source_id,
            platform,
            external_id,
            kind,
            title,
            author,
            published_at,
            url,
            locator,
            body,
            source_path,
            visibility,
            canonical_json(metadata),
            payload_checksum,
            now_utc(),
        ),
    )
    connection.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
    for ordinal, chunk in enumerate(chunks or []):
        chunk_locator = str(chunk["locator"])
        chunk_body = str(chunk.get("body") or "")
        chunk_id = f"chunk:{checksum_text(chunk_locator)[:24]}"
        chunk_metadata = chunk.get("metadata") or {}
        connection.execute(
            """
            INSERT INTO chunks (
                id, document_id, ordinal, locator, start_seconds, end_seconds,
                body, metadata_json, checksum
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chunk_id,
                document_id,
                ordinal,
                chunk_locator,
                chunk.get("start_seconds"),
                chunk.get("end_seconds"),
                chunk_body,
                canonical_json(chunk_metadata),
                checksum_value(chunk),
            ),
        )
        counters.chunks_written += 1


def upsert_edge(
    connection: sqlite3.Connection,
    counters: Counters,
    source_locator: str,
    target_locator: str,
    relation: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    edge_id = "edge:" + checksum_text(
        f"{source_locator}\0{target_locator}\0{relation}"
    )[:24]
    cursor = connection.execute(
        """
        INSERT OR IGNORE INTO edges (
            id, source_locator, target_locator, relation, metadata_json
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            edge_id,
            source_locator,
            target_locator,
            relation,
            canonical_json(metadata or {}),
        ),
    )
    if cursor.rowcount:
        counters.edges_written += 1


def parse_srt_timestamp(value: str) -> float:
    match = re.fullmatch(r"(\d+):(\d+):(\d+),(\d+)", value.strip())
    if not match:
        return 0.0
    hours, minutes, seconds, millis = map(int, match.groups())
    return hours * 3600 + minutes * 60 + seconds + millis / 1000


def parse_srt(path: Path, video_id: str) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    blocks = re.split(r"\n\s*\n", text.strip())
    cues: list[dict[str, Any]] = []
    for block in blocks:
        lines = [line.strip("\ufeff") for line in block.splitlines() if line.strip()]
        timing_index = next((i for i, line in enumerate(lines) if " --> " in line), None)
        if timing_index is None:
            continue
        start_raw, end_raw = lines[timing_index].split(" --> ", 1)
        cue_text = " ".join(lines[timing_index + 1 :]).strip()
        cue_text = re.sub(r"<[^>]+>", "", cue_text)
        if not cue_text:
            continue
        cues.append(
            {
                "start": parse_srt_timestamp(start_raw.split()[0]),
                "end": parse_srt_timestamp(end_raw.split()[0]),
                "body": cue_text,
            }
        )
    chunks: list[dict[str, Any]] = []
    buffer: list[dict[str, Any]] = []
    size = 0
    for cue in cues:
        buffer.append(cue)
        size += len(cue["body"])
        if size >= 1000 or len(buffer) >= 12:
            start = buffer[0]["start"]
            end = buffer[-1]["end"]
            chunks.append(
                {
                    "locator": f"youtube:{video_id}:{int(start)}-{int(end)}",
                    "start_seconds": start,
                    "end_seconds": end,
                    "body": " ".join(item["body"] for item in buffer),
                    "metadata": {"transcript_file": project_relative(path)},
                }
            )
            buffer = []
            size = 0
    if buffer:
        start = buffer[0]["start"]
        end = buffer[-1]["end"]
        chunks.append(
            {
                "locator": f"youtube:{video_id}:{int(start)}-{int(end)}",
                "start_seconds": start,
                "end_seconds": end,
                "body": " ".join(item["body"] for item in buffer),
                "metadata": {"transcript_file": project_relative(path)},
            }
        )
    return chunks


def youtube_channel_id(source: dict[str, Any]) -> str:
    raw = (
        source.get("channel_id")
        or source.get("uploader_id")
        or source.get("channel")
        or source.get("uploader")
        or "unknown"
    )
    return f"youtube:channel:{slugify(str(raw))}"


def ingest_youtube_video(
    connection: sqlite3.Connection,
    counters: Counters,
    stats_path: Path,
) -> None:
    stats = load_json(stats_path)
    if not isinstance(stats, dict) or stats.get("schema_version") != "2.0":
        counters.warnings.append(f"invalid YouTube stats: {project_relative(stats_path)}")
        return
    source = stats.get("source") or {}
    video_id = str(source.get("video_id") or "")
    if not video_id:
        counters.warnings.append(f"missing video id: {project_relative(stats_path)}")
        return
    source_id = youtube_channel_id(source)
    channel_name = str(source.get("channel") or source.get("uploader") or "Unknown YouTube")
    channel_metadata = {
        key: source.get(key)
        for key in (
            "channel",
            "channel_id",
            "channel_url",
            "uploader",
            "uploader_id",
            "uploader_url",
        )
        if source.get(key) is not None
    }
    upsert_source(
        connection,
        counters,
        source_id=source_id,
        platform="youtube",
        name=channel_name,
        source_type="youtube_channel",
        visibility="public",
        path=project_relative(stats_path.parent.parent),
        url=source.get("channel_url") or source.get("uploader_url"),
        collected_at=None,
        metadata=channel_metadata,
    )
    subtitles = stats.get("subtitles") or {}
    primary = subtitles.get("primary_transcript")
    transcript_path = (
        stats_path.parent / str(primary)[2:]
        if isinstance(primary, str) and primary.startswith("./")
        else None
    )
    chunks = (
        parse_srt(transcript_path, video_id)
        if transcript_path and transcript_path.is_file()
        else []
    )
    description_path = stats_path.parent / f"{video_id}.description"
    description = (
        description_path.read_text(encoding="utf-8", errors="replace")
        if description_path.is_file()
        else ""
    )
    transcript_body = " ".join(chunk["body"] for chunk in chunks)
    body = "\n\n".join(part for part in (description.strip(), transcript_body.strip()) if part)
    video_locator = f"youtube:{video_id}"
    upsert_document(
        connection,
        counters,
        document_id=f"youtube:video:{video_id}",
        source_id=source_id,
        platform="youtube",
        external_id=video_id,
        kind="youtube_video",
        title=source.get("title"),
        author=channel_name,
        published_at=normalize_published_date(source.get("upload_date")),
        url=source.get("url"),
        locator=video_locator,
        body=body,
        source_path=project_relative(stats_path),
        visibility="public",
        metadata={
            "statistics": stats.get("statistics") or {},
            "subtitles": subtitles,
            "limitations": stats.get("limitations") or [],
        },
        chunks=chunks,
    )
    comments_path = stats_path.parent / f"{video_id}.comments.json"
    comments_payload = load_json(comments_path, {})
    for comment in comments_payload.get("comments") or []:
        comment_id = str(comment.get("id") or "")
        if not comment_id:
            continue
        locator = f"youtube:{video_id}:comment:{comment_id}"
        published = comment.get("timestamp")
        if isinstance(published, (int, float)):
            published = dt.datetime.fromtimestamp(
                published, tz=dt.timezone.utc
            ).isoformat().replace("+00:00", "Z")
        upsert_document(
            connection,
            counters,
            document_id=f"youtube:comment:{video_id}:{comment_id}",
            source_id=source_id,
            platform="youtube",
            external_id=comment_id,
            kind="youtube_comment",
            title=None,
            author=comment.get("author"),
            published_at=published,
            url=None,
            locator=locator,
            body=str(comment.get("text") or ""),
            source_path=project_relative(comments_path),
            visibility="public",
            metadata={
                key: value
                for key, value in comment.items()
                if key not in {"text", "author_thumbnail"}
            },
        )
        parent = comment.get("parent")
        target = (
            video_locator
            if parent in (None, "root")
            else f"youtube:{video_id}:comment:{parent}"
        )
        upsert_edge(connection, counters, locator, target, "replies_to")
    counters.files_processed += 1


def ingest_youtube(
    connection: sqlite3.Connection,
    counters: Counters,
    path: Path,
) -> None:
    if path.is_file() and path.name.endswith(".stats.json"):
        ingest_youtube_video(connection, counters, path)
        return
    stats_paths = sorted(path.glob("**/*.stats.json")) if path.is_dir() else []
    for stats_path in stats_paths:
        ingest_youtube_video(connection, counters, stats_path)


def telegram_visibility(payload: dict[str, Any], path: Path) -> str:
    if payload.get("type") == "public_channel":
        return "public"
    if "сообщество" in path.name.lower() or "community" in path.name.lower():
        return "internal"
    return "internal"


TELEGRAM_PUBLIC_URLS = {
    "1633415027": "https://t.me/gptlovers",
    "1962191274": "https://t.me/matskevich",
    "1417132546": "https://t.me/aihappens",
}


def telegram_source_url(chat_id: str, visibility: str) -> str | None:
    if visibility == "internal":
        return f"https://t.me/c/{chat_id}"
    return TELEGRAM_PUBLIC_URLS.get(chat_id)


def telegram_message_url(chat_id: str, message_id: str, visibility: str) -> str | None:
    base = telegram_source_url(chat_id, visibility)
    return f"{base}/{message_id}" if base else None


def telegram_document_payload(message: dict[str, Any]) -> tuple[str, str] | None:
    if message.get("type") == "message":
        body = flatten_text(message.get("text"))
        if body.strip() or message.get("reply_to_message_id") is not None:
            return "telegram_message", body
        return None
    if message.get("action") == "topic_created" and str(message.get("title") or "").strip():
        return "telegram_topic", str(message["title"]).strip()
    return None


def ingest_telegram_file(
    connection: sqlite3.Connection,
    counters: Counters,
    path: Path,
) -> None:
    payload = load_json(path)
    if not isinstance(payload, dict) or not isinstance(payload.get("messages"), list):
        counters.warnings.append(f"invalid Telegram export: {project_relative(path)}")
        return
    chat_id = str(payload.get("id") or checksum_text(path.name)[:12])
    source_id = f"telegram:chat:{chat_id}"
    visibility = telegram_visibility(payload, path)
    source_url = telegram_source_url(chat_id, visibility)
    upsert_source(
        connection,
        counters,
        source_id=source_id,
        platform="telegram",
        name=str(payload.get("name") or path.stem),
        source_type=str(payload.get("type") or "telegram_chat"),
        visibility=visibility,
        path=project_relative(path),
        url=source_url,
        collected_at=None,
        metadata={"export_file": project_relative(path)},
    )
    for message in payload["messages"]:
        message_id = str(message.get("id") or "")
        if not message_id:
            continue
        normalized = telegram_document_payload(message)
        if normalized is None:
            continue
        kind, body = normalized
        locator = f"telegram:{chat_id}:{message_id}"
        upsert_document(
            connection,
            counters,
            document_id=f"telegram:message:{chat_id}:{message_id}",
            source_id=source_id,
            platform="telegram",
            external_id=message_id,
            kind=kind,
            title=message.get("title") if kind == "telegram_topic" else None,
            author=message.get("from") or message.get("actor"),
            published_at=message.get("date"),
            url=telegram_message_url(chat_id, message_id, visibility),
            locator=locator,
            body=body,
            source_path=project_relative(path),
            visibility=visibility,
            metadata={
                key: value
                for key, value in message.items()
                if key not in {"text", "text_entities"}
            },
        )
        reply_to = message.get("reply_to_message_id")
        if reply_to is not None:
            upsert_edge(
                connection,
                counters,
                locator,
                f"telegram:{chat_id}:{reply_to}",
                "replies_to",
            )
    counters.files_processed += 1


def ingest_telegram(
    connection: sqlite3.Connection,
    counters: Counters,
    path: Path,
) -> None:
    if path.is_file():
        paths = [path]
    else:
        candidates: dict[str, tuple[int, Path]] = {}
        invalid: list[Path] = []
        for item in sorted(path.glob("*.json")):
            payload = load_json(item)
            if not isinstance(payload, dict) or not isinstance(payload.get("messages"), list):
                invalid.append(item)
                continue
            chat_key = str(payload.get("id") or item.stem)
            size = len(payload["messages"])
            current = candidates.get(chat_key)
            if current is None or size > current[0]:
                candidates[chat_key] = (size, item)
        paths = [value[1] for value in sorted(candidates.values(), key=lambda value: value[1].name)]
        for item in invalid:
            counters.warnings.append(
                f"invalid Telegram export: {project_relative(item)}"
            )
    for item in paths:
        ingest_telegram_file(connection, counters, item)


def instagram_profile_key(payload: dict[str, Any], path: Path) -> str:
    profile = payload.get("profile") or {}
    return str(
        profile.get("username")
        or payload.get("profile_context")
        or path.stem
    )


def ingest_instagram_file(
    connection: sqlite3.Connection,
    counters: Counters,
    path: Path,
) -> None:
    payload = load_json(path)
    if (
        not isinstance(payload, dict)
        or not isinstance(payload.get("messages"), list)
        or not str(payload.get("schema_version") or "").startswith("1.")
    ):
        counters.warnings.append(f"invalid Instagram export: {project_relative(path)}")
        return
    profile_key = instagram_profile_key(payload, path)
    source_id = f"instagram:profile:{slugify(profile_key)}"
    upsert_source(
        connection,
        counters,
        source_id=source_id,
        platform="instagram",
        name=str(payload.get("name") or profile_key),
        source_type=str(payload.get("type") or "instagram_profile"),
        visibility="public",
        path=project_relative(path),
        url=payload.get("profile_url"),
        collected_at=payload.get("collected_at"),
        metadata={
            "profile": payload.get("profile") or {},
            "collection": payload.get("collection") or {},
        },
    )
    for post in payload["messages"]:
        post_id = str(post.get("id") or "")
        if not post_id:
            continue
        post_locator = f"instagram:{profile_key}:{post_id}"
        slides = ((post.get("media") or {}).get("slides") or [])
        slide_text = [
            str(slide.get("alt_text") or "").strip()
            for slide in slides
            if str(slide.get("alt_text") or "").strip()
        ]
        body = "\n\n".join(
            part
            for part in (
                str(post.get("caption") or "").strip(),
                "\n".join(slide_text),
            )
            if part
        )
        upsert_document(
            connection,
            counters,
            document_id=f"instagram:post:{profile_key}:{post_id}",
            source_id=source_id,
            platform="instagram",
            external_id=post_id,
            kind=str(post.get("type") or "instagram_post"),
            title=None,
            author=post.get("from"),
            published_at=post.get("date"),
            url=post.get("url"),
            locator=post_locator,
            body=body,
            source_path=project_relative(path),
            visibility="public",
            metadata={
                "media_type": post.get("media_type"),
                "metrics": post.get("metrics") or {},
                "coauthors": post.get("coauthors") or [],
                "collection": post.get("collection") or {},
            },
        )
        for comment in post.get("comments") or []:
            comment_id = str(comment.get("id") or "")
            if not comment_id:
                continue
            locator = (
                f"instagram:{profile_key}:{post_id}:comment:{comment_id}"
            )
            upsert_document(
                connection,
                counters,
                document_id=f"instagram:comment:{profile_key}:{post_id}:{comment_id}",
                source_id=source_id,
                platform="instagram",
                external_id=comment_id,
                kind="instagram_comment",
                title=None,
                author=comment.get("from"),
                published_at=comment.get("date"),
                url=comment.get("url"),
                locator=locator,
                body=str(comment.get("text") or ""),
                source_path=project_relative(path),
                visibility="public",
                metadata={
                    key: value
                    for key, value in comment.items()
                    if key not in {"text"}
                },
            )
            parent = comment.get("parent_comment_id")
            target = (
                f"instagram:{profile_key}:{post_id}:comment:{parent}"
                if parent
                else post_locator
            )
            upsert_edge(connection, counters, locator, target, "replies_to")
    counters.files_processed += 1


def ingest_instagram(
    connection: sqlite3.Connection,
    counters: Counters,
    path: Path,
) -> None:
    paths = [path] if path.is_file() else sorted(path.glob("*.json"))
    for item in paths:
        ingest_instagram_file(connection, counters, item)


def read_research_body(path: Path) -> str:
    if path.suffix.lower() == ".md":
        return path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".csv":
        rows: list[str] = []
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.reader(handle):
                rows.append(" | ".join(row))
        return "\n".join(rows)
    return ""


def ingest_research(
    connection: sqlite3.Connection,
    counters: Counters,
    path: Path,
) -> None:
    source_id = "research:local"
    upsert_source(
        connection,
        counters,
        source_id=source_id,
        platform="research",
        name="Local GCONF research",
        source_type="editorial_research",
        visibility="editorial",
        path=project_relative(SOURCE_ROOTS["research"]),
        url=None,
        collected_at=None,
        metadata={"epistemic_default": "inference"},
    )
    paths = (
        [path]
        if path.is_file()
        else sorted(
            item
            for item in path.glob("**/*")
            if item.is_file() and item.suffix.lower() in {".md", ".csv"}
        )
    )
    for item in paths:
        body = read_research_body(item)
        if not body.strip():
            continue
        relative = project_relative(item)
        locator = f"research:{relative}"
        upsert_document(
            connection,
            counters,
            document_id=f"research:document:{checksum_text(relative)[:24]}",
            source_id=source_id,
            platform="research",
            external_id=relative,
            kind="editorial_research",
            title=item.stem,
            author=None,
            published_at=dt.datetime.fromtimestamp(
                item.stat().st_mtime, tz=dt.timezone.utc
            ).isoformat().replace("+00:00", "Z"),
            url=None,
            locator=locator,
            body=body,
            source_path=relative,
            visibility="editorial",
            metadata={"epistemic_default": "inference"},
        )
        counters.files_processed += 1


WEB_REQUIRED_FIELDS = {
    "schema_version",
    "article_id",
    "title",
    "canonical_url",
    "collected_at",
    "language",
    "content_sha256",
    "extraction_status",
    "lab",
}


def load_web_article_package(metadata_path: Path) -> dict[str, Any]:
    metadata = load_json(metadata_path, {})
    if not isinstance(metadata, dict):
        raise ValueError(f"invalid web article metadata: {metadata_path}")
    missing = sorted(WEB_REQUIRED_FIELDS - set(metadata))
    if missing:
        raise ValueError(
            f"{project_relative(metadata_path)} missing fields: {', '.join(missing)}"
        )
    lab = metadata.get("lab")
    if not isinstance(lab, dict):
        raise ValueError(f"{project_relative(metadata_path)} lab must be an object")
    missing_lab = sorted({"id", "name", "official_domains"} - set(lab))
    if missing_lab:
        raise ValueError(
            f"{project_relative(metadata_path)} missing lab fields: {', '.join(missing_lab)}"
        )
    domains = lab.get("official_domains")
    if not isinstance(domains, list) or not domains:
        raise ValueError(
            f"{project_relative(metadata_path)} official_domains must be non-empty"
        )
    canonical_url = str(metadata.get("canonical_url") or "")
    parsed = urllib.parse.urlparse(canonical_url)
    allowed_domains = {str(item).lower() for item in domains}
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in allowed_domains:
        raise ValueError(
            f"{project_relative(metadata_path)} canonical URL is not on an official domain"
        )
    article_path = metadata_path.with_name("article.md")
    if not article_path.is_file():
        raise ValueError(f"missing web article body: {project_relative(article_path)}")
    body = article_path.read_text(encoding="utf-8", errors="replace")
    if not body.strip():
        raise ValueError(f"empty web article body: {project_relative(article_path)}")
    content_sha256 = checksum_text(body)
    if content_sha256 != str(metadata.get("content_sha256")):
        raise ValueError(
            f"{project_relative(metadata_path)} content_sha256 does not match article.md"
        )
    return {
        "metadata": metadata,
        "lab": lab,
        "body": body,
        "article_path": article_path,
        "content_sha256": content_sha256,
    }


def ingest_web_articles(
    connection: sqlite3.Connection,
    counters: Counters,
    path: Path,
) -> None:
    metadata_paths = (
        [path]
        if path.is_file() and path.name == "metadata.json"
        else sorted(path.glob("**/metadata.json"))
    )
    for metadata_path in metadata_paths:
        package = load_web_article_package(metadata_path)
        metadata = package["metadata"]
        lab = package["lab"]
        lab_id = str(lab["id"])
        source_id = f"web:lab:{lab_id}"
        upsert_source(
            connection,
            counters,
            source_id=source_id,
            platform="web",
            name=str(lab["name"]),
            source_type="official_ai_lab",
            visibility="public",
            path=project_relative(SOURCE_ROOTS["web_articles"] / str(lab["directory"])),
            url=str(lab.get("homepage") or metadata["canonical_url"]),
            collected_at=str(metadata["collected_at"]),
            metadata={
                "organization_type": "ai_lab",
                "official_domains": lab["official_domains"],
                "official_source": True,
            },
        )
        article_id = str(metadata["article_id"])
        digest = str(package["content_sha256"])
        locator = f"web:{lab_id}:{article_id}:{digest[:12]}"
        document_metadata = {
            key: value
            for key, value in metadata.items()
            if key not in {"lab", "content_sha256"}
        }
        document_metadata.update(
            {
                "lab_id": lab_id,
                "snapshot_checksum": digest,
                "official_domain_verified": True,
                "publisher_claims_require_corroboration": True,
            }
        )
        upsert_document(
            connection,
            counters,
            document_id=f"web:document:{lab_id}:{article_id}:{digest[:24]}",
            source_id=source_id,
            platform="web",
            external_id=f"{lab_id}:{article_id}",
            kind="official_lab_article",
            title=str(metadata["title"]),
            author=str(metadata.get("author") or lab["name"]),
            published_at=metadata.get("published_at") or metadata.get("first_seen_at"),
            url=str(metadata["canonical_url"]),
            locator=locator,
            body=str(package["body"]),
            source_path=project_relative(package["article_path"]),
            visibility="public",
            metadata=document_metadata,
        )
        counters.files_processed += 1


def detect_source(path: Path) -> str | None:
    try:
        relative = path.resolve().relative_to(PROJECT_ROOT.resolve())
        first = relative.parts[0].lower()
        if first == "youtube":
            return "youtube"
        if first == "telegram":
            return "telegram"
        if first == "instagram":
            return "instagram"
        if first == "research":
            return "research"
        if first == "web articles":
            return "web_articles"
    except ValueError:
        pass
    if path.is_file() and path.suffix.lower() == ".json":
        payload = load_json(path, {})
        if isinstance(payload, dict):
            if payload.get("schema_version") == "2.0" and "subtitles" in payload:
                return "youtube"
            if "profile" in payload and "messages" in payload:
                return "instagram"
            if {"id", "name", "messages"}.issubset(payload):
                return "telegram"
    if path.is_file() and path.name == "metadata.json":
        return "web_articles"
    if path.suffix.lower() in {".md", ".csv"}:
        return "research"
    return None


def ingest_source(
    connection: sqlite3.Connection,
    counters: Counters,
    source: str,
    path: Path,
) -> None:
    handlers = {
        "youtube": ingest_youtube,
        "telegram": ingest_telegram,
        "instagram": ingest_instagram,
        "research": ingest_research,
        "web_articles": ingest_web_articles,
    }
    handlers[source](connection, counters, path)


def rebuild_fts(connection: sqlite3.Connection) -> None:
    connection.execute("DELETE FROM documents_fts")
    connection.execute(
        """
        INSERT INTO documents_fts(document_id, locator, title, body, author)
        SELECT id, locator, COALESCE(title, ''), body, COALESCE(author, '')
        FROM documents
        """
    )
    connection.execute("DELETE FROM chunks_fts")
    connection.execute(
        """
        INSERT INTO chunks_fts(chunk_id, document_id, locator, body)
        SELECT id, document_id, locator, body FROM chunks
        """
    )


def source_card_text(row: sqlite3.Row, document_count: int) -> str:
    return (
        "---\n"
        "type: source\n"
        f"id: {yaml_string(row['id'])}\n"
        f"platform: {yaml_string(row['platform'])}\n"
        f"source_type: {yaml_string(row['source_type'])}\n"
        f"visibility: {yaml_string(row['visibility'])}\n"
        f"document_count: {document_count}\n"
        f"collected_at: {yaml_string(row['collected_at'])}\n"
        f"source_path: {yaml_string(row['path'])}\n"
        f"url: {yaml_string(row['url'])}\n"
        "generated: true\n"
        "---\n\n"
        f"# {row['name']}\n\n"
        f"- Platform: `{row['platform']}`\n"
        f"- Visibility: `{row['visibility']}`\n"
        f"- Documents indexed: **{document_count}**\n"
        f"- Local source: `{row['path'] or 'n/a'}`\n"
    )


def rebuild_source_cards(connection: sqlite3.Connection) -> None:
    SOURCE_CARDS_ROOT.mkdir(parents=True, exist_ok=True)
    expected: set[Path] = set()
    rows = connection.execute("SELECT * FROM sources ORDER BY platform, name").fetchall()
    for row in rows:
        count = connection.execute(
            "SELECT COUNT(*) FROM documents WHERE source_id = ?", (row["id"],)
        ).fetchone()[0]
        filename = f"{row['platform']}--{slugify(row['name'])}.md"
        path = SOURCE_CARDS_ROOT / filename
        expected.add(path.resolve())
        atomic_write(path, source_card_text(row, count))
    for path in SOURCE_CARDS_ROOT.glob("*.md"):
        if path.resolve() not in expected:
            path.unlink()


def database_summary(connection: sqlite3.Connection) -> dict[str, Any]:
    return {
        "sources": connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
        "documents": connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
        "chunks": connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0],
        "edges": connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0],
        "documents_fts": connection.execute(
            "SELECT COUNT(*) FROM documents_fts"
        ).fetchone()[0],
        "chunks_fts": connection.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0],
    }


def write_run_report(
    connection: sqlite3.Connection,
    run_id: str,
    started_at: str,
    command: str,
    status: str,
    report: dict[str, Any],
) -> Path:
    finished_at = now_utc()
    connection.execute(
        """
        INSERT OR REPLACE INTO ingestion_runs (
            id, started_at, finished_at, command, status, report_json
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            started_at,
            finished_at,
            command,
            status,
            canonical_json(report),
        ),
    )
    path = RUNS_ROOT / f"{run_id}.json"
    atomic_json(
        path,
        {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "started_at": started_at,
            "finished_at": finished_at,
            "command": command,
            "status": status,
            **report,
        },
    )
    return path


def run_ingest(paths: list[tuple[str, Path]], command: str) -> dict[str, Any]:
    started_at = now_utc()
    run_id = (
        dt.datetime.now(dt.timezone.utc)
        .strftime("%Y%m%dT%H%M%S%fZ")
    )
    counters = Counters()
    connection = connect()
    try:
        for source, path in paths:
            if not path.exists():
                counters.warnings.append(f"missing path: {project_relative(path)}")
                continue
            ingest_source(connection, counters, source, path)
        rebuild_fts(connection)
        rebuild_source_cards(connection)
        summary = database_summary(connection)
        report = {
            "ok": not counters.warnings,
            "counters": counters.as_dict(),
            "database": project_relative(DB_PATH),
            "summary": summary,
        }
        report_path = write_run_report(
            connection,
            run_id,
            started_at,
            command,
            "complete" if report["ok"] else "partial",
            report,
        )
        connection.commit()
        report["run_report"] = project_relative(report_path)
        return report
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def scan_report() -> dict[str, Any]:
    youtube = list(SOURCE_ROOTS["youtube"].glob("**/*.stats.json"))
    telegram = list(SOURCE_ROOTS["telegram"].glob("*.json"))
    instagram = list(SOURCE_ROOTS["instagram"].glob("*.json"))
    research = [
        path
        for path in SOURCE_ROOTS["research"].glob("**/*")
        if path.is_file() and path.suffix.lower() in {".md", ".csv"}
    ]
    web_articles = list(SOURCE_ROOTS["web_articles"].glob("**/metadata.json"))
    return {
        "ok": True,
        "sources": {
            "youtube_videos": len(youtube),
            "telegram_exports": len(telegram),
            "instagram_exports": len(instagram),
            "research_files": len(research),
            "web_articles": len(web_articles),
        },
        "paths": {key: project_relative(value) for key, value in SOURCE_ROOTS.items()},
    }


def doctor_report() -> dict[str, Any]:
    fts5 = False
    error = None
    try:
        test = sqlite3.connect(":memory:")
        test.execute("CREATE VIRTUAL TABLE test_fts USING fts5(body)")
        test.close()
        fts5 = True
    except sqlite3.Error as exc:
        error = str(exc)
    return {
        "ok": fts5 and all(path.exists() for path in SOURCE_ROOTS.values()),
        "python": sys.version.split()[0],
        "sqlite": sqlite3.sqlite_version,
        "fts5": {"available": fts5, "error": error},
        "project_root": str(PROJECT_ROOT),
        "knowledge_root": str(KNOWLEDGE_ROOT),
        "source_roots": {
            key: {"path": str(path), "exists": path.exists()}
            for key, path in SOURCE_ROOTS.items()
        },
        "network_required": False,
        "external_dependencies": [],
    }


def validate_report() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for metadata_path in sorted(SOURCE_ROOTS["web_articles"].glob("**/metadata.json")):
        try:
            load_web_article_package(metadata_path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
    if not DB_PATH.is_file():
        return {"ok": False, "errors": [f"missing database: {DB_PATH}"], "warnings": []}
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        foreign = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign:
            errors.append(f"foreign key violations: {len(foreign)}")
        required = {
            "sources",
            "documents",
            "chunks",
            "edges",
            "ingestion_runs",
            "documents_fts",
            "chunks_fts",
        }
        present = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
        }
        missing = sorted(required - present)
        if missing:
            errors.append("missing tables: " + ", ".join(missing))
        summary = database_summary(connection) if not missing else {}
        if summary and summary["documents"] != summary["documents_fts"]:
            errors.append("documents FTS count does not match documents")
        if summary and summary["chunks"] != summary["chunks_fts"]:
            errors.append("chunks FTS count does not match chunks")
        source_count = connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
        card_count = len(list(SOURCE_CARDS_ROOT.glob("*.md")))
        if source_count != card_count:
            errors.append(
                f"source card count mismatch: database={source_count}, cards={card_count}"
            )
        empty_documents = connection.execute(
            "SELECT COUNT(*) FROM documents WHERE trim(body) = ''"
        ).fetchone()[0]
        if empty_documents:
            warnings.append(f"empty documents retained for relations: {empty_documents}")
        return {
            "ok": not errors,
            "errors": errors,
            "warnings": warnings,
            "summary": summary,
        }
    finally:
        connection.close()


def search_report(query: str, limit: int, chunks: bool) -> dict[str, Any]:
    if not DB_PATH.is_file():
        return {"ok": False, "error": f"missing database: {DB_PATH}"}
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        if chunks:
            rows = connection.execute(
                """
                SELECT
                    c.locator,
                    d.title,
                    d.author,
                    d.published_at,
                    d.url,
                    s.name AS source_name,
                    s.visibility,
                    snippet(chunks_fts, 3, '[', ']', ' … ', 24) AS snippet,
                    bm25(chunks_fts) AS rank
                FROM chunks_fts
                JOIN chunks c ON c.id = chunks_fts.chunk_id
                JOIN documents d ON d.id = c.document_id
                JOIN sources s ON s.id = d.source_id
                WHERE chunks_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                    d.locator,
                    d.title,
                    d.author,
                    d.published_at,
                    d.url,
                    s.name AS source_name,
                    s.visibility,
                    snippet(documents_fts, 3, '[', ']', ' … ', 24) AS snippet,
                    bm25(documents_fts) AS rank
                FROM documents_fts
                JOIN documents d ON d.id = documents_fts.document_id
                JOIN sources s ON s.id = d.source_id
                WHERE documents_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()
        return {
            "ok": True,
            "query": query,
            "scope": "chunks" if chunks else "documents",
            "count": len(rows),
            "results": [dict(row) for row in rows],
        }
    except sqlite3.OperationalError as exc:
        return {
            "ok": False,
            "query": query,
            "error": str(exc),
            "hint": "Use SQLite FTS5 syntax, for example: agents OR context",
        }
    finally:
        connection.close()


def paths_for_args(args: argparse.Namespace) -> list[tuple[str, Path]]:
    if args.path:
        path = Path(args.path).expanduser()
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        source = args.source or detect_source(path)
        if source is None:
            raise RuntimeError(f"cannot detect source type for {path}")
        return [(source, path)]
    if args.all:
        if args.source:
            return [(args.source, SOURCE_ROOTS[args.source])]
        return list(SOURCE_ROOTS.items())
    raise RuntimeError("pass PATH or --all")


def rebuild() -> dict[str, Any]:
    if DB_PATH.exists():
        DB_PATH.unlink()
    for suffix in ("-wal", "-shm"):
        Path(str(DB_PATH) + suffix).unlink(missing_ok=True)
    if SOURCE_CARDS_ROOT.exists():
        for path in SOURCE_CARDS_ROOT.glob("*.md"):
            path.unlink()
    return run_ingest(list(SOURCE_ROOTS.items()), "rebuild")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GCONF local knowledge importer")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor")
    subparsers.add_parser("scan")
    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("path", nargs="?")
    ingest_parser.add_argument(
        "--source", choices=sorted(SOURCE_ROOTS), default=None
    )
    ingest_parser.add_argument("--all", action="store_true")
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--chunks", action="store_true")
    subparsers.add_parser("validate")
    subparsers.add_parser("rebuild")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            report = doctor_report()
        elif args.command == "scan":
            report = scan_report()
        elif args.command == "ingest":
            paths = paths_for_args(args)
            report = run_ingest(paths, "ingest")
        elif args.command == "search":
            report = search_report(args.query, max(1, min(args.limit, 100)), args.chunks)
        elif args.command == "validate":
            report = validate_report()
        elif args.command == "rebuild":
            report = rebuild()
        else:
            return 1
    except (RuntimeError, OSError, sqlite3.Error, json.JSONDecodeError) as exc:
        report = {"ok": False, "error": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

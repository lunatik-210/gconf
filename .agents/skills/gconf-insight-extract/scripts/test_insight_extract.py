#!/usr/bin/env python3
"""Offline tests for GCONF insight extraction state and validation."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("insight_extract.py")
SPEC = importlib.util.spec_from_file_location("insight_extract", MODULE_PATH)
assert SPEC and SPEC.loader
insight_extract = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = insight_extract
SPEC.loader.exec_module(insight_extract)


class InsightExtractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.knowledge = root / "knowledge"
        insight_extract.PROJECT_ROOT = root
        insight_extract.KNOWLEDGE_ROOT = self.knowledge
        insight_extract.DB_PATH = self.knowledge / "_index" / "gconf.sqlite"
        insight_extract.PROCESSING_ROOT = self.knowledge / "processing"
        insight_extract.RUNS_ROOT = self.knowledge / "runs" / "insight-extract"
        insight_extract.REVIEW_VIEW = self.knowledge / "views" / "Review Inbox.base"
        for folder in insight_extract.SEMANTIC_FOLDERS.values():
            (self.knowledge / folder).mkdir(parents=True, exist_ok=True)
        insight_extract.REVIEW_VIEW.parent.mkdir(parents=True, exist_ok=True)
        insight_extract.REVIEW_VIEW.write_text(
            'filters:\n  and:\n    - \'review_status == "candidate"\'\n',
            encoding="utf-8",
        )
        self.scope_dir = insight_extract.PROCESSING_ROOT / "test-scope"
        self.scope_dir.mkdir(parents=True)
        self.scope_path = self.scope_dir / "scope.json"
        self.scope_path.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "id": "test-scope",
                    "profile_version": "semantic-v1",
                    "event_ids": ["event-one", "event-two", "event-three", "cohort-test"],
                    "batches": [
                        {
                            "id": "batch-one",
                            "label": "Test batch",
                            "window_start": "2026-04-18",
                            "window_end": "2026-07-17",
                            "selectors": [
                                {
                                    "source_ids": ["source:one"],
                                    "kinds": ["youtube_video"],
                                    "include_chunks": True,
                                }
                            ],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self._write_database("checksum-a")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_database(self, checksum: str, with_chunk: bool = False) -> None:
        insight_extract.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        insight_extract.DB_PATH.unlink(missing_ok=True)
        connection = sqlite3.connect(insight_extract.DB_PATH)
        connection.executescript(
            """
            CREATE TABLE sources (
              id TEXT PRIMARY KEY, platform TEXT, name TEXT NOT NULL,
              source_type TEXT, visibility TEXT NOT NULL, path TEXT, url TEXT,
              collected_at TEXT, metadata_json TEXT, checksum TEXT, updated_at TEXT
            );
            CREATE TABLE documents (
              id TEXT PRIMARY KEY, source_id TEXT NOT NULL, platform TEXT,
              external_id TEXT, kind TEXT, title TEXT, author TEXT,
              published_at TEXT, url TEXT, locator TEXT UNIQUE, body TEXT,
              source_path TEXT, visibility TEXT, metadata_json TEXT,
              checksum TEXT, updated_at TEXT
            );
            CREATE TABLE chunks (
              id TEXT PRIMARY KEY, document_id TEXT, ordinal INTEGER,
              locator TEXT UNIQUE, start_seconds REAL, end_seconds REAL,
              body TEXT, metadata_json TEXT, checksum TEXT
            );
            CREATE TABLE edges (
              id TEXT PRIMARY KEY, source_locator TEXT, target_locator TEXT,
              relation TEXT, metadata_json TEXT
            );
            """
        )
        connection.execute(
            "INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "source:one", "telegram", "Source One", "public_channel",
                "public", "telegram/example.json", "https://t.me/example", None,
                "{}", "source-checksum", "2026-07-17T00:00:00Z",
            ),
        )
        connection.execute(
            "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "document:one",
                "source:one",
                "telegram",
                "1",
                "youtube_video",
                None,
                "Author",
                "2026-05-25T10:00:00Z",
                "https://t.me/example/1",
                "telegram:one:1",
                "Есть живая боль",
                "telegram/example.json",
                "public",
                "{}",
                checksum,
                "2026-07-17T00:00:00Z",
            ),
        )
        if with_chunk:
            connection.execute(
                "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    "chunk:one",
                    "document:one",
                    0,
                    "telegram:one:1:0-1",
                    0,
                    1,
                    "chunk",
                    "{}",
                    "chunk-checksum",
                ),
            )
        connection.commit()
        connection.close()

    def test_normalize_youtube_date(self) -> None:
        self.assertEqual(
            insight_extract.normalize_published_date("20260714"), "2026-07-14"
        )
        self.assertEqual(
            insight_extract.normalize_published_date("2026-07-14T10:00:00Z"),
            "2026-07-14",
        )

    def test_parse_obsidian_block_yaml_frontmatter(self) -> None:
        card = self.knowledge / "pains" / "pain-obsidian.md"
        card.write_text(
            """---
type: pain
id: pain-obsidian
status: inference
review_status: approved
evidence:
  - telegram:one:1
evidence_quotes:
  - locator: telegram:one:1
    role: primary
    quote: |-
      Есть живая боль
      И вторая строка
    supports: Подтверждает боль
event_context:
  - event_id: cohort-test
    phase: after
    attribution: explicit
---
""",
            encoding="utf-8",
        )
        data = insight_extract.parse_frontmatter(card)
        self.assertEqual(data["evidence"], ["telegram:one:1"])
        self.assertEqual(
            data["evidence_quotes"][0],
            {
                "locator": "telegram:one:1",
                "role": "primary",
                "quote": "Есть живая боль\nИ вторая строка",
                "supports": "Подтверждает боль",
            },
        )
        self.assertEqual(data["event_context"][0]["phase"], "after")

    def test_scope_window_excludes_old_documents(self) -> None:
        connection = sqlite3.connect(insight_extract.DB_PATH)
        connection.row_factory = sqlite3.Row
        connection.execute(
            "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "document:old",
                "source:one",
                "youtube",
                "old",
                "youtube_video",
                "Old video",
                "Author",
                "20260417",
                None,
                "youtube:old",
                "Outside the 90-day scope",
                "YouTube/old/info.json",
                "public",
                "{}",
                "checksum-old",
                "2026-07-17T00:00:00Z",
            ),
        )
        connection.commit()
        _, scope = insight_extract.load_scope(str(self.scope_path))
        documents, chunks = insight_extract.select_batch_records(
            connection, insight_extract.get_batch(scope, "batch-one")
        )
        connection.close()
        self.assertEqual([item["locator"] for item in documents], ["telegram:one:1"])
        self.assertEqual(chunks, [])

    def test_telegram_topic_selector_follows_nested_reply_chain(self) -> None:
        connection = sqlite3.connect(insight_extract.DB_PATH)
        connection.row_factory = sqlite3.Row
        connection.execute(
            "INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "telegram:chat:99", "telegram", "Topic chat", "private_chat",
                "internal", "telegram/topic.json", "https://t.me/c/99", None,
                "{}", "topic-source", "2026-07-17T00:00:00Z",
            ),
        )
        for external_id, kind, locator, body in (
            ("5", "telegram_topic", "telegram:99:5", "Кейсы"),
            ("10", "telegram_message", "telegram:99:10", "Первый кейс"),
            ("11", "telegram_message", "telegram:99:11", "Продолжение кейса"),
            ("20", "telegram_message", "telegram:99:20", "Другая ветка"),
        ):
            connection.execute(
                "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    f"document:topic:{external_id}", "telegram:chat:99", "telegram",
                    external_id, kind, body if kind == "telegram_topic" else None,
                    "Author", "2026-05-25T10:00:00Z",
                    f"https://t.me/c/99/{external_id}", locator, body,
                    "telegram/topic.json", "internal", "{}",
                    f"checksum-{external_id}", "2026-07-17T00:00:00Z",
                ),
            )
        connection.execute(
            "INSERT INTO edges VALUES (?, ?, ?, ?, ?)",
            ("edge:10", "telegram:99:10", "telegram:99:5", "replies_to", "{}"),
        )
        connection.execute(
            "INSERT INTO edges VALUES (?, ?, ?, ?, ?)",
            ("edge:11", "telegram:99:11", "telegram:99:10", "replies_to", "{}"),
        )
        connection.commit()
        batch = {
            "id": "topic-batch",
            "window_start": "2026-05-01",
            "window_end": "2026-05-31",
            "selectors": [{
                "source_ids": ["telegram:chat:99"],
                "kinds": ["telegram_topic", "telegram_message"],
                "topic_root_ids": ["5"],
            }],
        }
        documents, _ = insight_extract.select_batch_records(connection, batch)
        connection.close()
        self.assertEqual(
            {item["locator"] for item in documents},
            {"telegram:99:5", "telegram:99:10", "telegram:99:11"},
        )
        nested = next(item for item in documents if item["locator"] == "telegram:99:11")
        self.assertEqual(nested["thread_root_locator"], "telegram:99:5")
        self.assertEqual(nested["reply_to_locator"], "telegram:99:10")

    def test_pending_complete_and_stale_fingerprint(self) -> None:
        pending = insight_extract.status_report(str(self.scope_path))
        self.assertEqual(pending["counts"]["pending"], 1)
        prepared = insight_extract.prepare_report(str(self.scope_path), "batch-one")
        self.assertEqual(prepared["work_unit_count"], 1)
        finalized = insight_extract.finalize_report(
            str(self.scope_path), "batch-one", []
        )
        self.assertTrue(finalized["ok"])
        complete = insight_extract.status_report(str(self.scope_path))
        self.assertEqual(complete["counts"]["complete"], 1)
        connection = sqlite3.connect(insight_extract.DB_PATH)
        connection.execute(
            "UPDATE documents SET checksum = ? WHERE id = ?",
            ("checksum-b", "document:one"),
        )
        connection.commit()
        connection.close()
        stale = insight_extract.status_report(str(self.scope_path))
        self.assertEqual(stale["counts"]["stale"], 1)

    def test_processing_card_survives_database_rebuild(self) -> None:
        insight_extract.prepare_report(str(self.scope_path), "batch-one")
        insight_extract.finalize_report(str(self.scope_path), "batch-one", [])
        self._write_database("checksum-a")
        report = insight_extract.status_report(str(self.scope_path))
        self.assertEqual(report["counts"]["complete"], 1)

    def test_profile_change_makes_batch_stale(self) -> None:
        insight_extract.prepare_report(str(self.scope_path), "batch-one")
        insight_extract.finalize_report(str(self.scope_path), "batch-one", [])
        scope = json.loads(self.scope_path.read_text(encoding="utf-8"))
        scope["profile_version"] = "semantic-v2-human-evidence"
        self.scope_path.write_text(json.dumps(scope), encoding="utf-8")
        report = insight_extract.status_report(str(self.scope_path))
        self.assertEqual(report["counts"]["stale"], 1)

    def test_new_chunk_makes_batch_stale(self) -> None:
        insight_extract.prepare_report(str(self.scope_path), "batch-one")
        insight_extract.finalize_report(str(self.scope_path), "batch-one", [])
        connection = sqlite3.connect(insight_extract.DB_PATH)
        connection.execute(
            "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "chunk:one",
                "document:one",
                0,
                "telegram:one:1:0-1",
                0,
                1,
                "chunk",
                "{}",
                "chunk-checksum",
            ),
        )
        connection.commit()
        connection.close()
        report = insight_extract.status_report(str(self.scope_path))
        self.assertEqual(report["counts"]["stale"], 1)

    def test_finalize_with_card_is_idempotent(self) -> None:
        card = self.knowledge / "pains" / "pain-test.md"
        card.write_text(
            """---
type: "pain"
id: "pain-test"
label: "Тестовая боль"
status: "fact"
review_status: "candidate"
first_seen: "2026-05-25"
last_seen: "2026-05-25"
source_wave: "external"
evidence: ["telegram:one:1"]
evidence_quotes: [{"locator":"telegram:one:1","role":"primary","quote":"Есть живая боль","supports":"Подтверждает тестовую боль"}]
related: []
event_context: []
---
""",
            encoding="utf-8",
        )
        insight_extract.prepare_report(str(self.scope_path), "batch-one")
        first = insight_extract.finalize_report(
            str(self.scope_path), "batch-one", ["pain-test"]
        )
        second = insight_extract.finalize_report(
            str(self.scope_path), "batch-one", ["pain-test"]
        )
        self.assertTrue(first["ok"] and second["ok"])
        self.assertEqual(first["outputs"], ["pain-test"])
        self.assertEqual(second["outputs"], ["pain-test"])
        self.assertEqual(len(list((self.knowledge / "pains").glob("pain-test*.md"))), 1)

    def test_finalize_rejects_card_without_batch_evidence(self) -> None:
        connection = sqlite3.connect(insight_extract.DB_PATH)
        connection.execute(
            "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "document:old",
                "source:one",
                "youtube",
                "old",
                "youtube_video",
                "Old video",
                "Author",
                "2026-04-17",
                None,
                "youtube:old",
                "Outside this batch",
                "YouTube/old/info.json",
                "public",
                "{}",
                "checksum-old",
                "2026-07-17T00:00:00Z",
            ),
        )
        connection.commit()
        connection.close()
        card = self.knowledge / "pains" / "pain-old.md"
        card.write_text(
            """---
type: "pain"
id: "pain-old"
label: "Боль вне пакета"
status: "fact"
review_status: "candidate"
first_seen: "2026-04-17"
last_seen: "2026-04-17"
source_wave: "external"
evidence: ["youtube:old"]
evidence_quotes: [{"locator":"youtube:old","role":"primary","quote":"Outside this batch","supports":"Подтверждает старую боль"}]
related: []
event_context: []
---
""",
            encoding="utf-8",
        )
        insight_extract.prepare_report(str(self.scope_path), "batch-one")
        report = insight_extract.finalize_report(
            str(self.scope_path), "batch-one", ["pain-old"]
        )
        self.assertFalse(report["ok"])
        self.assertTrue(any("no evidence in batch" in error for error in report["errors"]))

    def test_semantic_card_validation_and_typed_candidate(self) -> None:
        card = self.knowledge / "pains" / "pain-test.md"
        card.write_text(
            """---
type: "pain"
id: "pain-test"
label: "Тестовая боль"
status: "fact"
review_status: "candidate"
first_seen: "2026-05-25"
last_seen: "2026-05-25"
source_wave: "external"
evidence: ["telegram:one:1"]
evidence_quotes: [{"locator":"telegram:one:1","role":"primary","quote":"Есть живая боль","supports":"Подтверждает тестовую боль"}]
related: []
event_context: [{"event_id":"cohort-test","phase":"after","attribution":"unattributed"}]
---
""",
            encoding="utf-8",
        )
        connection = insight_extract.connect()
        try:
            records = insight_extract.evidence_record_map(connection)
        finally:
            connection.close()
        data = insight_extract.parse_frontmatter(card)
        self.assertEqual(
            insight_extract.validate_semantic_card(
                card, data, records, require_rendered=False
            ),
            [],
        )
        self.assertEqual(insight_extract.card_write_action(data), "merge_candidate")
        data["review_status"] = "approved"
        self.assertEqual(
            insight_extract.card_write_action(data), "create_update_candidate"
        )

    def test_non_verbatim_quote_is_rejected(self) -> None:
        card = self.knowledge / "pains" / "pain-test.md"
        card.write_text(
            """---
type: "pain"
id: "pain-test"
label: "Тестовая боль"
status: "fact"
review_status: "candidate"
first_seen: "2026-05-25"
last_seen: "2026-05-25"
source_wave: "external"
evidence: ["telegram:one:1"]
evidence_quotes: [{"locator":"telegram:one:1","role":"primary","quote":"Это пересказ, а не цитата","supports":"Ничего не подтверждает"}]
related: []
event_context: []
---
""",
            encoding="utf-8",
        )
        connection = insight_extract.connect()
        try:
            errors = insight_extract.validate_semantic_card(
                card,
                insight_extract.parse_frontmatter(card),
                insight_extract.evidence_record_map(connection),
                require_rendered=False,
            )
        finally:
            connection.close()
        self.assertTrue(any("quote not found" in error for error in errors))

    def test_rendered_evidence_is_idempotent_and_preserves_human_text(self) -> None:
        card = self.knowledge / "pains" / "pain-test.md"
        card.write_text(
            """---
type: "pain"
id: "pain-test"
label: "Тестовая боль"
status: "fact"
review_status: "candidate"
first_seen: "2026-05-25"
last_seen: "2026-05-25"
source_wave: "external"
evidence: ["telegram:one:1"]
evidence_quotes: [{"locator":"telegram:one:1","role":"primary","quote":"Есть живая боль","supports":"Подтверждает боль"}]
related: []
event_context: []
---

# Тестовая боль

Ручной редакторский комментарий.
""",
            encoding="utf-8",
        )
        connection = insight_extract.connect()
        try:
            records = insight_extract.evidence_record_map(connection)
        finally:
            connection.close()
        data = insight_extract.parse_frontmatter(card)
        insight_extract.render_evidence_card(card, data, records)
        first = card.read_text(encoding="utf-8")
        insight_extract.render_evidence_card(card, data, records)
        second = card.read_text(encoding="utf-8")
        self.assertEqual(first, second)
        self.assertIn("Ручной редакторский комментарий.", second)
        self.assertIn("https://t.me/example/1", second)

    def test_case_taxonomy_is_required(self) -> None:
        card = self.knowledge / "cases" / "case-test.md"
        card.write_text(
            """---
type: "case"
id: "case-test"
label: "Тестовый кейс"
status: "fact"
review_status: "candidate"
first_seen: "2026-05-25"
last_seen: "2026-05-25"
source_wave: "internal"
evidence: ["telegram:one:1"]
evidence_quotes: [{"locator":"telegram:one:1","role":"primary","quote":"Есть живая боль","supports":"Тест"}]
related: []
event_context: []
case_origin: "audience"
reporting_mode: "direct_self_report"
proof_level: "described_result"
artifact_status: "working"
---
""",
            encoding="utf-8",
        )
        connection = insight_extract.connect()
        try:
            errors = insight_extract.validate_semantic_card(
                card,
                insight_extract.parse_frontmatter(card),
                insight_extract.evidence_record_map(connection),
                require_rendered=False,
            )
        finally:
            connection.close()
        self.assertTrue(any("invalid case_origin" in error for error in errors))

    def test_invalid_event_attribution_is_rejected(self) -> None:
        card = self.knowledge / "pains" / "pain-test.md"
        card.write_text(
            """---
type: "pain"
id: "pain-test"
label: "Тестовая боль"
status: "fact"
review_status: "candidate"
first_seen: "2026-05-25"
last_seen: "2026-05-25"
source_wave: "external"
evidence: ["telegram:one:1"]
evidence_quotes: [{"locator":"telegram:one:1","role":"primary","quote":"Есть живая боль","supports":"Подтверждает тестовую боль"}]
related: []
event_context: [{"event_id":"cohort-test","phase":"after","attribution":"guessed"}]
---
""",
            encoding="utf-8",
        )
        connection = insight_extract.connect()
        try:
            errors = insight_extract.validate_semantic_card(
                card,
                insight_extract.parse_frontmatter(card),
                insight_extract.evidence_record_map(connection),
                require_rendered=False,
            )
        finally:
            connection.close()
        self.assertTrue(any("attribution" in error for error in errors))

    def test_all_three_event_attribution_levels_are_distinct_and_valid(self) -> None:
        card = self.knowledge / "pains" / "pain-test.md"
        card.write_text(
            """---
type: "pain"
id: "pain-test"
label: "Тестовая боль"
status: "inference"
review_status: "candidate"
first_seen: "2026-05-25"
last_seen: "2026-05-25"
source_wave: "mixed"
evidence: ["telegram:one:1"]
evidence_quotes: [{"locator":"telegram:one:1","role":"primary","quote":"Есть живая боль","supports":"Подтверждает тестовую боль"}]
related: []
event_context: [{"event_id":"event-one","phase":"before","attribution":"explicit"},{"event_id":"event-two","phase":"during","attribution":"inferred_by_time"},{"event_id":"event-three","phase":"unknown","attribution":"unattributed"}]
---
""",
            encoding="utf-8",
        )
        connection = insight_extract.connect()
        try:
            errors = insight_extract.validate_semantic_card(
                card,
                insight_extract.parse_frontmatter(card),
                insight_extract.evidence_record_map(connection),
                require_rendered=False,
            )
        finally:
            connection.close()
        self.assertEqual(errors, [])

    def test_event_outside_scope_is_rejected(self) -> None:
        card = self.knowledge / "pains" / "pain-test.md"
        card.write_text(
            """---
type: "pain"
id: "pain-test"
label: "Тестовая боль"
status: "inference"
review_status: "candidate"
first_seen: "2026-05-25"
last_seen: "2026-05-25"
source_wave: "internal"
evidence: ["telegram:one:1"]
evidence_quotes: [{"locator":"telegram:one:1","role":"primary","quote":"Есть живая боль","supports":"Подтверждает тестовую боль"}]
related: []
event_context: [{"event_id":"event-outside","phase":"unknown","attribution":"unattributed"}]
---
""",
            encoding="utf-8",
        )
        connection = insight_extract.connect()
        try:
            errors = insight_extract.validate_semantic_card(
                card,
                insight_extract.parse_frontmatter(card),
                insight_extract.evidence_record_map(connection),
                {"event-one", "event-two"},
                require_rendered=False,
            )
        finally:
            connection.close()
        self.assertTrue(any("outside configured scope" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

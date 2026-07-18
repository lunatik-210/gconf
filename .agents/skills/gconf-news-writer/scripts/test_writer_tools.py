#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str):
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prepare = load("prepare_writer_context")
validator = load("validate_news_run")
TOPIC = "news-20260718-test-signal"


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {
            "candidates": [
                {
                    "topic_id": TOPIC,
                    "status": "recommended",
                    "score": {"priority_score": 85},
                }
            ],
            "rejected_signals": [
                {
                    "topic_id": "news-20260718-rejected",
                    "status": "reject",
                    "score": {"priority_score": 40},
                }
            ],
        }

    def test_requires_explicit_topic(self):
        with self.assertRaises(prepare.ContextError):
            prepare.select_topics(self.manifest, [], False)

    def test_reject_needs_explicit_override(self):
        with self.assertRaises(prepare.ContextError):
            prepare.select_topics(self.manifest, ["news-20260718-rejected"], False)
        selected = prepare.select_topics(self.manifest, ["news-20260718-rejected"], True)
        self.assertEqual(selected[0]["topic_id"], "news-20260718-rejected")

    def test_unknown_topic_is_rejected(self):
        with self.assertRaises(prepare.ContextError):
            prepare.select_topics(self.manifest, ["news-20260718-unknown"], False)

    def test_comment_locator_resolves_with_parent(self):
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.executescript(
            """
            CREATE TABLE sources(id TEXT, name TEXT);
            CREATE TABLE documents(id TEXT, source_id TEXT, locator TEXT, kind TEXT,
              title TEXT, author TEXT, published_at TEXT, url TEXT, body TEXT,
              source_path TEXT, visibility TEXT);
            CREATE TABLE chunks(id TEXT, document_id TEXT, locator TEXT, body TEXT,
              start_seconds REAL, end_seconds REAL);
            CREATE TABLE edges(source_locator TEXT, target_locator TEXT, relation TEXT);
            INSERT INTO sources VALUES ('youtube:channel:test','Test');
            INSERT INTO documents VALUES
              ('video','youtube:channel:test','youtube:v1','youtube_video','Video','Author',
               '2026-07-10','https://youtu.be/v1','Video body','YouTube/v1','public'),
              ('comment','youtube:channel:test','youtube:v1:comment:c1','youtube_comment',NULL,'Viewer',
               '2026-07-11',NULL,'Comment body','YouTube/v1','public');
            INSERT INTO edges VALUES ('youtube:v1:comment:c1','youtube:v1','replies_to');
            """
        )
        resolved = prepare.resolve_locator(
            connection,
            Path(tempfile.mkdtemp()),
            {"id": "e1", "locator": "youtube:v1:comment:c1"},
        )
        self.assertTrue(resolved["resolved"])
        self.assertEqual(resolved["parent"]["locator"], "youtube:v1")
        connection.close()


class ValidatorTests(unittest.TestCase):
    def make_run(self, word_count: int = 160, central_status: str = "unchanged") -> Path:
        run = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(run))
        post_file = f"news-{TOPIC}.md"
        (run / post_file).write_text(" ".join(["слово"] * word_count), encoding="utf-8")
        (run / "brief.md").write_text("# Brief", encoding="utf-8")
        (run / "audit.md").write_text("# Audit", encoding="utf-8")
        ledger = [
            {
                "id": "evidence-1",
                "topic_id": TOPIC,
                "evidence_status": "fact",
                "source_kind": "official_primary",
                "publisher": "Lab",
                "title": "Release",
                "published_at": "2026-07-18",
                "revalidated_at": "2026-07-18T12:00:00Z",
                "url": "https://example.com/release",
                "local_source": None,
                "locator": "https://example.com/release#release",
                "claim_supported": "The release is available.",
                "publisher_claim": False,
                "availability_status": "confirmed",
                "limitation": "Publisher source.",
                "used_in": [post_file],
            }
        ]
        coverage = [
            {
                "topic_id": TOPIC,
                "closest_coverage_refs": [],
                "coverage_delta": "Новый подтверждённый режим.",
                "central_claim_overlap": "partial",
                "new_editorial_unit": True,
            }
        ]
        manifest = {
            "schema_version": "1.0",
            "run_id": "20260718T120000Z",
            "generated_at": "2026-07-18T12:00:00Z",
            "review_status": "ready_for_human_review",
            "publication_ready": False,
            "radar_run": "research/news_analysis/runs/20260718T110000Z",
            "selected_topic_ids": [TOPIC],
            "human_selection": True,
            "voice_mode": "GCONF",
            "address": "vy",
            "cta_mode": "editorial",
            "posts": [
                {
                    "topic_id": TOPIC,
                    "file": post_file,
                    "format": "release_explainer",
                    "focus": "Один фокус",
                    "behavioral_transition": "от ответа к процессу",
                    "tension": "доступность",
                    "primary_evidence_ref": "evidence-1",
                    "evidence_refs": ["evidence-1"],
                    "coverage_delta": "Новый подтверждённый режим.",
                    "cta": {"type": "editorial", "text": "Проверьте на одной задаче."},
                    "source_revalidated_at": "2026-07-18T12:00:00Z",
                    "central_fact_status": central_status,
                    "format_change_reason": None,
                    "quality_scores": {
                        "taste": 2,
                        "philosophy": 2,
                        "research": 2,
                        "process_quality": 1,
                        "growth": 1,
                    },
                    "publication_ready": False,
                }
            ],
            "unresolved_items": ["manual review"],
            "output_files": [
                "brief.md",
                post_file,
                "evidence-ledger.json",
                "coverage.json",
                "audit.md",
                "manifest.json",
            ],
        }
        (run / "evidence-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
        (run / "coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
        (run / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return run

    def test_valid_writer_run(self):
        self.assertEqual(validator.validate(self.make_run()), [])

    def test_word_range_is_enforced(self):
        errors = validator.validate(self.make_run(word_count=20))
        self.assertTrue(any("word count" in error for error in errors))

    def test_changed_central_fact_stops_draft(self):
        errors = validator.validate(self.make_run(central_status="changed"))
        self.assertTrue(any("drafting should have stopped" in error for error in errors))

    def make_v11(self, permission_status: str = "not_required") -> Path:
        run = self.make_run()
        manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        manifest["schema_version"] = "1.1"
        ledger = json.loads((run / "evidence-ledger.json").read_text(encoding="utf-8"))
        ledger[0].update(
            {
                "evidence_role": "event_confirmation",
                "parent_locator": None,
                "visibility": "internal" if permission_status == "required" else "public",
                "permission_status": permission_status,
            }
        )
        (run / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (run / "evidence-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
        return run

    def test_schema_v11_writer_run_is_supported(self):
        self.assertEqual(validator.validate(self.make_v11()), [])

    def test_permission_required_blocks_publication_ready(self):
        run = self.make_v11("required")
        manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        manifest["posts"][0]["publication_ready"] = True
        manifest["publication_ready"] = True
        manifest["unresolved_items"] = []
        (run / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        errors = validator.validate(run)
        self.assertTrue(any("unresolved permission" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

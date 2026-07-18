#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import sqlite3
import tempfile
import unittest
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str):
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prepare = load("prepare_radar_context")
validator = load("validate_radar_run")
composer = load("compose_radar_candidates")


def valid_candidate() -> dict:
    return {
        "topic_id": "news-20260718-test-signal",
        "working_title": "Тестовый сигнал",
        "event_summary": "Вышло проверяемое обновление.",
        "event_date": "2026-07-18",
        "focus": "Один проверяемый фокус.",
        "why_now": "Сигнал опубликован сегодня.",
        "ai_market_significance": "Меняется рабочее поведение.",
        "gconf_theme": "AI Ops",
        "gconf_relevance": "Поддерживает работу с процессом.",
        "audience": "Практики AI",
        "previous_mode": "Разовая операция.",
        "changed_mode": "Повторяемый процесс.",
        "closest_coverage_refs": ["coverage-1"],
        "coverage_delta": "Добавляет новое подтверждённое действие.",
        "recommended_format": "release_explainer",
        "experiment_or_question": "Проверить на одной задаче.",
        "facts": ["Факт"],
        "inferences": ["Вывод"],
        "limitations": ["Ограничение"],
        "editorial_risks": ["Риск"],
        "evidence_refs": ["evidence-1"],
        "source_requirement": "product_release",
        "score": {
            "market_relevance": 18,
            "gconf_relevance": 18,
            "coverage_novelty": 17,
            "evidence_quality": 18,
            "freshness": 10,
            "actionability": 9,
            "risk_penalty": 5,
            "priority_score": 85,
        },
        "status": "recommended",
        "priority_rationale": "Сильный свежий сигнал.",
    }


def valid_manifest() -> dict:
    return {
        "schema_version": "1.0",
        "run_id": "20260718T120000Z",
        "generated_at": "2026-07-18T12:00:00Z",
        "review_status": "draft",
        "selected_topic_ids": [],
        "parameters": {
            "default_window_days": 14,
            "expanded_window_days": 45,
            "window_expansion_reason": None,
            "max_candidates": 10,
            "minimum_score": 65,
        },
        "source_snapshot": {},
        "candidates": [valid_candidate()],
        "rejected_signals": [],
        "evidence_index": [
            {
                "id": "evidence-1",
                "evidence_status": "fact",
                "source_kind": "official_primary",
                "publisher": "Lab",
                "title": "Release",
                "published_at": "2026-07-18",
                "accessed_at": "2026-07-18T12:00:00Z",
                "url": "https://example.com/release",
                "local_source": None,
                "locator": "https://example.com/release#release",
                "claim_supported": "A product was released.",
                "publisher_claim": False,
                "freshness_days": 0,
                "freshness_band": "live",
                "limitation": "Publisher source only.",
            }
        ],
        "coverage_index": [
            {
                "id": "coverage-1",
                "platform": "telegram",
                "published_at": "2026-07-10",
                "locator": "telegram:1633415027:1049",
                "url": "https://t.me/gptlovers/1049",
                "title": "Prior post",
                "excerpt": "Prior coverage.",
                "coverage_role": "closest_prior_post",
            }
        ],
        "ingestion_queue": [],
        "output_files": ["backlog.md", "manifest.json", "audit.md"],
    }


BACKLOG = "\n".join(validator.REQUIRED_SECTIONS)


def valid_manifest_v11() -> dict:
    manifest = valid_manifest()
    manifest["schema_version"] = "1.1"
    manifest["parameters"].update(
        {
            "local_window_days": 30,
            "local_max_days": 60,
            "reserved_lanes": ["protagonist", "gconf_case", "audience_reaction"],
        }
    )
    manifest["candidates"][0].update(
        {
            "primary_discovery_lane": "official_release",
            "supporting_lanes": ["semantic_context"],
            "window_expansion_reason": None,
        }
    )
    manifest["evidence_index"][0].update(
        {
            "evidence_role": "event_confirmation",
            "parent_locator": None,
            "visibility": "public",
            "permission_status": "not_required",
        }
    )
    manifest["source_review"] = {
        lane: {
            "available_items": 1,
            "meaningful_items": 1,
            "noise_excluded": 0,
            "pages_expected": 1,
            "pages_reviewed": 1,
            "complete": True,
            "freshest_published_at": "2026-07-18",
            "oldest_published_at": "2026-07-18",
            "fingerprint": f"fingerprint-{lane}",
            "signals_found": 0,
            "passing_candidates": 0,
        }
        for lane in prepare.LANES
    }
    return manifest


class PrepareTests(unittest.TestCase):
    def test_freshness_bands(self):
        now = datetime(2026, 7, 18, tzinfo=timezone.utc)
        self.assertEqual(prepare.freshness("2026-07-10", now)["freshness_band"], "live")
        self.assertEqual(prepare.freshness("2026-06-20", now)["freshness_band"], "fresh")

    def test_fts_query_is_tokenized(self):
        self.assertEqual(prepare.safe_fts_query('ChatGPT Work: "agents"'), '"ChatGPT" OR "Work" OR "agents"')

    def test_default_and_maximum_local_windows(self):
        self.assertEqual(prepare.DEFAULT_LOCAL_WINDOW_DAYS, 30)
        self.assertEqual(prepare.MAX_LOCAL_WINDOW_DAYS, 60)

    def test_extended_window_requires_reason(self):
        args = Namespace(
            window_days=14,
            local_window_days=30,
            local_max_days=60,
            use_extended_window=True,
            window_expansion_reason=None,
            max_candidates=10,
            coverage_limit=100,
            page_size=100,
            cursor=None,
            lane="protagonist",
        )
        with self.assertRaises(prepare.ContextError):
            prepare.validate_args(args)

    def test_all_semantic_card_types_are_collected(self):
        cards = prepare.collect_cards(prepare.project_root(), datetime(2026, 7, 18, tzinfo=timezone.utc))
        types = {card["type"] for card in cards}
        self.assertTrue({"actor", "case", "cohort", "lab"} <= types)

    def test_comment_parent_is_resolved(self):
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.executescript(
            """
            CREATE TABLE documents(locator TEXT, kind TEXT, title TEXT, author TEXT,
              published_at TEXT, url TEXT, body TEXT);
            CREATE TABLE edges(source_locator TEXT, target_locator TEXT, relation TEXT);
            INSERT INTO documents VALUES
              ('youtube:v1','youtube_video','Video','Author','2026-07-10','https://youtu.be/v1','Body'),
              ('youtube:v1:comment:c1','youtube_comment',NULL,'Viewer','2026-07-11',NULL,'Useful comment');
            INSERT INTO edges VALUES ('youtube:v1:comment:c1','youtube:v1','replies_to');
            """
        )
        edges, documents = prepare.parent_indexes(connection)
        parent = prepare.root_parent("youtube:v1:comment:c1", edges, documents)
        self.assertEqual(parent["locator"], "youtube:v1")
        connection.close()

    def test_current_corpus_covers_all_required_lanes(self):
        root = prepare.project_root()
        now = datetime(2026, 7, 18, tzinfo=timezone.utc)
        cards = prepare.collect_cards(root, now)
        config = prepare.load_lane_config(root)
        connection = prepare.readonly_connection(root / "knowledge/_index/gconf.sqlite")
        try:
            lane_data = {
                lane: prepare.lane_items(connection, root, config, cards, lane, now, 30)[0]
                for lane in prepare.LANES
            }
        finally:
            connection.close()
        self.assertTrue(all(lane_data[lane] for lane in prepare.LANES))
        self.assertTrue(
            {"youtube_comment", "instagram_comment"}
            <= {item["kind"] for item in lane_data["audience_reaction"]}
        )
        self.assertIn(
            "youtube_transcript_chunk",
            {item["kind"] for item in lane_data["protagonist"]},
        )
        self.assertTrue(
            {"telegram", "instagram", "youtube"}
            <= {item["platform"] for item in lane_data["ecosystem_posts"]}
        )
        internal = [item for item in lane_data["gconf_case"] if item["visibility"] == "internal"]
        self.assertTrue(internal)
        self.assertTrue(all(item["permission_status"] == "required" for item in internal))


class CompositionTests(unittest.TestCase):
    def candidate(self, topic: str, lane: str, score: int) -> dict:
        return {
            "topic_id": topic,
            "status": "recommended" if score >= 80 else "reserve",
            "primary_discovery_lane": lane,
            "event_date": "2026-07-18",
            "score": {
                "priority_score": score,
                "evidence_quality": score // 5,
                "freshness": 10,
            },
        }

    def test_three_lanes_are_reserved_when_eligible(self):
        pool = [
            self.candidate(f"news-20260718-official-{index}", "official_release", 100 - index)
            for index in range(10)
        ]
        pool.extend(
            [
                self.candidate("news-20260718-protagonist", "protagonist", 70),
                self.candidate("news-20260718-case", "gconf_case", 69),
                self.candidate("news-20260718-reaction", "audience_reaction", 68),
            ]
        )
        result = composer.compose(pool)
        selected = set(result["selected_topic_ids"])
        self.assertTrue(
            {"news-20260718-protagonist", "news-20260718-case", "news-20260718-reaction"}
            <= selected
        )

    def test_weak_lane_candidate_is_not_reserved(self):
        weak = self.candidate("news-20260718-weak-reaction", "audience_reaction", 64)
        self.assertNotIn(weak["topic_id"], composer.compose([weak])["selected_topic_ids"])


class ValidatorTests(unittest.TestCase):
    def make_run(self, manifest: dict) -> Path:
        temp = Path(tempfile.mkdtemp())
        (temp / "backlog.md").write_text(BACKLOG, encoding="utf-8")
        (temp / "audit.md").write_text("# Audit", encoding="utf-8")
        (temp / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.addCleanup(lambda: __import__("shutil").rmtree(temp))
        return temp

    def test_valid_run(self):
        self.assertEqual(validator.validate(self.make_run(valid_manifest())), [])

    def test_human_gate_cannot_be_preselected(self):
        manifest = valid_manifest()
        manifest["selected_topic_ids"] = ["news-20260718-test-signal"]
        errors = validator.validate(self.make_run(manifest))
        self.assertTrue(any("must remain empty" in error for error in errors))

    def test_score_arithmetic_is_enforced(self):
        manifest = valid_manifest()
        manifest["candidates"][0]["score"]["priority_score"] = 99
        errors = validator.validate(self.make_run(manifest))
        self.assertTrue(any("priority_score" in error for error in errors))

    def test_broad_trend_needs_independent_publishers(self):
        manifest = valid_manifest()
        manifest["candidates"][0]["source_requirement"] = "broad_trend"
        errors = validator.validate(self.make_run(manifest))
        self.assertTrue(any("two independent publishers" in error for error in errors))

    def test_public_copy_field_is_rejected(self):
        manifest = valid_manifest()
        manifest["candidates"][0]["headline"] = "Публичный заголовок"
        errors = validator.validate(self.make_run(manifest))
        self.assertTrue(any("public-copy fields" in error for error in errors))

    def test_schema_v11_requires_complete_source_review(self):
        manifest = valid_manifest_v11()
        self.assertEqual(validator.validate(self.make_run(manifest)), [])
        manifest["source_review"]["protagonist"]["complete"] = False
        errors = validator.validate(self.make_run(manifest))
        self.assertTrue(any("source_review.protagonist must be complete" in error for error in errors))

    def test_extended_candidate_requires_reason(self):
        manifest = valid_manifest_v11()
        manifest["candidates"][0]["event_date"] = "2026-06-01"
        errors = validator.validate(self.make_run(manifest))
        self.assertTrue(any("extended local window needs a reason" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("editorial_gates", HERE / "editorial_gates.py")
assert SPEC and SPEC.loader
gates = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gates)


class EditorialGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        radar = self.root / "research/news_analysis/runs/20260718T100000Z"
        radar.mkdir(parents=True)
        (radar / "manifest.json").write_text(json.dumps({
            "run_id": "20260718T100000Z",
            "candidates": [{"topic_id": "news-one"}, {"topic_id": "news-two"}],
            "rejected_signals": [],
        }), encoding="utf-8")
        analysis = self.root / "research/announcement_analysis/runs/20260718T110000Z"
        analysis.mkdir(parents=True)
        (analysis / "manifest.json").write_text(json.dumps({
            "run_id": "20260718T110000Z",
            "directions": [{"id": "direction-one"}],
        }), encoding="utf-8")

    def args(self, **overrides):
        base = dict(
            workflow="news", gate_type="news_topic_selection",
            upstream_ref="research/news_analysis/runs/20260718T100000Z",
            selected_ref=["news-one"], decision_source="human_explicit",
            instruction_excerpt="Берём первую", status="confirmed", supersedes=None,
            downstream_ref=None, decision_id=None, decided_at=None,
        )
        base.update(overrides)
        return argparse.Namespace(**base)

    def test_record_and_resolve_explicit_decision(self):
        created = gates.record(self.root, self.args())
        resolved = gates.resolve(self.root, argparse.Namespace(
            decision_id=created["decision_id"], workflow="news",
            gate_type="news_topic_selection",
            upstream_ref="research/news_analysis/runs/20260718T100000Z",
            selected_ref=[],
        ))
        self.assertTrue(resolved["ok"])
        self.assertEqual(resolved["decision"]["selected_refs"], ["news-one"])

    def test_unknown_topic_is_rejected(self):
        with self.assertRaises(gates.GateError):
            gates.record(self.root, self.args(selected_ref=["missing"]))

    def test_backfill_cannot_be_confirmed(self):
        with self.assertRaises(gates.GateError):
            gates.record(self.root, self.args(decision_source="inferred_backfill"))

    def test_superseded_decision_no_longer_resolves(self):
        first = gates.record(self.root, self.args())
        gates.record(self.root, self.args(selected_ref=["news-two"], supersedes=first["decision_id"]))
        with self.assertRaises(gates.GateError):
            gates.resolve(self.root, argparse.Namespace(
                decision_id=first["decision_id"], workflow="news",
                gate_type="news_topic_selection",
                upstream_ref="research/news_analysis/runs/20260718T100000Z",
                selected_ref=[],
            ))

    def test_artifact_approval_detects_changed_file(self):
        draft = self.root / "research/news_drafts/runs/one"
        draft.mkdir(parents=True)
        (draft / "manifest.json").write_text("{}", encoding="utf-8")
        post = draft / "post.md"
        post.write_text("approved", encoding="utf-8")
        created = gates.record(self.root, self.args(
            gate_type="news_copy_approval",
            upstream_ref="research/news_drafts/runs/one",
            selected_ref=["research/news_drafts/runs/one/post.md"],
        ))
        post.write_text("changed", encoding="utf-8")
        with self.assertRaises(gates.GateError):
            gates.resolve(self.root, argparse.Namespace(
                decision_id=created["decision_id"], workflow="news",
                gate_type="news_copy_approval",
                upstream_ref="research/news_drafts/runs/one",
                selected_ref=[],
            ))

    def test_backfill_creates_pending_only(self):
        draft = self.root / "research/news_drafts/runs/20260718T120000Z"
        draft.mkdir(parents=True)
        (draft / "manifest.json").write_text(json.dumps({
            "run_id": "20260718T120000Z", "generated_at": "2026-07-18T12:00:00Z",
            "radar_run": "research/news_analysis/runs/20260718T100000Z",
            "selected_topic_ids": ["news-one"], "human_selection": True,
        }), encoding="utf-8")
        result = gates.backfill(self.root)
        self.assertEqual(result["created"], 1)
        decisions, _ = gates.load_decisions(self.root)
        card = next(iter(decisions.values()))
        self.assertEqual(card["decision_source"], "inferred_backfill")
        self.assertEqual(card["status"], "needs_confirmation")

    def test_sync_builds_obsidian_control_plane(self):
        result = gates.sync(self.root)
        self.assertGreaterEqual(result["run_cards"], 1)
        self.assertTrue((self.root / "knowledge/editorial/Editorial Control Plane.md").exists())

    def test_semantic_review_applies_only_confirmed_decision(self):
        pain = self.root / "knowledge/pains/pain-one.md"
        pain.parent.mkdir(parents=True)
        pain.write_text('---\ntype: "pain"\nid: "pain-one"\nreview_status: "candidate"\n---\n', encoding="utf-8")
        created = gates.record(self.root, self.args(
            workflow="semantic", gate_type="semantic_evidence_review",
            upstream_ref="knowledge", selected_ref=["pain-one"],
        ))
        result = gates.apply_semantic_review(self.root, argparse.Namespace(
            decision_id=created["decision_id"], review_status="approved",
        ))
        self.assertEqual(result["changed"], ["knowledge/pains/pain-one.md"])
        self.assertIn('review_status: "approved"', pain.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

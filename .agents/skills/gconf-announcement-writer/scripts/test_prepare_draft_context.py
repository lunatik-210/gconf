#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[3]
sys.path.insert(0, str(SCRIPT_DIR))

import prepare_draft_context
import validate_draft


class PrepareContextTests(unittest.TestCase):
    def test_publisher_is_not_mislabeled_as_audience_voice(self) -> None:
        self.assertEqual(
            prepare_draft_context.evidence_source_role("Записки AI энтузиаста"),
            "organizer_interpretation",
        )
        self.assertEqual(
            prepare_draft_context.evidence_source_role("@reader-handle"),
            "audience_voice",
        )

    def test_real_context_is_read_only_and_selects_direction(self) -> None:
        watched = [
            ROOT / "knowledge/_index/gconf.sqlite",
            ROOT / "research/announcement_analysis/runs/20260717T200356Z/manifest.json",
        ]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
        args = argparse.Namespace(
            analysis_run=Path("research/announcement_analysis/runs/20260717T200356Z"),
            decision_id="decision-test-direction",
            facts_decision_id="decision-test-facts",
            direction_id="direction-living-ai-ops",
            product_name="Vibe Coding · AI Ops",
            voice_mode="GCONF",
            address="vy",
            facts_json=None,
            telegram_locator="telegram:1633415027:1040",
            instagram_locator="instagram:gconf.io:DafUhD0F5Yh",
            screenshots_dir=Path("Instagram/Прошлый Анонс"),
            card_id=[],
        )
        with mock.patch.object(
            prepare_draft_context,
            "resolve_direction_decision",
            return_value={"selected_refs": ["direction-living-ai-ops"]},
        ), mock.patch.object(
            prepare_draft_context,
            "resolve_fact_decision",
            return_value={"selected_refs": ["allowlist:none"]},
        ):
            packet = prepare_draft_context.prepare(args, ROOT)
        self.assertTrue(packet["read_only"])
        self.assertEqual(packet["direction"]["id"], "direction-living-ai-ops")
        self.assertEqual(len(packet["screenshot_snapshot"]), 6)
        self.assertGreaterEqual(len(packet["approved_pain_evidence"]), 6)
        self.assertEqual(packet["freshness_policy"]["fresh_max_days"], 30)
        self.assertTrue(
            all(item["review_status"] == "approved" for item in packet["approved_pain_evidence"])
        )
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
        self.assertEqual(before, after)

    def test_unknown_direction_fails(self) -> None:
        args = argparse.Namespace(
            analysis_run=Path("research/announcement_analysis/runs/20260717T200356Z"),
            decision_id="decision-test-direction",
            facts_decision_id="decision-test-facts",
            direction_id="missing",
            product_name="x",
            voice_mode="GCONF",
            address="vy",
            facts_json=None,
            telegram_locator="telegram:1633415027:1040",
            instagram_locator="instagram:gconf.io:DafUhD0F5Yh",
            screenshots_dir=Path("Instagram/Прошлый Анонс"),
            card_id=[],
        )
        with mock.patch.object(
            prepare_draft_context,
            "resolve_direction_decision",
            return_value={"selected_refs": ["missing"]},
        ), mock.patch.object(
            prepare_draft_context,
            "resolve_fact_decision",
            return_value={"selected_refs": ["allowlist:none"]},
        ):
            with self.assertRaises(prepare_draft_context.ContextError):
                prepare_draft_context.prepare(args, ROOT)


class DraftValidatorTests(unittest.TestCase):
    def test_missing_files_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            errors = validate_draft.validate(Path(temp), ROOT)
        self.assertIn("missing file: brief.md", errors)

    def test_previous_run_regression_rejects_copied_slide_four(self) -> None:
        source = ROOT / "research/announcement_drafts/runs/20260718T091009Z"
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp) / "copied-old-slide"
            shutil.copytree(source, run)
            ledger_path = run / "evidence-ledger.json"
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            old_request_ids = [
                item["id"] for item in ledger
                if "instagram-slide-4" in item.get("used_in", [])
            ]
            for item in ledger:
                item["public_usage_mode"] = (
                    "exact_quote" if item.get("exact_quote") else "anonymized_synthesis"
                )
                item["source_role"] = (
                    "prior_announcement" if item["id"] in old_request_ids
                    else "case_proof" if item.get("kind") == "case"
                    else "offer_fact"
                )
                item["freshness_band"] = "recent"
                item["attribution_verified"] = True
            ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")

            manifest_path = run / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["program_evidence_map"] = [
                {
                    "block_id": f"block-{index}",
                    "pain_refs": [old_request_ids[index - 1]],
                    "program_action": "action",
                    "so_that": "outcome",
                }
                for index in range(1, 7)
            ]
            manifest["slide4_evidence_summary"] = {
                "request_refs": old_request_ids,
                "fresh_recent_non_prior_count": 0,
                "historical_carry_forward_count": 0,
                "unique_locator_count": 1,
                "carry_forward_reasons": {item: "claimed carry-forward" for item in old_request_ids},
            }
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            errors = validate_draft.validate(run, ROOT)

        self.assertIn("slide 4 needs at least four fresh/recent non-prior sources", errors)
        self.assertIn("slide 4 may use at most two prior-announcement sources", errors)
        self.assertIn("slide 4 needs at least four unique locators", errors)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Tests for the read-only GCONF announcement context builder."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("prepare_context.py")
SPEC = importlib.util.spec_from_file_location("prepare_context", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

VALIDATE_SCRIPT = Path(__file__).with_name("validate_run.py")


class PrepareContextTests(unittest.TestCase):
    def test_frontmatter_parses_block_and_inline_evidence(self) -> None:
        block = """---
type: pain
id: pain-test
label: "Тест"
review_status: approved
evidence:
  - telegram:1:2
  - youtube:x:3-4
---
# Тест
"""
        inline = """---
type: case
id: case-test
evidence: ["telegram:2:3"]
---
# Test
"""
        self.assertEqual(
            MODULE.parse_frontmatter(block)["evidence"],
            ["telegram:1:2", "youtube:x:3-4"],
        )
        self.assertEqual(
            MODULE.parse_frontmatter(inline)["evidence"], ["telegram:2:3"]
        )

    def test_rendered_evidence_keeps_exact_quote_and_url(self) -> None:
        text = """# Card
## Evidence

### 1. Channel · Telegram · 2026-07-17

- **Автор:** Person
- **Роль:** `primary`
- **Подтверждает:** Живой запрос
- **Visibility:** `public`

> первая строка
>
> вторая строка

- Locator: `telegram:1:2`
- [Открыть источник](https://t.me/example/2)
- Local source: `telegram/example.json`

<!-- evidence:end -->
"""
        evidence = MODULE.rendered_evidence(text)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["exact_quote"], "первая строка\n\nвторая строка")
        self.assertEqual(evidence[0]["source_url"], "https://t.me/example/2")
        self.assertEqual(evidence[0]["locator"], "telegram:1:2")
        self.assertTrue(evidence[0]["quote_verified_from_rendered_evidence"])

    def test_real_packet_preserves_database(self) -> None:
        root = MODULE.project_root()
        database = root / "knowledge/_index/gconf.sqlite"
        before = MODULE.sha256(database)
        packet = MODULE.build_packet(root, run_preflight=False)
        after = MODULE.sha256(database)
        self.assertEqual(before, after)
        self.assertTrue(packet["integrity"]["read_only_packet"])
        self.assertEqual(
            packet["site_requirement"]["role"],
            "canonical_live_baseline_of_latest_known_cohort",
        )
        self.assertGreaterEqual(packet["semantic_summary"]["total"], 1)
        self.assertEqual(
            packet["semantic_summary"]["case_origins"].get("internal_protagonist", 0),
            0,
        )
        self.assertEqual(packet["source_priority_policy"]["editorial_weights"]["freshness"], 35)
        self.assertTrue(
            all("freshness" in card for card in packet["semantic_cards"])
        )
        quoted = [card for card in packet["semantic_cards"] if card["evidence_quotes"]]
        self.assertGreater(len(quoted), 0)
        self.assertTrue(
            all(item["locator"] and item["exact_quote"] for card in quoted for item in card["evidence_quotes"])
        )

    def test_freshness_bands(self) -> None:
        now = MODULE.datetime(2026, 7, 17, tzinfo=MODULE.timezone.utc)
        self.assertEqual(MODULE.freshness("2026-07-17", now)["freshness_band"], "live")
        self.assertEqual(MODULE.freshness("2026-06-20", now)["freshness_band"], "fresh")
        self.assertEqual(MODULE.freshness("2026-05-01", now)["freshness_band"], "recent")
        self.assertEqual(MODULE.freshness("2025-01-01", now)["freshness_band"], "historical")

    def test_cli_emits_json_and_keeps_database_hash(self) -> None:
        root = MODULE.project_root()
        database = root / "knowledge/_index/gconf.sqlite"
        before = MODULE.sha256(database)
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--skip-preflight", "--compact"],
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
        )
        packet = json.loads(result.stdout)
        self.assertEqual(before, MODULE.sha256(database))
        self.assertEqual(packet["schema_version"], "1.0")
        self.assertIn("history", packet)
        self.assertIn("semantic_cards", packet)

    def test_current_analysis_run_validates(self) -> None:
        root = MODULE.project_root()
        run_dir = root / "research/announcement_analysis/runs/20260717T200356Z"
        if not run_dir.exists():
            self.skipTest("current analysis run has not been created")
        result = subprocess.run(
            [sys.executable, "-B", str(VALIDATE_SCRIPT), str(run_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

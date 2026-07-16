#!/usr/bin/env python3
"""Offline tests for deterministic GCONF knowledge helpers."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("knowledge_ingest.py")
SPEC = importlib.util.spec_from_file_location("knowledge_ingest", MODULE_PATH)
assert SPEC and SPEC.loader
knowledge_ingest = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = knowledge_ingest
SPEC.loader.exec_module(knowledge_ingest)


class KnowledgeIngestTests(unittest.TestCase):
    def test_flatten_telegram_rich_text(self) -> None:
        self.assertEqual(
            knowledge_ingest.flatten_text(
                ["hello ", {"text": "site", "href": "https://example.com"}]
            ),
            "hello site [https://example.com]",
        )

    def test_source_detection(self) -> None:
        self.assertEqual(
            knowledge_ingest.detect_source(
                knowledge_ingest.PROJECT_ROOT / "telegram/example.json"
            ),
            "telegram",
        )

    def test_srt_chunks_preserve_time(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test.srt"
            path.write_text(
                "1\n00:00:01,000 --> 00:00:03,500\nПервый текст\n\n"
                "2\n00:00:04,000 --> 00:00:06,000\nВторой текст\n",
                encoding="utf-8",
            )
            chunks = knowledge_ingest.parse_srt(path, "abc")
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["start_seconds"], 1.0)
        self.assertEqual(chunks[0]["end_seconds"], 6.0)
        self.assertEqual(chunks[0]["locator"], "youtube:abc:1-6")

    def test_slug_falls_back_for_cyrillic(self) -> None:
        self.assertTrue(knowledge_ingest.slugify("ИИ сообщество"))


if __name__ == "__main__":
    unittest.main()

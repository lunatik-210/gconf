#!/usr/bin/env python3
"""Offline unit tests for the GCONF YouTube collector."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("youtube_collect.py")
SPEC = importlib.util.spec_from_file_location("youtube_collect", MODULE_PATH)
assert SPEC and SPEC.loader
youtube_collect = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(youtube_collect)


class CollectorTests(unittest.TestCase):
    def test_safe_name_normalizes_path_separators(self) -> None:
        self.assertEqual(
            youtube_collect.safe_name("  AI/Agents: 2026  "),
            "AI - Agents - 2026",
        )

    def test_start_time_seconds_and_hms(self) -> None:
        self.assertEqual(
            youtube_collect.parse_start_seconds("https://youtu.be/x?t=673s"), 673
        )
        self.assertEqual(
            youtube_collect.parse_start_seconds("https://youtu.be/x?t=1h2m3s"),
            3723,
        )

    def test_chapter_context(self) -> None:
        chapters = [
            {"title": "A", "start_time": 0, "end_time": 10},
            {"title": "B", "start_time": 10, "end_time": 20},
        ]
        self.assertEqual(
            youtube_collect.chapter_for_time(chapters, 12)["title"], "B"
        )

    def test_channel_fallback(self) -> None:
        root = Path("/tmp/YouTube")
        self.assertEqual(
            youtube_collect.resolve_creator_dir(root, {"channel": "Matt Wolfe"}, None),
            root / "Matt Wolfe",
        )
        self.assertEqual(
            youtube_collect.resolve_creator_dir(root, {"uploader": "Uploader"}, None),
            root / "Uploader",
        )

    def test_caption_preference(self) -> None:
        info = {
            "subtitles": {"ru": []},
            "automatic_captions": {"ru-orig": [], "ru": []},
        }
        self.assertEqual(
            youtube_collect.caption_candidates(info, "ru"),
            ["ru", "ru-orig"],
        )

    def test_comment_counts(self) -> None:
        info = {
            "comment_count": 3,
            "comments": [
                {"parent": "root"},
                {"parent": "root"},
                {"parent": "abc"},
            ],
        }
        self.assertEqual(
            youtube_collect.comment_counts(info),
            (3, 3, 2, 1, "complete"),
        )

    def test_unavailable_comments_are_not_complete(self) -> None:
        self.assertEqual(
            youtube_collect.comment_counts({"comment_count": 5}),
            (5, 0, 0, 0, "unavailable"),
        )

    def test_reported_zero_comments_are_complete(self) -> None:
        self.assertEqual(
            youtube_collect.comment_counts({"comment_count": 0}),
            (0, 0, 0, 0, "complete"),
        )


if __name__ == "__main__":
    unittest.main()

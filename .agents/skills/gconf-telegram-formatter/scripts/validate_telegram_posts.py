#!/usr/bin/env python3
"""Validate editable Markdown handoffs for Telegram posts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


MAX_VISIBLE_CHARACTERS = 4096
LINK_RE = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+)\)")
ANY_MARKDOWN_LINK_RE = re.compile(r"\[[^\]\n]*\]\([^\n)]*\)")
HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
INTERNAL_PATTERNS = {
    "topic_id": re.compile(r"\btopic_id\b", re.IGNORECASE),
    "review_status": re.compile(r"\breview_status\b", re.IGNORECASE),
    "publication_ready": re.compile(r"\bpublication_ready\b", re.IGNORECASE),
    "coverage_delta": re.compile(r"\bcoverage_delta\b", re.IGNORECASE),
    "evidence_ledger": re.compile(r"\bevidence[-_ ]ledger\b", re.IGNORECASE),
    "quality_scores": re.compile(r"\bquality_scores\b", re.IGNORECASE),
    "source_revalidated_at": re.compile(
        r"\bsource_revalidated_at\b", re.IGNORECASE
    ),
}


def visible_text(markdown: str) -> str:
    """Return a conservative approximation of text visible after parsing."""
    text = LINK_RE.sub(lambda match: match.group(1), markdown)
    text = re.sub(r"(?m)^\s*[-+*]\s+", "• ", text)
    text = re.sub(r"[*_~`]", "", text)
    return text


def validate(path: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.is_file():
        return {"file": str(path), "valid": False, "errors": ["file not found"]}
    if path.suffix.lower() != ".md":
        errors.append("output must use the .md extension")

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"file": str(path), "valid": False, "errors": ["not valid UTF-8"]}

    if not content.strip():
        errors.append("post is empty")
    if content.startswith("---\n"):
        errors.append("YAML frontmatter is not allowed in a public post")
    if HTML_TAG_RE.search(content):
        errors.append("raw HTML is not allowed in the Markdown handoff")
    if content.count("**") % 2:
        errors.append("unbalanced bold markers")

    bold_spans = content.count("**") // 2
    if bold_spans > 2:
        errors.append(f"too many bold spans: {bold_spans}; maximum is 2")

    all_links = ANY_MARKDOWN_LINK_RE.findall(content)
    valid_links = LINK_RE.findall(content)
    if len(all_links) != len(valid_links):
        errors.append("named links must use a non-empty label and an http(s) URL")
    if content.count("](") != len(all_links):
        errors.append("malformed or incomplete Markdown link")

    list_items = re.findall(r"(?m)^\s*[-+*]\s+\S", content)
    if list_items and not 3 <= len(list_items) <= 7:
        errors.append(
            f"list has {len(list_items)} items; use 3–7 items or prose"
        )

    for label, pattern in INTERNAL_PATTERNS.items():
        if pattern.search(content):
            errors.append(f"internal field leaked into post: {label}")

    if re.search(r"\n{4,}", content):
        warnings.append("more than two consecutive blank lines")

    visible = visible_text(content)
    visible_characters = len(visible)
    if visible_characters > MAX_VISIBLE_CHARACTERS:
        errors.append(
            f"visible character limit exceeded: {visible_characters} > "
            f"{MAX_VISIBLE_CHARACTERS}"
        )
    elif visible_characters > 3600:
        warnings.append("post is close to Telegram's 4096-character limit")

    return {
        "file": str(path),
        "valid": not errors,
        "raw_characters": len(content),
        "visible_characters": visible_characters,
        "bold_spans": bold_spans,
        "named_links": len(valid_links),
        "list_items": len(list_items),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Telegram-ready GFM Markdown post files."
    )
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    results = [validate(path) for path in args.files]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(result["valid"] for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())

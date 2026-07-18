#!/usr/bin/env python3
"""Compose a scored radar backlog while reserving eligible source lanes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


RESERVED_LANES = ("protagonist", "gconf_case", "audience_reaction")


class CompositionError(RuntimeError):
    """Raised when candidate input is malformed."""


def score_key(item: dict[str, Any]) -> tuple[int, int, int, str]:
    score = item.get("score", {})
    return (
        int(score.get("priority_score", -1)),
        int(score.get("evidence_quality", -1)),
        int(score.get("freshness", -1)),
        str(item.get("event_date", "")),
    )


def eligible(item: dict[str, Any], minimum_score: int) -> bool:
    return (
        item.get("status") in {"recommended", "reserve"}
        and isinstance(item.get("score", {}).get("priority_score"), int)
        and item["score"]["priority_score"] >= minimum_score
    )


def compose(
    candidates: list[dict[str, Any]],
    maximum: int = 10,
    minimum_score: int = 65,
) -> dict[str, Any]:
    if not 1 <= maximum <= 10:
        raise CompositionError("maximum must be between 1 and 10")
    passing = [item for item in candidates if eligible(item, minimum_score)]
    topic_ids = [item.get("topic_id") for item in passing]
    if any(not topic_id for topic_id in topic_ids) or len(topic_ids) != len(set(topic_ids)):
        raise CompositionError("Passing candidates need unique topic IDs")
    ranked = sorted(passing, key=score_key, reverse=True)
    selected: list[dict[str, Any]] = []
    reserved: dict[str, str | None] = {}
    for lane in RESERVED_LANES:
        match = next(
            (
                item
                for item in ranked
                if item.get("primary_discovery_lane") == lane and item not in selected
            ),
            None,
        )
        reserved[lane] = match.get("topic_id") if match else None
        if match and len(selected) < maximum:
            selected.append(match)
    for item in ranked:
        if len(selected) >= maximum:
            break
        if item not in selected:
            selected.append(item)
    selected.sort(key=score_key, reverse=True)
    return {
        "schema_version": "1.0",
        "maximum": maximum,
        "minimum_score": minimum_score,
        "reserved_lanes": list(RESERVED_LANES),
        "reservation_result": reserved,
        "eligible_count": len(ranked),
        "selected_topic_ids": [item["topic_id"] for item in selected],
        "candidates": selected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="?", help="JSON list or object with candidates")
    parser.add_argument("--max-candidates", type=int, default=10)
    parser.add_argument("--minimum-score", type=int, default=65)
    args = parser.parse_args()
    try:
        raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
        payload = json.loads(raw)
        candidates = payload.get("candidates", []) if isinstance(payload, dict) else payload
        if not isinstance(candidates, list):
            raise CompositionError("Input must be a candidate list or an object with candidates")
        result = compose(candidates, args.max_candidates, args.minimum_score)
    except (OSError, json.JSONDecodeError, CompositionError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

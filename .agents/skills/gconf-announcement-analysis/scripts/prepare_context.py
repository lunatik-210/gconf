#!/usr/bin/env python3
"""Build a compact, read-only evidence packet for GCONF announcement analysis."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CARD_DIRS = (
    "actors",
    "cohorts",
    "pains",
    "cases",
    "trends",
    "technologies",
    "claims",
    "labs",
)

SCALAR_FIELDS = (
    "type",
    "id",
    "label",
    "status",
    "review_status",
    "first_seen",
    "last_seen",
    "source_wave",
    "actor_kind",
    "pain_kind",
    "case_origin",
    "reporting_mode",
    "proof_level",
    "artifact_status",
    "initial_task",
    "process",
    "result",
    "behavior_shift",
    "limitations",
    "positioning",
    "event_kind",
    "start_date",
    "end_date",
)


class ContextError(RuntimeError):
    """Raised when the evidence packet cannot be prepared safely."""


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    return text[4:end] if end >= 0 else ""


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value in {"null", "~"}:
        return None
    if value in {"true", "false"}:
        return value == "true"
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(value)
            except (SyntaxError, ValueError):
                return value
    return value


def parse_frontmatter(text: str) -> dict[str, Any]:
    raw = frontmatter(text)
    data: dict[str, Any] = {}
    lines = raw.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):(?:\s*(.*))?$", line)
        if not match:
            index += 1
            continue
        key, value = match.group(1), match.group(2) or ""
        if key == "evidence":
            if value.strip():
                parsed = parse_scalar(value)
                data[key] = parsed if isinstance(parsed, list) else []
            else:
                items: list[str] = []
                cursor = index + 1
                while cursor < len(lines):
                    item = re.match(r"^\s+-\s+(.+?)\s*$", lines[cursor])
                    if not item:
                        break
                    items.append(str(parse_scalar(item.group(1))))
                    cursor += 1
                data[key] = items
                index = cursor - 1
        elif key in SCALAR_FIELDS:
            data[key] = parse_scalar(value)
        index += 1
    return data


def body_abstract(text: str) -> str:
    title = re.search(r"^# .+$", text, flags=re.MULTILINE)
    if not title:
        return ""
    tail = text[title.end() :]
    stop = re.search(r"^## Evidence|^<!-- evidence:start -->", tail, flags=re.MULTILINE)
    body = tail[: stop.start()] if stop else tail
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    return re.sub(r"\s+", " ", " ".join(paragraphs[:2]))[:900]


def rendered_evidence(text: str) -> list[dict[str, Any]]:
    marker = text.find("## Evidence")
    if marker < 0:
        return []
    section = text[marker:]
    end = section.find("<!-- evidence:end -->")
    if end >= 0:
        section = section[:end]
    headings = list(re.finditer(r"^### \d+\. .+$", section, flags=re.MULTILINE))
    items: list[dict[str, Any]] = []
    for index, heading in enumerate(headings):
        stop = headings[index + 1].start() if index + 1 < len(headings) else len(section)
        block = section[heading.end() : stop]

        def field(label: str) -> str | None:
            match = re.search(rf"^- \*\*{re.escape(label)}:\*\*\s*(.+)$", block, re.MULTILINE)
            return match.group(1).strip().strip("`") if match else None

        quote_lines: list[str] = []
        for line in block.splitlines():
            if line == ">":
                quote_lines.append("")
            elif line.startswith("> "):
                quote_lines.append(line[2:])
        quote = "\n".join(quote_lines).strip()
        locator_match = re.search(r"^- Locator:\s*`([^`]+)`", block, re.MULTILINE)
        url_match = re.search(r"^- \[Открыть источник\]\(([^)]+)\)", block, re.MULTILINE)
        local_match = re.search(r"^- Local source:\s*`([^`]+)`", block, re.MULTILINE)
        heading_text = heading.group(0).split(". ", 1)[1]
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})\s*$", heading_text)
        if not locator_match or not quote:
            continue
        items.append(
            {
                "locator": locator_match.group(1),
                "role": field("Роль"),
                "author": field("Автор"),
                "source_date": date_match.group(1) if date_match else None,
                "visibility": field("Visibility"),
                "exact_quote": quote,
                "supports": field("Подтверждает"),
                "source_url": url_match.group(1) if url_match else None,
                "local_source": local_match.group(1) if local_match else None,
                "quote_verified_from_rendered_evidence": True,
            }
        )
    return items


def freshness(value: Any, now: datetime) -> dict[str, Any]:
    if not value:
        return {"freshness_days": None, "freshness_band": "unknown"}
    try:
        observed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        try:
            observed = datetime.strptime(str(value), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return {"freshness_days": None, "freshness_band": "unknown"}
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=timezone.utc)
    days = max(0, (now - observed.astimezone(timezone.utc)).days)
    if days <= 14:
        band = "live"
    elif days <= 45:
        band = "fresh"
    elif days <= 90:
        band = "recent"
    else:
        band = "historical"
    return {"freshness_days": days, "freshness_band": band}


def collect_cards(root: Path, now: datetime) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for directory in CARD_DIRS:
        for path in sorted((root / "knowledge" / directory).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            card = parse_frontmatter(text)
            if not card.get("id"):
                continue
            card["evidence"] = card.get("evidence", [])
            card["evidence_quotes"] = rendered_evidence(text)
            card["abstract"] = body_abstract(text)
            card["path"] = path.relative_to(root).as_posix()
            card["freshness"] = freshness(card.get("last_seen"), now)
            cards.append(card)
    return cards


def run_json(root: Path, command: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ContextError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n{result.stderr.strip()}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ContextError(f"Command did not return JSON: {' '.join(command)}") from exc


def preflight(root: Path) -> dict[str, Any]:
    python = sys.executable
    ingest = root / ".agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py"
    extract = root / ".agents/skills/gconf-insight-extract/scripts/insight_extract.py"
    results = {
        "knowledge_validate": run_json(root, [python, "-B", str(ingest), "validate"]),
        "insight_validate": run_json(root, [python, "-B", str(extract), "validate"]),
        "scopes": {},
    }
    for scope in ("next-gconf", "lab-signals"):
        status = run_json(
            root,
            [python, "-B", str(extract), "status", "--scope", scope],
        )
        results["scopes"][scope] = status
    invalid = not results["knowledge_validate"].get("ok") or not results[
        "insight_validate"
    ].get("ok")
    incomplete = any(
        status.get("counts", {}).get("pending", 0)
        or status.get("counts", {}).get("stale", 0)
        for status in results["scopes"].values()
    )
    results["ready"] = not invalid and not incomplete
    if not results["ready"]:
        raise ContextError(
            "Knowledge preflight is not ready. Run $gconf-knowledge-ingest, then "
            "$gconf-insight-extract, and repeat this command."
        )
    return results


def history(root: Path) -> dict[str, Any]:
    summary_path = root / "research/gconf_history/analysis_summary.json"
    raw = json.loads(summary_path.read_text(encoding="utf-8"))
    launches = []
    for launch in raw.get("launches", []):
        launches.append(
            {
                key: launch.get(key)
                for key in (
                    "label",
                    "start",
                    "announcement_date",
                    "positioning",
                    "status",
                    "daily_use",
                    "business_process",
                    "behavior_change",
                    "community_practice",
                    "automation_agents",
                    "content_creation",
                    "meta_skills",
                )
            }
        )
    return {
        "launches": launches,
        "source_paths": [
            "research/gconf_history/announcement_corpus.md",
            "research/gconf_history/GCONF_history_report.md",
            "research/gconf_history/analysis_summary.json",
        ],
    }


def latest_instagram_offer(root: Path) -> dict[str, Any]:
    path = root / "Instagram/gconf.io.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    messages = raw.get("messages", []) if isinstance(raw, dict) else raw
    messages = sorted(messages, key=lambda item: item.get("date", ""), reverse=True)
    latest = messages[0] if messages else {}
    return {
        "profile_url": raw.get("profile_url") if isinstance(raw, dict) else None,
        "collected_at": raw.get("collected_at") if isinstance(raw, dict) else None,
        "latest_post": {
            "id": latest.get("id"),
            "date": latest.get("date"),
            "url": latest.get("url"),
            "caption": latest.get("caption"),
            "metrics": latest.get("metrics"),
            "slides_count": latest.get("media", {}).get("slides_count_detected"),
        },
        "role": "adaptation_and_audience_response_not_offer_source_of_truth",
    }


def build_packet(root: Path, run_preflight: bool = True) -> dict[str, Any]:
    database = root / "knowledge/_index/gconf.sqlite"
    now = datetime.now(timezone.utc)
    cards = collect_cards(root, now)
    review_counts = Counter(str(card.get("review_status", "unknown")) for card in cards)
    type_counts = Counter(str(card.get("type", "unknown")) for card in cards)
    origins = Counter(
        str(card.get("case_origin"))
        for card in cards
        if card.get("type") == "case" and card.get("case_origin")
    )
    packet = {
        "schema_version": "1.0",
        "generated_at": now.isoformat(),
        "project_root": str(root),
        "preflight": preflight(root) if run_preflight else {"ready": None, "skipped": True},
        "site_requirement": {
            "url": "https://www.gconf.io/",
            "role": "canonical_live_baseline_of_latest_known_cohort",
            "requires_live_fetch": True,
            "fallback_allowed": False,
        },
        "history": history(root),
        "instagram": latest_instagram_offer(root),
        "semantic_summary": {
            "total": len(cards),
            "review_status": dict(sorted(review_counts.items())),
            "types": dict(sorted(type_counts.items())),
            "case_origins": dict(sorted(origins.items())),
            "known_gap": (
                "No case with case_origin=internal_protagonist; do not relabel "
                "participant or community cases."
            ),
        },
        "semantic_cards": cards,
        "source_roles": {
            "telegram_announcements": "historical_product_trajectory",
            "live_site": "current_offer_baseline",
            "instagram_gconf": "channel_adaptation_and_public_response",
            "internal_participants": "cohort_experience",
            "gconf_community": "post_cohort_or_unattributed_internal_work",
            "dima_matskevich": "internal_protagonist",
            "matt_wolfe_and_wes_roth": "external_protagonists",
            "official_labs": "primary_technical_signals_not_protagonists",
        },
        "source_priority_policy": {
            "principle": (
                "Prefer fresher evidence within comparable verification quality; "
                "freshness never converts an unsupported claim into a fact."
            ),
            "freshness_bands_days": {
                "live": "0-14",
                "fresh": "15-45",
                "recent": "46-90",
                "historical": ">90",
            },
            "editorial_weights": {
                "freshness": 35,
                "next_offer_relevance": 25,
                "evidence_strength": 20,
                "audience_specificity": 10,
                "novelty_vs_current_offer": 10,
            },
            "mandatory_constraints_not_scored": [
                "live gconf.io current-offer baseline",
                "canonical GCONF tone of voice",
                "brand spine: environment, agency, process, meta-skills, behavior change",
            ],
        },
        "integrity": {
            "database_path": database.relative_to(root).as_posix(),
            "database_sha256": sha256(database),
            "read_only_packet": True,
        },
    }
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=project_root())
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip command preflight; intended only for unit tests and debugging.",
    )
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    try:
        packet = build_packet(args.root.resolve(), run_preflight=not args.skip_preflight)
    except (ContextError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(
        json.dumps(
            packet,
            ensure_ascii=False,
            indent=None if args.compact else 2,
            sort_keys=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

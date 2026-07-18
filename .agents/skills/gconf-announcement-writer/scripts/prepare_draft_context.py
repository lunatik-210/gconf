#!/usr/bin/env python3
"""Prepare a compact, read-only context packet for GCONF announcement writing."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ContextError(RuntimeError):
    pass


def writer_freshness(value: Any, now: datetime) -> dict[str, Any]:
    """Classify evidence freshness for announcement writing.

    The writer intentionally uses broader bands than the strategic-analysis
    helper: current audience language stays usable for 90 days, while prior
    announcements remain structurally useful but never count as fresh demand.
    """
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
    if days <= 30:
        band = "fresh"
    elif days <= 90:
        band = "recent"
    else:
        band = "historical"
    return {"freshness_days": days, "freshness_band": band}


def evidence_source_role(author: Any) -> str:
    normalized = str(author or "").casefold()
    organizer_markers = (
        "gconf",
        "саппорт",
        "ai lovers",
        "записки ai энтузиаста",
        "matskevich",
        "dzmitry",
        "мацкевич",
    )
    if any(marker in normalized for marker in organizer_markers):
        return "organizer_interpretation"
    return "audience_voice"


def pain_evidence(cards: list[dict[str, Any]], now: datetime) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    approved: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for card in cards:
        if not str(card.get("path", "")).startswith("knowledge/pains/"):
            continue
        target = approved if card.get("review_status") == "approved" else candidates
        for evidence in card.get("evidence_quotes", []):
            item = {
                "card_id": card.get("id"),
                "card_label": card.get("label"),
                "status": card.get("status"),
                "review_status": card.get("review_status"),
                "source_wave": card.get("source_wave"),
                "source_role": evidence_source_role(evidence.get("author")),
                **evidence,
                **writer_freshness(evidence.get("source_date"), now),
            }
            target.append(item)

    def sort_key(item: dict[str, Any]) -> tuple[int, int, str]:
        days = item.get("freshness_days")
        return (
            days if isinstance(days, int) else 10**9,
            0 if item.get("source_role") == "audience_voice" else 1,
            str(item.get("locator") or ""),
        )

    approved.sort(key=sort_key)
    candidates.sort(key=sort_key)
    return approved, candidates


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def load_analysis_helpers(root: Path):
    path = root / ".agents/skills/gconf-announcement-analysis/scripts/prepare_context.py"
    spec = importlib.util.spec_from_file_location("gconf_analysis_context", path)
    if not spec or not spec.loader:
        raise ContextError(f"Cannot load analysis context helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_direction_decision(
    root: Path, decision_id: str, analysis_run: str
) -> dict[str, Any]:
    path = root / ".agents/skills/gconf-editorial-gates/scripts/editorial_gates.py"
    spec = importlib.util.spec_from_file_location("gconf_editorial_gates", path)
    if not spec or not spec.loader:
        raise ContextError(f"Editorial gate dependency is missing: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        result = module.resolve(
            root,
            argparse.Namespace(
                decision_id=decision_id,
                workflow="announcement",
                gate_type="announcement_direction_selection",
                upstream_ref=analysis_run,
                selected_ref=[],
            ),
        )
    except module.GateError as exc:
        raise ContextError(f"Announcement direction gate failed: {exc}") from exc
    return result["decision"]


def resolve_fact_decision(
    root: Path, decision_id: str, analysis_run: str, expected_ref: str
) -> dict[str, Any]:
    path = root / ".agents/skills/gconf-editorial-gates/scripts/editorial_gates.py"
    spec = importlib.util.spec_from_file_location("gconf_editorial_gates_facts", path)
    if not spec or not spec.loader:
        raise ContextError(f"Editorial gate dependency is missing: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        result = module.resolve(
            root,
            argparse.Namespace(
                decision_id=decision_id,
                workflow="announcement",
                gate_type="offer_fact_and_cta_allowlist",
                upstream_ref=analysis_run,
                selected_ref=[expected_ref],
            ),
        )
    except module.GateError as exc:
        raise ContextError(f"Offer fact and CTA gate failed: {exc}") from exc
    return result["decision"]


def flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(flatten_text(item) for item in value)
    if isinstance(value, dict):
        return str(value.get("text", ""))
    return ""


def find_message(path: Path, message_id: str) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    for message in data.get("messages", []):
        if str(message.get("id")) == message_id:
            item = dict(message)
            if "text" in item:
                item["plain_text"] = flatten_text(item["text"])
            return item
    raise ContextError(f"Message {message_id} not found in {path}")


def file_snapshot(paths: list[Path], root: Path) -> list[dict[str, Any]]:
    result = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        result.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": digest,
                "bytes": path.stat().st_size,
            }
        )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-run", type=Path, required=True)
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--facts-decision-id", required=True)
    parser.add_argument("--direction-id")
    parser.add_argument("--product-name", required=True)
    parser.add_argument("--voice-mode", choices=("GCONF", "Dima"), default="GCONF")
    parser.add_argument("--address", choices=("vy", "ty"), default="vy")
    parser.add_argument("--facts-json", type=Path)
    parser.add_argument("--telegram-locator", default="telegram:1633415027:1040")
    parser.add_argument("--instagram-locator", default="instagram:gconf.io:DafUhD0F5Yh")
    parser.add_argument("--screenshots-dir", type=Path, default=Path("Instagram/Прошлый Анонс"))
    parser.add_argument("--card-id", action="append", default=[])
    return parser.parse_args()


def prepare(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    run = args.analysis_run if args.analysis_run.is_absolute() else root / args.analysis_run
    manifest_path = run / "manifest.json"
    analysis_path = run / "analysis.md"
    if not manifest_path.exists() or not analysis_path.exists():
        raise ContextError(f"Invalid analysis run: {run}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    analysis_ref = run.relative_to(root).as_posix()
    decision = resolve_direction_decision(root, args.decision_id, analysis_ref)
    if len(decision["selected_refs"]) != 1:
        raise ContextError("Announcement direction decision must select exactly one direction")
    direction_id = decision["selected_refs"][0]
    if args.direction_id and args.direction_id != direction_id:
        raise ContextError("--direction-id does not match the confirmed decision")
    direction = next(
        (item for item in manifest.get("directions", []) if item.get("id") == direction_id),
        None,
    )
    if not direction:
        raise ContextError(f"Direction not found: {direction_id}")

    tg_match = re.fullmatch(r"telegram:[^:]+:(\d+)", args.telegram_locator)
    ig_match = re.fullmatch(r"instagram:[^:]+:([^:]+)", args.instagram_locator)
    if not tg_match or not ig_match:
        raise ContextError("Previous announcement locators are malformed")
    telegram = find_message(root / "telegram/GCONF : AI LOVERS.json", tg_match.group(1))
    instagram = find_message(root / "Instagram/gconf.io.json", ig_match.group(1))

    screenshot_dir = args.screenshots_dir if args.screenshots_dir.is_absolute() else root / args.screenshots_dir
    screenshots = sorted(screenshot_dir.glob("*.jpg"))
    if len(screenshots) != 6:
        raise ContextError(f"Expected six prior-announcement screenshots, found {len(screenshots)}")

    facts: dict[str, Any] = {}
    facts_ref = "allowlist:none"
    if args.facts_json:
        path = args.facts_json if args.facts_json.is_absolute() else root / args.facts_json
        facts = json.loads(path.read_text(encoding="utf-8"))
        facts_ref = path.resolve().relative_to(root.resolve()).as_posix()
    resolve_fact_decision(root, args.facts_decision_id, analysis_ref, facts_ref)

    helper = load_analysis_helpers(root)
    now = datetime.now(timezone.utc)
    cards = helper.collect_cards(root, now)
    wanted = set(args.card_id)
    wanted.update(item.get("card_id") for item in manifest.get("case_shortlist", []))
    wanted.update(item.get("card_id") for item in manifest.get("audience_signals", []))
    selected_cards = [card for card in cards if card.get("id") in wanted]
    selected_cards.sort(
        key=lambda card: (
            card.get("review_status") != "approved",
            str(card.get("last_seen") or ""),
        )
    )
    approved_pains, candidate_pains = pain_evidence(cards, now)

    return {
        "schema_version": "2.0",
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "decision_refs": [args.decision_id, args.facts_decision_id],
        "workflow_status": "selected",
        "publication_status": "not_ready",
        "inputs": {
            "analysis_run": analysis_ref,
            "direction_id": direction_id,
            "product_name": args.product_name,
            "voice_mode": args.voice_mode,
            "address": args.address,
            "telegram_locator": args.telegram_locator,
            "instagram_locator": args.instagram_locator,
        },
        "direction": direction,
        "current_offer_baseline": manifest.get("current_offer_baseline", {}),
        "historical_trajectory": manifest.get("historical_trajectory", []),
        "case_shortlist": manifest.get("case_shortlist", []),
        "audience_signals": manifest.get("audience_signals", []),
        "approved_pain_evidence": approved_pains,
        "candidate_pain_evidence": candidate_pains,
        "source_roles": [
            "audience_voice",
            "organizer_interpretation",
            "prior_announcement",
            "case_proof",
            "offer_fact",
        ],
        "freshness_policy": {
            "fresh_max_days": 30,
            "recent_max_days": 90,
            "historical_min_days": 91,
            "prior_announcement_counts_as_current_demand": False,
        },
        "evidence_index": [
            item for item in manifest.get("evidence_index", [])
            if item.get("id") in set(direction.get("evidence_refs", []))
        ],
        "semantic_cards": selected_cards,
        "confirmed_facts": facts,
        "previous_telegram": {
            "id": telegram.get("id"),
            "date": telegram.get("date"),
            "from": telegram.get("from"),
            "plain_text": telegram.get("plain_text"),
            "url": "https://t.me/gptlovers/1040",
        },
        "previous_instagram": {
            "id": instagram.get("id"),
            "date": instagram.get("date"),
            "from": instagram.get("from"),
            "url": instagram.get("url"),
            "caption": instagram.get("caption"),
            "slides_count": instagram.get("media", {}).get("slides_count_detected"),
        },
        "screenshot_snapshot": file_snapshot(screenshots, root),
    }


def main() -> int:
    args = parse_args()
    try:
        packet = prepare(args, project_root())
    except (ContextError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate an announcement-analysis Markdown/JSON run and its exact quotes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import prepare_context


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "run_id",
    "generated_at",
    "review_status",
    "selected_direction",
    "source_snapshot",
    "current_offer_baseline",
    "historical_trajectory",
    "audience_signals",
    "protagonist_movements",
    "external_ai_signals",
    "case_shortlist",
    "source_priority",
    "strategic_classification",
    "directions",
    "unknown_future_cohort_details",
    "ingestion_queue",
    "evidence_index",
}

REQUIRED_UNKNOWNS = {
    "date",
    "price",
    "duration",
    "format",
    "curriculum",
    "speakers_and_protagonists",
    "capacity",
    "commercial_terms",
    "claimed_results",
    "cta_destination",
}

REQUIRED_SECTIONS = (
    "# Анализ следующего анонса GCONF",
    "## Вердикт по данным и свежести",
    "## Ядро текущего потока: gconf.io",
    "## Историческая траектория Telegram-анонсов",
    "## Сохранить, развить, перестать повторять, добавить",
    "## Приоритет источников и свежесть",
    "## Внутренние и внешние запросы аудитории",
    "## Движения протагонистов",
    "## Внешние AI-сигналы",
    "## Кейсы для доказательства",
    "## Пробелы, противоречия и неизвестные",
    "## Направления следующего анонса",
    "## Рекомендация",
    "## Evidence appendix",
)


def walk(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def validate(run_dir: Path, project_root: Path) -> list[str]:
    errors: list[str] = []
    analysis_path = run_dir / "analysis.md"
    manifest_path = run_dir / "manifest.json"
    if not analysis_path.exists():
        errors.append("analysis.md is missing")
    if not manifest_path.exists():
        errors.append("manifest.json is missing")
    if errors:
        return errors

    analysis = analysis_path.read_text(encoding="utf-8")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"manifest.json is invalid JSON: {exc}"]

    missing = REQUIRED_TOP_LEVEL - set(manifest)
    if missing:
        errors.append(f"manifest missing keys: {sorted(missing)}")
    for section in REQUIRED_SECTIONS:
        if section not in analysis:
            errors.append(f"analysis missing section: {section}")

    if manifest.get("selected_direction") is not None:
        errors.append("selected_direction must remain null for human review")
    if manifest.get("review_status") != "draft":
        errors.append("review_status must be draft")
    schema_version = str(manifest.get("schema_version", "1.0"))
    if schema_version not in {"1.0", "2.0"}:
        errors.append("schema_version must be 1.0 or 2.0")
    if schema_version == "2.0":
        if manifest.get("decision_refs") != []:
            errors.append("schema 2.0 analysis decision_refs must remain empty")
        if manifest.get("workflow_status") != "awaiting_human_selection":
            errors.append("schema 2.0 analysis must await human selection")
        if manifest.get("publication_status") != "not_ready":
            errors.append("schema 2.0 analysis publication_status must be not_ready")
    directions = manifest.get("directions", [])
    if len(directions) not in {2, 3}:
        errors.append("directions must contain two or three items")
    direction_ids = [item.get("id") for item in directions]
    if len(direction_ids) != len(set(direction_ids)):
        errors.append("direction IDs must be unique")
    for direction_id in direction_ids:
        if direction_id and direction_id not in analysis:
            errors.append(f"direction missing from analysis.md: {direction_id}")

    recommendation_order = manifest.get("recommendation_order", direction_ids)
    if recommendation_order != direction_ids:
        errors.append("direction order and recommendation order differ")
    unknowns = set(manifest.get("unknown_future_cohort_details", []))
    if not REQUIRED_UNKNOWNS.issubset(unknowns):
        errors.append(
            f"future cohort unknowns missing: {sorted(REQUIRED_UNKNOWNS - unknowns)}"
        )

    site = manifest.get("source_snapshot", {}).get("site", {})
    if site.get("url") != "https://www.gconf.io/" or site.get("status") != "live":
        errors.append("gconf.io must be recorded as the live current-offer baseline")
    if not site.get("accessed_at"):
        errors.append("live site accessed_at is missing")

    evidence_ids = {item.get("id") for item in manifest.get("evidence_index", [])}
    for direction in directions:
        unresolved = set(direction.get("evidence_refs", [])) - evidence_ids
        if unresolved:
            errors.append(
                f"direction {direction.get('id')} has unresolved evidence refs: {sorted(unresolved)}"
            )

    cards = {
        card["id"]: card
        for card in prepare_context.collect_cards(
            project_root, prepare_context.datetime.now(prepare_context.timezone.utc)
        )
    }
    for item in walk(manifest):
        if item.get("quote_verified") is not True:
            continue
        quote = item.get("exact_quote")
        card_id = item.get("card_id")
        locator = item.get("locator")
        if not quote or not card_id or not locator:
            errors.append("verified quote lacks exact_quote, card_id, or locator")
            continue
        card = cards.get(card_id)
        if not card:
            errors.append(f"verified quote references missing card: {card_id}")
            continue
        matched = any(
            evidence.get("locator") == locator
            and quote in evidence.get("exact_quote", "")
            and (evidence.get("source_url") or evidence.get("local_source"))
            for evidence in card.get("evidence_quotes", [])
        )
        if not matched:
            errors.append(f"quote does not match rendered evidence: {card_id} / {locator}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--root", type=Path, default=prepare_context.project_root())
    args = parser.parse_args()
    errors = validate(args.run_dir.resolve(), args.root.resolve())
    result = {"ok": not errors, "run_dir": str(args.run_dir.resolve()), "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

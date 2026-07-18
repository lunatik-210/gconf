#!/usr/bin/env python3
"""Validate a GCONF news-radar run without changing it."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_FILES = {"backlog.md", "manifest.json", "audit.md"}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "run_id",
    "generated_at",
    "review_status",
    "selected_topic_ids",
    "parameters",
    "source_snapshot",
    "candidates",
    "rejected_signals",
    "evidence_index",
    "coverage_index",
    "ingestion_queue",
    "output_files",
}
REQUIRED_SECTIONS = (
    "# GCONF News Radar",
    "## Вердикт по данным и свежести",
    "## Покрытие источников",
    "## Приоритетный backlog",
    "## Резерв",
    "## Отклонённые сильные сигналы",
    "## Покрытие GCONF и дубли",
    "## Пробелы и ingestion queue",
    "## Human review",
    "## Evidence appendix",
)
LEGACY_REQUIRED_SECTIONS = tuple(
    section for section in REQUIRED_SECTIONS if section != "## Покрытие источников"
)
REQUIRED_CANDIDATE = {
    "topic_id",
    "working_title",
    "event_summary",
    "event_date",
    "focus",
    "why_now",
    "ai_market_significance",
    "gconf_theme",
    "gconf_relevance",
    "audience",
    "previous_mode",
    "changed_mode",
    "closest_coverage_refs",
    "coverage_delta",
    "recommended_format",
    "experiment_or_question",
    "facts",
    "inferences",
    "limitations",
    "editorial_risks",
    "evidence_refs",
    "source_requirement",
    "score",
    "status",
    "priority_rationale",
}
REQUIRED_V11_CANDIDATE = {
    "primary_discovery_lane",
    "supporting_lanes",
    "window_expansion_reason",
}
SCORE_MAX = {
    "market_relevance": 20,
    "gconf_relevance": 20,
    "coverage_novelty": 20,
    "evidence_quality": 20,
    "freshness": 10,
    "actionability": 10,
    "risk_penalty": 20,
}
FORMATS = {
    "flash",
    "release_explainer",
    "trend_translation",
    "gconf_field_note",
    "story_lore",
}
EVIDENCE_STATUS = {"fact", "inference", "proposal", "unindexed_observation"}
SOURCE_KINDS = {
    "official_primary",
    "independent_primary",
    "secondary",
    "social",
    "local_semantic_card",
}
FRESHNESS_BANDS = {"live", "fresh", "recent", "historical", "unknown"}
REQUIRED_EVIDENCE = {
    "id",
    "evidence_status",
    "source_kind",
    "publisher",
    "title",
    "published_at",
    "accessed_at",
    "url",
    "local_source",
    "locator",
    "claim_supported",
    "publisher_claim",
    "freshness_days",
    "freshness_band",
    "limitation",
}
REQUIRED_V11_EVIDENCE = {
    "evidence_role",
    "parent_locator",
    "visibility",
    "permission_status",
}
REQUIRED_COVERAGE = {
    "id",
    "platform",
    "published_at",
    "locator",
    "url",
    "title",
    "excerpt",
    "coverage_role",
}
PUBLIC_COPY_KEYS = {"headline", "lead", "post", "draft", "cta_copy", "public_copy"}
LANES = {
    "official_release",
    "protagonist",
    "gconf_case",
    "audience_reaction",
    "ecosystem_posts",
    "semantic_context",
}
RESERVED_LANES = {"protagonist", "gconf_case", "audience_reaction"}
EVIDENCE_ROLES = {
    "event_confirmation",
    "protagonist_observation",
    "audience_reaction",
    "gconf_case",
    "historical_context",
}
VISIBILITIES = {"public", "internal", "editorial"}
PERMISSION_STATUS = {"not_required", "required", "confirmed", "unknown"}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_candidate(
    item: dict[str, Any],
    expected_status: str | None,
    evidence: dict[str, dict[str, Any]],
    coverage: set[str],
    schema_version: str = "1.0",
    generated_at: str | None = None,
    local_window_days: int = 30,
    local_max_days: int = 60,
) -> list[str]:
    errors: list[str] = []
    topic_id = item.get("topic_id", "<missing-topic-id>")
    missing = REQUIRED_CANDIDATE - set(item)
    if schema_version in {"1.1", "2.0"}:
        missing |= REQUIRED_V11_CANDIDATE - set(item)
    if missing:
        errors.append(f"{topic_id}: missing fields {sorted(missing)}")
        return errors
    if not re.fullmatch(r"news-\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*", str(topic_id)):
        errors.append(f"{topic_id}: invalid topic_id format")
    if expected_status and item.get("status") != expected_status:
        errors.append(f"{topic_id}: expected status {expected_status}")
    if item.get("status") not in {"recommended", "reserve", "reject"}:
        errors.append(f"{topic_id}: invalid status")
    if item.get("recommended_format") not in FORMATS:
        errors.append(f"{topic_id}: invalid recommended_format")
    for field in (
        "working_title",
        "event_summary",
        "focus",
        "why_now",
        "ai_market_significance",
        "gconf_theme",
        "gconf_relevance",
        "audience",
        "previous_mode",
        "changed_mode",
        "coverage_delta",
        "experiment_or_question",
        "priority_rationale",
    ):
        if not nonempty(item.get(field)):
            errors.append(f"{topic_id}: {field} must be non-empty")
    score = item.get("score", {})
    missing_scores = (set(SCORE_MAX) | {"priority_score"}) - set(score)
    if missing_scores:
        errors.append(f"{topic_id}: missing score fields {sorted(missing_scores)}")
    else:
        for key, maximum in SCORE_MAX.items():
            value = score.get(key)
            if not isinstance(value, int) or not 0 <= value <= maximum:
                errors.append(f"{topic_id}: invalid score {key}={value}")
        expected = sum(score.get(key, 0) for key in SCORE_MAX if key != "risk_penalty")
        expected -= score.get("risk_penalty", 0)
        if score.get("priority_score") != expected:
            errors.append(f"{topic_id}: priority_score must equal {expected}")
        status = item.get("status")
        if status == "recommended" and expected < 80:
            errors.append(f"{topic_id}: recommended score must be at least 80")
        if status == "reserve" and not 65 <= expected <= 79:
            errors.append(f"{topic_id}: reserve score must be 65–79")
        if status == "reject" and expected >= 65 and not item.get("rejection_reasons"):
            errors.append(f"{topic_id}: high-scoring reject needs rejection_reasons")
    evidence_refs = item.get("evidence_refs", [])
    unresolved = set(evidence_refs) - set(evidence)
    if unresolved:
        errors.append(f"{topic_id}: unresolved evidence refs {sorted(unresolved)}")
    unresolved_coverage = set(item.get("closest_coverage_refs", [])) - coverage
    if unresolved_coverage:
        errors.append(f"{topic_id}: unresolved coverage refs {sorted(unresolved_coverage)}")
    sources = [evidence[ref] for ref in evidence_refs if ref in evidence]
    if schema_version in {"1.1", "2.0"}:
        lane = item.get("primary_discovery_lane")
        if lane not in LANES:
            errors.append(f"{topic_id}: invalid primary_discovery_lane")
        supporting = item.get("supporting_lanes")
        if not isinstance(supporting, list) or any(value not in LANES for value in supporting):
            errors.append(f"{topic_id}: supporting_lanes must contain valid lanes")
        if not any(source.get("visibility") == "public" for source in sources):
            errors.append(f"{topic_id}: a public evidence source is required")
        for source in sources:
            if source.get("visibility") == "internal" and source.get("permission_status") != "required":
                errors.append(f"{topic_id}: internal evidence must require permission")
        try:
            generated = datetime.fromisoformat(str(generated_at).replace("Z", "+00:00"))
            event = datetime.fromisoformat(str(item.get("event_date"))).replace(tzinfo=timezone.utc)
            if generated.tzinfo is None:
                generated = generated.replace(tzinfo=timezone.utc)
            age_days = max(0, (generated.astimezone(timezone.utc) - event).days)
            reason = item.get("window_expansion_reason")
            if age_days > local_max_days:
                errors.append(f"{topic_id}: event is older than local_max_days")
            elif age_days > local_window_days and not nonempty(reason):
                errors.append(f"{topic_id}: extended local window needs a reason")
        except (TypeError, ValueError):
            errors.append(f"{topic_id}: event_date or generated_at is invalid")
    requirement = item.get("source_requirement")
    if requirement == "product_release" and not any(
        source.get("source_kind") == "official_primary" for source in sources
    ):
        errors.append(f"{topic_id}: product release lacks official primary source")
    if requirement == "broad_trend":
        publishers = {
            source.get("publisher")
            for source in sources
            if source.get("source_kind") in {"official_primary", "independent_primary"}
            and source.get("publisher")
        }
        if len(publishers) < 2:
            errors.append(f"{topic_id}: broad trend needs two independent publishers")
    if PUBLIC_COPY_KEYS & set(item):
        errors.append(f"{topic_id}: public-copy fields are forbidden in radar output")
    return errors


def validate(run_dir: Path) -> list[str]:
    errors: list[str] = []
    missing_files = [name for name in REQUIRED_FILES if not (run_dir / name).exists()]
    if missing_files:
        return [f"missing required files: {sorted(missing_files)}"]
    backlog = (run_dir / "backlog.md").read_text(encoding="utf-8")
    manifest_path = run_dir / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"manifest.json is invalid JSON: {exc}"]
    schema_version = str(manifest.get("schema_version", "1.0"))
    sections = REQUIRED_SECTIONS if schema_version in {"1.1", "2.0"} else LEGACY_REQUIRED_SECTIONS
    for section in sections:
        if section not in backlog:
            errors.append(f"backlog missing section: {section}")
    if schema_version not in {"1.0", "1.1", "2.0"}:
        errors.append("schema_version must be 1.0, 1.1, or 2.0")
    missing = REQUIRED_TOP_LEVEL - set(manifest)
    if missing:
        errors.append(f"manifest missing keys: {sorted(missing)}")
    if manifest.get("selected_topic_ids") != []:
        errors.append("selected_topic_ids must remain empty for human review")
    if manifest.get("review_status") != "draft":
        errors.append("review_status must be draft")
    if schema_version == "2.0":
        if manifest.get("decision_refs") != []:
            errors.append("schema 2.0 radar decision_refs must remain empty")
        if manifest.get("workflow_status") != "awaiting_human_selection":
            errors.append("schema 2.0 radar must await human selection")
        if manifest.get("publication_status") != "not_ready":
            errors.append("schema 2.0 radar publication_status must be not_ready")
    if set(manifest.get("output_files", [])) != REQUIRED_FILES:
        errors.append("output_files must list exactly the three required files")
    candidates = manifest.get("candidates", [])
    maximum = manifest.get("parameters", {}).get("max_candidates", 10)
    if not isinstance(maximum, int) or not 1 <= maximum <= 10:
        errors.append("parameters.max_candidates must be 1–10")
        maximum = 10
    if len(candidates) > maximum:
        errors.append("candidate count exceeds max_candidates")
    parameters = manifest.get("parameters", {})
    local_window_days = parameters.get("local_window_days", 30)
    local_max_days = parameters.get("local_max_days", 60)
    if schema_version in {"1.1", "2.0"}:
        if local_window_days != 30 or local_max_days != 60:
            errors.append("schema 1.1+ requires local windows of 30 and 60 days")
        source_review = manifest.get("source_review")
        if not isinstance(source_review, dict):
            errors.append("schema 1.1+ requires source_review")
            source_review = {}
        missing_lanes = LANES - set(source_review)
        if missing_lanes:
            errors.append(f"source_review missing lanes {sorted(missing_lanes)}")
        for lane in LANES & set(source_review):
            review = source_review[lane]
            required_review = {
                "available_items",
                "meaningful_items",
                "noise_excluded",
                "pages_expected",
                "pages_reviewed",
                "complete",
                "freshest_published_at",
                "oldest_published_at",
                "fingerprint",
                "signals_found",
                "passing_candidates",
            }
            missing_review = required_review - set(review)
            if missing_review:
                errors.append(f"source_review.{lane} missing {sorted(missing_review)}")
                continue
            if review.get("complete") is not True:
                errors.append(f"source_review.{lane} must be complete")
            if review.get("pages_reviewed", -1) < review.get("pages_expected", 0):
                errors.append(f"source_review.{lane} pages are incomplete")
            for key in (
                "available_items",
                "meaningful_items",
                "noise_excluded",
                "pages_expected",
                "pages_reviewed",
                "signals_found",
                "passing_candidates",
            ):
                if not isinstance(review.get(key), int) or review[key] < 0:
                    errors.append(f"source_review.{lane}.{key} must be a non-negative integer")
    evidence_items = manifest.get("evidence_index", [])
    evidence = {item.get("id"): item for item in evidence_items if item.get("id")}
    if len(evidence) != len(evidence_items):
        errors.append("evidence IDs must be present and unique")
    for item in evidence_items:
        missing_evidence = REQUIRED_EVIDENCE - set(item)
        if schema_version in {"1.1", "2.0"}:
            missing_evidence |= REQUIRED_V11_EVIDENCE - set(item)
        if missing_evidence:
            errors.append(f"evidence {item.get('id')}: missing fields {sorted(missing_evidence)}")
        if item.get("evidence_status") not in EVIDENCE_STATUS:
            errors.append(f"evidence {item.get('id')}: invalid evidence_status")
        if item.get("source_kind") not in SOURCE_KINDS:
            errors.append(f"evidence {item.get('id')}: invalid source_kind")
        if item.get("freshness_band") not in FRESHNESS_BANDS:
            errors.append(f"evidence {item.get('id')}: invalid freshness_band")
        if not isinstance(item.get("publisher_claim"), bool):
            errors.append(f"evidence {item.get('id')}: publisher_claim must be boolean")
        if schema_version in {"1.1", "2.0"}:
            if item.get("evidence_role") not in EVIDENCE_ROLES:
                errors.append(f"evidence {item.get('id')}: invalid evidence_role")
            if item.get("visibility") not in VISIBILITIES:
                errors.append(f"evidence {item.get('id')}: invalid visibility")
            if item.get("permission_status") not in PERMISSION_STATUS:
                errors.append(f"evidence {item.get('id')}: invalid permission_status")
            if item.get("visibility") == "internal" and item.get("permission_status") != "required":
                errors.append(f"evidence {item.get('id')}: internal evidence must require permission")
        if not item.get("url") and not item.get("local_source"):
            errors.append(f"evidence {item.get('id')}: source location is missing")
        for field in ("publisher", "title", "published_at", "accessed_at", "locator", "claim_supported"):
            if not nonempty(item.get(field)):
                errors.append(f"evidence {item.get('id')}: {field} must be non-empty")
    coverage_items = manifest.get("coverage_index", [])
    coverage_ids = [item.get("id") for item in coverage_items]
    if any(not value for value in coverage_ids) or len(coverage_ids) != len(set(coverage_ids)):
        errors.append("coverage IDs must be present and unique")
    for item in coverage_items:
        missing_coverage = REQUIRED_COVERAGE - set(item)
        if missing_coverage:
            errors.append(f"coverage {item.get('id')}: missing fields {sorted(missing_coverage)}")
        for field in ("platform", "published_at", "locator", "title", "excerpt", "coverage_role"):
            if not nonempty(item.get(field)):
                errors.append(f"coverage {item.get('id')}: {field} must be non-empty")
    topic_ids: list[str] = []
    for item in candidates:
        topic_ids.append(item.get("topic_id"))
        errors.extend(
            validate_candidate(
                item,
                None,
                evidence,
                set(coverage_ids),
                schema_version,
                manifest.get("generated_at"),
                local_window_days,
                local_max_days,
            )
        )
        if item.get("status") == "reject":
            errors.append(f"{item.get('topic_id')}: rejected item belongs in rejected_signals")
    for item in manifest.get("rejected_signals", []):
        topic_ids.append(item.get("topic_id"))
        errors.extend(
            validate_candidate(
                item,
                "reject",
                evidence,
                set(coverage_ids),
                schema_version,
                manifest.get("generated_at"),
                local_window_days,
                local_max_days,
            )
        )
    if len(topic_ids) != len(set(topic_ids)):
        errors.append("topic IDs must be unique across candidates and rejected_signals")
    if schema_version in {"1.1", "2.0"}:
        source_review = manifest.get("source_review", {})
        present_lanes = {item.get("primary_discovery_lane") for item in candidates}
        for lane in RESERVED_LANES:
            if source_review.get(lane, {}).get("passing_candidates", 0) > 0 and lane not in present_lanes:
                errors.append(f"reserved passing lane is absent from backlog: {lane}")
    if re.search(r"^##\s+(?:Заголовок|Лид|CTA|Пост)\b", backlog, flags=re.I | re.M):
        errors.append("backlog contains forbidden public-copy section")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    errors = validate(run_dir)
    print(json.dumps({"ok": not errors, "run_dir": str(run_dir), "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

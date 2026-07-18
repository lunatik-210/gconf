#!/usr/bin/env python3
"""Validate a GCONF news-writer run and its human-selection boundary."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


BASE_FILES = {"brief.md", "evidence-ledger.json", "coverage.json", "audit.md", "manifest.json"}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "run_id",
    "generated_at",
    "review_status",
    "publication_ready",
    "radar_run",
    "selected_topic_ids",
    "human_selection",
    "voice_mode",
    "address",
    "cta_mode",
    "posts",
    "unresolved_items",
    "output_files",
}
POST_FIELDS = {
    "topic_id",
    "file",
    "format",
    "focus",
    "behavioral_transition",
    "tension",
    "primary_evidence_ref",
    "evidence_refs",
    "coverage_delta",
    "cta",
    "source_revalidated_at",
    "central_fact_status",
    "format_change_reason",
    "quality_scores",
    "publication_ready",
}
FORMAT_RANGES = {
    "flash": (40, 90),
    "release_explainer": (150, 260),
    "trend_translation": (220, 360),
    "gconf_field_note": (150, 300),
    "story_lore": (150, 260),
}
BANNED = (
    "ии изменит всё",
    "нейросети уже изменили мир навсегда",
    "революционный курс",
    "уникальная возможность",
    "профессия будущего",
    "секретные промпты",
    "раскройте безграничный потенциал",
    "гарантированный результат",
    "подойдёт абсолютно каждому",
    "подойдет абсолютно каждому",
)
QUALITY_KEYS = {"taste", "philosophy", "research", "process_quality", "growth"}
LEDGER_FIELDS = {
    "id",
    "topic_id",
    "evidence_status",
    "source_kind",
    "publisher",
    "title",
    "published_at",
    "revalidated_at",
    "url",
    "local_source",
    "locator",
    "claim_supported",
    "publisher_claim",
    "availability_status",
    "limitation",
    "used_in",
}
V11_LEDGER_FIELDS = {"evidence_role", "parent_locator", "visibility", "permission_status"}
EVIDENCE_STATUS = {"fact", "inference", "proposal"}
SOURCE_KINDS = {
    "official_primary",
    "independent_primary",
    "secondary",
    "social",
    "local_semantic_card",
}
AVAILABILITY = {"confirmed", "partial", "unavailable", "not_applicable", "unknown"}
EVIDENCE_ROLES = {
    "event_confirmation",
    "protagonist_observation",
    "audience_reaction",
    "gconf_case",
    "historical_context",
}
VISIBILITIES = {"public", "internal", "editorial"}
PERMISSION_STATUS = {"not_required", "required", "confirmed", "unknown"}
COVERAGE_FIELDS = {
    "topic_id",
    "closest_coverage_refs",
    "coverage_delta",
    "central_claim_overlap",
    "new_editorial_unit",
}


def words(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text, flags=re.UNICODE))


def load_json(path: Path, label: str, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label} is invalid JSON: {exc}")
        return None


def validate(run_dir: Path) -> list[str]:
    errors: list[str] = []
    missing_base = [name for name in BASE_FILES if not (run_dir / name).exists()]
    if missing_base:
        return [f"missing required files: {sorted(missing_base)}"]
    manifest = load_json(run_dir / "manifest.json", "manifest.json", errors)
    ledger = load_json(run_dir / "evidence-ledger.json", "evidence-ledger.json", errors)
    coverage = load_json(run_dir / "coverage.json", "coverage.json", errors)
    if manifest is None or ledger is None or coverage is None:
        return errors
    schema_version = str(manifest.get("schema_version", "1.0"))
    if schema_version not in {"1.0", "1.1", "2.0"}:
        errors.append("schema_version must be 1.0, 1.1, or 2.0")
    missing = REQUIRED_TOP_LEVEL - set(manifest)
    if missing:
        errors.append(f"manifest missing keys: {sorted(missing)}")
    selected = manifest.get("selected_topic_ids", [])
    if not selected:
        errors.append("selected_topic_ids must contain explicit human selections")
    if len(selected) != len(set(selected)):
        errors.append("selected_topic_ids must be unique")
    if manifest.get("human_selection") is not True:
        errors.append("human_selection must be true")
    if schema_version == "2.0":
        decision_refs = manifest.get("decision_refs")
        if not isinstance(decision_refs, list) or len(decision_refs) != 1:
            errors.append("schema 2.0 writer requires one topic-selection decision")
        if manifest.get("workflow_status") != "awaiting_copy_approval":
            errors.append("schema 2.0 writer must await copy approval")
        if manifest.get("publication_status") != "not_ready":
            errors.append("schema 2.0 writer publication_status must be not_ready")
    if manifest.get("review_status") != "ready_for_human_review":
        errors.append("review_status must be ready_for_human_review")
    if manifest.get("voice_mode") not in {"GCONF", "Dima"}:
        errors.append("voice_mode must be GCONF or Dima")
    if manifest.get("address") not in {"vy", "ty"}:
        errors.append("address must be vy or ty")
    if manifest.get("cta_mode") not in {"editorial", "commercial"}:
        errors.append("cta_mode must be editorial or commercial")
    posts = manifest.get("posts", [])
    if len(posts) != len(selected):
        errors.append("post count must equal selected topic count")
    post_topic_ids = [post.get("topic_id") for post in posts]
    if post_topic_ids != selected:
        errors.append("post order and topic IDs must match selected_topic_ids")
    evidence_by_id = {item.get("id"): item for item in ledger if item.get("id")}
    if len(evidence_by_id) != len(ledger):
        errors.append("evidence ledger IDs must be present and unique")
    for item in ledger:
        missing_ledger = LEDGER_FIELDS - set(item)
        if schema_version in {"1.1", "2.0"}:
            missing_ledger |= V11_LEDGER_FIELDS - set(item)
        if missing_ledger:
            errors.append(f"evidence {item.get('id')}: missing fields {sorted(missing_ledger)}")
        if item.get("evidence_status") not in EVIDENCE_STATUS:
            errors.append(f"evidence {item.get('id')}: invalid evidence_status")
        if item.get("source_kind") not in SOURCE_KINDS:
            errors.append(f"evidence {item.get('id')}: invalid source_kind")
        if item.get("availability_status") not in AVAILABILITY:
            errors.append(f"evidence {item.get('id')}: invalid availability_status")
        if not isinstance(item.get("publisher_claim"), bool):
            errors.append(f"evidence {item.get('id')}: publisher_claim must be boolean")
        if schema_version in {"1.1", "2.0"}:
            if item.get("evidence_role") not in EVIDENCE_ROLES:
                errors.append(f"evidence {item.get('id')}: invalid evidence_role")
            if item.get("visibility") not in VISIBILITIES:
                errors.append(f"evidence {item.get('id')}: invalid visibility")
            if item.get("permission_status") not in PERMISSION_STATUS:
                errors.append(f"evidence {item.get('id')}: invalid permission_status")
            if item.get("visibility") == "internal" and item.get("permission_status") not in {"required", "confirmed"}:
                errors.append(f"evidence {item.get('id')}: internal evidence needs required or confirmed permission")
        for field in ("publisher", "title", "published_at", "revalidated_at", "locator", "claim_supported"):
            if not str(item.get(field, "")).strip():
                errors.append(f"evidence {item.get('id')}: {field} must be non-empty")
        if not isinstance(item.get("used_in"), list) or not item.get("used_in"):
            errors.append(f"evidence {item.get('id')}: used_in must be a non-empty list")
    coverage_by_topic = {item.get("topic_id"): item for item in coverage if item.get("topic_id")}
    if len(coverage_by_topic) != len(coverage):
        errors.append("coverage topic IDs must be present and unique")
    for item in coverage:
        missing_coverage = COVERAGE_FIELDS - set(item)
        if missing_coverage:
            errors.append(f"coverage {item.get('topic_id')}: missing fields {sorted(missing_coverage)}")
        if item.get("central_claim_overlap") not in {"none", "partial", "high"}:
            errors.append(f"coverage {item.get('topic_id')}: invalid central_claim_overlap")
    expected_files = set(BASE_FILES)
    all_posts_ready = True
    for post in posts:
        topic_id = post.get("topic_id", "<missing-topic-id>")
        missing_post = POST_FIELDS - set(post)
        if missing_post:
            errors.append(f"{topic_id}: missing post fields {sorted(missing_post)}")
            continue
        expected_name = f"news-{topic_id}.md"
        if post.get("file") != expected_name:
            errors.append(f"{topic_id}: file must be {expected_name}")
        path = run_dir / expected_name
        expected_files.add(expected_name)
        if not path.exists():
            errors.append(f"{topic_id}: public post file is missing")
            continue
        text = path.read_text(encoding="utf-8").strip()
        post_format = post.get("format")
        if post_format not in FORMAT_RANGES:
            errors.append(f"{topic_id}: invalid format")
        else:
            minimum, maximum = FORMAT_RANGES[post_format]
            count = words(text)
            if not minimum <= count <= maximum:
                errors.append(f"{topic_id}: {post_format} word count {count} outside {minimum}–{maximum}")
        lowered = text.casefold()
        for phrase in BANNED:
            if phrase in lowered:
                errors.append(f"{topic_id}: banned cliché found: {phrase}")
        if post.get("central_fact_status") != "unchanged":
            errors.append(f"{topic_id}: central fact changed; drafting should have stopped")
        if not post.get("source_revalidated_at"):
            errors.append(f"{topic_id}: source_revalidated_at is missing")
        cta = post.get("cta", {})
        if cta.get("type") not in {"editorial", "commercial"} or not str(cta.get("text", "")).strip():
            errors.append(f"{topic_id}: exactly one typed CTA is required")
        refs = post.get("evidence_refs", [])
        if post.get("primary_evidence_ref") not in refs:
            errors.append(f"{topic_id}: primary evidence must be included in evidence_refs")
        unresolved_refs = set(refs) - set(evidence_by_id)
        if unresolved_refs:
            errors.append(f"{topic_id}: unresolved evidence refs {sorted(unresolved_refs)}")
        for ref in refs:
            item = evidence_by_id.get(ref, {})
            if item.get("topic_id") != topic_id:
                errors.append(f"{topic_id}: evidence {ref} belongs to another topic")
            if not item.get("revalidated_at"):
                errors.append(f"{topic_id}: evidence {ref} was not revalidated")
            if not item.get("url") and not item.get("local_source"):
                errors.append(f"{topic_id}: evidence {ref} has no source location")
            if item.get("availability_status") in {"partial", "unavailable", "unknown"} and post.get("publication_ready") is True:
                errors.append(f"{topic_id}: unresolved availability cannot be publication-ready")
            if schema_version in {"1.1", "2.0"} and item.get("permission_status") in {"required", "unknown"} and post.get("publication_ready") is True:
                errors.append(f"{topic_id}: unresolved permission cannot be publication-ready")
        primary = evidence_by_id.get(post.get("primary_evidence_ref"), {})
        if (
            schema_version in {"1.1", "2.0"}
            and post.get("format") == "release_explainer"
            and primary.get("evidence_role") in {"audience_reaction", "protagonist_observation"}
        ):
            errors.append(f"{topic_id}: social observation cannot be primary product proof")
        coverage_item = coverage_by_topic.get(topic_id)
        if not coverage_item:
            errors.append(f"{topic_id}: coverage entry is missing")
        else:
            if coverage_item.get("new_editorial_unit") is not True:
                errors.append(f"{topic_id}: topic is not a new editorial unit")
            if not str(coverage_item.get("coverage_delta", "")).strip():
                errors.append(f"{topic_id}: coverage delta is missing")
        scores = post.get("quality_scores", {})
        if set(scores) != QUALITY_KEYS:
            errors.append(f"{topic_id}: quality_scores must contain exactly {sorted(QUALITY_KEYS)}")
        else:
            invalid = [key for key, value in scores.items() if not isinstance(value, int) or not 0 <= value <= 2]
            if invalid:
                errors.append(f"{topic_id}: invalid quality scores {invalid}")
            elif sum(scores.values()) < 8 or scores["research"] == 0:
                errors.append(f"{topic_id}: quality threshold is not met")
        if not isinstance(post.get("publication_ready"), bool):
            errors.append(f"{topic_id}: publication_ready must be boolean")
        all_posts_ready = all_posts_ready and post.get("publication_ready") is True
    actual_output = set(manifest.get("output_files", []))
    if actual_output != expected_files:
        errors.append("output_files must list exactly all required artifacts")
    expected_publication = all_posts_ready and not manifest.get("unresolved_items")
    if manifest.get("publication_ready") is not expected_publication:
        errors.append("top-level publication_ready does not match post readiness and unresolved_items")
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

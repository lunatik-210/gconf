#!/usr/bin/env python3
"""Validate a GCONF Telegram/Instagram announcement draft run."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_FILES = (
    "brief.md",
    "telegram.md",
    "instagram-carousel.md",
    "instagram-caption.md",
    "evidence-ledger.json",
    "audit.md",
    "manifest.json",
)
SLIDES = tuple(f"## Слайд {index}" for index in range(1, 7))
PLACEHOLDERS = ("[ДАТА — НУЖНО ПОДТВЕРДИТЬ]", "[CTA — НУЖНО ПОДТВЕРДИТЬ]")
PERMISSIONS = {"confirmed", "previously_public_by_gconf", "unknown"}
SOURCE_ROLES = {
    "audience_voice",
    "organizer_interpretation",
    "prior_announcement",
    "case_proof",
    "offer_fact",
}
FRESHNESS_BANDS = {"fresh", "recent", "historical", "not_applicable"}
PUBLIC_USAGE_MODES = {
    "exact_quote",
    "attributed_case",
    "anonymized_synthesis",
    "internal_only",
}


def validate_cta_policy(public_copy: str, manifest: dict[str, Any]) -> list[str]:
    """Require either the exact confirmed CTA or the canonical placeholder."""
    confirmed_cta = manifest.get("confirmed_facts", {}).get("cta")
    placeholder = "[CTA — НУЖНО ПОДТВЕРДИТЬ]"
    errors: list[str] = []
    if confirmed_cta:
        if not isinstance(confirmed_cta, str) or not confirmed_cta.strip():
            errors.append("confirmed CTA must be a non-empty string")
        elif confirmed_cta not in public_copy:
            errors.append("exact confirmed CTA is missing from public copy")
        if placeholder in public_copy:
            errors.append("CTA placeholder must be removed when CTA is confirmed")
    elif placeholder not in public_copy:
        errors.append(f"required placeholder missing: {placeholder}")
    return errors


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def load_cards(root: Path) -> dict[str, dict[str, Any]]:
    path = root / ".agents/skills/gconf-announcement-analysis/scripts/prepare_context.py"
    spec = importlib.util.spec_from_file_location("gconf_analysis_context", path)
    if not spec or not spec.loader:
        return {}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {card["id"]: card for card in module.collect_cards(root, module.datetime.now(module.timezone.utc))}


def raw_source_contains(path: Path, quote: str) -> bool:
    if path.suffix.lower() != ".json":
        return quote in path.read_text(encoding="utf-8")
    data = json.loads(path.read_text(encoding="utf-8"))

    def strings(value: Any):
        if isinstance(value, str):
            yield value
        elif isinstance(value, list):
            for item in value:
                yield from strings(item)
        elif isinstance(value, dict):
            for item in value.values():
                yield from strings(item)

    return any(quote in value for value in strings(data))


def validate(run_dir: Path, root: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (run_dir / name).exists():
            errors.append(f"missing file: {name}")
    if errors:
        return errors

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    ledger = json.loads((run_dir / "evidence-ledger.json").read_text(encoding="utf-8"))
    telegram = (run_dir / "telegram.md").read_text(encoding="utf-8")
    carousel = (run_dir / "instagram-carousel.md").read_text(encoding="utf-8")
    caption = (run_dir / "instagram-caption.md").read_text(encoding="utf-8")
    public_copy = "\n".join((telegram, carousel, caption))

    if manifest.get("review_status") != "draft":
        errors.append("review_status must be draft")
    if manifest.get("publication_ready") is not False:
        errors.append("publication_ready must be false while placeholders remain")
    if manifest.get("voice_mode") not in {"GCONF", "Dima"}:
        errors.append("invalid voice_mode")
    if manifest.get("address") not in {"vy", "ty"}:
        errors.append("invalid address")
    if manifest.get("channels") != ["telegram", "instagram"]:
        errors.append("channels must be telegram and instagram")
    if not manifest.get("direction_id"):
        errors.append("direction_id is missing")
    if str(manifest.get("schema_version")) == "2.0":
        decision_refs = manifest.get("decision_refs")
        if not isinstance(decision_refs, list) or len(decision_refs) != 1:
            errors.append("schema 2.0 draft requires one direction-selection decision")
        if manifest.get("workflow_status") != "awaiting_copy_approval":
            errors.append("schema 2.0 draft must await copy approval")
        if manifest.get("publication_status") != "not_ready":
            errors.append("schema 2.0 draft publication_status must be not_ready")

    positions = [carousel.find(prefix) for prefix in SLIDES]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        errors.append("carousel must contain six ordered slide headings")
    if len(re.findall(r"^## Слайд \d", carousel, flags=re.MULTILINE)) != 6:
        errors.append("carousel must contain exactly six slides")

    date_placeholder = PLACEHOLDERS[0]
    if date_placeholder not in public_copy:
        errors.append(f"required placeholder missing: {date_placeholder}")
    errors.extend(validate_cta_policy(public_copy, manifest))
    if re.search(r"\b27\s+июля\b|\bgconf\s*1[34]\b", public_copy, re.IGNORECASE):
        errors.append("historical cohort date or number leaked into future draft")
    facts = manifest.get("confirmed_facts", {})
    allowed_numbers = {1, 2, 3, 4, 5, 6}
    allowed_numbers.update(
        value for value in facts.values()
        if isinstance(value, int) and not isinstance(value, bool)
    )
    found_numbers = {
        int(match.replace(" ", "").replace("\u00a0", ""))
        for match in re.findall(r"(?<!\w)\d{1,3}(?:[ \u00a0]\d{3})*(?!\w)", public_copy)
    }
    if unexpected := found_numbers - allowed_numbers:
        errors.append(f"public copy contains numbers outside confirmed allowlist: {sorted(unexpected)}")
    if manifest.get("address") == "vy" and re.search(
        r"\b(ты|тебе|тебя|твой|твоя|твои|сделаешь|пойм[её]шь|собер[её]шь)\b",
        public_copy,
        re.IGNORECASE,
    ):
        errors.append("second-person singular leaked into vy-mode public copy")

    cards = load_cards(root)
    ledger_ids: set[str] = set()
    ledger_by_id: dict[str, dict[str, Any]] = {}
    for item in ledger:
        evidence_id = item.get("id")
        if not evidence_id or evidence_id in ledger_ids:
            errors.append(f"missing or duplicate evidence id: {evidence_id}")
        ledger_ids.add(evidence_id)
        ledger_by_id[evidence_id] = item
        permission = item.get("publication_permission")
        if permission not in PERMISSIONS:
            errors.append(f"invalid publication permission: {evidence_id}")
        usage_mode = item.get("public_usage_mode")
        if usage_mode not in PUBLIC_USAGE_MODES:
            errors.append(f"invalid public usage mode: {evidence_id}")
        if item.get("source_role") not in SOURCE_ROLES:
            errors.append(f"invalid source role: {evidence_id}")
        if item.get("freshness_band") not in FRESHNESS_BANDS:
            errors.append(f"invalid freshness band: {evidence_id}")
        if item.get("attribution_verified") is not True:
            errors.append(f"unverified attribution: {evidence_id}")
        anonymous_public = (
            permission == "unknown"
            and usage_mode == "anonymized_synthesis"
            and item.get("visibility") == "public"
        )
        if item.get("publish_ready") and (
            item.get("review_status") == "candidate"
            or (permission == "unknown" and not anonymous_public)
        ):
            errors.append(f"unsafe publish_ready evidence: {evidence_id}")
        quote = item.get("exact_quote")
        if quote:
            card = cards.get(item.get("card_id"))
            if card:
                matched = any(
                    evidence.get("locator") == item.get("locator")
                    and quote in evidence.get("exact_quote", "")
                    for evidence in card.get("evidence_quotes", [])
                )
                if not matched:
                    errors.append(f"quote does not match rendered evidence: {evidence_id}")
            elif item.get("quote_verified_against") == "visual_screenshot":
                local_source = item.get("local_source")
                if not local_source or not (root / local_source).exists():
                    errors.append(f"visual quote source is missing: {evidence_id}")
            elif item.get("quote_verified_against") == "raw_local_source":
                local_source = item.get("local_source")
                source_path = root / str(local_source or "")
                if not local_source or not source_path.exists():
                    errors.append(f"raw quote source is missing: {evidence_id}")
                elif not raw_source_contains(source_path, str(quote)):
                    errors.append(f"quote does not match raw source: {evidence_id}")
            else:
                errors.append(f"quoted evidence references missing card: {evidence_id}")
        if anonymous_public and quote:
            normalized_quote = re.sub(r"\s+", " ", str(quote)).strip(" «»\"").casefold()
            normalized_copy = re.sub(r"\s+", " ", public_copy).casefold()
            if normalized_quote and normalized_quote in normalized_copy:
                errors.append(f"unknown-permission quote leaked verbatim: {evidence_id}")

    program_map = manifest.get("program_evidence_map", [])
    if len(program_map) != 6:
        errors.append("program_evidence_map must contain exactly six blocks")
    for block in program_map:
        block_id = block.get("block_id") or "missing"
        pain_refs = block.get("pain_refs")
        if not isinstance(pain_refs, list) or not pain_refs:
            errors.append(f"program block has no pain_refs: {block_id}")
            continue
        if not str(block.get("so_that") or "").strip():
            errors.append(f"program block has no so_that outcome: {block_id}")
        if not str(block.get("program_action") or "").strip():
            errors.append(f"program block has no program_action: {block_id}")
        if missing_pains := set(pain_refs) - ledger_ids:
            errors.append(f"program block has unresolved pain refs {block_id}: {sorted(missing_pains)}")

    slide4 = manifest.get("slide4_evidence_summary", {})
    request_refs = slide4.get("request_refs", [])
    if len(request_refs) != 6:
        errors.append("slide4_evidence_summary must contain six request refs")
    if unresolved_slide4 := set(request_refs) - ledger_ids:
        errors.append(f"slide 4 has unresolved request refs: {sorted(unresolved_slide4)}")
    slide4_items = [ledger_by_id[item] for item in request_refs if item in ledger_by_id]
    current = [
        item for item in slide4_items
        if item.get("source_role") != "prior_announcement"
        and item.get("freshness_band") in {"fresh", "recent"}
    ]
    historical = [item for item in slide4_items if item.get("freshness_band") == "historical"]
    prior = [item for item in slide4_items if item.get("source_role") == "prior_announcement"]
    locators = {item.get("locator") for item in slide4_items if item.get("locator")}
    if len(current) < 4:
        errors.append("slide 4 needs at least four fresh/recent non-prior sources")
    if len(historical) > 2:
        errors.append("slide 4 may use at most two historical carry-forward sources")
    if len(prior) > 2:
        errors.append("slide 4 may use at most two prior-announcement sources")
    if len(locators) < 4:
        errors.append("slide 4 needs at least four unique locators")
    locator_counts: dict[str, int] = {}
    for item in slide4_items:
        locator = str(item.get("locator") or "")
        locator_counts[locator] = locator_counts.get(locator, 0) + 1
    if any(count >= 4 for count in locator_counts.values()):
        errors.append("four or more slide-4 requests come from one locator")
    carry_reasons = slide4.get("carry_forward_reasons", {})
    for item in historical + prior:
        if not str(carry_reasons.get(item.get("id")) or "").strip():
            errors.append(f"historical slide-4 request lacks carry-forward reason: {item.get('id')}")
    reported = {
        "fresh_recent_non_prior_count": len(current),
        "historical_carry_forward_count": len(historical),
        "unique_locator_count": len(locators),
    }
    for key, value in reported.items():
        if slide4.get(key) != value:
            errors.append(f"slide4 evidence summary mismatch for {key}: expected {value}")

    refs = set(manifest.get("evidence_refs", {}).get("telegram", []))
    refs.update(manifest.get("evidence_refs", {}).get("instagram", []))
    refs.update(request_refs)
    if missing := refs - ledger_ids:
        errors.append(f"manifest has unresolved evidence refs: {sorted(missing)}")
    ready = {item["id"] for item in ledger if item.get("publish_ready")}
    if unsafe := refs - ready:
        errors.append(f"public channels depend on non-publish-ready evidence: {sorted(unsafe)}")
    ready_quotes = [
        str(item.get("exact_quote") or "").strip("«»")
        for item in ledger
        if item.get("publish_ready") and item.get("exact_quote")
    ]
    for quote in re.findall(r"«([^»]+)»", public_copy):
        if not any(quote == source_quote or quote in source_quote for source_quote in ready_quotes):
            errors.append(f"public quotation has no publish-ready ledger match: {quote[:80]}")

    audit = (run_dir / "audit.md").read_text(encoding="utf-8")
    score_match = re.search(r"Итого:\s*(\d+)/10", audit)
    if not score_match or int(score_match.group(1)) < 8:
        errors.append("audit must record a rubric result of at least 8/10")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--root", type=Path, default=project_root())
    args = parser.parse_args()
    try:
        errors = validate(args.run_dir.resolve(), args.root.resolve())
    except (OSError, json.JSONDecodeError) as exc:
        errors = [str(exc)]
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

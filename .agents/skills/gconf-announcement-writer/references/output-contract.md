# Announcement writer output contract

Create a unique UTC run at
`research/announcement_drafts/runs/<YYYYMMDDTHHMMSSZ>/`. Do not overwrite runs
or create a mutable `latest` copy.

## Required files

- `brief.md` — neutral internal writing brief;
- `telegram.md` — clean standalone Telegram copy;
- `instagram-carousel.md` — exactly six slide-copy sections;
- `instagram-caption.md` — clean caption;
- `evidence-ledger.json` — proof and publication basis;
- `audit.md` — fact, voice, permission, and channel audit;
- `manifest.json` — run inputs, allowlist, output status, and evidence refs.

## Brief

Record voice mode, address, audience, one behavioral transition, one tension,
3–5 meaning pillars, inherited offer/program elements, genuinely new delta,
case shortlist, audience-language bank, confirmed facts, unknowns, one CTA,
and growth signals. Add a six-item `program_evidence_map`; every item records a
live pain, `pain_refs`, the program action, a concrete `so_that` outcome, and
locators. Label internal judgments as `fact`, `inference`, or `proposal`.

## Public drafts

`telegram.md` contains only the proposed public post. It must not be a slide
transcript and must follow: shift → tension → frame → experience/evidence →
terms/limits → one CTA.

`instagram-carousel.md` contains these headings exactly once and in order:

1. `## Слайд 1 — Обложка`
2. `## Слайд 2 — За 3 недели вы`
3. `## Слайд 3 — Программа потока`
4. `## Слайд 4 — С чем приходят`
5. `## Слайд 5 — С чем уходят`
6. `## Слайд 6 — CTA и условия`

Slide 4 uses sourced audience language. At least four of its six requests must
use fresh/recent non-prior-announcement evidence from at least four unique
locators. At most two may be historical carry-forward requests, each with a
reason. Slide 5 uses cases with explicit origin and publication basis.
`instagram-caption.md` adds context; it does not repeat every slide.

Unknown date and CTA must remain exactly:

- `[ДАТА — НУЖНО ПОДТВЕРДИТЬ]`;
- `[CTA — НУЖНО ПОДТВЕРДИТЬ]`.

When `confirmed_facts.cta` is present, use that exact string in both Instagram
artifacts and the same primary action in Telegram, remove the CTA placeholder,
and record the confirmation basis in the evidence ledger. A confirmed CTA
never authorizes a new bot, link, keyword, or destination beyond its exact text.

## Evidence ledger

Write a JSON array. Every entry contains:

```json
{
  "id": "stable-evidence-id",
  "kind": "case | quote | pain | claim | offer_fact | prior_format",
  "status": "fact | inference | proposal",
  "review_status": "approved | candidate | not_applicable",
  "card_id": null,
  "case_origin": null,
  "proof_level": null,
  "exact_quote": null,
  "author": null,
  "source_date": "YYYY-MM-DD",
  "visibility": "public | internal | restricted",
  "locator": "exact locator",
  "source_url": null,
  "local_source": null,
  "limitation": "",
  "publication_permission": "confirmed | previously_public_by_gconf | unknown",
  "public_usage_mode": "exact_quote | attributed_case | anonymized_synthesis | internal_only",
  "source_role": "audience_voice | organizer_interpretation | prior_announcement | case_proof | offer_fact",
  "freshness_band": "fresh | recent | historical | not_applicable",
  "attribution_verified": true,
  "used_in": ["telegram", "instagram-slide-5"],
  "publish_ready": true
}
```

An exact quote requires a locator, author or honest source-level attribution,
date, visibility, and a real URL or local path. `publish_ready` must be false
for candidate evidence. Unknown permission is allowed only for
`anonymized_synthesis` of an already-public source: the public copy must not
repeat the exact quote, name, role, location, or unique biography. All other
unknown-permission evidence remains non-publish-ready.

## Manifest and audit

`manifest.json` contains: schema version, run ID/time, review status, analysis
run, direction ID, prior announcement locators and screenshot paths, product
name, voice mode, address, channels, confirmed-facts allowlist, placeholders,
evidence refs by channel, output files, `publication_ready`, `decision_refs`,
`workflow_status`, and `publication_status`.

For schema 2.0, `decision_refs` contains the confirmed
`announcement_direction_selection` decision. Set `workflow_status` to
`awaiting_copy_approval` and `publication_status` to `not_ready`. Later fact,
permission, and copy approvals remain separate append-only decision cards and
must not be written back into this immutable run.

Also record `program_evidence_map` with exactly six blocks and
`slide4_evidence_summary` with six request refs, fresh/recent non-prior count,
historical carry-forward count, unique locator count, and carry-forward
reasons.

Keep `review_status: draft` and `publication_ready: false` while placeholders
remain. `audit.md` records all canonical voice-audit answers, numeric/fact
allowlist results, quote verification, permission findings, unresolved items,
and the 0–2 rubric scores for Taste, Philosophy, Research, Process quality, and
Growth.

# News writer output contract

Create a unique UTC run at
`research/news_drafts/runs/<YYYYMMDDTHHMMSSZ>/`. Never overwrite another run or
create a mutable `latest` copy.

## Required files

- `brief.md`;
- one `news-<topic-id>.md` per selected topic;
- `evidence-ledger.json`;
- `coverage.json`;
- `audit.md`;
- `manifest.json`.

## `brief.md`

Write a neutral internal brief. Record the radar run, explicit human-selected
topic IDs, voice mode, address, CTA mode, and source revalidation time. For each
topic include the selected focus, audience, behavioral transition, tension,
primary evidence, limitation, format, format-change reason when applicable,
coverage delta, GCONF theme, CTA, and unresolved items.

## Public posts

Create exactly one clean Telegram post per topic. Name the file by prefixing the
full topic ID with `news-`, for example:
`news-news-20260718-example-topic.md`.

Do not include evidence annotations, internal status labels, audit notes, or
alternative headlines. Follow the format word range and use one CTA.

## `evidence-ledger.json`

Write a JSON array. Every entry contains:

```json
{
  "id": "stable-evidence-id",
  "topic_id": "news-YYYYMMDD-topic",
  "evidence_status": "fact | inference | proposal",
  "source_kind": "official_primary | independent_primary | secondary | social | local_semantic_card",
  "publisher": "",
  "title": "",
  "published_at": "ISO-8601 or YYYY-MM-DD",
  "revalidated_at": "ISO-8601 UTC",
  "url": null,
  "local_source": null,
  "locator": "",
  "claim_supported": "",
  "publisher_claim": false,
  "availability_status": "confirmed | partial | unavailable | not_applicable | unknown",
  "limitation": "",
  "used_in": ["news-news-...md"]
}
```

Schema 1.1 ledger entries additionally contain:

```json
{
  "evidence_role": "event_confirmation | protagonist_observation | audience_reaction | gconf_case | historical_context",
  "parent_locator": null,
  "visibility": "public | internal | editorial",
  "permission_status": "not_required | required | confirmed | unknown"
}
```

Every material public fact resolves to at least one ledger item. An entry needs
a real URL or local source. Availability claims require a live revalidation
time and non-unknown availability status.

## `coverage.json`

Write an array with one entry per selected topic:

```json
{
  "topic_id": "",
  "closest_coverage_refs": [],
  "coverage_delta": "",
  "central_claim_overlap": "none | partial | high",
  "new_editorial_unit": true
}
```

`new_editorial_unit` must be true. A high-overlap topic requires a concrete new
fact or changed consequence in `coverage_delta`.

## `manifest.json`

Use this top-level shape:

```json
{
  "schema_version": "1.0 | 1.1 | 2.0",
  "run_id": "YYYYMMDDTHHMMSSZ",
  "generated_at": "ISO-8601 UTC",
  "review_status": "ready_for_human_review",
  "publication_ready": false,
  "radar_run": "research/news_analysis/runs/RUN_ID",
  "selected_topic_ids": [],
  "human_selection": true,
  "decision_refs": ["decision-..."],
  "workflow_status": "awaiting_copy_approval",
  "publication_status": "not_ready",
  "voice_mode": "GCONF",
  "address": "vy",
  "cta_mode": "editorial",
  "posts": [],
  "unresolved_items": [],
  "output_files": []
}
```

Every post object contains `topic_id`, `file`, `format`, `focus`,
`behavioral_transition`, `tension`, `primary_evidence_ref`, `evidence_refs`,
`coverage_delta`, `cta`, `source_revalidated_at`, `central_fact_status`,
`format_change_reason`, `quality_scores`, and `publication_ready`.

`cta` contains one `type` (`editorial` or `commercial`) and non-empty `text`.
`central_fact_status` must be `unchanged`; if it is not, stop without drafting.
`quality_scores` contains integer 0–2 scores for `taste`, `philosophy`,
`research`, `process_quality`, and `growth`. Total must be at least 8 and
`research` must be greater than zero.

Schema 2.0 requires one confirmed `news_topic_selection` decision in
`decision_refs`. Keep `workflow_status: awaiting_copy_approval` until a later
append-only copy-approval decision exists. Keep `publication_status: not_ready`;
formatting is a manual handoff and never proves publication.

Set top-level `publication_ready` to true only when every post is ready and
`unresolved_items` is empty. A commercial CTA, partial rollout, unknown
availability, sensitive case, or other material limitation remains false until
explicitly resolved.

For a schema 1.1 radar handoff, use writer schema 1.1 and preserve
`evidence_role`, nullable `parent_locator`, `visibility`, and
`permission_status` in every ledger item. Evidence with permission `required`
or `unknown` forces the related post and top-level `publication_ready` to
remain false. An audience comment or protagonist observation cannot be the
primary proof for a `release_explainer`.

## `audit.md`

Record the complete canonical voice audit, claim-to-evidence result, live
source checks, availability, publisher-claim labels, coverage delta, format and
word count, CTA count, unknown GCONF facts, unresolved items, five rubric
scores, and the publication-readiness decision for every post.

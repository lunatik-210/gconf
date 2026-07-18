# News radar output contract

Create a unique UTC run at
`research/news_analysis/runs/<YYYYMMDDTHHMMSSZ>/`. Never overwrite a run or
create a mutable `latest` copy.

## Required files

- `backlog.md` — neutral human-review backlog;
- `manifest.json` — machine-readable candidates, evidence, and coverage;
- `audit.md` — source, freshness, scoring, and boundary checks.

## `backlog.md`

Use neutral Russian and these sections in order:

1. `# GCONF News Radar`
2. `## Вердикт по данным и свежести`
3. `## Покрытие источников`
4. `## Приоритетный backlog`
5. `## Резерв`
6. `## Отклонённые сильные сигналы`
7. `## Покрытие GCONF и дубли`
8. `## Пробелы и ingestion queue`
9. `## Human review`
10. `## Evidence appendix`

The source-coverage section lists every required lane, its window, meaningful
and excluded counts, pages reviewed, signals found, passing candidates, stale
or empty inputs, and any 60-day expansion reason.

For every passing candidate show its `topic_id`, neutral working title, event
and date, one focus, why-now, AI-market significance, next-GCONF relevance,
audience, before/after change, closest coverage, coverage delta, proposed
format, experiment/question, facts, inferences, limitations, editorial risks,
score, status, and evidence refs.

Do not include sample headlines, leads, post paragraphs, rhetorical hooks, or
CTA copy. End the human-review section by asking the reviewer to pass explicit
topic IDs to `$gconf-news-writer`; do not select them.

## `manifest.json`

Use this top-level shape:

```json
{
  "schema_version": "2.0",
  "run_id": "YYYYMMDDTHHMMSSZ",
  "generated_at": "ISO-8601 UTC",
  "review_status": "draft",
  "selected_topic_ids": [],
  "decision_refs": [],
  "workflow_status": "awaiting_human_selection",
  "publication_status": "not_ready",
  "parameters": {
    "default_window_days": 14,
    "expanded_window_days": 45,
    "local_window_days": 30,
    "local_max_days": 60,
    "max_candidates": 10,
    "minimum_score": 65,
    "reserved_lanes": ["protagonist", "gconf_case", "audience_reaction"]
  },
  "source_snapshot": {},
  "source_review": {},
  "candidates": [],
  "rejected_signals": [],
  "evidence_index": [],
  "coverage_index": [],
  "ingestion_queue": [],
  "output_files": ["backlog.md", "manifest.json", "audit.md"]
}
```

Every candidate contains:

```json
{
  "topic_id": "news-YYYYMMDD-short-topic-slug",
  "working_title": "neutral title",
  "event_summary": "",
  "event_date": "YYYY-MM-DD",
  "focus": "one editorial focus",
  "why_now": "",
  "ai_market_significance": "",
  "gconf_theme": "",
  "gconf_relevance": "",
  "audience": "",
  "previous_mode": "",
  "changed_mode": "",
  "closest_coverage_refs": [],
  "coverage_delta": "",
  "recommended_format": "flash | release_explainer | trend_translation | gconf_field_note | story_lore",
  "experiment_or_question": "",
  "facts": [],
  "inferences": [],
  "limitations": [],
  "editorial_risks": [],
  "evidence_refs": [],
  "source_requirement": "product_release | broad_trend | field_note | other",
  "score": {
    "market_relevance": 0,
    "gconf_relevance": 0,
    "coverage_novelty": 0,
    "evidence_quality": 0,
    "freshness": 0,
    "actionability": 0,
    "risk_penalty": 0,
    "priority_score": 0
  },
  "status": "recommended | reserve | reject",
  "priority_rationale": "",
  "primary_discovery_lane": "official_release | protagonist | gconf_case | audience_reaction | ecosystem_posts | semantic_context",
  "supporting_lanes": [],
  "window_expansion_reason": null
}
```

Evidence entries contain `id`, `evidence_status`, `source_kind`, `publisher`,
`title`, `published_at`, `accessed_at`, `url` or `local_source`, `locator`,
`claim_supported`, `publisher_claim`, `freshness_days`, `freshness_band`, and
`limitation`. Allowed evidence statuses are `fact`, `inference`, `proposal`,
and `unindexed_observation`. Allowed source kinds include `official_primary`,
`independent_primary`, `secondary`, `social`, and `local_semantic_card`.
Schema 1.1 evidence also contains `evidence_role`, nullable `parent_locator`,
`visibility`, and `permission_status`. Roles are `event_confirmation`,
`protagonist_observation`, `audience_reaction`, `gconf_case`, and
`historical_context`. Internal evidence always uses
`permission_status: required` and cannot be a candidate's only evidence.

`source_review` contains all six required lanes. Each records available and
meaningful items, technical-noise exclusions, expected and reviewed pages,
completion, first/last dates, fingerprint, signals found, and passing
candidates. A schema 1.1 run is invalid until every lane is complete.

Coverage entries contain `id`, `platform`, `published_at`, `locator`, `url`,
`title`, `excerpt`, and `coverage_role`. Every closest-coverage ref must resolve
into this index. Every evidence ref must resolve into `evidence_index`.

Keep `selected_topic_ids` empty. Put live public evidence absent from the local
pipeline in `ingestion_queue`; this records a handoff, not an ingestion action.
Keep `decision_refs` empty in the immutable radar run. When the human later
selects topics, `$gconf-editorial-gates` writes a separate decision card.

## `audit.md`

Record source hierarchy, source independence, freshness window, lane pages,
coverage queries, duplicate decisions, score arithmetic, reserved-lane composition, boundary
compliance, unresolved limitations, and confirmation that no public copy was
written and no topic was selected.

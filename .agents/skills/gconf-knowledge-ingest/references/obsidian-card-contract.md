# Obsidian card contract

The `knowledge/` directory is both an Obsidian vault and the human-reviewed
semantic layer.

## Generated cards

Files under `knowledge/sources/` are generated from the SQLite source index.
They must include `generated: true` and may be overwritten by rebuilds.

## Semantic cards

Candidate and approved cards use YAML frontmatter:

```yaml
type: pain
id: pain-agent-context-chaos
label: "Агентов много, но нет системы контекста"
status: inference
review_status: candidate
first_seen: "2026-05-25"
last_seen: "2026-07-15"
source_wave: internal
evidence:
  - "telegram:1633415027:1040"
  - "youtube:J9cvaJ5enIw:1120-1185"
evidence_quotes:
  - locator: "telegram:1633415027:1040"
    role: "primary"
    quote: "Точная короткая цитата из источника"
    supports: "Что именно эта цитата подтверждает"
related:
  - "actor-dima-matskevich"
event_context:
  - event_id: "cohort-ai-vibe-coding-may-2026"
    phase: "after"
    attribution: "inferred_by_time"
```

Allowed `type` values:

- `actor`
- `cohort`
- `pain`
- `case`
- `trend`
- `technology`
- `claim`

Allowed epistemic statuses are `fact`, `inference`, and `proposal`. Allowed
review statuses are `candidate`, `approved`, `rejected`, and `superseded`.

Write candidates directly to their typed folder with `review_status: candidate`.
The Review Inbox Base selects candidates across all typed folders. Human review
changes their status to `approved`, `rejected`, or `superseded`; it does not
move files. Never remove evidence locators during review.

Every semantic card also records `source_wave: internal | external | mixed`
and `event_context`. Publication time alone does not prove event membership:
use `explicit`, `inferred_by_time`, or `unattributed` attribution.

Semantic profile v2 also requires an exact excerpt for every evidence locator.
The insight extractor validates these excerpts against SQLite and renders a
human-readable `## Evidence` section with source links. Case cards additionally
record `case_origin`, `reporting_mode`, `proof_level`, `artifact_status`, the
initial task, process, tools, result, behavior shift, and limitations.

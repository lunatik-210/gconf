# Editorial decision contract

## Gate types

| Gate | Workflow | Required before |
| --- | --- | --- |
| `semantic_evidence_review` | `semantic` | promoting candidate evidence |
| `news_topic_selection` | `news` | news writer |
| `news_copy_approval` | `news` | Telegram formatter |
| `freshness_acceptance` | `news` or `announcement` | proceeding with a material limitation |
| `announcement_direction_selection` | `announcement` | announcement writer |
| `offer_fact_and_cta_allowlist` | `announcement` | announcement public copy |
| `publication_permission` | `announcement` or `news` | named cases or exact quotations |
| `announcement_copy_approval` | `announcement` | carousel designer or formatter |
| `carousel_visual_approval` | `design` | manual publication handoff |
| `publication_confirmation` | `publication` | recording actual publication |

## Card fields

Decision cards are append-only Markdown files with flat YAML frontmatter:

```yaml
type: "editorial_decision"
schema_version: "1.0"
decision_id: "decision-20260718T120000000000Z-news-topic-selection"
workflow: "news"
gate_type: "news_topic_selection"
upstream_ref: "research/news_analysis/runs/20260718T110000Z"
selected_refs: ["news-20260718-example"]
artifact_refs: []
decision_source: "human_explicit"
recorded_by: "agent"
instruction_excerpt: "Берём example"
decided_at: "2026-07-18T12:00:00Z"
status: "confirmed"
supersedes: ""
downstream_ref: ""
```

Allowed decision sources are `human_explicit`, `agent_choice_authorized`, and
`inferred_backfill`. Backfills must use `needs_confirmation`. Only `confirmed`
decisions resolve a gate.

`artifact_refs` use `relative/path#sha256=HEX`. Copy and visual approvals must
bind to exact artifacts. A changed file invalidates the approval.

## Immutability and current state

Never edit a decision. A correction or confirmation creates a new decision with
`supersedes`. A confirmed newer record makes the referenced decision unusable.
Reject missing supersede targets, cycles, duplicate IDs, unknown selected IDs,
and paths outside the repository.

## Editorial status model

- Evidence: `candidate | approved | rejected | superseded`.
- Editorial: `awaiting_human_selection | selected | awaiting_copy_approval |
  approved | blocked`.
- Publication: `not_ready | ready_for_manual_handoff | published_confirmed`.

Legacy `human_selection` and `publication_ready` may remain in schema 1.x runs,
but new downstream runs must also carry `decision_refs`, `workflow_status`, and
`publication_status`.

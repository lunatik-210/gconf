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
evidence:
  - "telegram:1633415027:1040"
  - "youtube:J9cvaJ5enIw:1120-1185"
related:
  - "actor-dima-matskevich"
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

Keep candidates in `knowledge/_inbox/`. Move them to their typed folder only
after human review. Never remove evidence locators during promotion.

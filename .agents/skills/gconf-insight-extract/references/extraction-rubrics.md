# Extraction rubrics

## Common card contract

Write every semantic candidate with:

- `type`, stable `id`, `label`;
- `status: fact | inference | proposal`;
- `review_status: candidate`;
- `first_seen`, `last_seen`;
- `source_wave: internal | external | mixed`;
- exact primary `evidence` locators;
- `evidence_quotes`, one exact excerpt for every locator, with `role`, `quote`,
  and a human-readable `supports` statement;
- `related` card IDs;
- `event_context` as an inline JSON array.

Event context items use:

```json
{"event_id":"cohort-ai-vibe-coding-may-2026","phase":"after","attribution":"explicit"}
```

Allowed phases are `before`, `during`, `after`, and `unknown`. Allowed
attributions are `explicit`, `inferred_by_time`, and `unattributed`. Time alone
never proves that a pain or case originated in an event.

Each quote must be a verbatim, contiguous excerpt of at most 1,200 characters.
Prefer the smallest passage that lets a reviewer accept or reject the card.
The rendered `## Evidence` block includes author, date, source link, locator,
visibility, and local artifact path. `first_seen` and `last_seen` must match the
earliest and latest quoted evidence dates.

## Types

- `pain`: label the subtype as `barrier`, `fear`, `desire`, or `objection`;
  preserve audience language and distinguish repeated patterns from anecdotes.
- `case`: record `initial_task`, `process`, `tools`, `result`,
  `behavior_shift`, `limitations`, and the taxonomy below. A case is a
  concrete implemented artifact or changed process, not a generic lesson or
  aspiration. Do not assign a cohort without proof.
- `trend`: describe the changed capability, newly available behavior,
  maturity, freshness, and hype risk. Commentary is a signal, not product fact.
- `technology`: record a tool or capability without promoting it to a trend.
  Treat it as a living entity: append new evidence, track `lifecycle_status`
  (`announced`, `available`, `mature`, `deprecated`, `retired`, or `unknown`),
  and preserve obsolete cards as history. Create a new card for a major model
  version and connect it with `supersedes`; do not silently rewrite the old one.
- `claim`: connect at least one pain with another supported semantic type. Do
  not create a claim from one comment.
- `actor`: use `internal_protagonist`, `external_protagonist`,
  `community_member`, or `source_author`.
- `lab`: use for an AI research organization publishing primary material.
  Record official domains and SQLite source IDs. Do not use `actor` for labs.
- `cohort`: include dates, `event_kind`, positioning, and verified properties
  only. Use `experiment` for AI weekend.

## Case taxonomy

Every case requires:

- `case_origin`: `gconf_participant`, `gconf_community`,
  `internal_protagonist`, or `external`;
- `reporting_mode`: `direct_self_report`, `organizer_report`, or
  `third_party_report`;
- `proof_level`: `linked_artifact`, `described_result`, or `claim_only`;
- `artifact_status`: `prototype`, `working`, `deployed`, or `unknown`.

`gconf_participant` requires explicit evidence that the artifact was made in
the cohort or its prework. A message in an old cohort chat months later is a
`gconf_community` case unless the author explicitly connects it to the cohort.
Organizer compilations are valuable but remain `organizer_report`; preserve
the participant's exact quoted language.

## Source waves

- GCONF and Dima-authored content describes the internal narrative.
- Closed-community messages describe the internal audience.
- Comments under public GCONF or Dima content describe the external audience
  unless the author is explicitly identified as a participant.
- Matt Wolfe, Wes Roth, other public AI/business channels, and their audiences
  belong to the external wave.
- Official lab publications belong to the external wave. Product availability
  is primary evidence; publisher-authored benchmark superiority remains a
  claim until independently corroborated.

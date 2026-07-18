---
name: gconf-insight-extract
description: Convert already-ingested GCONF SQLite evidence into traceable Obsidian semantic cards and track processed source batches. Use when identifying pains, cases, trends, technologies, labs, actors, cohorts, or evidence-backed claims from newly added or changed Telegram, Instagram, YouTube, official lab Web Articles, or local research data; checking which insight batches are pending or stale; preparing work units; finalizing processing markers; or validating the semantic knowledge layer. Do not use to collect sources, download media, transcribe, draft announcements or news, approve candidates, or publish content.
---

# GCONF Insight Extract

Turn normalized evidence into reusable knowledge without mixing collection,
semantic judgment, and editorial writing.

## Run the workflow

1. Run `$gconf-knowledge-ingest` after source artifacts change.
2. Check the configured scope and pending work:

```bash
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py doctor
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py status --scope next-gconf
```

3. Prepare one pending or stale logical batch:

```bash
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py prepare --scope next-gconf --batch BATCH_ID
```

4. Read every generated work unit and its reply/thread context. Consolidate
   repeated evidence before creating cards. Follow
   [extraction-rubrics.md](references/extraction-rubrics.md).
5. Write candidates directly to their typed folders under `knowledge/`, never
   to `knowledge/sources/`. Use JSON-compatible inline arrays in YAML
   frontmatter so validation remains dependency-free.
6. Finalize the logical batch only after its cards exist:

```bash
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py finalize --scope next-gconf --batch BATCH_ID --outputs CARD_ID ...
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py validate
```

An empty `--outputs` list is valid when every work unit was reviewed and no
semantic signal was found.

Before review, render or inspect the human evidence layer:

```bash
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py show-evidence LOCATOR
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py render-evidence
```

`render-evidence` builds the Markdown `## Evidence` section from validated
`evidence_quotes`. Do not hand-edit content between the evidence markers.

## Preserve boundaries

- Read SQLite and local evidence only. Never call a network API, yt-dlp, or
  Whisper.
- Keep raw artifacts immutable.
- Do not create one semantic card per message. Cluster repeated evidence.
- Preserve exact primary locators and exact, short source excerpts in
  `evidence_quotes`. A reviewer must understand and open every source without
  querying SQLite manually. Treat local research as navigation rather than
  primary proof.
- Write new cards with `review_status: candidate` directly to `actors/`,
  `labs/`, `cohorts/`, `pains/`, `cases/`, `trends/`, `technologies/`, or `claims/`.
- Merge new evidence into an existing candidate. Never overwrite an approved
  card; create a dated candidate with `updates: EXISTING_ID`.
- Do not infer event membership from publication date. Record `explicit`,
  `inferred_by_time`, or `unattributed` event attribution.
- Separate participant outcomes (`gconf_participant`) from later community
  work (`gconf_community`), protagonist examples (`internal_protagonist`), and
  outside examples (`external`).
- Do not draft an announcement, news post, CTA, or positioning thesis.
- After candidates are ready, expose them in the shared Editorial Control Plane.
  When the human explicitly approves or rejects candidates in conversation,
  use `$gconf-editorial-gates` to record `semantic_evidence_review` before
  applying the existing `review_status` change. Never infer approval from a
  completed processing fingerprint.

Read [processing-contract.md](references/processing-contract.md) when changing
scope selection, fingerprints, or processing cards. Read
[scope-contract.md](references/scope-contract.md) when adding a scope or batch.

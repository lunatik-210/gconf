---
name: gconf-news-radar
description: Analyze current public AI signals and the local GCONF evidence corpus to create a prioritized, deduplicated newsroom backlog for human review. Use when Codex must discover possible GCONF / AI LOVERS news topics, compare them with prior channel coverage and existing drafts, explain why each topic matters now, and rank evidence-backed topic candidates without writing public posts. Do not use to draft copy, select topics on a human's behalf, publish, collect source packages, ingest evidence, or mutate SQLite or Obsidian.
---

# GCONF News Radar

Create a neutral, reviewable bridge between current AI signals and later GCONF
news writing. Stop before public copy. Leave topic selection to a human.

## Run the workflow

1. Read the repository `AGENTS.md`, the complete
   `editorial/gconf-tone-of-voice.md`, and both files in `references/`. Apply
   the voice standard as an evaluation frame; keep the radar artifact neutral.
2. Prepare a compact, read-only local context:

```bash
python3 -B .agents/skills/gconf-news-radar/scripts/prepare_radar_context.py \
  --window-days 14 --max-candidates 10 > /tmp/gconf-news-radar-context.json
```

   The packet inventories a 30-day local window and a maximum 60-day window
   across all required source lanes. Read every primary-window page before
   finalizing the run:

```bash
python3 -B .agents/skills/gconf-news-radar/scripts/prepare_radar_context.py \
  --lane protagonist --page-size 100
```

   Repeat with the returned `--cursor` until `complete: true`, then do the same
   for `official_release`, `gconf_case`, `audience_reaction`,
   `ecosystem_posts`, and `semantic_context`. Use `--use-extended-window`
   only with a non-empty `--window-expansion-reason`; it may extend discovery
   to 60 days, never farther. Record page completion, signals, and passing
   candidates in `source_review`.

   Use `--coverage-query 'QUERY'` once per shortlisted event or claim to add
   FTS matches from the full public-channel archive; the initial packet keeps a
   compact recent slice only. The script must never modify the
   database, semantic cards, source exports, announcement runs, or prior news
   runs.
3. Search live public sources for signals published in the last 14 days.
   Expand to 45 days only for a developing structural trend and record why.
   Prefer official releases, research, documentation, papers, and repositories.
4. Merge multiple mentions of the same event before scoring. Separate a
   product event from a wider market interpretation when they require different
   evidence.
5. Compare every candidate with all supplied GCONF coverage: entity, central
   claim, behavioral transition, audience consequence, and editorial angle.
   Reject an equivalent angle unless a concrete new delta is supported.
   Run at least one topic-specific `--coverage-query` before finalizing each
   candidate so the comparison spans the full archive, not only the recent slice.
6. Score candidates using `references/scoring-and-coverage.md`. Return zero to
   ten passing candidates; never invent candidates to fill a reserved lane.
   Pass the eligible pool through `scripts/compose_radar_candidates.py` so one
   eligible place each is preserved for `protagonist`, `gconf_case`, and
   `audience_reaction`.
7. Write the three artifacts required by `references/output-contract.md` under
   `research/news_analysis/runs/<UTC-run-id>/`.
8. Run the validator:

```bash
python3 -B .agents/skills/gconf-news-radar/scripts/validate_radar_run.py \
  research/news_analysis/runs/RUN_ID
```

9. Report the backlog as ready for human review. Never populate
   `selected_topic_ids`, recommend that a writer start automatically, or create
   Telegram copy. Set `workflow_status: awaiting_human_selection`, ask the
   human for explicit topic IDs, and stop. A later explicit answer is recorded
   by `$gconf-editorial-gates`; never mutate this radar run.

## Apply source rules

- Require at least one official primary source for a product release.
- Require at least two independent publishers for a broad market trend.
- Treat publisher benchmarks as publisher claims, not neutral comparisons.
- Use social posts and secondary media only for discovery, audience reaction,
  or corroboration; they cannot replace primary confirmation.
- A protagonist source confirms that person's documented observation or
  experience, not a product capability. A comment is audience-reaction
  evidence, never product proof.
- Treat internal GCONF/community material as discovery-only. It requires public
  corroboration or explicit permission before writer publication readiness.
- Record direct URL, publisher, publication date, access time, source kind,
  evidence status, and limitation for every material source.
- Label live material absent from the local knowledge pipeline as
  `unindexed_observation` and add it to `ingestion_queue`; do not ingest it.
- Prefer approved semantic cards. Use candidates only as labeled emerging
  evidence with their limitations intact.
- Do not infer availability, safety, pricing, benchmark comparability, or
  future release dates.

## Protect the human gate

- Use stable IDs in the form `news-YYYYMMDD-short-topic-slug`.
- Set candidate status to `recommended`, `reserve`, or `reject`.
- Keep `selected_topic_ids: []` in every radar manifest.
- Do not write headlines, leads, post paragraphs, CTA copy, or other public
  prose. A neutral working title and a proposed editorial focus are allowed.
- Do not change old runs. Create a new UTC run for every analysis snapshot.
- Do not publish or call `$gconf-news-writer` automatically.

## Preserve system boundaries

This skill may read the live web and local evidence and may write only its new
run directory. It must not collect platform exports, alter raw artifacts,
refresh SQLite, edit Obsidian cards, rewrite the canonical voice standard,
draft posts, or publish content.

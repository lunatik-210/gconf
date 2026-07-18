---
name: gconf-news-writer
description: Turn human-selected topic IDs from a validated GCONF news-radar run into evidence-backed Telegram news drafts in the canonical GCONF voice. Use when Codex receives an explicit radar run path and one or more topic IDs, must revalidate the primary sources and central fact, preserve the selected editorial focus, and produce one reviewable Telegram post per topic. Do not use to discover or rank topics, bypass human selection, replace a stale topic, invent GCONF facts, mutate the knowledge base, or publish content.
---

# GCONF News Writer

Write only topics explicitly selected by a human from a validated radar run.
Preserve the selected focus and stop if live evidence materially changes it.

## Require a human selection

Require all of these before drafting:

- a radar-run directory;
- a confirmed `$gconf-editorial-gates` `news_topic_selection` decision;
- voice mode and address form, defaulting to `GCONF` and `вы`;
- an editorial CTA, or a confirmed commercial CTA supplied by the user.

When the current user instruction explicitly selects topics, record it through
`$gconf-editorial-gates` and continue with the returned `decision_id`. When the
instruction is ambiguous, ask and stop. Do not infer topic IDs from ranking.
Do not accept an unknown topic. Accept a
`reject` topic or a passing-score override only when the user explicitly asks
and the context preparation uses `--allow-rejected`.

## Run the workflow

1. Read the repository `AGENTS.md`, the complete
   `editorial/gconf-tone-of-voice.md`, and both files in `references/`.
2. Prepare a read-only writer packet:

```bash
python3 -B .agents/skills/gconf-news-writer/scripts/prepare_writer_context.py \
  --radar-run research/news_analysis/runs/RUN_ID \
  --decision-id DECISION_ID \
  --voice-mode GCONF \
  --address vy \
  --cta-mode editorial > /tmp/gconf-news-writer-context.json
```

   Topic IDs come from the resolved decision. Use
   `--cta-mode commercial --cta-text 'CONFIRMED CTA'` only when the CTA is
   confirmed. The script must not change the radar run or local knowledge.
   For radar schema 1.1 it resolves local evidence locators back to the exact
   document or transcript chunk and includes the parent post/video for a
   comment. Treat `publication_permission_blocked: true` as an unresolved
   publication gate.
3. Reopen every primary public source used by each selected topic. Record the
   access time, availability, and whether the central fact remains `unchanged`.
4. Stop and return the topic to human review when the release was delayed,
   withdrawn, materially changed, or no longer supports the selected focus.
   Never substitute a new topic or silently rewrite the central angle.
5. Build `brief.md` before public copy. For each topic fix one audience, one
   behavioral transition, one tension, one primary evidence item, one format,
   one limitation, and one CTA. Explain any format change from the radar.
6. Write one standalone Telegram post for each topic using
   `references/news-formats.md`. Keep the required movement:
   `event -> real change -> behavioral meaning -> limitation -> one action`.
7. Create every artifact required by `references/output-contract.md`, then run:

```bash
python3 -B .agents/skills/gconf-news-writer/scripts/validate_news_run.py \
  research/news_drafts/runs/RUN_ID
```

8. Report the drafts as ready for human review. Never publish them.

## Protect facts and focus

- Map every material factual claim to an evidence-ledger entry.
- Preserve publisher benchmarks as publisher claims and keep methodological
  limitations visible in the brief and, when material, the public post.
- Confirm current availability, plan access, dates, and future promises live.
- Keep `fact`, `inference`, and `proposal` distinct in internal artifacts.
- Preserve schema 1.1 `evidence_role`, `visibility`, `parent_locator`, and
  `permission_status` in the writer ledger. A comment supports audience
  reaction only; a protagonist observation does not replace official product
  confirmation.
- Do not add unverified cohort dates, prices, format, curriculum, speakers,
  capacity, outcomes, testimonials, availability, safety, or CTA destination.
- Use the radar's `coverage_delta`; do not fall back to an already published
  generic GCONF angle.
- One topic produces one post and one central focus. Tool names support the
  behavioral meaning rather than replace it.

## Apply GCONF voice

- Use `GCONF` by default. Use `Dima` only for genuinely attributed personal
  content and never invent his position or experience.
- Choose `ты` or `вы` before drafting and keep it consistent outside quotes.
- Prefer concrete behavior, process, context, boundaries, and a small test over
  generic futurism or model hype.
- Use one CTA. A source link is attribution, not a second CTA.
- Add a commercial CTA only when the relation is natural and its details are
  confirmed; otherwise use an experiment, a specific question, or a request to
  share a process.

## Preserve system boundaries

This skill may read live sources and local evidence and may write only its new
writer-run directory. It must not discover new topics, change radar rankings,
mutate prior runs, ingest evidence, edit SQLite or Obsidian, publish, or send
messages externally. The only permitted Obsidian mutation before drafting is
the append-only decision written through `$gconf-editorial-gates`.

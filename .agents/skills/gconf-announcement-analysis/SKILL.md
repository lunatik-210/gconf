---
name: gconf-announcement-analysis
description: Prepare an evidence-backed strategic analysis for the next GCONF cohort announcement. Use when Codex must treat the live gconf.io page as the current-offer baseline, reconstruct the Telegram announcement trajectory, combine internal and external audience pains, cases, protagonists, and current AI signals, and propose 2–3 directions for later Telegram, website, and Instagram announcement drafting. Do not use to write the final announcement, invent future cohort details, collect sources, or mutate the GCONF knowledge base.
---

# GCONF Announcement Analysis

Produce a reviewable bridge between the current GCONF offer and the next one.
Do not draft public copy. Separate evidence extraction, strategic judgment, and
later channel writing.

## Run the workflow

1. Read the repository `AGENTS.md` and the complete
   `editorial/gconf-tone-of-voice.md`. Use the voice standard as an evaluation
   frame, not as the voice of this neutral research artifact.
2. Build the local evidence packet:

```bash
python3 -B .agents/skills/gconf-announcement-analysis/scripts/prepare_context.py > /tmp/gconf-announcement-context.json
```

   If preflight reports invalid, pending, or stale state, stop. Give a concrete
   handoff to `$gconf-knowledge-ingest` and then `$gconf-insight-extract`. Never
   refresh, rebuild, or edit the knowledge base silently.
3. Open `https://www.gconf.io/` live. Treat it as the canonical baseline of the
   latest known cohort, not as another historical announcement. Record the URL,
   page title, access timestamp, and the offer facts used in the analysis.
   If the page cannot be opened, stop: a historical or cached approximation is
   not sufficient for this analysis.
4. Read `references/output-contract.md` completely before writing outputs.
5. Reconstruct three layers in this order:
   - current offer from the live site;
   - product trajectory from Telegram announcement history;
   - newer evidence from the knowledge system, Instagram adaptation, public
     audience responses, external protagonists, and official AI labs.
6. Classify each strategic meaning as `carry_forward`, `evolve`, `retire`, or
   `new_signal`. Explain the delta from the live current offer.
7. Rank evidence with the freshness policy below before selecting cases,
   tensions, protagonist movements, or external signals.
8. Propose two or three materially different directions. Rank them, but leave
   the human selection unset.
9. Create both required artifacts under
   `research/announcement_analysis/runs/<UTC-run-id>/`:
   `analysis.md` and `manifest.json`.
10. Validate the pair against the output contract before reporting completion.
11. Set `workflow_status: awaiting_human_selection`, ask the human to choose
    one direction ID, and stop. Record a later explicit answer through
    `$gconf-editorial-gates`; never write it back into this analysis run.

## Prioritize sources and freshness

Use freshness as a primary ranking signal within comparable evidence quality,
never as permission to prefer an unsupported new claim over a verified fact.

Apply this hierarchy:

1. The live site is always the current-offer baseline, regardless of the age of
   historical files.
2. The canonical tone-of-voice standard and recurring brand spine are
   guardrails. They do not become obsolete merely because they are older.
3. For emerging audience pains, cases, protagonist ideas, videos, news, and
   technical changes, prefer the newest relevant evidence that passes the same
   or stronger verification bar.
4. Use older evidence for longitudinal patterns, brand continuity, or a uniquely
   strong proof case. State why an older item remains necessary.
5. When a newer source contradicts an older one, show the change explicitly;
   do not average them into a timeless claim.

Assign every shortlisted evidence item:

- publication/event date and access date when applicable;
- `freshness_days` and `freshness_band`: `live` (0–14), `fresh` (15–45),
  `recent` (46–90), or `historical` (>90);
- evidence strength and review status;
- relevance to the next offer;
- a short selection rationale.

Rank shortlisted evidence on a 100-point editorial scale: freshness 35,
relevance to the next offer 25, evidence strength 20, audience specificity 10,
and novelty relative to the current offer 10. Do not score brand rules or the
live-site baseline; treat them as mandatory constraints. The model assigns the
non-deterministic components and explains close calls.

## Evidence rules

- Prefer `review_status: approved`. Candidate cards may inform a direction only
  when labeled and accompanied by their limitations.
- When approved items are otherwise comparable, choose the fresher one. A
  candidate may outrank an older approved card only as a labeled emerging signal,
  never as established proof.
- Preserve semantic card IDs and exact evidence locators. Use short quotations
  from the rendered Evidence blocks whenever an audience pain, protagonist idea,
  or case enters the shortlist.
- Every shortlisted audience or protagonist signal requires one short, exact,
  contiguous quote, its locator, author/date/visibility metadata, and a real
  source URL when the source exposes one. Never synthesize a representative
  quote, clean up its wording, or invent a link.
- If evidence is internal or has no openable public URL, cite its exact locator,
  visibility, and local artifact path. Explicitly say that the source is local
  or access-restricted; do not manufacture a public reference.
- Treat live facts not yet in the local pipeline as
  `unindexed_observation`; add their URLs to `ingestion_queue`.
- Keep `fact`, `inference`, `proposal`, and `unindexed_observation` distinct.
- Separate GCONF participants, later GCONF community work, external audience,
  Dima as the internal protagonist, Matt Wolfe and Wes Roth as external
  protagonists, and official labs as primary technical sources.
- Do not infer `internal_protagonist` case origin. The current corpus contains no
  cases with that taxonomy; state the gap instead of relabeling community cases.
- Do not treat comments as product facts, organizer reports as independent
  verification, or publisher benchmarks as neutral proof.
- Never invent the next cohort's dates, price, duration, curriculum, speakers,
  capacity, results, testimonials, availability, or safety guarantees.

## Direction quality bar

Each direction must specify its thesis, behavioral transition, audience tension,
why-now, inherited current-offer elements, genuinely new delta, evidence set,
risks, growth hypothesis, and implications for Telegram, the website, and
Instagram. Channel implications are editorial jobs-to-be-done, not copy.

Reject directions that merely rename the current promise, lead with a tool list,
collapse all audiences into one persona, or cannot be supported by exact local
locators and fresh public URLs.

Audit every direction against the brand spine and canonical tone-of-voice:
environment, agency, process, meta-skills, behavior change, adult honesty, and
specific evidence. Preserve audience language without mechanically copying a
participant, protagonist, or prior announcement.

Before finalizing, cross-check every quoted string against the rendered
`## Evidence` block in the semantic card. If it cannot be matched exactly, remove
it from the analysis.

## Preserve system boundaries

- This skill reads sources and writes analysis run artifacts only.
- It never edits raw artifacts, SQLite, source cards, semantic cards, processing
  cards, or the canonical tone-of-voice standard.
- It never collects or ingests YouTube, Telegram, Instagram, or web articles.
- It never writes the final Telegram announcement, landing page, carousel, or
  CTA copy.

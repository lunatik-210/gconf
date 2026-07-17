# GCONF hiring test — agent guide

## Project purpose

This workspace is for completing the GCONF hiring work sample for an **AI-first content & growth generalist**.

Our goal is to produce a submission that demonstrates the full chain:

> taste → understanding → process → audience action

The result should feel native to GCONF, reflect current shifts in AI and agents, and turn messy live information into a credible repeatable content system.

## Source of truth

- Assignment: https://gconf-hiring-test.jmatsako.chatgpt.site/
- Expected effort stated in the brief: **3–4 hours**.
- Deadline stated in the brief: **4 days from receiving the assignment**.
- Use **only public information**: Telegram channels, websites, public posts, descriptions of previous cohorts, and clearly identified observations/inferences.
- Do not invent facts about the next cohort. Mark unknowns, assumptions, and proposed positioning explicitly.

## Required outcomes

### 1. Announcement for the next GCONF cohort

Research public GCONF materials and produce a complete announcement for the next cohort.

The announcement must:

- sound alive, precise, and recognizably GCONF;
- avoid generic course-launch language, “marathon” advertising, and claims such as “neural networks will change everything”;
- communicate environment, agency, processes, meta-skills, and behavior change—not merely faster text generation;
- connect the offer to concrete tensions, desires, and language found in the audience and source material;
- distinguish verified facts from editorial proposals and assumptions.

Alongside the announcement, explain **3–5 key takes**: why these meanings matter to the audience and what evidence supports each one.

### 2. AI-first process for news and case content

Design a concrete daily loop for content about AI and agents, including news, cases, tools, and meaningful changes.

The process must specify:

- inputs and source types;
- collection and normalization;
- storage and retrieval;
- selection and prioritization criteria;
- fact-checking and freshness checks;
- synthesis and editorial framing;
- outputs and publishing handoff;
- feedback signals and how the loop improves;
- where human taste and judgment remain mandatory;
- how the process can be implemented with AI agents without pretending full automation is always desirable.

The process should connect content to audience action and growth: attention, follows/clicks, replies and conversations, applications, payments, and long-term trust.

## Evaluation rubric

Use these five criteria as a checklist for every major artifact:

1. **Taste** — lively and exact; no generic info-product advertising.
2. **Philosophy** — environment, agency, processes, meta-skills, and behavior change are present.
3. **Research** — claims visibly rely on public GCONF material and fresh AI signals rather than vacuum generation.
4. **Process quality** — the daily loop has explicit inputs, outputs, storage, selection rules, and improvement mechanics.
5. **Growth** — content is linked to observable audience behavior, conversion, and trust.

Polish is secondary to demonstrating this coherent chain well.

## Local research corpus

Telegram exports are stored in `telegram/`:

- `GCONF : AI LOVERS.json` — 87 messages, 2026-04-01 through 2026-07-13.
- `ИИ-сообщество GCONF.json` — 58 messages, 2026-04-02 through 2026-07-05.
- `ии и новый мир @matskevich.json` — 27 messages, 2026-04-04 through 2026-07-12.
- `Записки AI энтузиаста.json` — 257 messages, 2026-04-01 through 2026-07-14.
- `[айдженси] ИИ в бизнесе.json` — 14 messages, 2026-04-01 through 2026-05-26.
- `AI Happens.json` — 1 message dated 2026-04-11.

Instagram exports are stored in `Instagram/`:

- `matskevich.json` — 15 latest posts from 2026-05-17 through 2026-07-13, including public metrics, available comments, and structured carousel slides.
- `gconf.io.json` — 7 latest posts from 2026-05-15 through 2026-07-13, including public metrics, available comments, and structured carousel slides.

Treat these files as research inputs, not automatically authoritative facts. Preserve links, dates, channel names, and message identifiers when extracting evidence so important statements remain traceable.

## Working principles for agents

1. Read this file before project work and keep all work aligned with the two required outcomes.
2. Research before drafting. Build an evidence map of recurring language, audience pains, promises, proof, objections, and GCONF-specific philosophy.
3. Keep three labels distinct in notes and drafts: **fact**, **inference**, and **proposal**.
4. Prefer primary/public sources and recent signals. Record source URL or local file, publication date, and access date for consequential claims.
5. Never fabricate cohort dates, price, speakers, program details, results, testimonials, metrics, or product capabilities.
6. Preserve the original Russian voice found in the corpus; do not mechanically imitate individual phrasing or paste long source passages.
7. Optimize for signal, specificity, and editorial judgment—not the largest possible volume of generated text.
8. Keep the proposed content system realistically operable by a small team and explicit about costs, failure modes, and human checkpoints.
9. Tie recommendations to the rubric and to measurable audience actions.
10. Before finalizing, audit factual support, tone, freshness, duplication, generic AI language, and unsupported promises.

## GCONF voice standard

The canonical public-content voice standard is
`editorial/gconf-tone-of-voice.md`. Its evidence and editorial rationale are in
`research/tone_of_voice/gconf_voice_analysis.md`.

Before drafting or revising any public-facing announcement, post, landing page,
email, carousel, case story, or script, agents must:

1. Read `editorial/gconf-tone-of-voice.md` in full.
2. Declare one voice mode in the working brief: `GCONF` or `Dima`.
   Use `GCONF` by default. Use `Dima` only for content genuinely published as
   or explicitly attributed to Dzmitry Matskevich.
3. Choose one form of address, `ты` or `вы`, and keep it consistent throughout
   the artifact except inside sourced quotations.
4. Identify one behavioral transition, one audience tension, one evidence item
   with an exact locator, and one primary CTA before drafting.
5. Keep unverified cohort details as explicit placeholders or proposals. Never
   infer dates, prices, speakers, capacity, curriculum, results, testimonials,
   product availability, or safety from the voice corpus.
6. Complete the mandatory voice audit in the canonical standard before
   finalizing the content.

Do not apply the GCONF public voice to research notes, evidence maps,
fact-checks, ingestion reports, databases, technical documentation, or agent
instructions. Those artifacts should remain neutral and traceable.

Do not copy the full voice standard into project skills or other agent files.
Link to the canonical document so there is one source of truth. The `Dima`
mode transfers publicly evidenced reasoning patterns, not verbal tics, invented
feelings, or unverified personal positions.

## YouTube research workflow

- Route requests such as “разбери YouTube-видео”, “собери статистику”,
  “выгрузи комментарии” or “сохрани субтитры” through
  `$gconf-youtube-research`.
- Run the bundled doctor before the first live collection or after a tool
  failure. If a dependency is missing, show its setup suggestion and request
  explicit approval before running Homebrew, pip, pipx, a system package
  manager, or a model download.
- When the user supplies a destination folder, save the video there. Otherwise
  use YouTube `channel`, then `uploader`, then `UnknownChannel`.
- Probe first. Prefer manual SRT, then original-language automatic captions.
  Use temporary audio and local Whisper only when captions are unavailable.
- Do not download video for research collection. Remove temporary fallback
  audio after successful transcription.
- Treat views, likes, subscriber counts, and comments as a time-bound public
  snapshot. Always report collected-at time, comment completeness, and the
  transcript source.
- Keep cookies, credentials, browser profiles, and Whisper models outside the
  repository.
- Use the CLI documented in
  `.agents/skills/gconf-youtube-research/SKILL.md` and the artifact contract in
  `.agents/skills/gconf-youtube-research/references/artifact-contract.md`.
- The YouTube collector must not write to SQLite or Obsidian. When the user
  also asks to index, analyze, or curate the result, hand the completed local
  video package to `$gconf-knowledge-ingest`.

## Local knowledge system

The project uses a local pipeline:

> collected artifacts → deterministic ingestion → SQLite retrieval → Obsidian review → approved semantic knowledge

### Project skills and boundaries

- `$gconf-youtube-research` collects and normalizes one YouTube research
  package. It owns metadata, statistics, comments, chapters, description,
  captions, transcript fallback, thumbnails, and `YouTube/catalog.json`.
- `$gconf-yt-dlp` is the low-level YouTube diagnostic and probe skill. Do not
  use it instead of the complete YouTube research workflow.
- `$gconf-local-whisper` transcribes local media or provides the transcript
  fallback when YouTube captions are unavailable.
- `$gconf-knowledge-ingest` imports already-collected YouTube, Telegram,
  Instagram, and local research artifacts into the knowledge system. It must
  never scrape, download, transcribe, call a network API, or publish content.

Do not duplicate collection logic in downstream skills. A request such as
“collect this video and add it to the knowledge base” should invoke
`$gconf-youtube-research` first and `$gconf-knowledge-ingest` second.

### Storage responsibilities

- `telegram/`, `Instagram/`, `YouTube/`, and `research/` contain source
  artifacts. Treat them as immutable evidence during ingestion.
- `knowledge/_index/gconf.sqlite` is the derived machine index. It contains
  normalized sources, documents, comments, transcript chunks, reply edges,
  checksums, provenance, and full-text search indexes.
- `knowledge/` is also an Obsidian vault. Open this directory directly in
  Obsidian.
- `knowledge/sources/` contains generated source cards. They may be refreshed
  or recreated by the importer.
- `knowledge/_inbox/` contains AI-proposed semantic cards awaiting human
  review.
- Typed folders such as `knowledge/pains/`, `knowledge/cases/`,
  `knowledge/trends/`, `knowledge/actors/`, and `knowledge/cohorts/` contain
  reviewed semantic knowledge.
- `knowledge/runs/` contains JSON ingestion reports for auditability.

SQLite is not the editorial source of truth. Raw artifacts remain the evidence,
and reviewed Markdown cards are the approved semantic layer. The SQLite file
must be rebuildable from local artifacts without deleting reviewed cards.

### Knowledge ingestion commands

```bash
# Check SQLite/FTS and source directories
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py doctor

# Show available local source packages
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py scan

# Import or refresh the complete corpus
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py ingest --all

# Import one export, video folder, or research file
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py ingest PATH

# Search normalized documents
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py search 'агенты OR контекст'

# Search timestamped YouTube transcript chunks
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py search 'agent OR context' --chunks

# Validate database, FTS, relations, and generated source cards
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py validate
```

Use `rebuild` only for the derived index:

```bash
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py rebuild
```

It may remove and recreate `knowledge/_index/gconf.sqlite` and generated source
cards, but it must never remove source exports or approved semantic cards.

### Semantic-card rules

After deterministic ingestion, create AI candidates only in
`knowledge/_inbox/`. Allowed semantic types are:

- `actor`;
- `cohort`;
- `pain`;
- `case`;
- `trend`;
- `technology`;
- `claim`.

Every candidate must include:

- a stable ID;
- `status: fact | inference | proposal`;
- `review_status: candidate`;
- exact evidence locators;
- relevant first/last-seen dates;
- supported relationships to other cards.

Do not automatically promote candidates, silently rewrite approved cards, or
treat research summaries as primary evidence. Comments are useful evidence of
audience language and pain, but not automatically proof of a factual claim.
Reported participant cases remain reported cases unless independently
verified.

### Current knowledge snapshot

The first completed import contains:

- 14 source records;
- 5,437 normalized documents;
- 2,405 timestamped YouTube transcript chunks;
- 4,130 reply or parent relations;
- public, internal, and editorial visibility labels;
- generated Obsidian source cards and Bases views.

These counts are a snapshot, not a permanent invariant. Run `scan`, `ingest`,
and `validate` after adding new exports. The semantic folders are intentionally
not considered complete until their candidate cards have been reviewed.

## Definition of done

The project is complete when the submission includes:

- a source-backed announcement for the next GCONF cohort;
- 3–5 evidence-backed key takes with audience rationale;
- a concrete, implementable daily AI-content loop;
- explicit growth hypotheses, signals, and feedback mechanics;
- a source/assumption appendix sufficient to audit important claims;
- a final rubric review covering taste, philosophy, research, process, and growth.

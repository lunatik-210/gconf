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

## End-to-end project process

The complete operating chain is:

> collection → deterministic ingestion → semantic extraction → human review → editorial analysis → human selection → writing → human approval → formatting/design → manual publication

Do not collapse adjacent stages into one agent action. Collection does not
perform semantic judgment, ingestion does not write editorial conclusions,
analysis does not silently become public copy, and no project skill publishes.

### Collection boundaries

- YouTube is the only platform with a complete repository-local collection
  workflow. Route a YouTube URL through `$gconf-youtube-research`; use
  `$gconf-yt-dlp` only for low-level probing or extractor diagnostics and
  `$gconf-local-whisper` only for a local transcript or a captions-unavailable
  fallback.
- Telegram exports, Instagram exports, official-lab Web Articles, and local
  research files must already exist as local artifacts before ingestion. The
  project currently has no Telegram, Instagram, or general web crawler skill.
- `$gconf-knowledge-ingest` never downloads, scrapes, transcribes, opens live
  sources, or calls a network API. It imports local packages only.
- Live pages opened by `$gconf-announcement-analysis`, `$gconf-news-radar`, or
  `$gconf-news-writer` are editorial evidence checks, not collection. Material
  absent from the local pipeline remains `unindexed_observation`; record its
  URL in `ingestion_queue`. To index it later, first create a valid local source
  package through an authorized collection step, then run ingestion.
- Official AI-lab articles live under
  `Web Articles/<Lab>/<article>/<snapshot>/`. They require checksum-verified
  `metadata.json` and a full normalized `article.md`; `research-note.md` is
  secondary editorial navigation. Only exact official domains are accepted,
  and the importer never fetches the page itself.

### Project skills and boundaries

- `$gconf-editorial-gates` records, resolves, backfills, synchronizes, and
  validates append-only human decision cards under `knowledge/editorial/`.
  Use it whenever a human selects topics, directions, facts, permissions,
  exact copy files, or final images, or explicitly delegates a bounded choice.
  An agent may record an explicit natural-language decision and continue; it
  must stop and ask on preference-only or ambiguous language. Rankings,
  validators, prior drafts, and inferred backfills never count as approval.

- `$gconf-youtube-research` takes one YouTube URL or an existing video snapshot,
  collects and normalizes metadata, time-bound statistics, comments, chapters,
  description, thumbnail, captions or transcript fallback, and updates
  `YouTube/catalog.json`. It writes only the YouTube research package, never
  SQLite or Obsidian. Hand the resulting `video_folder` to
  `$gconf-knowledge-ingest` when indexing or later analysis is requested.
- `$gconf-yt-dlp` takes a video URL and produces a probe or diagnostic result.
  It is a low-level helper for caption and extractor troubleshooting, not the
  complete artifact workflow, a static-web research tool, or a media archiver.
  Return to `$gconf-youtube-research` after diagnosis.
- `$gconf-local-whisper` takes an existing local audio or video file plus an
  output base and produces `.srt` and `.txt` transcripts. It may serve the
  YouTube fallback, but it never ingests the transcript, stores a model in the
  repository, or installs dependencies without explicit approval. Pass a
  completed local artifact to `$gconf-knowledge-ingest` only when indexing is
  separately requested.
- `$gconf-knowledge-ingest` takes an already-collected YouTube, Telegram,
  Instagram, official-lab Web Article, or local research package. It preserves
  raw sources, updates `knowledge/_index/gconf.sqlite`, refreshes generated
  `knowledge/sources/` cards, and writes an auditable report to
  `knowledge/runs/`. It never collects, transcribes, performs semantic
  extraction, or publishes. Hand off to `$gconf-insight-extract` when semantic
  knowledge must be identified or refreshed.
- `$gconf-insight-extract` takes a valid SQLite index and one pending or stale
  logical evidence batch. It reads complete evidence context and writes only
  traceable `review_status: candidate` cards in typed `knowledge/` folders plus
  processing markers. It never calls the network, approves candidates, drafts
  content, or publishes. Human review decides whether a candidate becomes part
  of the approved semantic layer used by editorial work.
- `$gconf-announcement-analysis` takes a ready local knowledge context, the live
  `gconf.io` page, announcement history, the tone standard, and current public
  signals. It writes `analysis.md` and `manifest.json` only under a new
  `research/announcement_analysis/runs/<UTC-run-id>/`, proposes two or three
  directions, and leaves selection unset. It never refreshes knowledge,
  collects sources, writes public copy, or chooses the direction. A human must
  select a direction before `$gconf-announcement-writer` may run.
- `$gconf-announcement-writer` takes a validated announcement-analysis run, a
  human-selected `direction_id`, prior Telegram and Instagram locators,
  screenshots, product name, voice mode, address form, and a confirmed-facts
  allowlist. It writes a brief, evidence ledger, standalone Telegram draft,
  and exactly six Instagram slides plus caption under a new
  `research/announcement_drafts/runs/<UTC-run-id>/`. It never selects strategy,
  invents offer facts, designs graphics, mutates evidence, or publishes. After
  human copy and permission review, hand approved Instagram copy to
  `$gconf-instagram-carousel-designer` and an explicitly selected clean
  Telegram draft to `$gconf-telegram-formatter`.
- `$gconf-instagram-carousel-designer` takes approved six-slide copy from one
  announcement-writer run and the required local visual references. It uses one
  approved 1080×1350 master frame and grayscale structural derivatives to write
  a new `research/instagram_carousels/runs/<UTC-run-id>/` containing source,
  normalized, and validated six-image assets. It never rewrites strategy or
  copy, invents facts, modifies source references, or publishes. Human visual
  approval is required before manual publication.
- `$gconf-news-radar` takes current public AI signals, a mandatory 30-day sweep
  of all local source lanes (with a documented maximum extension to 60 days),
  all semantic-card types, full GCONF-owned prior-channel coverage, and earlier
  news runs. The lanes include public Telegram, Instagram posts and comments,
  YouTube videos, transcript chunks and comments, protagonist sources, and
  internal GCONF/community material as discovery-only evidence. It writes a
  validated, deduplicated, scored backlog only
  under a new `research/news_analysis/runs/<UTC-run-id>/`, with
  `selected_topic_ids: []`. It never drafts public copy, selects topics,
  collects or ingests sources, alters knowledge, or invokes the writer. A human
  must explicitly choose topic IDs before `$gconf-news-writer` may run.
- `$gconf-news-writer` takes a validated radar run, one or more explicit
  human-selected `topic_id` values, voice mode, address form, and an editorial
  or confirmed commercial CTA. It reopens primary sources and writes one
  reviewable Telegram draft per topic under a new
  `research/news_drafts/runs/<UTC-run-id>/`. It never discovers or substitutes
  topics, changes radar rankings, mutates evidence, or publishes. If freshness
  changes the central fact or selected focus, return the topic to human review;
  otherwise hand an explicitly selected clean draft to
  `$gconf-telegram-formatter` after editorial approval.
- `$gconf-telegram-formatter` takes explicit clean public-copy paths or explicit
  filenames from a writer run. It preserves facts, voice, CTA, links, and
  limitations while writing new, validated Markdown derivatives to
  `Telegram, News to publish/` by default. It never infers `latest`, selects or
  rewrites posts, overwrites source drafts, calls Telegram, schedules, or
  publishes. The output is a handoff for manual publication only.

### Knowledge flow

Do not duplicate collection logic in downstream skills. Route common requests
as follows:

- collect one YouTube video:
  `$gconf-youtube-research`;
- collect and index a YouTube video:
  `$gconf-youtube-research` → `$gconf-knowledge-ingest`;
- collect, index, and identify new pains, cases, labs, technologies, trends, or
  claims:
  `$gconf-youtube-research` → `$gconf-knowledge-ingest` →
  `$gconf-insight-extract`;
- index an already-collected Telegram, Instagram, Web Article, YouTube, or
  local research package:
  `$gconf-knowledge-ingest`, followed by `$gconf-insight-extract` only when
  semantic extraction is requested.

SQLite and generated source cards are a derived machine index, not the
editorial source of truth. Raw artifacts remain the evidence. Insight Extract
creates candidates only; a completed processing fingerprint means the evidence
batch was reviewed, not that its semantic candidates were human-approved.
Reviewed Markdown cards are the approved semantic layer.

### Announcement flow

Keep the announcement handoff explicit:

> knowledge readiness → `$gconf-announcement-analysis` → human direction selection → `$gconf-announcement-writer` → human copy and permission approval → `$gconf-instagram-carousel-designer` and/or `$gconf-telegram-formatter` → manual publication

- The live `https://www.gconf.io/` page is the mandatory current-offer
  baseline. A cached or historical approximation is not sufficient.
- If announcement preflight finds invalid, pending, or stale knowledge, stop
  and hand off to `$gconf-knowledge-ingest` and then
  `$gconf-insight-extract`; never refresh either layer silently.
- Analysis ranks and proposes directions but writes no announcement copy and
  leaves human selection unset.
- Writing requires an explicit `direction_id` and confirmed-facts allowlist.
  Unknown dates, prices, speakers, capacity, curriculum, results, availability,
  CTA destinations, or permissions remain placeholders or blockers.
- Evidence approval and publication permission are separate gates. Named or
  exact quoted material requires documented permission or prior official GCONF
  publication before it enters clean public copy.
- The carousel designer accepts approved copy only and may not solve visual
  constraints by deleting meaning or adding claims. The Telegram formatter
  accepts an explicitly selected clean public post only.

### News flow

Keep the news handoff explicit:

> live signals plus local knowledge → `$gconf-news-radar` → human topic selection → `$gconf-news-writer` → human draft selection → `$gconf-telegram-formatter` → manual publication

A request for possible or priority news topics stops after the radar backlog.
The radar must review all required source lanes and full prior coverage, leave
`selected_topic_ids` empty, and never invoke the writer. Only a later request
containing a validated radar run and explicit topic IDs may produce drafts.
The writer must recheck primary-source freshness and may not replace a stale or
materially changed topic. Neither news skill silently ingests live web evidence;
use `unindexed_observation` and `ingestion_queue` until a valid local source
package exists. Formatting starts only from a human-selected clean draft, and
publication remains manual.

### Mandatory human gates

Human judgment is required for:

1. reviewing and approving semantic candidates;
2. selecting one announcement direction;
3. confirming the announcement fact and CTA allowlist;
4. deciding quotation, case, attribution, and publication permissions;
5. selecting news topic IDs from a validated radar run;
6. accepting primary-source freshness and any material limitations;
7. approving final public copy and selecting the exact draft to hand off;
8. approving the six final carousel images;
9. publishing or scheduling any content.

No completion marker, score, ranking, validator result, or approved evidence
card replaces these editorial and publication gates.

Agents perform the technical recording. Human decisions may be expressed in
ordinary language. Record explicit choices through `$gconf-editorial-gates`
before the downstream action and pass the resulting `decision_id`. A changed
choice creates a new decision with `supersedes`; never rewrite the old card.
Backfilled historical decisions use `inferred_backfill` and
`needs_confirmation` until a human confirms them. Publication remains manual.

### Artifact and storage responsibilities

- Source packages: `telegram/`, `Instagram/`, `YouTube/`, `Web Articles/`, and
  local source material under `research/`. Treat source evidence as immutable
  during ingestion.
- Derived machine index: `knowledge/_index/gconf.sqlite`, containing normalized
  sources, documents, comments, transcript chunks, reply edges, checksums,
  provenance, and full-text search indexes.
- Generated source cards and ingestion reports: `knowledge/sources/` and
  `knowledge/runs/`. They may be refreshed or recreated by the importer.
- Obsidian semantic layer: typed folders such as `knowledge/pains/`,
  `knowledge/cases/`, `knowledge/trends/`, `knowledge/technologies/`,
  `knowledge/labs/`, `knowledge/actors/`, `knowledge/cohorts/`, and
  `knowledge/claims/`. Use `review_status`, not folder location, to distinguish
  candidates from reviewed knowledge. Open `knowledge/` directly as the
  Obsidian vault.
- Processing state: `knowledge/processing/`. Fingerprint completion records
  extraction review, not semantic approval.
- Editorial control plane: `knowledge/editorial/`. Generated run cards and
  Obsidian Bases expose workflow state; append-only decision cards preserve
  human-gate provenance. These card types are operational metadata and must
  never enter SQLite evidence or semantic extraction.
- Editorial analysis runs: `research/announcement_analysis/` and
  `research/news_analysis/`.
- Public-copy writer runs: `research/announcement_drafts/` and
  `research/news_drafts/`.
- Visual runs: `research/instagram_carousels/`.
- Telegram publication handoff: `Telegram, News to publish/`. Files here are
  formatted derivatives, not proof of publication.

The SQLite file must remain rebuildable from local artifacts without deleting
reviewed semantic cards.

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

### Insight extraction and semantic-card rules

After deterministic ingestion, run:

```bash
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py status --scope next-gconf
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py prepare --scope next-gconf --batch BATCH_ID
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py finalize --scope next-gconf --batch BATCH_ID --outputs CARD_ID
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py validate
```

Write candidates directly to their typed folders. Allowed semantic types are:

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
- `source_wave: internal | external | mixed`;
- exact evidence locators;
- an exact short quote and human-readable support statement for every locator;
- relevant first/last-seen dates;
- explicit event context with `explicit`, `inferred_by_time`, or `unattributed`
  attribution;
- supported relationships to other cards.

Do not automatically promote candidates, silently rewrite approved cards, or
treat research summaries as primary evidence. Comments are useful evidence of
audience language and pain, but not automatically proof of a factual claim.
Reported participant cases remain reported cases unless independently
verified.

Case cards distinguish `gconf_participant`, `gconf_community`,
`internal_protagonist`, and `external` origins. A message published in a cohort
chat after the event is not automatically a participant outcome. Run
`render-evidence` so every candidate remains reviewable in Obsidian without a
manual SQLite lookup.

### Current knowledge snapshot

The first completed import contains:

- 20 source records;
- 7,942 normalized documents;
- 2,405 timestamped YouTube transcript chunks;
- 6,359 reply or parent relations;
- public, internal, and editorial visibility labels;
- generated Obsidian source cards and Bases views.

These counts are a snapshot, not a permanent invariant. Run `scan`, `ingest`,
and `validate` after adding new exports, then inspect Insight Extract status.
Semantic candidates are not approved merely because their processing batch is
complete.

## Definition of done

The project is complete when the submission includes:

- a source-backed announcement for the next GCONF cohort;
- 3–5 evidence-backed key takes with audience rationale;
- a concrete, implementable daily AI-content loop;
- explicit growth hypotheses, signals, and feedback mechanics;
- a source/assumption appendix sufficient to audit important claims;
- a final rubric review covering taste, philosophy, research, process, and growth.

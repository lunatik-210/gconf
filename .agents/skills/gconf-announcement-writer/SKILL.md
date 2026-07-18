---
name: gconf-announcement-writer
description: Turn a human-selected direction from a GCONF announcement-analysis run into evidence-backed Telegram and Instagram announcement drafts. Use when Codex must preserve the structure of prior GCONF announcements, adapt the current offer into a genuinely new cohort narrative, write in the canonical GCONF voice with real audience language, and produce a six-slide Instagram carousel plus caption and a standalone Telegram announcement. Do not use to choose the strategic direction, invent cohort facts, collect sources, alter the knowledge base, design carousel graphics, or publish content.
---

# GCONF Announcement Writer

Create one channel-neutral writing brief, then adapt it into Telegram and
Instagram copy. Treat the selected analysis direction as the strategy and the
canonical tone standard as the writing constraint.

## Run the workflow

1. Read the repository `AGENTS.md`, the complete
   `editorial/gconf-tone-of-voice.md`, and both files in `references/`.
2. Confirm these inputs before drafting:
   - analysis run directory;
   - confirmed `$gconf-editorial-gates` `announcement_direction_selection` decision;
   - confirmed `offer_fact_and_cta_allowlist` decision, using
     `allowlist:none` when no future offer facts are confirmed;
   - previous Telegram and Instagram locators;
   - screenshots directory;
   - product name, voice mode, address form, and confirmed-facts allowlist.
   If the current instruction explicitly selects the direction, record it and
   continue. If it only expresses a preference, ask the human and stop.
3. Prepare a compact, read-only context packet:

```bash
python3 -B .agents/skills/gconf-announcement-writer/scripts/prepare_draft_context.py \
  --analysis-run research/announcement_analysis/runs/RUN_ID \
  --decision-id DECISION_ID \
  --facts-decision-id FACTS_DECISION_ID \
  --product-name 'PRODUCT NAME' \
  --voice-mode GCONF \
  --address vy \
  --facts-json PATH_TO_FACTS_JSON > /tmp/gconf-announcement-draft-context.json
```

The script must not write to SQLite, Obsidian, raw sources, or the analysis
run. The separate gate command owns the append-only decision write. Stop when
the run, decision, direction, previous references, or screenshot set is
missing.
4. Build `brief.md` before public copy. Fix one behavioral transition, one
   primary tension, 3–5 meaning pillars, the inherited program frame, a case
   shortlist, audience-language phrases, confirmed facts, placeholders, and
   one primary CTA. Use a confirmed CTA verbatim; create the CTA placeholder
   only when the allowlist has no CTA. Before drafting slide 3, build six explicit mappings:
   `audience pain -> program action -> so-that outcome -> evidence locators`.
5. Search deeper only when a proof slot in the brief is unresolved. Prefer
   approved semantic cards. Use candidate cards only when fresher or uniquely
   relevant, and preserve their status and limitation in the ledger.
6. Write Telegram as a self-contained narrative: world shift, tension after the
   first artifact, new frame, experience/program, evidence, confirmed terms,
   limitation, and one CTA.
7. Write Instagram as exactly six slides plus a caption. Preserve the jobs of
   the previous carousel, not its old claims or tool-led promise. Slide 4 must
   use at least four fresh or recent non-prior-announcement locators. Reuse at
   most two historical requests and record why each remains relevant.
8. Create every artifact required by `references/output-contract.md`, then run:

```bash
python3 -B .agents/skills/gconf-announcement-writer/scripts/validate_draft.py \
  research/announcement_drafts/runs/RUN_ID
```

9. Report the drafts as ready for human review, never publish-ready while a
   placeholder or unresolved publication permission remains.

## Apply source priority

Use this order: user-confirmed facts; selected direction; live-site baseline;
approved cards; candidate cards when uniquely relevant; previous public
announcements; raw or live observations. Within comparable quality, prefer the
fresher source. Brand spine and canonical voice remain constraints rather than
freshness-ranked claims.

Classify evidence as `fresh` at 0–30 days, `recent` at 31–90 days, and
`historical` after 90 days. Classify its role as `audience_voice`,
`organizer_interpretation`, `prior_announcement`, `case_proof`, or
`offer_fact`. A prior announcement defines structure and voice; it never
satisfies a fresh-audience slot merely because it was recently published.

Never let a candidate silently become an approved fact. Never let freshness
override a missing locator, exact quote, limitation, or attribution.

## Protect evidence and publication rights

For every meaningful case or quotation record its card ID, exact locator,
source URL or local path, date, author/attribution, visibility, review status,
case origin, proof level, limitation, and publication-permission status.

Use these permission values:

- `confirmed` — explicit permission is documented;
- `previously_public_by_gconf` — the exact case or phrase was already published
  by an official public GCONF account;
- `unknown` — no publication basis is documented.

`review_status: approved` concerns evidence quality, not advertising rights.
Named or exact quoted material may enter clean public copy only with
`confirmed` or `previously_public_by_gconf`. Otherwise paraphrase without
adding facts and mark the internal draft `[НУЖНО СОГЛАСОВАТЬ]`, or omit it.

Public audience language with unknown advertising permission may support a
close anonymized synthesis when the source itself is public. Do not use quote
marks, names, roles, locations, or unique biographical facts in that synthesis;
keep the exact wording and locator in the evidence ledger.

Keep `gconf_participant`, `gconf_community`, `internal_protagonist`, and
`external` distinct. Do not claim that a community case was produced in a
cohort unless event attribution is explicit. Do not present an external case
as a GCONF result.

## Enforce writing constraints

- Use the selected `GCONF` or `Dima` mode; default to `GCONF`.
- Choose `вы` or `ты` once. Quoted speech may retain its original form.
- Lead with behavior change, not a list of models or tools.
- Reuse only allowlisted product facts. A confirmed CTA is an exact allowlisted
  string with a real locator or explicit user approval. Keep every other date,
  cohort number, CTA destination, speaker, metric, result, and availability
  claim as a clear placeholder.
- Preserve one primary CTA across both channels.
- Reject slide-3 blocks that only name a component or sequence. Each block must
  say what becomes easier, safer, repeatable, or possible for the participant.
- Do not copy names, professions, countries, or requests from a previous launch
  unless the exact current evidence and a carry-forward reason are recorded.
- Keep evidence annotations out of clean public copy; put them in the ledger.
- Do not create landing-page copy, graphics, or publication actions.

Complete the canonical voice audit and require at least 8/10 with no zero for
Research. A clean style cannot compensate for unsupported claims.

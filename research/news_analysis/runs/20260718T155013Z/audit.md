# Audit — GCONF News Radar 20260718T155013Z

## Scope

- Запрос: минимум две темы для каждого формата `flash`, `gconf_field_note`, `story_lore`.
- Результат: 6 passing candidates; 2 на формат; 5 `recommended`, 1 `reserve`.
- Public copy не создавалась. Рабочие названия нейтральны.
- `selected_topic_ids: []`; human gate сохранён.
- `$gconf-news-writer` не запускался.

## Read-only boundaries

- Подготовлен compact context через `prepare_radar_context.py --window-days 14 --max-candidates 10`.
- SQLite, Obsidian cards, Telegram/Instagram/YouTube exports, Web Articles и прежние runs не изменялись.
- Создан только новый каталог `research/news_analysis/runs/20260718T155013Z/`.
- Live sources не ingest-ились; отсутствующие материалы записаны в `ingestion_queue`.

## Source hierarchy

1. Official primary: GitHub changelog, Anthropic product/research history, GCONF / AI LOVERS first-party posts.
2. Independent primary: White House EO 14409 and GOLD EAGLE release.
3. Approved local semantic cards: только как traceable normalization уже существующего public source, не как независимое подтверждение.
4. Secondary/social material не использовался для material facts.

Product-release candidates имеют официальный первичный источник. Broad-trend candidate `news-20260714-fable-cyber-governance-sequence` имеет двух независимых официальных publishers: Anthropic и White House.

## Freshness

- Default live window: 2026-07-04 through 2026-07-18.
- Live candidates/events: Anthropic origin story 6 July; GCONF weekend results 8 July; GCONF team processes 13 July; GitHub and GOLD EAGLE 14 July; GitHub Models brownout 16 July.
- Expanded window applied only to:
  - GitHub Models retirement: source announcement 1 July, but first scheduled brownout occurred 16 July and next is 23 July.
  - Fable governance sequence: began 9 June, but received new institutional delta with GOLD EAGLE on 14 July.
- Older GCONF cases are context for the comparative field hypothesis, not sole news events.

## Coverage queries

Each shortlisted candidate received a topic-specific full-archive query:

1. `GitHub Models`
2. `code scanning AI security`
3. `Claude Code internal CLI`
4. `Fable 5 jailbreak safeguards`
5. `Codex architecture requirements`
6. `AI weekend ticket calendar`

Coverage packet used the complete public AI LOVERS archive snapshot: 321 documents, 2023-06-14 through 2026-07-13.

## Semantic duplicate decisions

### Claude Code origin story — pass

- Entity already present: yes.
- Central claim already present: no; archive covers setup/release, not origin sequence.
- Same behavioral transition: no.
- Same audience consequence: partial.
- Same editorial angle: no.
- New delta: official inside history of internal CLI becoming a product.

### Fable cyber governance sequence — pass

- Entity already present: yes.
- Central claim already present: only availability.
- Same behavioral transition: no.
- Same audience consequence: partial.
- Same editorial angle: no.
- New delta: full sequence plus published severity framework and GOLD EAGLE.

### GitHub AI security detections — pass

- Entity already present: GitHub/Copilot broadly, exact release absent.
- Central claim already present: no.
- Same behavioral transition: no.
- Same audience consequence: no.
- Same editorial angle: no.
- New delta: AI-labeled findings inside PR review, informational status and billing conditions.

### GitHub Models retirement — pass

- Entity/release already present: no direct coverage.
- Central claim already present: no.
- Same behavioral transition: model routing is adjacent, provider shutdown is new.
- Same audience consequence: no.
- Same editorial angle: no.
- New delta: brownouts and hard migration deadline.

### GCONF Telegram control plane — conditional pass

- Entity and events already present: yes.
- Central claim already present: substantially yes in post 1058.
- Same behavioral transition: yes at each stage separately.
- Same audience consequence: yes.
- Same editorial angle: partial.
- New delta: five-week sequence and decision-rights analysis.
- Condition: publication requires a new safe end-to-end workflow artifact. Without it this becomes a semantic duplicate and must be rejected.

### GCONF format time horizon — reserve

- Cases already present: yes.
- Central comparative claim already present: no.
- Same behavioral transition: cases are individual; comparative format hypothesis is new.
- Audience consequence: adjacent.
- Editorial angle: new but weakly evidenced.
- New delta: weekend and three-week formats treated as different activation/support mechanisms.
- Limitation: selection bias and lack of matched follow-up prevent a causal conclusion.

## Score arithmetic

Formula: market + GCONF + novelty + evidence + freshness + actionability − risk.

- `news-20260706-claude-code-origin-story`: 18 + 19 + 19 + 18 + 10 + 9 − 4 = **89**.
- `news-20260714-fable-cyber-governance-sequence`: 20 + 18 + 19 + 18 + 9 + 8 − 7 = **85**.
- `news-20260714-github-ai-security-detections`: 17 + 17 + 19 + 19 + 10 + 9 − 7 = **84**.
- `news-20260716-github-models-retirement-brownout`: 15 + 16 + 20 + 20 + 10 + 10 − 7 = **84**.
- `news-20260713-gconf-telegram-control-plane`: 18 + 20 + 14 + 17 + 10 + 10 − 8 = **81**.
- `news-20260708-gconf-format-time-horizon`: 14 + 20 + 12 + 14 + 10 + 10 − 6 = **74**.

No score was raised to meet the requested quota. The second Field Note remains reserve rather than recommended.

## Evidence limitations and unresolved checks

- Anthropic origin story is a retrospective first-party narrative.
- The original Amazon jailbreak report underlying the Fable incident was not found as a public primary artifact.
- White House sources establish policy/initiative facts but do not prove operational efficacy or direct causality with Fable 5.
- GitHub changelog confirms product behavior and access conditions, not accuracy or false-positive rates.
- GCONF internal-process claims are public first-party self-reports without technical logs, costs or complete permission models.
- GCONF participant outcomes are selected organizer/self-reports; they do not provide denominator, matched cohorts or longitudinal retention.
- New quotations or identifying details require permission review before any Field Note is drafted.

## Format compliance

- `flash`: only narrow operational changes that fit a 40–90 word future handoff; no feature-list explainer was substituted.
- `story_lore`: each candidate contains a material event sequence, not a release rewritten as a story.
- `gconf_field_note`: only GCONF first-party practice and GCONF-observed participant evidence; no external event was rewritten as team experience.

## Quota independence

The requested two-per-format target was met without reclassifying earlier Release Explainer or Trend Translation candidates. If the Telegram control-plane team cannot provide a new artifact, the run still remains valid but that candidate should fail human review; the radar must not invent a replacement solely to preserve a quota.

## Boundary confirmation

- No headline options, leads, post paragraphs, CTA copy or publication-ready prose were written.
- No topic was selected.
- No writer or publisher was called.
- No ingestion occurred.
- Human review remains mandatory before any downstream writing.

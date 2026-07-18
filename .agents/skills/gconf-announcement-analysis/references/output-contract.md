# Announcement analysis output contract

## Contents

1. Run identity and source status
2. `analysis.md`
3. `manifest.json`
4. Final validation

## Run identity and source status

Use a unique UTC identifier in `YYYYMMDDTHHMMSSZ` format. Write both artifacts
to `research/announcement_analysis/runs/<run-id>/`. Do not overwrite another
run or create a mutable `latest` copy.

Record:

- generation time and corpus preflight result;
- live site URL, title, and access time;
- local source collection dates when available;
- pending/stale counts for `next-gconf` and `lab-signals`;
- the number of approved and candidate semantic cards used.

## `analysis.md`

Write neutral Russian. Use these sections in order:

1. `# Анализ следующего анонса GCONF`
2. `## Вердикт по данным и свежести`
3. `## Ядро текущего потока: gconf.io`
4. `## Историческая траектория Telegram-анонсов`
5. `## Сохранить, развить, перестать повторять, добавить`
6. `## Приоритет источников и свежесть`
7. `## Внутренние и внешние запросы аудитории`
8. `## Движения протагонистов`
9. `## Внешние AI-сигналы`
10. `## Кейсы для доказательства`
11. `## Пробелы, противоречия и неизвестные`
12. `## Направления следующего анонса`
13. `## Рекомендация`
14. `## Evidence appendix`

The current-offer section must extract, rather than merely summarize:
positioning, audience, behavioral transition, product mechanism, promised
outputs, proof cases, objections, CTA, page structure, and verified commercial
facts. Mark those commercial facts as belonging to the current cohort only.

The source-priority section must explain which fresh items displaced older
evidence, which historical items remain because they express a brand invariant
or unique proof, and where freshness conflicts with verification strength.

For every direction include:

- stable ID and short working title;
- central thesis;
- behavioral transition (`from` → `to`);
- primary audience and tension;
- why now;
- what is inherited from the live current offer;
- what is genuinely new;
- 3–6 evidence IDs/locators;
- risks, contradictions, and unsupported edges;
- growth hypothesis and observable behavior;
- separate Telegram, website, and Instagram editorial jobs-to-be-done;
- confidence: `high`, `medium`, or `low`.

Every pain, protagonist movement, and shortlisted case must show at least one
short exact quote alongside its card ID, locator, source author, source date,
visibility, and real source link. If there is no public link, show the local
artifact path and label access as internal/restricted. Do not write composite,
representative, corrected, or model-generated quotations.

Do not include sample headlines, lead paragraphs, CTA copy, page copy, or
carousel slide text.

## `manifest.json`

Write valid UTF-8 JSON with this top-level shape:

```json
{
  "schema_version": "2.0",
  "run_id": "YYYYMMDDTHHMMSSZ",
  "generated_at": "ISO-8601 UTC timestamp",
  "review_status": "draft",
  "selected_direction": null,
  "decision_refs": [],
  "workflow_status": "awaiting_human_selection",
  "publication_status": "not_ready",
  "source_snapshot": {
    "local_preflight": {},
    "site": {
      "url": "https://www.gconf.io/",
      "title": "",
      "accessed_at": "",
      "status": "live"
    }
  },
  "current_offer_baseline": {},
  "historical_trajectory": [],
  "audience_signals": [],
  "protagonist_movements": [],
  "external_ai_signals": [],
  "case_shortlist": [],
  "source_priority": {
    "weights": {
      "freshness": 35,
      "next_offer_relevance": 25,
      "evidence_strength": 20,
      "audience_specificity": 10,
      "novelty_vs_current_offer": 10
    },
    "ranked_evidence": []
  },
  "strategic_classification": {
    "carry_forward": [],
    "evolve": [],
    "retire": [],
    "new_signal": []
  },
  "directions": [],
  "unknown_future_cohort_details": [],
  "ingestion_queue": [],
  "evidence_index": []
}
```

Every evidence-bearing item must contain `evidence_status` with one of:
`fact`, `inference`, `proposal`, or `unindexed_observation`. Local items include
card IDs and locators; live items include a direct URL and access time.

Audience, protagonist, and case entries also contain `exact_quote`, `author`,
`source_date`, `visibility`, `source_url` or `local_source`, and `quote_verified`.
Set `quote_verified` to `true` only after exact comparison with the rendered
semantic-card Evidence block.

Every item in `ranked_evidence` contains `published_at` or `event_date`,
`accessed_at` where applicable, `freshness_days`, `freshness_band`, component
scores, total `priority_score`, and `selection_rationale`. Do not assign this
score to the live-site baseline or brand/voice rules; list those separately as
mandatory constraints.

Each direction object mirrors the fields required in `analysis.md` and contains
an `evidence_refs` array pointing into `evidence_index`. Keep
`selected_direction` as `null`; human review owns that decision.
Keep `decision_refs` empty. The later selection is an append-only
`announcement_direction_selection` card and never mutates this analysis run.

`unknown_future_cohort_details` must explicitly cover date, price, duration,
format, curriculum, speakers/protagonists, capacity, commercial terms, claimed
results, and CTA destination unless verified future facts were supplied by the
user.

`ingestion_queue` contains only public live sources that materially influenced
the analysis but are not present in the local knowledge pipeline. It is a queue,
not proof that ingestion occurred.

## Final validation

Before completion confirm:

- the site is the current-offer baseline and has a live access timestamp;
- Telegram provides trajectory, while Instagram is treated as adaptation and
  audience response;
- every important claim has a locator or direct URL;
- every quoted audience/protagonist/case phrase matches a real rendered Evidence
  block exactly and carries complete provenance;
- no synthetic quotation or guessed source URL appears;
- candidate and unindexed evidence is labeled;
- shortlisted pains, cases, news, protagonist ideas, and videos prefer the
  freshest evidence at comparable quality and expose their freshness metadata;
- older evidence has an explicit longitudinal, brand, or unique-proof reason;
- all directions preserve the brand spine and pass the canonical voice audit;
- internal participant, community, external audience, protagonist, and lab
  roles remain distinct;
- two or three directions differ in behavioral transition or primary tension,
  not merely wording;
- no future cohort fact was invented;
- no announcement copy appears in either artifact;
- Markdown and JSON contain the same direction IDs and recommendation order.

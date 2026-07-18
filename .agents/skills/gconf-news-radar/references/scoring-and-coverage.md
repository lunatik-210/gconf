# Radar scoring and coverage

## Eligibility gates

A candidate is ineligible when any of these is true:

- no material claim has a direct source;
- a product release lacks an official primary source;
- a broad market conclusion has fewer than two independent publishers;
- the central event is a rumor or future promise without attributable status;
- the same entity, claim, behavioral transition, and audience consequence were
  already covered and no evidence-backed delta exists;
- the candidate requires an invented GCONF fact or a safety/performance claim
  that cannot be qualified.

Keep strong but ineligible signals as `reject` only when their rejection teaches
the reviewer something useful. Otherwise omit them.

## Score

Score each component with integers and record a short rationale:

| Component | Maximum |
| --- | ---: |
| AI market and audience relevance | 20 |
| Relevance to the next GCONF themes | 20 |
| Novelty versus GCONF coverage | 20 |
| Evidence quality and sufficiency | 20 |
| Freshness | 10 |
| Actionability or experiment potential | 10 |

Apply an integer `risk_penalty` from 0 to 20 for publisher-only benchmarks,
uncertain availability, a weakly supported extrapolation, or hype that may
overstate practical change.

`priority_score = sum(component scores) - risk_penalty`.

- `recommended`: eligible, score 80–100;
- `reserve`: eligible, score 65–79;
- `reject`: ineligible or score below 65.

Never raise a score to meet a quota. Rank passing candidates by score, then
evidence quality, then freshness. Rank rejected items separately.

After eligibility and scoring, reserve at most one backlog place for each of
`protagonist`, `gconf_case`, and `audience_reaction` when that lane has a
passing candidate at 65 or above. Fill the other places by the common ranking.
Release an unused place to the common pool; never lower eligibility or scoring
to populate it. A candidate satisfies only its `primary_discovery_lane`.

## Freshness

- `live`: 0–14 days;
- `fresh`: 15–45 days;
- `recent`: 46–90 days;
- `historical`: more than 90 days.

Default discovery to `live`. A `fresh` structural trend may enter only when its
continued development or newly relevant evidence is explained. `recent` and
`historical` items can support context or coverage, not serve as the only news
event.

For the local corpus, use 30 days by default. A documented developing story may
extend to 60 days. Material older than 60 days is historical context or duplicate
coverage only.

## Semantic coverage test

For every candidate list the closest prior GCONF posts and drafts, then answer:

1. Is the main entity or release already present?
2. Is the central claim already present?
3. Is the same from-to behavioral transition already present?
4. Is the same audience consequence already present?
5. Is the proposed GCONF angle already present?
6. What exact new fact, consequence, contradiction, or practice makes this a
   new editorial unit?

Reject when answers 1–5 are substantially yes and question 6 has no supported
answer. Keyword difference alone is not a delta.

## Format recommendation

- `flash`: availability or operational change that can be useful in 40–90 words;
- `release_explainer`: a discrete release requiring before/after and access detail;
- `trend_translation`: multiple signals supporting one market or behavior shift;
- `gconf_field_note`: verified first-hand GCONF practice, never an external event
  rewritten as team experience;
- `story_lore`: an event sequence whose story explains a material cultural,
  technical, or security shift.

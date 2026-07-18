---
name: gconf-editorial-gates
description: Record, resolve, backfill, synchronize, and validate human editorial decisions across the GCONF evidence, news, announcement, design, formatting, and manual-publication workflows. Use whenever a user explicitly selects topics, directions, facts, permissions, copy, files, or final images; delegates a bounded choice to an agent; asks what decision is pending; or when a downstream GCONF skill must prove that its mandatory human gate passed. Do not infer a decision from ranking, preference language, a validator result, or an existing downstream artifact.
---

# GCONF Editorial Gates

Keep human judgment conversational and make its provenance machine-checkable.
Write append-only decision cards to `knowledge/editorial/decisions/`; keep full
agent runs immutable under `research/`.

## Interpret the user's instruction

- Treat `Берём X`, `делай вариант 2`, `напиши по X`, and an invocation that
  names the exact upstream run and selected item as `human_explicit`.
- Treat a bounded instruction such as `выбери сам две лучшие` as
  `agent_choice_authorized`; apply the upstream skill's existing ranking rules,
  record the authorization, and never broaden the delegated choice.
- Treat preference language such as `X выглядит сильнее` as ambiguous. Ask one
  concise question and stop the downstream workflow until answered.
- Never convert a score, recommendation, completion marker, old draft, or
  inferred backfill into a confirmed human decision.

Read [decision-contract.md](references/decision-contract.md) before adding a
gate type or changing decision provenance.

## Record and resolve

Record an explicit decision before taking the downstream action:

```bash
python3 -B .agents/skills/gconf-editorial-gates/scripts/editorial_gates.py record \
  --workflow news \
  --gate-type news_topic_selection \
  --upstream-ref research/news_analysis/runs/RUN_ID \
  --selected-ref TOPIC_ID \
  --decision-source human_explicit \
  --instruction-excerpt 'Берём TOPIC_ID'
```

Pass the returned `decision_id` to the downstream skill. Resolve it again in
the downstream context-preparation script. Resolution fails when the decision
is unconfirmed, superseded, mismatched, stale, or points to unknown selections.

```bash
python3 -B .agents/skills/gconf-editorial-gates/scripts/editorial_gates.py resolve \
  --decision-id DECISION_ID \
  --workflow news \
  --gate-type news_topic_selection \
  --upstream-ref research/news_analysis/runs/RUN_ID
```

Create a new decision with `--supersedes OLD_ID` when the human changes their
mind. Never edit the old card.

For an explicit semantic-card review, record `semantic_evidence_review` with
the selected card paths or IDs, then apply it deterministically:

```bash
python3 -B .agents/skills/gconf-editorial-gates/scripts/editorial_gates.py \
  apply-semantic-review --decision-id DECISION_ID --review-status approved
```

## Maintain the control plane

```bash
python3 -B .agents/skills/gconf-editorial-gates/scripts/editorial_gates.py sync
python3 -B .agents/skills/gconf-editorial-gates/scripts/editorial_gates.py status
python3 -B .agents/skills/gconf-editorial-gates/scripts/editorial_gates.py backfill
python3 -B .agents/skills/gconf-editorial-gates/scripts/editorial_gates.py validate
```

`backfill` creates only `inferred_backfill / needs_confirmation` cards. Ask the
human to confirm them; confirmation is a new append-only decision that
supersedes the inferred candidate.

## Preserve boundaries

- Never publish, schedule, approve evidence, or select strategy without a
  matching human decision.
- Never insert editorial cards into SQLite or semantic extraction.
- Record manual publication only after the human reports that it happened.
- Keep evidence review, editorial approval, and publication status distinct.
- Do not modify prior analysis, writer, design, or formatting runs.

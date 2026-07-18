---
name: gconf-telegram-formatter
description: Format explicitly selected, already-written GCONF Telegram posts into clean publish-handoff Markdown copies. Use when Codex is asked to move or copy approved news or post drafts into `Telegram, News to publish`, apply restrained Telegram formatting, create descriptive filenames, or validate a Telegram-ready handoff. Preserve the source text, facts, voice, CTA, links, and limitations; never choose posts, rewrite the editorial angle, overwrite source drafts, or publish to Telegram.
---

# GCONF Telegram Formatter

Create formatted derivatives of human-selected posts. Treat source drafts as
immutable and keep this skill separate from research, writing, and publishing.

Typical invocation:

> `$gconf-telegram-formatter Возьми POST_PATH и подготовь форматированную копию для Telegram.`

## Require explicit inputs

Require one or more source file paths, or a run directory plus explicit post
filenames, and a confirmed `news_copy_approval` or
`announcement_copy_approval` decision plus a separate confirmed
`publication_permission` decision from `$gconf-editorial-gates`. If the
current instruction explicitly selects and approves exact clean files, record
the decision first. Never infer `latest`, select posts by ranking, or sweep a
directory unless the user explicitly requests the whole directory.

Use `Telegram, News to publish/` at the repository root as the default output
directory. Honor a different destination when the user provides one.

## Run the workflow

1. Read repository `AGENTS.md`, the complete canonical
   `editorial/gconf-tone-of-voice.md`, and
   `references/telegram-formatting.md`.
2. Open every selected source in full. Accept only a clean public post. Stop on
   briefs, manifests, audits, evidence ledgers, unresolved placeholders, or a
   document that mixes public copy with internal notes.
3. Resolve the approval before formatting:

```bash
python3 -B .agents/skills/gconf-telegram-formatter/scripts/prepare_format_context.py \
  --writer-run research/news_drafts/runs/RUN_ID \
  --workflow news \
  --decision-id DECISION_ID \
  --permission-decision-id PERMISSION_DECISION_ID \
  --source research/news_drafts/runs/RUN_ID/POST.md
```

   Use `--workflow announcement` for announcement copy. Stop if the approval
   is missing, superseded, or bound to a different file SHA. When a news writer
   manifest has material `unresolved_items`, additionally require
   `--freshness-decision-id` for a confirmed `freshness_acceptance` decision.
4. Fix a formatting brief without changing the editorial brief:
   - preserve voice mode, address, lowercase or regular case, facts, dates,
     product names, limitations, source attribution, and the single CTA;
   - choose at most two meaningful bold spans;
   - keep one idea per short paragraph;
   - turn an existing parallel sequence of 3–7 items into a list;
   - keep links named and sources at the end.
5. Create one Markdown output per source. Use a descriptive human-readable
   filename based on the subject and behavioral angle, not `post.md`,
   `draft.md`, or an opaque topic ID.
6. Never overwrite. If the exact output already exists with identical content,
   report `already present`. If the name exists with different content, append
   a short UTC timestamp before `.md`.
7. Validate every output:

```bash
python3 -B .agents/skills/gconf-telegram-formatter/scripts/validate_telegram_posts.py \
  'Telegram, News to publish/POST.md'
```

8. Report the created file paths, visible character counts, and validation
   result. Do not publish or send the posts.

## Preserve editorial integrity

- Format only. Do not shorten, expand, fact-check, refresh, translate, or
  improve the argument unless the user separately asks for editorial work.
- Do not remove a material caveat to make the post cleaner.
- Do not add emoji, hashtags, a commercial CTA, a headline, or a second action
  unless they were present or the user explicitly requests them.
- Do not silently split a post that exceeds Telegram's text limit. Return it
  for human editorial review.
- Do not feed GFM directly to Bot API `MarkdownV2`; its escaping contract is
  different. Use a rendered Markdown handoff or a compatible Rich Markdown
  publisher as described in the reference.
- If the user requests a bot/API payload instead of an editable handoff,
  recheck the current official Telegram formatting contract before conversion.

## Protect system boundaries

Write only new files in the chosen handoff directory. Do not mutate writer
runs, radar runs, Telegram exports, SQLite, Obsidian, source evidence, or agent
manifests. Do not call Telegram, schedule a post, or claim that a file has been
published.

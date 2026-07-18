# Telegram formatting contract

Checked against the official Telegram Bot API on 2026-07-18:
https://core.telegram.org/bots/api#formatting-options

## Project handoff format

Use UTF-8 `.md` files with GitHub-flavored Markdown as the editable handoff.
Telegram Rich Markdown is GFM-compatible where possible. For manual posting,
copy from a rendered Markdown preview so formatting entities remain intact.

Do not send these files unchanged through Bot API `parse_mode=MarkdownV2`.
MarkdownV2 uses single-marker bold and requires escaping many punctuation
characters. If a downstream publisher only accepts `sendMessage`, convert the
approved handoff to Telegram HTML or MarkdownV2 at that integration boundary.

## Allowed default formatting

- Separate paragraphs with one blank line.
- Keep social paragraphs to 1–3 sentences.
- Use `**bold**` for no more than two meaningful spans.
- Use `- ` lists only for 3–7 parallel items.
- Use `[source name](https://...)` for named links.
- Keep source attribution as the final paragraph.
- Preserve 0–3 existing meaningful emoji; add none by default.
- Preserve lowercase when it is part of the approved GCONF artifact.

Do not add headings, tables, code fences, blockquotes, spoilers, decorative
dividers, emoji bullets, raw HTML, or multiple CTAs by default.

## Telegram limits and validation

The standard Telegram message text limit is 4096 characters after entity
parsing. The validator estimates visible characters after removing Markdown
syntax and fails above 4096. It also rejects internal metadata, raw HTML,
unbalanced bold markers, malformed named links, and lists outside the 3–7 item
range.

Formatting does not make a draft publication-approved. Preserve any existing
editorial caveat or readiness restriction and report it to the user.

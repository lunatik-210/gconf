# Source contracts

## YouTube

Treat `YouTube/catalog.json` and each video's stats schema 2.0 as the normalized
contract. Read the primary transcript named in `subtitles.primary_transcript`,
the comments wrapper, chapters, and description. Read raw `.info.json` only as
a fallback for missing normalized fields.

Locators:

- video: `youtube:<video_id>`
- transcript chunk: `youtube:<video_id>:<start>-<end>`
- comment: `youtube:<video_id>:comment:<comment_id>`

Never invoke yt-dlp or Whisper from the knowledge importer.

## Telegram

Accept Telegram Desktop-style exports with top-level `id`, `name`, `type`, and
`messages`. Flatten rich text while preserving embedded link URLs. Ignore
service messages without useful text but retain ordinary empty messages only
when their metadata carries a meaningful relation.

Locator: `telegram:<chat_id>:<message_id>`.

Use the chat type and filename to classify public versus internal sources.

## Instagram

Accept the current project export with `schema_version`, `profile`, and
`messages`. Combine caption and carousel slide alt text for the post body.
Store exposed comments as separate documents and preserve collection caveats.

Locators:

- post: `instagram:<profile>:<post_id>`
- comment: `instagram:<profile>:<post_id>:comment:<comment_id>`

## Local research

Import Markdown and CSV files under `research/` as secondary editorial
analysis. Use `research:<project-relative-path>` locators. Never treat a
research statement as a primary fact unless its semantic card links back to a
primary Telegram, Instagram, or YouTube locator.

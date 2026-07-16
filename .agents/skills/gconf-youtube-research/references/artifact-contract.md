# YouTube artifact contract

## Stats schema 2.0

Every video folder must contain `<id>.stats.json` with:

- `schema_version`, `status`, and `collected_at`;
- `workspace` with project-relative creator and video folders;
- `source` with canonical/original URL, title, channel, uploader, timing, tags,
  availability, and publication data;
- `statistics` with the public snapshot and comment completeness;
- `subtitles` with source type, language, primary transcript, and Whisper state;
- `files` with project-portable relative paths;
- `limitations` with explicit collection caveats.

## Comments schema 2.0

`<id>.comments.json` always exists. `collection.status` is:

- `complete` when reported and extracted counts match;
- `partial` when extraction returned fewer public comments than reported;
- `available` when comments were extracted but YouTube did not report a total;
- `unavailable` when the extractor did not expose a comments collection.

Never represent unavailable comments as a successful empty collection.

## Other files

- `<id>.info.json`: raw yt-dlp metadata and provenance source.
- `<id>.chapters.json`: wrapper with source identity and ordered chapters.
- `<id>.description`: original description.
- `<id>.thumbnail.<ext>`: selected thumbnail.
- `<id>.<lang>.srt`: primary YouTube caption when available.
- `<id>.transcript.srt` and `.txt`: Whisper-only fallback.

YouTube can expose both an original-language track (`ru-orig`) and a regular
language track (`ru`). Preserve both for provenance even when a snapshot shows
identical bytes; `subtitles.primary_transcript` identifies the preferred one.

All paths stored inside JSON are relative to their video folder or project root.

---
name: gconf-youtube-research
description: Collect and normalize a complete GCONF research package for a single YouTube video. Use when the user says to analyze a YouTube URL, collect statistics, download public comments, save captions or a transcript, place video research in YouTube/, refresh an existing video snapshot, validate the YouTube corpus, or migrate old YouTube artifacts. Prefer captions and use local Whisper only when captions are unavailable.
---

# GCONF YouTube Research

Run the bundled CLI rather than assembling ad-hoc yt-dlp commands.

## Collect one video

```bash
python3 .agents/skills/gconf-youtube-research/scripts/youtube_collect.py collect 'URL'
python3 .agents/skills/gconf-youtube-research/scripts/youtube_collect.py collect 'URL' --creator-dir YouTube/MatskevichDima
```

Apply this order:

1. Run the doctor.
2. Probe the URL without media download.
3. Reuse an existing folder when the video ID is already present.
4. Save metadata, comments, chapters, description, thumbnail, and source-language captions.
5. Prefer manual captions, then original-language automatic captions.
6. Download temporary audio and run local Whisper only if captions are unavailable.
7. Update `YouTube/catalog.json`.
8. Report exact paths, statistics freshness, comment completeness, and transcript source.

If a required tool is missing, show the doctor's setup suggestion and ask for
approval. Never run an installer automatically.

## Corpus operations

```bash
python3 .agents/skills/gconf-youtube-research/scripts/youtube_collect.py doctor
python3 .agents/skills/gconf-youtube-research/scripts/youtube_collect.py validate
python3 .agents/skills/gconf-youtube-research/scripts/youtube_collect.py normalize
```

Read [artifact-contract.md](references/artifact-contract.md) when changing the
JSON format. Use `$gconf-yt-dlp` for extractor troubleshooting and
`$gconf-local-whisper` for standalone local transcription.

The CLI result already exposes `collected_at`, `statistics`,
`transcript_source`, `primary_transcript_file`, and `video_folder`; use these
fields for the user-facing completion summary. Caption variants such as
`ru-orig` and `ru` may both be retained because they represent distinct YouTube
tracks even when their current bytes happen to match.

## Downstream handoff

Do not write to SQLite or Obsidian from this skill. When the user also asks to
add, index, analyze, or curate the collected package, use
`$gconf-knowledge-ingest` after collection succeeds. Pass its local
`video_folder` or `stats` path; never repeat yt-dlp or transcription work.

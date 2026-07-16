---
name: gconf-yt-dlp
description: Diagnose and use yt-dlp for GCONF YouTube work. Use when probing a video URL, inspecting metadata or caption availability, troubleshooting yt-dlp/ffmpeg, or preparing the low-level extraction used by gconf-youtube-research. Do not use for static web research, DRM bypass, or silent media archiving.
---

# GCONF yt-dlp

Run the bundled doctor before the first live request or after an extractor error:

```bash
python3 .agents/skills/gconf-yt-dlp/scripts/doctor.py
```

Probe a single video without downloading media:

```bash
python3 .agents/skills/gconf-yt-dlp/scripts/probe_url.py --url 'https://www.youtube.com/watch?v=...'
```

Follow these rules:

1. Probe before extracting files.
2. Use `--no-playlist` unless the user explicitly requests playlist enumeration.
3. Prefer subtitles over media downloads.
4. Never store cookies, credentials, or browser profiles in the repository.
5. If a binary is missing, show the doctor's installation suggestion and request approval before running any installer.
6. Treat public statistics as a time-bound snapshot.

For the complete project artifact workflow, use `$gconf-youtube-research`.
Read [setup.md](references/setup.md) only when a dependency is missing.

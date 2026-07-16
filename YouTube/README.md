# YouTube research workflow

This directory contains reproducible, source-backed YouTube research packages.
The repository-local Codex skill is `$gconf-youtube-research`.

## 1. First run

From the project root:

```bash
python3 .agents/skills/gconf-youtube-research/scripts/youtube_collect.py doctor
```

The doctor checks Python, `yt-dlp`, `ffmpeg`, `whisper-cli`, the local Whisper
model, project configuration, and the output directory. Missing tools are
reported with macOS or Linux setup suggestions. Installation is never automatic:
review the command and explicitly approve it before an agent runs it.

Whisper is optional when YouTube captions are available.

## 2. Use from Codex

Explicit invocation:

```text
$gconf-youtube-research https://www.youtube.com/watch?v=VIDEO_ID
```

With an explicit protagonist or creator folder:

```text
$gconf-youtube-research URL; save it in YouTube/MatskevichDima
```

Natural-language requests such as “разбери это YouTube-видео”, “собери
комментарии” or “выгрузи статистику и субтитры” should trigger the same skill.

## 3. Use from the command line

```bash
python3 .agents/skills/gconf-youtube-research/scripts/youtube_collect.py collect 'URL'
python3 .agents/skills/gconf-youtube-research/scripts/youtube_collect.py collect 'URL' --creator-dir YouTube/MatskevichDima
python3 .agents/skills/gconf-youtube-research/scripts/youtube_collect.py validate
python3 .agents/skills/gconf-youtube-research/scripts/youtube_collect.py normalize
```

Without `--creator-dir`, the collector uses YouTube `channel`, then `uploader`,
then `UnknownChannel`. Existing videos are found by video ID and refreshed in
place.

## 4. Missing dependencies

On macOS the doctor may suggest:

```bash
brew install yt-dlp ffmpeg whisper-cpp
```

On Linux it may suggest `pipx install yt-dlp`, a system ffmpeg package, and an
external whisper.cpp setup. Keep the Whisper model outside this repository and
point to it with:

```bash
export WHISPER_MODEL="/absolute/path/to/ggml-large-v3.bin"
```

`WHISPER_CLI` can override the `whisper-cli` executable path.

The collector never stores cookies, credentials, or browser profiles. Public
statistics are snapshots and may change after collection.

---
name: gconf-local-whisper
description: Transcribe local audio or video with whisper.cpp for the GCONF project. Use when YouTube captions are unavailable, when a user requests a local transcript, or when diagnosing ffmpeg, whisper-cli, and Whisper model availability on macOS or Linux. Do not install tools or download models without explicit user approval.
---

# GCONF Local Whisper

Run the doctor:

```bash
python3 .agents/skills/gconf-local-whisper/scripts/doctor.py
```

Transcribe:

```bash
python3 .agents/skills/gconf-local-whisper/scripts/transcribe.py INPUT --output-base OUTPUT --language ru
```

The script:

1. Finds `ffmpeg` and `whisper-cli` on `PATH`.
2. Honors `WHISPER_CLI` and `WHISPER_MODEL`.
3. Converts input to temporary 16 kHz mono WAV.
4. Retries on CPU if the default GPU/Metal run fails.
5. Produces `.srt` and `.txt`.
6. Removes only its temporary WAV.

Never place a Whisper model in the repository. When dependencies are missing,
read [setup.md](references/setup.md), show the suggestion, and ask before
running installation commands.

#!/usr/bin/env python3
"""Convert media to 16 kHz mono WAV and transcribe it with whisper.cpp."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from doctor import executable_from_env, find_model


def run(command: list[str]) -> None:
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"command failed with exit code {result.returncode}: {command[0]}")


def transcribe(source: Path, output_base: Path, language: str) -> None:
    ffmpeg = shutil.which("ffmpeg")
    whisper = executable_from_env("whisper-cli", "WHISPER_CLI")
    model = find_model()
    if not ffmpeg or not whisper or not model:
        raise RuntimeError("Whisper fallback is not configured; run scripts/doctor.py")
    output_base.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gconf-whisper-") as temp_dir:
        wav = Path(temp_dir) / "audio_16k.wav"
        run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(source),
                "-map",
                "0:a",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-c:a",
                "pcm_s16le",
                str(wav),
            ]
        )
        whisper_command = [
            whisper,
            "-m",
            model,
            "-f",
            str(wav),
            "-l",
            language,
            "-otxt",
            "-osrt",
            "-of",
            str(output_base),
            "-pp",
        ]
        result = subprocess.run(whisper_command, check=False)
        if result.returncode != 0:
            # Metal/GPU allocation can fail even when discovery succeeds. Retry
            # deterministically on CPU before asking the user to reconfigure.
            output_base.with_suffix(".srt").unlink(missing_ok=True)
            output_base.with_suffix(".txt").unlink(missing_ok=True)
            cpu_result = subprocess.run([*whisper_command, "-ng"], check=False)
            if cpu_result.returncode != 0:
                raise RuntimeError(
                    "whisper-cli failed on GPU "
                    f"({result.returncode}) and CPU ({cpu_result.returncode})"
                )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Transcribe local media")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-base", type=Path, required=True)
    parser.add_argument("--language", default="auto")
    args = parser.parse_args(argv)
    source = args.input.expanduser().resolve()
    if not source.is_file():
        print(f"input file not found: {source}", file=sys.stderr)
        return 1
    try:
        transcribe(source, args.output_base.expanduser().resolve(), args.language)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

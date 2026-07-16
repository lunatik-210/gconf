#!/usr/bin/env python3
"""Discover ffmpeg, whisper-cli, and a local Whisper model."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any


MODEL_CANDIDATES = (
    "~/.cache/hyperframes/whisper/models/ggml-large-v3.bin",
    "~/.cache/whisper.cpp/ggml-large-v3.bin",
    "~/.cache/whisper/ggml-large-v3.bin",
)


def executable_from_env(name: str, env_name: str) -> str | None:
    configured = os.environ.get(env_name)
    if configured:
        path = Path(configured).expanduser()
        return str(path) if path.is_file() and os.access(path, os.X_OK) else None
    return shutil.which(name)


def find_model() -> str | None:
    configured = os.environ.get("WHISPER_MODEL")
    candidates = ([configured] if configured else []) + list(MODEL_CANDIDATES)
    for candidate in candidates:
        if candidate and Path(candidate).expanduser().is_file():
            return str(Path(candidate).expanduser().resolve())
    return None


def setup(tool: str, system: str) -> dict[str, Any]:
    if system == "Darwin":
        package = "whisper-cpp" if tool == "whisper-cli" else "ffmpeg"
        return {
            "command": ["brew", "install", package],
            "requires_approval": True,
        }
    return {
        "instructions": "See references/setup.md for Linux installation.",
        "requires_approval": True,
    }


def build_report() -> dict[str, Any]:
    system = platform.system()
    ffmpeg = shutil.which("ffmpeg")
    whisper = executable_from_env("whisper-cli", "WHISPER_CLI")
    model = find_model()
    checks = [
        {
            "name": "ffmpeg",
            "status": "ok" if ffmpeg else "warn",
            "path": ffmpeg,
            **({} if ffmpeg else {"setup": setup("ffmpeg", system)}),
        },
        {
            "name": "whisper-cli",
            "status": "ok" if whisper else "warn",
            "path": whisper,
            **({} if whisper else {"setup": setup("whisper-cli", system)}),
        },
        {
            "name": "whisper-model",
            "status": "ok" if model else "warn",
            "path": model,
            **(
                {}
                if model
                else {
                    "setup": {
                        "instructions": "Place a ggml model outside the repo and set WHISPER_MODEL.",
                        "requires_approval": True,
                    }
                }
            ),
        },
    ]
    return {
        "ok": all(c["status"] == "ok" for c in checks),
        "available_for_fallback": all(c["status"] == "ok" for c in checks),
        "platform": {"system": system, "machine": platform.machine()},
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check local Whisper dependencies")
    parser.add_argument("--human", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.human:
        for check in report["checks"]:
            print(f"{check['status'].upper():4} {check['name']}: {check.get('path') or 'not found'}")
    else:
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

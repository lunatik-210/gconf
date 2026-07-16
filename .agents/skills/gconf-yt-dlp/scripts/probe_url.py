#!/usr/bin/env python3
"""Read-only single-video yt-dlp probe."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from typing import Any


def summarize(info: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "channel": info.get("channel"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "upload_date": info.get("upload_date"),
        "availability": info.get("availability"),
        "live_status": info.get("live_status"),
        "webpage_url": info.get("webpage_url"),
        "start_time": info.get("start_time"),
        "comment_count": info.get("comment_count"),
        "manual_subtitles": sorted((info.get("subtitles") or {}).keys()),
        "automatic_captions": sorted((info.get("automatic_captions") or {}).keys()),
    }


def probe(url: str, timeout: int = 120) -> dict[str, Any]:
    binary = shutil.which("yt-dlp")
    if not binary:
        raise RuntimeError("yt-dlp is missing; run scripts/doctor.py")
    command = [
        binary,
        "--dump-single-json",
        "--skip-download",
        "--no-playlist",
        "--no-warnings",
        "--no-progress",
        url,
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, timeout=timeout, check=False
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip())
    info = json.loads(result.stdout)
    return {"ok": True, "url": url, "summary": summarize(info), "info": info}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe one video without media download")
    parser.add_argument("--url", required=True)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args(argv)
    try:
        payload = probe(args.url, args.timeout)
    except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        payload = {"ok": False, "url": args.url, "error": str(exc)}
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 1
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

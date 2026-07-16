#!/usr/bin/env python3
"""Collect, normalize, and validate GCONF YouTube research artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


SCHEMA_VERSION = "2.0"
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[4]
CONFIG_PATH = PROJECT_ROOT / "youtube.config.json"
YT_DLP_DOCTOR = (
    PROJECT_ROOT / ".agents/skills/gconf-yt-dlp/scripts/doctor.py"
)
WHISPER_DOCTOR = (
    PROJECT_ROOT / ".agents/skills/gconf-local-whisper/scripts/doctor.py"
)
WHISPER_TRANSCRIBE = (
    PROJECT_ROOT / ".agents/skills/gconf-local-whisper/scripts/transcribe.py"
)


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temp_name = handle.name
    os.replace(temp_name, path)


def load_config() -> dict[str, Any]:
    config = load_json(CONFIG_PATH)
    if not isinstance(config, dict):
        raise RuntimeError(f"invalid or missing config: {CONFIG_PATH}")
    return config


def safe_name(value: str, limit: int = 140) -> str:
    value = unicodedata.normalize("NFC", value or "").strip()
    value = re.sub(r"[\x00-\x1f/:\\]+", " - ", value)
    value = re.sub(r"\s+", " ", value).strip(" .-")
    return (value or "Untitled")[:limit].rstrip(" .-")


def parse_start_seconds(url: str, info: dict[str, Any] | None = None) -> int | None:
    if info and info.get("start_time") is not None:
        try:
            return int(float(info["start_time"]))
        except (TypeError, ValueError):
            pass
    query = parse_qs(urlparse(url).query)
    raw = (query.get("t") or query.get("start") or [None])[0]
    if raw is None:
        return None
    if str(raw).isdigit():
        return int(raw)
    match = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", str(raw))
    if not match:
        return None
    hours, minutes, seconds = (int(part or 0) for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds


def chapter_for_time(chapters: list[dict[str, Any]], seconds: int | None) -> dict[str, Any] | None:
    if seconds is None:
        return None
    for chapter in chapters:
        start = chapter.get("start_time", 0)
        end = chapter.get("end_time")
        if start <= seconds and (end is None or seconds < end):
            return chapter
    return None


def infer_language(info: dict[str, Any], requested: str) -> str:
    if requested != "auto":
        return requested
    language = info.get("language")
    if isinstance(language, str) and language:
        return language.split("-")[0]
    automatic = info.get("automatic_captions") or {}
    original = [key[:-5] for key in automatic if key.endswith("-orig")]
    for preferred in ("ru", "en"):
        if preferred in original:
            return preferred
    if original:
        return original[0]
    manual = list((info.get("subtitles") or {}).keys())
    return (manual[0].split("-")[0] if manual else "en")


def caption_candidates(info: dict[str, Any], language: str) -> list[str]:
    manual = info.get("subtitles") or {}
    automatic = info.get("automatic_captions") or {}
    candidates: list[str] = []
    if language in manual:
        candidates.append(language)
    candidates.extend(
        key for key in (f"{language}-orig", language) if key in automatic and key not in candidates
    )
    if not candidates:
        original = [key for key in automatic if key.endswith("-orig")]
        candidates.extend(original[:1])
    return candidates


def comment_counts(info: dict[str, Any]) -> tuple[int | None, int, int, int, str]:
    reported = info.get("comment_count")
    comments = info.get("comments")
    if not isinstance(comments, list):
        if reported == 0:
            return 0, 0, 0, 0, "complete"
        return reported, 0, 0, 0, "unavailable"
    roots = sum(1 for item in comments if item.get("parent") in (None, "root"))
    replies = len(comments) - roots
    if reported is None:
        status = "available"
    elif len(comments) == reported:
        status = "complete"
    else:
        status = "partial"
    return reported, len(comments), roots, replies, status


def project_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def video_relative(path: Path, video_dir: Path) -> str:
    return f"./{path.relative_to(video_dir).as_posix()}"


def run_json_script(path: Path) -> tuple[int, dict[str, Any]]:
    result = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, json.loads(result.stdout or "{}")


def doctor_report() -> dict[str, Any]:
    config: dict[str, Any] | None = None
    config_error: str | None = None
    try:
        config = load_config()
    except RuntimeError as exc:
        config_error = str(exc)
    yt_code, yt = run_json_script(YT_DLP_DOCTOR)
    whisper_code, whisper = run_json_script(WHISPER_DOCTOR)
    root = PROJECT_ROOT / (config or {}).get("root", "YouTube")
    checks = [
        {
            "name": "python",
            "status": "ok",
            "version": sys.version.split()[0],
            "path": sys.executable,
        },
        {
            "name": "project-config",
            "status": "ok" if config else "fail",
            "path": str(CONFIG_PATH),
            **({} if config else {"reason": config_error}),
        },
        {
            "name": "youtube-root",
            "status": "ok" if root.is_dir() else "warn",
            "path": str(root),
        },
    ]
    return {
        "ok": yt_code == 0 and config is not None,
        "youtube_collection_ready": yt_code == 0 and config is not None,
        "whisper_fallback_ready": whisper_code == 0,
        "checks": checks,
        "yt_dlp": yt,
        "whisper": whisper,
    }


def probe_video(url: str) -> dict[str, Any]:
    binary = shutil.which("yt-dlp")
    if not binary:
        raise RuntimeError("yt-dlp is missing; run the doctor")
    result = subprocess.run(
        [
            binary,
            "--dump-single-json",
            "--skip-download",
            "--no-playlist",
            "--no-warnings",
            "--no-progress",
            url,
        ],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return json.loads(result.stdout)


def find_existing_video(root: Path, video_id: str) -> Path | None:
    matches = sorted(root.glob(f"**/{video_id}.info.json"))
    return matches[0].parent if matches else None


def resolve_creator_dir(
    root: Path, info: dict[str, Any], explicit: str | None
) -> Path:
    if explicit:
        candidate = Path(explicit).expanduser()
        return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate
    return root / safe_name(info.get("channel") or info.get("uploader") or "UnknownChannel")


def vtt_to_srt(source: Path, destination: Path) -> None:
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    output: list[str] = []
    cue: list[str] = []
    counter = 1

    def flush() -> None:
        nonlocal counter, cue
        if not cue:
            return
        timing_index = next((i for i, line in enumerate(cue) if "-->" in line), None)
        if timing_index is not None:
            timing = cue[timing_index].split(" align:")[0].replace(".", ",")
            text = cue[timing_index + 1 :]
            if text:
                output.extend([str(counter), timing, *text, ""])
                counter += 1
        cue = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        if not stripped:
            flush()
        else:
            cue.append(line)
    flush()
    destination.write_text("\n".join(output), encoding="utf-8")


def extract_with_ytdlp(
    url: str, staging: Path, video_id: str, candidates: list[str]
) -> dict[str, Any]:
    binary = shutil.which("yt-dlp")
    assert binary
    command = [
        binary,
        "--skip-download",
        "--no-playlist",
        "--write-info-json",
        "--write-comments",
        "--write-description",
        "--write-thumbnail",
        "--write-subs",
        "--write-auto-subs",
        "--sub-format",
        "vtt/best",
        "--no-warnings",
        "--no-progress",
        "-o",
        str(staging / f"{video_id}.%(ext)s"),
    ]
    if candidates:
        command.extend(["--sub-langs", ",".join(candidates)])
    else:
        command.extend(["--sub-langs", "none"])
    command.append(url)
    result = subprocess.run(
        command, capture_output=True, text=True, timeout=3600, check=False
    )
    info_path = staging / f"{video_id}.info.json"
    if not info_path.is_file():
        raise RuntimeError((result.stderr or result.stdout or "yt-dlp produced no info JSON").strip())
    info = load_json(info_path, {})
    if result.returncode != 0:
        info["_collection_warning"] = (result.stderr or result.stdout).strip()
    for vtt in staging.glob(f"{video_id}*.vtt"):
        srt = vtt.with_suffix(".srt")
        vtt_to_srt(vtt, srt)
        vtt.unlink()
    return info


def run_whisper_fallback(
    url: str, staging: Path, video_id: str, language: str
) -> tuple[bool, str | None]:
    doctor = doctor_report()
    if not doctor["whisper_fallback_ready"]:
        return False, "Whisper fallback dependencies are not configured"
    binary = shutil.which("yt-dlp")
    assert binary
    output = staging / f"{video_id}.source.%(ext)s"
    result = subprocess.run(
        [
            binary,
            "--no-playlist",
            "-f",
            "ba",
            "-o",
            str(output),
            url,
        ],
        capture_output=True,
        text=True,
        timeout=3600,
        check=False,
    )
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()
    media = next(iter(staging.glob(f"{video_id}.source.*")), None)
    if not media:
        return False, "temporary audio download produced no file"
    transcript_base = staging / f"{video_id}.transcript"
    transcribe = subprocess.run(
        [
            sys.executable,
            str(WHISPER_TRANSCRIBE),
            str(media),
            "--output-base",
            str(transcript_base),
            "--language",
            language,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    media.unlink(missing_ok=True)
    if transcribe.returncode != 0:
        return False, (transcribe.stderr or transcribe.stdout).strip()
    return True, None


def select_primary_transcript(video_dir: Path, video_id: str) -> Path | None:
    whisper = video_dir / f"{video_id}.transcript.srt"
    if whisper.is_file():
        return whisper
    files = sorted(video_dir.glob(f"{video_id}*.srt"))
    original = [path for path in files if "-orig.srt" in path.name]
    return (original or files or [None])[0]


def artifact_files(video_dir: Path, video_id: str) -> dict[str, str]:
    known: dict[str, str] = {}
    names = {
        "raw_metadata": video_dir / f"{video_id}.info.json",
        "stats": video_dir / f"{video_id}.stats.json",
        "comments": video_dir / f"{video_id}.comments.json",
        "chapters": video_dir / f"{video_id}.chapters.json",
        "description": video_dir / f"{video_id}.description",
    }
    for key, path in names.items():
        if path.is_file() or key == "stats":
            known[key] = video_relative(path, video_dir)
    thumbnail = next(
        (
            path
            for path in sorted(video_dir.glob(f"{video_id}.*"))
            if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        ),
        None,
    )
    if thumbnail:
        known["thumbnail"] = video_relative(thumbnail, video_dir)
    primary = select_primary_transcript(video_dir, video_id)
    if primary:
        known["primary_transcript"] = video_relative(primary, video_dir)
    transcript_txt = video_dir / f"{video_id}.transcript.txt"
    if transcript_txt.is_file():
        known["transcript_text"] = video_relative(transcript_txt, video_dir)
    return known


def build_normalized_artifacts(
    info: dict[str, Any],
    video_dir: Path,
    original_url: str,
    collected_at: str,
    collection_warning: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    video_id = str(info["id"])
    comments = info.get("comments") if isinstance(info.get("comments"), list) else []
    reported, extracted, roots, replies, comment_status = comment_counts(info)
    chapters = info.get("chapters") if isinstance(info.get("chapters"), list) else []
    start_seconds = parse_start_seconds(original_url, info)
    start_chapter = chapter_for_time(chapters, start_seconds)
    primary = select_primary_transcript(video_dir, video_id)
    whisper_used = bool(primary and primary.name.endswith(".transcript.srt"))
    primary_language = infer_language(info, "auto")
    manual_keys = set((info.get("subtitles") or {}).keys())
    automatic_keys = set((info.get("automatic_captions") or {}).keys())
    if whisper_used:
        transcript_source = "whisper"
    elif primary and any(f".{key}." in primary.name for key in manual_keys):
        transcript_source = "manual"
    elif primary:
        transcript_source = "automatic"
    else:
        transcript_source = "unavailable"
    limitations = ["Public statistics are a time-bound snapshot and may change."]
    if comment_status == "unavailable":
        limitations.append("Public comments were not exposed by the extractor.")
    elif comment_status == "partial":
        limitations.append("Fewer comments were extracted than YouTube reported.")
    if transcript_source == "automatic":
        limitations.append("The primary transcript is automatically generated and may contain errors.")
    if transcript_source == "unavailable":
        limitations.append("No YouTube captions or local Whisper transcript is available.")
    if collection_warning:
        limitations.append(f"Collection warning: {collection_warning}")
    creator_dir = video_dir.parent
    stats = {
        "schema_version": SCHEMA_VERSION,
        "status": "partial"
        if comment_status in {"partial", "unavailable"} or transcript_source == "unavailable"
        else "complete",
        "collected_at": collected_at,
        "workspace": {
            "creator_folder": project_relative(creator_dir),
            "video_folder": project_relative(video_dir),
        },
        "source": {
            "platform": "youtube",
            "video_id": video_id,
            "url": info.get("webpage_url") or f"https://www.youtube.com/watch?v={video_id}",
            "original_url": original_url,
            "requested_start_seconds": start_seconds,
            "requested_start_context": start_chapter,
            "title": info.get("title"),
            "channel": info.get("channel"),
            "channel_id": info.get("channel_id"),
            "uploader": info.get("uploader"),
            "uploader_id": info.get("uploader_id"),
            "description": info.get("description"),
            "duration_seconds": info.get("duration"),
            "duration_display": info.get("duration_string"),
            "upload_date": info.get("upload_date"),
            "published_timestamp_utc": info.get("timestamp"),
            "availability": info.get("availability"),
            "live_status": info.get("live_status"),
            "license": info.get("license"),
            "categories": info.get("categories") or [],
            "tags": info.get("tags") or [],
        },
        "statistics": {
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "comment_count_reported": reported,
            "comments_extracted": extracted,
            "root_comments": roots,
            "replies": replies,
            "comments_status": comment_status,
            "channel_follower_count": info.get("channel_follower_count"),
            "chapters_count": len(chapters),
        },
        "subtitles": {
            "manual_available": bool(manual_keys),
            "manual_languages": sorted(manual_keys),
            "automatic_available": bool(automatic_keys),
            "automatic_language_count": len(automatic_keys),
            "source_language": primary_language,
            "primary_source": transcript_source,
            "primary_transcript": video_relative(primary, video_dir) if primary else None,
            "whisper_used": whisper_used,
        },
        "files": artifact_files(video_dir, video_id),
        "limitations": limitations,
    }
    comments_payload = {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "platform": "youtube",
            "video_id": video_id,
            "url": stats["source"]["url"],
            "title": info.get("title"),
            "channel": info.get("channel"),
        },
        "collection": {
            "tool": "yt-dlp",
            "tool_version": (info.get("_version") or {}).get("version"),
            "collected_at": collected_at,
            "status": comment_status,
            "reported_comment_count": reported,
            "extracted_comment_count": extracted,
            "scope": "public comments and replies accessible without authentication",
        },
        "comments": comments,
    }
    chapters_payload = {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "platform": "youtube",
            "video_id": video_id,
            "url": stats["source"]["url"],
            "title": info.get("title"),
        },
        "chapters": chapters,
    }
    return stats, comments_payload, chapters_payload


def rebuild_catalog(root: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for stats_path in sorted(root.glob("**/*.stats.json")):
        stats = load_json(stats_path, {})
        if stats.get("schema_version") != SCHEMA_VERSION:
            continue
        source = stats.get("source") or {}
        statistics = stats.get("statistics") or {}
        subtitles = stats.get("subtitles") or {}
        entries.append(
            {
                "video_id": source.get("video_id"),
                "title": source.get("title"),
                "channel": source.get("channel"),
                "upload_date": source.get("upload_date"),
                "collected_at": stats.get("collected_at"),
                "status": stats.get("status"),
                "video_folder": project_relative(stats_path.parent),
                "view_count": statistics.get("view_count"),
                "like_count": statistics.get("like_count"),
                "comments_extracted": statistics.get("comments_extracted"),
                "primary_transcript": subtitles.get("primary_transcript"),
            }
        )
    payload = {
        "schema_version": "1.0",
        "generated_at": now_utc(),
        "video_count": len(entries),
        "videos": entries,
    }
    atomic_json(root / "catalog.json", payload)
    return payload


def collect(args: argparse.Namespace) -> int:
    config = load_config()
    root = PROJECT_ROOT / config.get("root", "YouTube")
    report = doctor_report()
    if not report["youtube_collection_ready"]:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    probe = probe_video(args.url)
    video_id = str(probe["id"])
    language = infer_language(probe, args.lang or config.get("default_language", "auto"))
    candidates = caption_candidates(probe, language)
    existing = find_existing_video(root, video_id)
    creator_dir = existing.parent if existing else resolve_creator_dir(root, probe, args.creator_dir)
    video_dir = existing or creator_dir / safe_name(
        config.get("folder_template", "{title} [{id}]").format(
            title=probe.get("title") or video_id, id=video_id
        )
    )
    creator_dir.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".youtube-staging-", dir=creator_dir))
    warning: str | None = None
    try:
        info = extract_with_ytdlp(args.url, staging, video_id, candidates)
        warning = info.pop("_collection_warning", None)
        description = staging / f"{video_id}.description"
        if not description.is_file():
            description.write_text(info.get("description") or "", encoding="utf-8")
        if not list(staging.glob(f"{video_id}*.srt")):
            ok, whisper_error = run_whisper_fallback(args.url, staging, video_id, language)
            if not ok:
                warning = "; ".join(filter(None, [warning, whisper_error]))
        video_dir.mkdir(parents=True, exist_ok=True)
        for source in staging.iterdir():
            if source.is_file():
                os.replace(source, video_dir / source.name)
        collected_at = now_utc()
        info_path = video_dir / f"{video_id}.info.json"
        info = load_json(info_path, info)
        stats, comments, chapters = build_normalized_artifacts(
            info, video_dir, args.url, collected_at, warning
        )
        atomic_json(video_dir / f"{video_id}.comments.json", comments)
        atomic_json(video_dir / f"{video_id}.chapters.json", chapters)
        atomic_json(video_dir / f"{video_id}.stats.json", stats)
        catalog = rebuild_catalog(root)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    result = {
        "ok": stats["status"] == "complete",
        "status": stats["status"],
        "collected_at": stats["collected_at"],
        "video_id": video_id,
        "video_folder": project_relative(video_dir),
        "stats": project_relative(video_dir / f"{video_id}.stats.json"),
        "comments": project_relative(video_dir / f"{video_id}.comments.json"),
        "primary_transcript": stats["subtitles"]["primary_transcript"],
        "primary_transcript_file": (
            project_relative(video_dir / stats["subtitles"]["primary_transcript"][2:])
            if stats["subtitles"]["primary_transcript"]
            else None
        ),
        "transcript_source": stats["subtitles"]["primary_source"],
        "statistics": stats["statistics"],
        "catalog_video_count": catalog["video_count"],
        "setup_required": report if warning and "not configured" in warning else None,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if stats["status"] == "complete" else 2


def validate(root: Path) -> tuple[int, dict[str, Any]]:
    errors: list[dict[str, str]] = []
    checked = 0
    for path in sorted(root.glob("**/*.stats.json")):
        checked += 1
        payload = load_json(path)
        if not isinstance(payload, dict):
            errors.append({"file": project_relative(path), "error": "invalid JSON"})
            continue
        if payload.get("schema_version") != SCHEMA_VERSION:
            errors.append({"file": project_relative(path), "error": "schema_version is not 2.0"})
            continue
        for key in (
            "status",
            "collected_at",
            "workspace",
            "source",
            "statistics",
            "subtitles",
            "files",
            "limitations",
        ):
            if key not in payload:
                errors.append({"file": project_relative(path), "error": f"missing {key}"})
        for relative in (payload.get("files") or {}).values():
            if isinstance(relative, str) and relative.startswith("./"):
                if not (path.parent / relative[2:]).is_file():
                    errors.append(
                        {"file": project_relative(path), "error": f"missing artifact {relative}"}
                    )
    report = {"ok": not errors, "checked": checked, "errors": errors}
    return (0 if not errors else 1), report


def normalize(root: Path) -> int:
    changed: list[str] = []
    warnings: list[dict[str, str]] = []
    for info_path in sorted(root.glob("**/*.info.json")):
        info = load_json(info_path)
        if not isinstance(info, dict) or not info.get("id"):
            warnings.append({"file": project_relative(info_path), "warning": "invalid info JSON"})
            continue
        video_id = str(info["id"])
        video_dir = info_path.parent
        old_stats = load_json(video_dir / f"{video_id}.stats.json", {})
        original_url = (
            (old_stats.get("source") or {}).get("original_url")
            or info.get("original_url")
            or info.get("webpage_url")
            or f"https://www.youtube.com/watch?v={video_id}"
        )
        description = video_dir / f"{video_id}.description"
        if not description.is_file():
            description.write_text(info.get("description") or "", encoding="utf-8")
        stats, comments, chapters = build_normalized_artifacts(
            info, video_dir, original_url, now_utc()
        )
        atomic_json(video_dir / f"{video_id}.comments.json", comments)
        atomic_json(video_dir / f"{video_id}.chapters.json", chapters)
        atomic_json(video_dir / f"{video_id}.stats.json", stats)
        changed.append(project_relative(video_dir))
    catalog = rebuild_catalog(root)
    legacy_media = [
        project_relative(path)
        for path in root.glob("**/*")
        if path.is_file() and path.suffix.lower() in {".mp4", ".mkv", ".webm", ".wav", ".m4a"}
    ]
    report = {
        "schema_version": "1.0",
        "generated_at": now_utc(),
        "normalized_video_count": len(changed),
        "normalized_video_folders": changed,
        "legacy_media_preserved": legacy_media,
        "warnings": warnings,
        "catalog_video_count": catalog["video_count"],
    }
    atomic_json(root / "migration-report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not warnings else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GCONF YouTube research collector")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor")
    collect_parser = subparsers.add_parser("collect")
    collect_parser.add_argument("url")
    collect_parser.add_argument("--creator-dir")
    collect_parser.add_argument("--lang", default=None)
    subparsers.add_parser("validate")
    subparsers.add_parser("normalize")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            report = doctor_report()
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["ok"] else 1
        config = load_config()
        root = PROJECT_ROOT / config.get("root", "YouTube")
        root.mkdir(parents=True, exist_ok=True)
        if args.command == "collect":
            return collect(args)
        if args.command == "validate":
            code, report = validate(root)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return code
        if args.command == "normalize":
            return normalize(root)
        return 1
    except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "status": "failed",
                    "error": str(exc),
                    "next_step": "Run the doctor; if this is a network sandbox failure, retry with network permission.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

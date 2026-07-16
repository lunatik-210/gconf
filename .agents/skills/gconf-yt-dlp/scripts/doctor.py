#!/usr/bin/env python3
"""Portable preflight for the GCONF yt-dlp workflow."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from typing import Any


def version(binary: str, args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            [binary, *args], capture_output=True, text=True, timeout=15, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (result.stdout or result.stderr).strip()
    return output.splitlines()[0] if result.returncode == 0 and output else None


def install_suggestion(tool: str, system: str) -> dict[str, Any]:
    if system == "Darwin":
        packages = {"yt-dlp": "yt-dlp", "ffmpeg": "ffmpeg"}
        return {
            "manager": "homebrew",
            "command": ["brew", "install", packages[tool]],
            "requires_approval": True,
        }
    if tool == "yt-dlp":
        return {
            "manager": "pipx",
            "command": ["pipx", "install", "yt-dlp"],
            "fallback": ["python3", "-m", "pip", "install", "--user", "-U", "yt-dlp"],
            "requires_approval": True,
        }
    return {
        "manager": "system-package-manager",
        "command_example": ["sudo", "apt-get", "install", "ffmpeg"],
        "requires_approval": True,
    }


def build_report() -> dict[str, Any]:
    system = platform.system()
    checks: list[dict[str, Any]] = []
    for name, args, required in (
        ("yt-dlp", ["--version"], True),
        ("ffmpeg", ["-version"], False),
    ):
        binary = shutil.which(name)
        if binary:
            checks.append(
                {
                    "name": name,
                    "status": "ok",
                    "required": required,
                    "path": binary,
                    "version": version(binary, args),
                }
            )
        else:
            checks.append(
                {
                    "name": name,
                    "status": "fail" if required else "warn",
                    "required": required,
                    "reason": f"{name} is not available on PATH",
                    "setup": install_suggestion(name, system),
                }
            )
    return {
        "ok": not any(c["status"] == "fail" for c in checks),
        "platform": {"system": system, "machine": platform.machine()},
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check yt-dlp workflow dependencies")
    parser.add_argument("--human", action="store_true", help="Print a compact human report")
    args = parser.parse_args(argv)
    report = build_report()
    if args.human:
        for check in report["checks"]:
            print(f"{check['status'].upper():4} {check['name']}: {check.get('path') or check.get('reason')}")
            if "setup" in check:
                print(f"     suggested setup: {json.dumps(check['setup'], ensure_ascii=False)}")
    else:
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

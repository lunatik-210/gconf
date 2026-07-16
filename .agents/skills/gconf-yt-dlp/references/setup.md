# Dependency setup

Always run `scripts/doctor.py` first. Installation commands are suggestions, not
authorization to execute them.

## macOS

```bash
brew install yt-dlp ffmpeg
```

## Linux

Prefer an isolated yt-dlp installation:

```bash
pipx install yt-dlp
```

Install ffmpeg with the system package manager, for example:

```bash
sudo apt-get install ffmpeg
```

Ask before running Homebrew, pip, pipx, or privileged package-manager commands.

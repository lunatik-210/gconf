# Local Whisper setup

Run `scripts/doctor.py` before changing the machine.

## macOS

```bash
brew install ffmpeg whisper-cpp
```

Set the model path:

```bash
export WHISPER_MODEL="$HOME/.cache/whisper.cpp/ggml-large-v3.bin"
```

## Linux

Install ffmpeg with the system package manager. Build whisper.cpp from its
official repository or install a distribution-provided package that exposes
`whisper-cli`. Download a compatible ggml model outside the repository and set
`WHISPER_MODEL`.

All installation and model-download actions require explicit approval.

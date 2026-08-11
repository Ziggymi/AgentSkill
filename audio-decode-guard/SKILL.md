---
name: audio-decode-guard
description: This skill should be used before transcribing local audio or video when M4A, AAC, MP3, WAV, OGG, FLAC, WMA, MP4, MOV, or similar media may require FFmpeg/ffprobe decoding; especially when Whisper reports that ffmpeg is missing, decoding did not actually run, the file has a Chinese/space-containing Windows path, or another session says an audio decoder is unavailable.
agent_created: true
---

# Audio Decode Guard

## Purpose

Prevent false starts in local speech-to-text work. Detect a usable FFmpeg installation, register a checksum-pinned isolated decoder from a trusted local archive when explicitly needed, inspect the media, and normalize it to a Whisper-friendly mono 16 kHz PCM WAV without modifying the source file.

## Mandatory trigger

Run this skill before any local recording transcription when the input is compressed media or decoder availability has not already been verified in the current session. Also run it immediately after errors such as `ffmpeg not found`, `No such file or directory: ffmpeg`, `Invalid data found when processing input`, or a report that transcription completed suspiciously fast without producing text.

## Safety boundaries

- Treat the source media as read-only.
- Never overwrite, move, rename, or delete the source media.
- Write decoded audio only under the active workspace or a user-approved output directory.
- Never modify the system `PATH`, registry, shell profile, or global package installation.
- Never invoke `winget`, Chocolatey, Homebrew, `apt`, global pip, or global npm installation.
- Never pass user-controlled text through a shell. Invoke FFmpeg with an argument list and `shell=False`.
- Accept only a locally available FFmpeg archive whose SHA-256 matches the pinned value in `scripts/audio_decode_guard.py`. Stop on any mismatch.
- Do not claim transcription has started until both `probe` and `decode` succeed and the WAV output exists with non-zero duration.

## Workflow

### 1. Probe before transcription

Run with the managed Python runtime:

```text
<managed-python> <skill-dir>/scripts/audio_decode_guard.py probe --input <absolute-media-path>
```

Read the JSON result. Continue only when `ok` is true and both `ffmpeg` and `ffprobe` paths are present.

### 2. Prepare an isolated decoder only when missing

When `probe` returns `decoder_missing`, first locate a trusted local copy of `ffmpeg-9.0-essentials_build.zip`. If none exists, use an approved local package source or ask the user to provide that exact archive; keep it in the active workspace or managed binary area, and then run:

```text
<managed-python> <skill-dir>/scripts/audio_decode_guard.py ensure --archive <absolute-zip-path>
```

The script verifies the pinned SHA-256, validates ZIP paths and size limits, and copies only the decoder binaries under `~/.workbuddy/binaries/ffmpeg/9.0`. It does not install software globally or alter the system environment. Re-run `probe` after preparation. Never continue on hash mismatch.

### 3. Normalize to Whisper-compatible WAV

Choose a new output path under the active workspace, then run:

```text
<managed-python> <skill-dir>/scripts/audio_decode_guard.py decode --input <absolute-media-path> --output <workspace>/audio-decoded/<neutral-name>.wav
```

The output is mono, 16 kHz, signed 16-bit PCM WAV. Existing outputs are never overwritten; select a new neutral output name when a destination already exists.

### 4. Validate before transcription

Require all of the following:

- command exits with code 0;
- JSON result has `ok: true`;
- output exists and `bytes > 44`;
- `duration_seconds > 0`;
- sample rate is 16000 and channel count is 1.

Then pass the normalized WAV to Whisper or another transcription engine. Report progress from the audio timeline, not from model-download progress.

## Common failure handling

- `decoder_missing`: run `ensure`, then retry `probe`.
- `hash_mismatch`: stop; do not extract or execute the archive. Report expected and actual SHA-256.
- `unsupported_or_corrupt_media`: keep the source untouched and report the decoder error.
- `output_exists`: select a new neutral output name; do not overwrite by default.
- `no_audio_stream`: report that the media contains no decodable audio stream.
- Chinese or spaced paths: pass absolute paths as individual process arguments; never concatenate a shell command.

## Resources

- Run `scripts/audio_decode_guard.py` for deterministic probe, preparation, and decoding.
- Read `references/operations.md` for decoder discovery order, pinned artifact details, JSON fields, and troubleshooting.

# Audio Decode Guard Operations Reference

## Decoder discovery order

1. `WORKBUDDY_FFMPEG_DIR` for an explicitly provided directory.
2. Isolated installation at `~/.workbuddy/binaries/ffmpeg/9.0/bin/`.
3. Current process `PATH` without modifying it.
4. Existing Windows WinGet package directories under `%LOCALAPPDATA%/Microsoft/WinGet/Packages/`.

A decoder is accepted only when `ffmpeg` and the sibling `ffprobe` both exist.

## Pinned decoder artifact

- Version: FFmpeg 9.0 essentials build
- Expected archive name: `ffmpeg-9.0-essentials_build.zip`
- Expected upstream: Gyan.dev FFmpeg 9.0 essentials release
- SHA-256: `e6b54767a6065919048f1a098eb27211ca4e12b4348a05d88777a5855d0b6e71`
- Isolated destination: `~/.workbuddy/binaries/ffmpeg/9.0/`

Preparation uses a bounded download, checksum verification, ZIP entry count and expanded-size limits, ZIP path traversal validation, and copies only the decoder `bin` directory. It does not execute an installer.

## Commands

```text
python scripts/audio_decode_guard.py probe --input "D:/recordings/interview.m4a"
python scripts/audio_decode_guard.py ensure --archive "C:/workspace/ffmpeg-9.0-essentials_build.zip"
python scripts/audio_decode_guard.py decode --input "D:/recordings/interview.m4a" --output "C:/workspace/audio-decoded/interview.wav"
```

Use the managed Python runtime available in the current WorkBuddy session. Use absolute paths.

## JSON contract

Successful `probe` fields:

- `ok`
- `input`
- `ffmpeg`
- `ffprobe`
- `decoder_version`
- `duration_seconds`
- `codec`
- `sample_rate`
- `channels`

Successful `decode` fields additionally include:

- `output`
- `bytes`
- normalized `sample_rate` = 16000
- normalized `channels` = 1
- normalized `codec` = `pcm_s16le`
- original stream metadata under `source`

## Error codes

- `input_not_found`: supplied media path is not a file.
- `decoder_missing`: no valid FFmpeg/ffprobe pair was found.
- `archive_required`: no decoder was found and no trusted local archive path was supplied.
- `archive_not_found`: an explicitly supplied archive is missing.
- `hash_mismatch`: archive SHA-256 differs from the pinned value.
- `no_audio_stream`: the file has no decodable audio stream.
- `unsupported_or_corrupt_media`: ffprobe rejected the media.
- `output_exists`: destination already exists; select a new generated output name.
- `decode_failed`: ffmpeg failed; source remains unchanged.
- `output_validation_failed`: generated WAV did not pass duration or format checks.

## Operational notes

- Preserve source timestamps and bytes by never opening the source for writing.
- Prefer a generated output directory such as `<workspace>/audio-decoded/`.
- Choose a versioned or neutral output filename when a generated destination already exists.
- If a source is very long, decode once and reuse the normalized WAV for transcription retries.
- Base transcription progress on media duration reported by `probe`, not on model initialization or download progress.

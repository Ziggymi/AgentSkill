#!/usr/bin/env python3
"""Safely locate FFmpeg and normalize local media for speech-to-text."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any

PINNED_VERSION = "9.0"
PINNED_SHA256 = "e6b54767a6065919048f1a098eb27211ca4e12b4348a05d88777a5855d0b6e71"
INSTALL_ROOT = Path.home() / ".workbuddy" / "binaries" / "ffmpeg" / PINNED_VERSION
MAX_EXTRACTED_BYTES = 2 * 1024 * 1024 * 1024
MAX_ZIP_ENTRIES = 10000


def emit(payload: dict[str, Any], exit_code: int = 0) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(exit_code)


def binary_name(name: str) -> str:
    return f"{name}.exe" if os.name == "nt" else name


def paired_probe(ffmpeg: Path) -> Path | None:
    probe = ffmpeg.with_name(binary_name("ffprobe"))
    return probe if probe.is_file() else None


def valid_pair(ffmpeg: Path) -> tuple[Path, Path] | None:
    if not ffmpeg.is_file():
        return None
    ffprobe = paired_probe(ffmpeg)
    if ffprobe is None:
        return None
    return ffmpeg.resolve(), ffprobe.resolve()


def discover_decoder() -> tuple[Path, Path] | None:
    env_dir = os.environ.get("WORKBUDDY_FFMPEG_DIR")
    candidates: list[Path] = []
    if env_dir:
        candidates.append(Path(env_dir) / binary_name("ffmpeg"))

    candidates.extend(
        [
            INSTALL_ROOT / "bin" / binary_name("ffmpeg"),
            INSTALL_ROOT / f"ffmpeg-{PINNED_VERSION}-essentials_build" / "bin" / binary_name("ffmpeg"),
        ]
    )

    path_hit = shutil.which("ffmpeg")
    if path_hit:
        candidates.append(Path(path_hit))

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        winget_root = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_root.is_dir():
            candidates.extend(winget_root.glob("Gyan.FFmpeg_*/ffmpeg-*-build/bin/ffmpeg.exe"))
            candidates.extend(winget_root.glob("Gyan.FFmpeg_*/ffmpeg-*/bin/ffmpeg.exe"))

    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate).lower()
        if key in seen:
            continue
        seen.add(key)
        pair = valid_pair(candidate)
        if pair:
            return pair
    return None


def run_process(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        shell=False,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def decoder_version(ffmpeg: Path) -> str:
    result = run_process([str(ffmpeg), "-version"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Unable to execute FFmpeg")
    return result.stdout.splitlines()[0] if result.stdout else "unknown"


def media_probe(ffprobe: Path, source: Path) -> dict[str, Any]:
    result = run_process(
        [
            str(ffprobe),
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "format=duration:stream=codec_name,sample_rate,channels",
            "-of",
            "json",
            str(source),
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Unable to probe media")
    data = json.loads(result.stdout or "{}")
    streams = data.get("streams") or []
    if not streams:
        raise ValueError("no_audio_stream")
    stream = streams[0]
    duration_raw = (data.get("format") or {}).get("duration")
    return {
        "duration_seconds": float(duration_raw) if duration_raw is not None else None,
        "codec": stream.get("codec_name"),
        "sample_rate": int(stream["sample_rate"]) if stream.get("sample_rate") else None,
        "channels": stream.get("channels"),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_extract(archive: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len(entries) > MAX_ZIP_ENTRIES:
            raise RuntimeError("too_many_archive_entries")
        total_size = sum(entry.file_size for entry in entries)
        if total_size > MAX_EXTRACTED_BYTES:
            raise RuntimeError("extracted_content_too_large")
        for entry in entries:
            target = (destination / entry.filename).resolve()
            if os.path.commonpath([str(destination_resolved), str(target)]) != str(destination_resolved):
                raise RuntimeError("unsafe_archive_path")
        bundle.extractall(destination)


def install_from_archive(archive: Path) -> tuple[Path, Path]:
    actual_hash = sha256_file(archive)
    if actual_hash.lower() != PINNED_SHA256.lower():
        emit(
            {
                "ok": False,
                "error": "hash_mismatch",
                "expected_sha256": PINNED_SHA256,
                "actual_sha256": actual_hash,
                "archive": str(archive),
            },
            2,
        )

    INSTALL_ROOT.parent.mkdir(parents=True, exist_ok=True)
    if INSTALL_ROOT.exists():
        existing = discover_decoder()
        if existing:
            return existing
        raise RuntimeError(f"install_destination_exists_but_invalid: {INSTALL_ROOT}")

    with tempfile.TemporaryDirectory(prefix="audio-decode-guard-", dir=str(INSTALL_ROOT.parent)) as temp_dir:
        staging = Path(temp_dir) / "payload"
        staging.mkdir()
        safe_extract(archive, staging)
        ffmpeg_matches = list(staging.rglob(binary_name("ffmpeg")))
        ffprobe_matches = list(staging.rglob(binary_name("ffprobe")))
        if not ffmpeg_matches or not ffprobe_matches:
            raise RuntimeError("decoder_binaries_missing_from_archive")
        INSTALL_ROOT.mkdir()
        source_bin = ffmpeg_matches[0].parent
        target_bin = INSTALL_ROOT / "bin"
        shutil.copytree(source_bin, target_bin)

    pair = valid_pair(INSTALL_ROOT / "bin" / binary_name("ffmpeg"))
    if pair is None:
        raise RuntimeError("installed_decoder_validation_failed")
    return pair


def command_probe(source: Path) -> None:
    if not source.is_file():
        emit({"ok": False, "error": "input_not_found", "input": str(source)}, 2)
    pair = discover_decoder()
    if pair is None:
        emit(
            {
                "ok": False,
                "error": "decoder_missing",
                "input": str(source.resolve()),
                "next_action": "run ensure, then retry probe",
            },
            3,
        )
    ffmpeg, ffprobe = pair
    try:
        info = media_probe(ffprobe, source)
        version = decoder_version(ffmpeg)
    except ValueError as error:
        emit({"ok": False, "error": str(error), "input": str(source.resolve())}, 4)
    except Exception as error:
        emit({"ok": False, "error": "unsupported_or_corrupt_media", "detail": str(error)}, 4)
    emit(
        {
            "ok": True,
            "input": str(source.resolve()),
            "ffmpeg": str(ffmpeg),
            "ffprobe": str(ffprobe),
            "decoder_version": version,
            **info,
        }
    )


def command_ensure(archive: Path | None) -> None:
    existing = discover_decoder()
    if existing:
        ffmpeg, ffprobe = existing
        emit(
            {
                "ok": True,
                "status": "already_available",
                "ffmpeg": str(ffmpeg),
                "ffprobe": str(ffprobe),
                "decoder_version": decoder_version(ffmpeg),
            }
        )

    if archive is None:
        emit(
            {
                "ok": False,
                "error": "archive_required",
                "expected_filename": "ffmpeg-9.0-essentials_build.zip",
                "expected_sha256": PINNED_SHA256,
                "next_action": "obtain the trusted archive, then rerun ensure --archive <absolute-path>",
            },
            2,
        )
    if not archive.is_file():
        emit({"ok": False, "error": "archive_not_found", "archive": str(archive)}, 2)
    pair = install_from_archive(archive)

    ffmpeg, ffprobe = pair
    emit(
        {
            "ok": True,
            "status": "installed",
            "install_root": str(INSTALL_ROOT),
            "ffmpeg": str(ffmpeg),
            "ffprobe": str(ffprobe),
            "decoder_version": decoder_version(ffmpeg),
            "verified_sha256": PINNED_SHA256,
        }
    )


def command_decode(source: Path, output: Path) -> None:
    if not source.is_file():
        emit({"ok": False, "error": "input_not_found", "input": str(source)}, 2)
    if source.resolve() == output.resolve():
        emit({"ok": False, "error": "source_and_output_must_differ"}, 2)
    if output.exists():
        emit({"ok": False, "error": "output_exists", "output": str(output.resolve())}, 2)

    pair = discover_decoder()
    if pair is None:
        emit({"ok": False, "error": "decoder_missing", "next_action": "run ensure"}, 3)
    ffmpeg, ffprobe = pair

    try:
        source_info = media_probe(ffprobe, source)
    except ValueError as error:
        emit({"ok": False, "error": str(error), "input": str(source.resolve())}, 4)
    except Exception as error:
        emit({"ok": False, "error": "unsupported_or_corrupt_media", "detail": str(error)}, 4)

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output.with_name(f".{output.stem}.partial-{os.getpid()}.wav")
    if temporary_output.exists():
        emit({"ok": False, "error": "temporary_output_exists", "path": str(temporary_output)}, 2)

    result = run_process(
        [
            str(ffmpeg),
            "-hide_banner",
            "-nostdin",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-map",
            "0:a:0",
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            "-y",
            str(temporary_output),
        ]
    )
    if result.returncode != 0:
        if temporary_output.exists():
            temporary_output.unlink()
        emit(
            {
                "ok": False,
                "error": "decode_failed",
                "detail": result.stderr.strip(),
                "input": str(source.resolve()),
            },
            6,
        )

    try:
        output_info = media_probe(ffprobe, temporary_output)
        if temporary_output.stat().st_size <= 44 or not output_info.get("duration_seconds"):
            raise RuntimeError("decoded_output_empty")
        if output_info.get("sample_rate") != 16000 or output_info.get("channels") != 1:
            raise RuntimeError("decoded_output_format_invalid")
        temporary_output.replace(output)
    except Exception as error:
        if temporary_output.exists():
            temporary_output.unlink()
        emit({"ok": False, "error": "output_validation_failed", "detail": str(error)}, 7)

    emit(
        {
            "ok": True,
            "input": str(source.resolve()),
            "output": str(output.resolve()),
            "bytes": output.stat().st_size,
            "duration_seconds": output_info["duration_seconds"],
            "sample_rate": output_info["sample_rate"],
            "channels": output_info["channels"],
            "codec": output_info["codec"],
            "source": source_info,
            "ffmpeg": str(ffmpeg),
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe_parser = subparsers.add_parser("probe", help="Locate decoder and inspect a media file")
    probe_parser.add_argument("--input", required=True, type=Path)

    ensure_parser = subparsers.add_parser("ensure", help="Prepare a pinned isolated FFmpeg decoder")
    ensure_parser.add_argument("--archive", type=Path)

    decode_parser = subparsers.add_parser("decode", help="Normalize media to mono 16 kHz PCM WAV")
    decode_parser.add_argument("--input", required=True, type=Path)
    decode_parser.add_argument("--output", required=True, type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "probe":
        command_probe(args.input)
    elif args.command == "ensure":
        command_ensure(args.archive)
    elif args.command == "decode":
        command_decode(args.input, args.output)


if __name__ == "__main__":
    main()

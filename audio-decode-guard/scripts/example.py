#!/usr/bin/env python3
"""Non-destructive smoke test for audio-decode-guard imports."""

from audio_decode_guard import PINNED_SHA256, PINNED_VERSION, discover_decoder


def main() -> None:
    pair = discover_decoder()
    print(
        {
            "pinned_version": PINNED_VERSION,
            "pinned_sha256": PINNED_SHA256,
            "decoder_found": bool(pair),
            "ffmpeg": str(pair[0]) if pair else None,
            "ffprobe": str(pair[1]) if pair else None,
        }
    )


if __name__ == "__main__":
    main()

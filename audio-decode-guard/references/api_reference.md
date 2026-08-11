# Compatibility Notes

The skill supports local media formats that the pinned FFmpeg build can decode, including M4A/AAC, MP3, WAV, FLAC, OGG/Opus, WMA, MP4, and MOV audio streams.

The normalized output contract is:

- container: WAV
- codec: signed 16-bit little-endian PCM (`pcm_s16le`)
- sample rate: 16,000 Hz
- channels: mono

This format is directly readable by common Whisper implementations and avoids relying on the transcription library to find FFmpeg at runtime.

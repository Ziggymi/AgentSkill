# AgentSkill

This repository contains reusable Codex skills.

## Included skills

- [`feishu-chrome-reader`](./feishu-chrome-reader): Read and extract content from Feishu/Lark documents through an already-authenticated Chrome session.
- [`windows-sandbox-report-fallback`](./windows-sandbox-report-fallback): Safely generate derived artifacts when Windows sandbox restrictions block source edits.
- [`audio-decode-guard`](./audio-decode-guard): Verify local FFmpeg availability and normalize compressed media into Whisper-compatible WAV without modifying the source.

Each skill is kept in its own directory. The skill definition is in `SKILL.md`, with optional Codex metadata under `agents/`.

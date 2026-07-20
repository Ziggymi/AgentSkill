---
name: windows-sandbox-report-fallback
description: Safely finish generated reports, metrics, JSON, Markdown, and other derived artifacts when Codex apply_patch fails on Windows with split writable root or restricted-token sandbox errors. Use for Windows desktop tasks where source edits are blocked but existing project scripts or read-only code can still produce the requested output.
---

# Windows Sandbox Report Fallback

Use this workflow only after apply_patch fails with a sandbox setup error such as windows unelevated restricted-token sandbox cannot enforce split writable root sets.

## Preserve The Boundary

- Do not disable sandboxing, change ACLs, or broaden writable roots.
- Do not replace blocked source edits with Set-Content, shell redirection, Python file rewriting, or similar manual source-edit bypasses.
- Use this fallback for generated artifacts only: reports, metrics, predictions, exported data, screenshots, and validation output.
- If completion genuinely requires a source edit, stop after the user's retry limit and report the exact blocked file and intended patch.

## Fallback Workflow

1. Confirm the failure occurs before file access and is specific to apply_patch.
2. Check whether an existing script already performs the requested computation. Run it first to produce a baseline artifact.
3. For additional generated fields such as timings, run a one-off in-memory program through the project's configured runtime and write only the requested derived artifacts.
4. Keep all generated outputs under the workspace, preferably its existing outputs or results directory.
5. Validate generated JSON by parsing it, validate row counts and labels, and read the final Markdown before reporting success.

## Nested Windows Command Rules

When JavaScript launches PowerShell which streams code to Python:

- Use a PowerShell single-quoted here-string for Python source.
- Use forward slashes in Windows executable paths, for example D:/Apps/Python/python.exe.
- Do not place raw Markdown backticks inside a JavaScript template literal.
- Avoid escaped newline literals across nested parsers; use chr(10).join(lines) in Python.
- Keep secrets out of command output.
- For a network call, clear a known-invalid proxy only in the child process and request scoped network escalation.

## Timing Reports

- Measure wall-clock time with time.perf_counter().
- State whether BERT timing includes model loading.
- State whether LLM timing includes batching and network latency.
- Do not compare prediction timing with training timing.
- Include total seconds and average milliseconds per query.

## Completion Check

Report artifact paths, accuracy metrics, timing scope, and API errors. Never claim a source fix was applied when only a generated artifact fallback succeeded.

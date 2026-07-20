# Feishu Chrome Reader

Read and extract content from Feishu/Lark documents through the user's already-authenticated Chrome session.

## What It Does

- Reads the document that is already open in the user's authorized Chrome tab
- Extracts titles, headings, paragraphs, lists, tables, and code blocks
- Handles virtualized and lazy-loaded document content by scrolling incrementally
- Produces summaries or structured extracted artifacts

## Requirements

- The target Feishu/Lark document is open in Chrome
- The user is already signed in to Feishu/Lark
- A supported browser bridge or Chrome extension is connected to the tab

If the document is not open, the browser bridge is unavailable, or access has expired, the user must complete that step in Chrome first.

## Read-Only And Privacy Boundaries

This skill is read-only unless the user explicitly requests an edit. It does not ask for or access passwords, cookies, local storage, request headers, or access tokens. It stays within the document authorized by the user and does not bypass Feishu/Lark permissions.

Shareable copies of this skill must contain only generic instructions. Do not add document URLs, account names, extracted document content, or other user-specific information.

## Files

- `SKILL.md`: Detailed workflow and safety rules used by Codex
- `agents/openai.yaml`: Display metadata for the skill
- `README.md`: Human-facing overview and usage boundaries

## Scope

The skill is intended for reading, summarizing, searching, exporting, and verifying content from Feishu/Lark documents through an existing authenticated browser session. It does not replace Feishu permissions or perform account sign-in.

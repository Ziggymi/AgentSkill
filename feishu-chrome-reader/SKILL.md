---
name: feishu-chrome-reader
description: Read and extract content from Feishu/Lark documents through the user's already-authenticated Chrome session. Use when Codex must inspect, summarize, search, export, or verify a Feishu/Lark document without asking for credentials or bypassing document permissions.
---

# Feishu Chrome Reader

Use the browser/Chrome bridge that is available in the current Codex environment to read the document already open in the user's Chrome session. This skill is for read-only extraction unless the user explicitly requests an edit.

## Preconditions

- The user has opened the target Feishu/Lark document in Chrome and is already signed in.
- A supported browser bridge or Chrome extension is connected to that tab.
- If no connected tab is available, ask the user to open the document and connect the browser bridge. Do not attempt to log in, request a password, or use a stored session outside the browser bridge.

## Workflow

1. Identify the intended tab from its visible title and Feishu/Lark domain. Do not inspect or print cookies, local storage, request headers, access tokens, or other session data.
2. Capture a DOM snapshot or equivalent page inspection. Inspect the document outline and visible body before choosing locators; do not guess selectors blindly.
3. Use read-only browser operations (for example, locators and a read-only page evaluation) to collect the title, headings, paragraphs, lists, tables, and code blocks. Preserve the document's section order and code formatting.
4. For virtualized or lazy-loaded content, scroll the document incrementally and collect newly rendered content after each scroll. Deduplicate repeated text, stop at the end of the document, and record sections that could not be loaded.
5. Stay within the document the user authorized. Do not follow unrelated links, change document content, download private files, or bypass Feishu permissions.
6. Produce the requested summary or extracted artifact. When writing a file, use the active project's `outputs/` directory, then re-read it and verify that it is non-empty and contains the expected headings or sections.
7. Report the extraction scope and any limitations. Redact personal names, account identifiers, private URLs, and other identifying details from a shareable skill or example unless the user explicitly asks to retain them.

## Browser-tool guidance

Browser integrations expose different tool names. Use the tools available in the current environment; common capabilities are a tab listing, DOM snapshot, Playwright-style locator, scrolling, and read-only page evaluation. Never invent a login flow or claim to have read content when the browser bridge is unavailable.

For a sign-in prompt, expired session, or permission error, stop and ask the user to complete authentication or obtain access in Chrome themselves. Continue only after the target document is visible in the connected tab.

## Privacy boundary

This skill depends on the user's active Chrome session but never needs the session's credentials. Do not copy cookies or tokens into files, prompts, logs, or output artifacts. A distributable copy of this skill must contain only generic instructions and no user-specific document URL, account name, local path, or extracted document content.

<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — committed catalog of per-developer AI preferences. Ships ready to use.

  HOW TO USE THIS FILE:
   1. Keep it committed as `context/preferences.example.md`.
   2. The ONLY repo-specific spot is the "Cannot be overridden" list at the bottom —
      align it with your entry-point safety-rails table (tagged >>> FILL IN below).
   3. Each developer copies it to `context/preferences.md` and edits down to their overrides.
   4. Gitignore `context/preferences.md` (keep THIS `.example` file tracked).
   5. Delete this banner when done.

  KEEP (reusable spine — do not change): the scope + precedence header, and the four
  override groups (Communication, Workflow ceremony, Delegation, Tooling).
═════════════════════════════════════════════════════════════════════════════ -->

# AI personal preferences — example / catalog

This is a **template**. Copy it to `preferences.md` (same folder, `context/`) and keep **only the
lines you want to change**. The AI agent reads `context/preferences.md` at session startup and applies
it silently for the rest of the session. `context/preferences.md` is gitignored, so your copy stays
personal — it is never committed and never affects teammates.

## Scope

- **This repo only.** For preferences that follow you across *every* repo, use your AI tool's
  user-level settings instead — that's out of scope for this file.
- These are **behavioral** overrides: how the agent talks, how much workflow ceremony it uses, what
  it delegates, and which tools it reaches for.

## Precedence — what these prefs can and cannot change

Highest wins:

1. **Agent safety rails** (the confirmation table in the entry point) and **security**
   ([globals/security.md](globals/security.md)) — always win.
2. **Committed-code standards** — [globals/coding-style.md](globals/coding-style.md),
   [workflow/review.md](workflow/review.md), and the CI gates — always win.
3. **Your personal preferences** (this file) — override the project's behavioral defaults below.
4. **Project behavioral defaults** — the fallback when you've said nothing.

In short: personal prefs change *how the agent works with you*, never *what standard the committed
code must meet* and never *the safety confirmations*.

## The catalog

Each item shows the **project default**. Keep a line in your `preferences.md` only if you want
something different.

### A. Communication style

- **Prompt style** — *default: prose, not menus.* e.g. "Never use multiple-choice / multi-select
  prompts — always ask me in prose."
- **Verbosity** — *default: concise.* e.g. "Be more terse — skip preamble" or "Explain your
  reasoning in more depth before acting."
- **Language** — *default: English.* e.g. "Reply in <language>."

### B. Workflow ceremony

- **Structured-workflow gate** — *default: ask before using the full workflow on non-trivial tasks.*
  e.g. "Never ask — just implement directly" or "Always use the full workflow."
- **Trivial-change threshold** — *default: single-line / config / typo skip ceremony.*
  e.g. "Treat anything under ~20 lines as trivial."
- **Approval before code / before running tests** — *default: wait for explicit go-ahead.*
  e.g. "Proceed without waiting once the path is clear."

### C. Delegation

- **Specialized frameworks** — *default: hand off <framework> work to its expert agent rather than
  editing or running pipelines blind.* e.g. "Never run <framework> pipelines yourself — always delegate."
- **Issues / PRs** — *default: use the repo's issue/PR skills.* e.g. "Draft the text for me to paste
  — don't invoke the skill."

### D. Tooling behavior

- **Linters/formatters during implementation** — *default: don't run them early; trust the commit
  hook.* e.g. "Run <linter> after each file so I see problems immediately."
- **Test routing** — *default: route by diff type (see [workflow/test.md](workflow/test.md)).*
  e.g. "Always run the full local checks even for small changes."

## Cannot be overridden here

These stay in force no matter what you write above — expect review/CI to push back if you try:

<!-- >>> FILL IN: list YOUR repo's safety rails here so the boundary is explicit — copy the
     danger-zone rows from your entry-point safety-rails table (prod deploys, infra/terraform,
     force-push / hard reset, release tags, data-affecting operations, etc.). -->
- The **Agent safety rails** — **>>> FILL IN: your repo's danger zones (mirror the entry-point table).**
- **Security** — no PII/secrets in code, logs, or fixtures; injection-safe patterns
  ([globals/security.md](globals/security.md)).
- **Committed-code standards** — function size, error handling, type hints, etc.
  ([globals/coding-style.md](globals/coding-style.md)).
- **Review gates** — the CRITICAL/HIGH checklist ([workflow/review.md](workflow/review.md)).
- **CI gates** — the formatters/linters that block a merge; never bypass verification without asking.

<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — Claude Code entry point. Twin of .github/copilot-instructions.md.

  HOW TO USE THIS FILE:
   1. Fill in every line tagged  >>> FILL IN:  (search the file for that tag).
   2. Replace every  <angle-bracket placeholder>  with your value.
   3. Delete every  <!-- ... -->  comment (including this banner) when done.
   4. Mirror EXACTLY the same changes into .github/copilot-instructions.md — the
      only difference between the two files is the `../` path prefix on doc links.

  FILL-IN CHECKLIST for this file (each is tagged >>> FILL IN: below):
   [ ] Project context — one paragraph
   [ ] Hard-rule source dirs — your top-level code folders
   [ ] PR-restriction decision — can your agent open PRs directly? note it here and in create-pr.md if not
   [ ] Agent safety-rails table — your project's danger zones

  NOTE: the per-subsystem doc routing table and the common-multi-file-task table now live
  in context/index.md — fill them in THERE, not here. The workflow phases, their order, and
  their entry conditions live in context/globals/workflows.md — THE ONLY definition. Never
  restate them here; this file only explains when to reach for the orchestrator.

  KEEP (the reusable spine — do not change): router framing, session-startup +
  personal-preferences wiring, instruction-precedence, interaction-style, "read docs
  before code" rule, the short workflow section + orchestrator explanation, the
  safety-rails PATTERN, the "keep docs in sync" rule.
═════════════════════════════════════════════════════════════════════════════ -->

# CLAUDE.md

Entry point for Claude Code (and any AI agent). This file is a **router**: it tells you what to read and which workflow to follow. All project context lives under [context/](context/) — **always start at [context/index.md](context/index.md).**

## Session startup

**Before anything else**: check whether `.ai-handoff.md` exists at the repo root. If it does, read it and use it as the starting context for this session — it contains the goal, approach, progress, and next action from the previous session. Ask the user if they want to resume that work or start fresh.

**Also check for `context/preferences.md`**. If it exists, read it and apply it silently for the rest of the session — it holds this developer's personal behavioral overrides (interaction style, workflow ceremony, delegation, tooling). Unlike the handoff, don't announce it or ask anything; just honor it. The catalog of overridable behaviors is [context/preferences.example.md](context/preferences.example.md).

## Instruction precedence

This file (`CLAUDE.md`) is the authoritative entry point. If guidance here conflicts with anything in other agent config, **this file wins**. Workflow phase rules live in `context/workflow/*.md` — read each phase prompt only when entering that phase.

**Personal preferences** in `context/preferences.md` (if present) override this repo's **behavioral** defaults — interaction style, workflow ceremony, delegation, and tooling. They do **not** override the Agent safety rails, [context/globals/security.md](context/globals/security.md), or the committed-code standards in [context/globals/coding-style.md](context/globals/coding-style.md) and [context/workflow/review.md](context/workflow/review.md). Precedence, highest first: safety rails + security → committed-code standards (coding-style, review, CI) → personal preferences → project behavioral defaults.

## Interaction style

**Default to prose, not menus.** Do **not** use multiple-choice prompts for open, exploratory, or design questions — ask in plain text and let the user answer freely. Reserve closed multiple-choice prompts only for genuinely closed, mutually-exclusive decisions where a short menu is clearly faster for the user than typing. When in doubt, write a sentence, not a menu.

## Project context

<!-- >>> FILL IN: One short paragraph (3–5 sentences). What the product does, who it's
     for, and the core tech stack (language, key frameworks, runtime/cloud). This is the
     ONLY project context the entry point carries — everything else lives in
     context/locals/architecture.md. Mirror this paragraph verbatim in copilot-instructions.md. -->
**>>> FILL IN — one-paragraph project summary: what it does, for whom, and the core stack.**

**Always read [context/index.md](context/index.md) first**, then [context/globals/workflows.md](context/globals/workflows.md). The index routes you to the right docs; [context/locals/architecture.md](context/locals/architecture.md) is the shared mental model to read on every code task — business model, repo map, subsystem stack, glossary, the core processing pattern, how to run things, and gotchas. `context/` is split into **globals/** (org-agnostic, identical across projects), **locals/** (project-specific domain docs), and **workflow/** (phase prompts).

## When to read each doc

**Before writing or exploring code, read the matching docs for every subsystem your task touches.** The full routing tables — which `context/locals/*.md` to read per subsystem, plus the common multi-file task groupings — live in [context/index.md](context/index.md). Tasks usually span 2–3 docs, not just the closest one; when in doubt, read more. Two docs are **always read first**: [context/index.md](context/index.md), then [context/globals/workflows.md](context/globals/workflows.md).

When asked to create **or modify** a PR — including editing the title or description of an existing PR — follow [context/workflow/create-pr.md](context/workflow/create-pr.md); to create an issue or project task, follow [context/workflow/create-issue.md](context/workflow/create-issue.md). Both apply **even outside the structured workflow**.

## CRITICAL — read documentation before exploring code

After identifying which subsystems your task touches (using the routing tables in [context/index.md](context/index.md)), **read [context/locals/architecture.md](context/locals/architecture.md) plus every matching `context/locals/*.md` — and the cross-cutting [context/globals/coding-style.md](context/globals/coding-style.md) / [context/globals/security.md](context/globals/security.md) — in full before** running `grep`, `find`, `Read`, or any other tool against project source files. The docs explain what the code IS — reading code without that context produces wrong assumptions and wastes the user's time.

<!-- >>> FILL IN: replace the <...> below with your project's top-level source-code
     folders. KEEP the rule itself — it is what forces docs-first exploration. -->
**Hard rule**: do not open any file under `<your source dirs — e.g. transformations/, app/, infrastructure/, scripts/>` until you have first read the relevant `context/` docs for the task. The only files you may open before reading the docs are the docs themselves and the workflow prompts in `context/workflow/`.

## The workflow

Development work moves through a defined sequence of phases — discuss → plan → implement → test →
review → update docs → PR. Each phase has its own prompt in [context/workflow/](context/workflow/),
read on entry rather than upfront.

**The phases, their order, and their entry conditions are defined in exactly one place:**
[context/globals/workflows.md](context/globals/workflows.md). Never restate them — here or anywhere
else. The sequence is driven by the **`orchestrator` agent** ([.github/agents/agentic/](.github/agents/agentic/)),
which loads that file and runs the phases, delegating each to its specialist agent.

### When to use the orchestrator

Use it for **development work**: a new feature, a multi-file bug fix, a schema or architectural
change, anything spanning more than one service — anything you would open a PR for.

Do **not** use it for:

- a quick question about how the code works, or any read-only exploration
- a single-line fix, a config value, a typo
- non-development tasks — writing an issue, summarizing a PR, generating a deck, analyzing data

If the user explicitly asks for the workflow or for the orchestrator, **use it** — regardless of size.

**When you decide to use it, say so and explain why before starting.** Name the agent and give the
one-line reason, e.g. *"This changes a shared schema and the three services that speak it, so I'll
run it through the `orchestrator` agent — it drives the discuss → … → PR workflow."* Never switch
into the workflow silently.

Some phases apply on their own, outside the sequence: when asked to create **or modify** a PR —
including editing an existing PR's title or description — follow
[context/workflow/create-pr.md](context/workflow/create-pr.md); to create an issue or project task,
follow [context/workflow/create-issue.md](context/workflow/create-issue.md).

<!-- >>> FILL IN (decision): can your agent open PRs directly, or does it need to hand off
     (e.g. org SAML restrictions blocking one tool)? Decide, then reflect it in
     create-pr.md. Keep both entry-point files consistent. -->


## Agent safety rails

Before executing any of the following, **stop and ask the user for explicit confirmation**. State what you are about to do and why, then wait for a yes.

<!-- >>> FILL IN: the PATTERN (a confirm-before-doing table) is reusable; the ROWS are
     project-specific. Replace the <...> rows with your danger zones. Categories worth
     covering: writing to shared/prod data, mutating a live schema, deploying, editing
     infra-as-code, editing CI/CD config, destructive git, editing env-scoped config.
     The last row (destructive git) applies to every project — keep it. -->

| Action | Why it needs confirmation |
|---|---|
| `<your pipeline run / schema deploy>` against shared dev or prod (not sandbox) | Writes to shared tables / mutates a live warehouse schema |
| `<your live schema migration / deploy>` | Irreversible without a rollback |
| Any edit inside `<your infra-as-code dir, e.g. infrastructure/>` | One `apply` away from mutating live resources |
| Any edit inside `<your CI/CD config dir, e.g. .github/workflows/>` | Changes gates that protect every future merge |
| `git push --force`, `git reset --hard`, or `git rebase` on already-pushed commits | Destructive — can overwrite teammates' work |

For all other actions, proceed without asking.

## Keeping docs in sync

In the structured workflow, this happens in **step 6 (Update docs)** — follow [context/workflow/update-docs.md](context/workflow/update-docs.md) for the routing table and procedure. For ad-hoc changes outside the structured workflow, follow the same prompt to update affected `context/locals/*.md` files in the same PR. Don't let the docs drift.

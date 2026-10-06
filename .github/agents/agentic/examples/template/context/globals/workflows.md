<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — the META-DOC that explains the whole system. Mostly structural and reusable
  as-is. READ IT END TO END FIRST — it tells you how the layers fit together and where new
  content belongs, which makes filling in every other file much easier.

  Only two spots need your input, both tagged >>> FILL IN below and both OPTIONAL:

  FILL-IN CHECKLIST:
   [ ] (optional) Entry-point auto-load behavior for YOUR tools — confirm or adjust
   [ ] (optional) Test-phase sandbox / locked-down identity — fill if your Test phase
       touches shared infra; delete the section if it only runs local checks

  Delete the comments when done.
═════════════════════════════════════════════════════════════════════════════ -->

# AI Workflow Architecture

Single source of truth for how AI guidance is organised in this repo. This file lives in
`context/globals/` — it is **org-agnostic** and identical across every project that uses this kit.
It is **always read**, right after [`../index.md`](../index.md). **Read this before changing any
workflow file or adding new instruction / prompt / docs files.**

## The layered model

```
┌─────────────────────────────────────────────────────────────────────┐
│ ENTRY POINTS — always loaded at session start                        │
│   CLAUDE.md                          (Claude Code)                   │
│   .github/copilot-instructions.md    (GitHub Copilot)                │
│                                                                      │
│   Job: route the agent. They hold no project context — they point    │
│   at context/index.md, which routes everything else.                 │
└─────────────────────────────────────────────────────────────────────┘
                                  │ "always start at context/index.md"
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ context/index.md — ALWAYS READ FIRST (navigation router)             │
│ context/globals/workflows.md — ALWAYS READ 2nd (this file)           │
└─────────────────────────────────────────────────────────────────────┘
            │                        │                        │
            ▼                        ▼                        ▼
┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐
│ context/globals/    │   │ context/locals/     │   │ context/workflow/   │
│ ORG-AGNOSTIC        │   │ PROJECT-SPECIFIC    │   │ PHASE PROMPTS       │
│ (identical across   │   │ (what this codebase │   │ (pulled per phase)  │
│  all projects)      │   │  IS)                │   │                     │
│                     │   │                     │   │ discuss.md          │
│ workflows.md (this) │   │ architecture.md     │   │ plan.md             │
│ coding-style.md     │   │ <subsystem-a>.md    │   │ implement.md        │
│ security.md         │   │ <subsystem-b>.md    │   │ test.md             │
│                     │   │ infrastructure.md   │   │ review.md           │
│                     │   │ ci-cd.md            │   │ update-docs.md      │
│                     │   │ data-pipelines.md   │   │ create-pr.md        │
│                     │   │ <rule>-overrides.md │   │ create-issue.md     │
│                     │   │                     │   │ context-handoff.md  │
└────────────────────┘   └────────────────────┘   └────────────────────┘
```

**Why this shape?**

- **Entry points** are short, always-present routers. They hold no project context and no workflow
  rules — they point at [`../index.md`](../index.md), which routes everything else. This keeps the
  always-on context tiny.
- **`globals/`** is the reusable spine — this file plus the cross-cutting `coding-style.md` /
  `security.md`. It is **copied verbatim into every project and never localized.** If a project needs
  to bend a global rule, it adds a `locals/<rule>-overrides.md` doc rather than editing the global.
- **`locals/`** is everything specific to *this* project: `architecture.md` (the shared mental model,
  read on every task) plus one doc per subsystem. Agents may add new `locals/*.md` as they learn the
  codebase, but **every new or changed local doc must be reviewed by the user** and listed in
  `index.md`.
- **`workflow/`** holds the phase prompts, pulled only when the agent enters that phase. The Implement
  prompt isn't loaded during Discuss; the PR prompt isn't loaded during Plan.
- Two docs are read more broadly than "on demand": `globals/coding-style.md` and
  `globals/security.md` apply to all code edits, and **`locals/architecture.md` is read on *every*
  task** — it's the shared mental model the entry points route to unconditionally.

## Folder map

| Path | Purpose | Loading model |
|---|---|---|
| `CLAUDE.md` | Claude Code entry point | Always loaded (Claude) |
| `.github/copilot-instructions.md` | Copilot entry point | Always loaded (Copilot) |
| `context/index.md` | Navigation router — the doc map + maintenance rules | Read **first**, every session |
| `context/globals/workflows.md` | This file — how the system works | Read **2nd**, every session |
| `context/globals/coding-style.md`, `security.md` | Cross-cutting code rules (org-agnostic) | Before any code edit |
| `context/locals/architecture.md` | The shared mental model — business model, repo map, glossary, core pattern, run commands, gotchas | Read on **every** code task |
| `context/locals/*.md` (other) | Domain knowledge — what this codebase IS | Pulled when `index.md` routes the agent there |
| `context/workflow/*.md` | Workflow phase prompts — what to do at each phase | Pulled when the agent enters that phase |
| `context/preferences.md` | Per-developer behavioral overrides (gitignored) | Read at session start, applied silently |
| `.github/agents/agentic/*.agent.md` | `orchestrator` + one thin agent per phase | Loaded only when that agent runs; each carries no rules of its own, only pointers into `context/` |

## Decision rules — where does new content belong?

```
Is the content a workflow phase procedure (what to do during step N)?
  → context/workflow/<phase>.md  (and add a row to "The loop" table below — in this file only)

Is the content domain knowledge about a subsystem (what some part of the codebase IS)?
  → context/locals/<subsystem>.md  (and add a row to the doc table in context/index.md;
                                    get the user to review the new doc)

Is the content a broadly-applicable code rule that is the SAME for every project (style, security)?
  → context/globals/<rule>.md      (rare — globals are org-shared; propose it upstream, don't fork)

Is it a project-specific tweak to a global rule?
  → context/locals/<rule>-overrides.md  (add a row to context/index.md)

Is the content a routing rule (which doc to read when)?
  → context/index.md  (the entry points just point here)
```

## Loading model summary

- **What auto-loads on every session**: `CLAUDE.md` (Claude) or `.github/copilot-instructions.md`
  (Copilot). Nothing else auto-loads.
- **What is read on every session**: `context/index.md` then this file. The entry points instruct the
  agent to start there. On any code task, `context/locals/architecture.md` is read next.
- **What pulls on demand**: the rest of `context/locals/` and all of `context/workflow/`, plus
  `globals/coding-style.md` / `globals/security.md` before any code edit.
- **Why this matters**: the always-on context is what shapes every agent response. Keeping it small
  and routing-only is what makes the agent reliably follow the right phase prompt and read the right
  domain doc, instead of drowning in always-on rules that may not apply to the current task.

<!-- >>> FILL IN (optional): how your specific tools auto-load entry points. In the source
     project, Claude Code auto-loaded CLAUDE.md and Copilot auto-loaded
     copilot-instructions.md, with no tool-specific auto-load beyond that. Confirm this
     matches your tooling, or adjust. If you only use one tool, you can drop the twin and
     keep a single entry point — but then update every "keep both in sync" reference. -->

## The loop — the single definition

**This table is the only place the workflow is defined.** The entry points, the context index, and
the orchestrator agent all link here instead of restating it. If you need to change a phase, its
order, or when it is entered, change it here and nowhere else.

| # | Phase | Enter when | Prompt |
|---|---|---|---|
| 1 | **Discuss** | Starting any development task — scope, approach, and acceptance criteria are settled here | [discuss.md](../workflow/discuss.md) |
| 2 | **Plan** | The approach is agreed and the change spans multiple files or services | [plan.md](../workflow/plan.md) |
| 3 | **Implement** | The plan is approved — code only | [implement.md](../workflow/implement.md) |
| 4 | **Test** | Code is written — routes by what the diff touched | [test.md](../workflow/test.md) |
| 5 | **Review** | Tests pass, or there was nothing runnable to test | [review.md](../workflow/review.md) |
| 6 | **Update docs** | Review is clean and the change touched something these docs describe | [update-docs.md](../workflow/update-docs.md) |
| 7 | **Create PR** | Docs are in sync — commit and open the PR | [create-pr.md](../workflow/create-pr.md) |

Read each prompt **when you enter that phase**, not upfront.

### Skipping and looping

- Not every task runs all seven. A small, well-understood change can start at Implement; a
  docs-only diff has nothing to Test.
- **Skipping is the user's decision, not yours.** Say which phase you propose to skip and why, then
  wait. The one exception is Test, which decides for itself that a diff has nothing runnable
  ([test.md](../workflow/test.md)).
- Phases advance only when the current phase's own gate is satisfied — Discuss needs a confirmed
  approach *and* acceptance criteria; Plan needs explicit approval. Each phase prints a hand-off
  line when it is done.
- Review loops back: CRITICAL or HIGH findings return to Implement, then re-review.

### On-demand phases

These sit outside the sequence and are pulled whenever the situation calls for them:

| Phase | Pull when | Prompt |
|---|---|---|
| **Create issue** | Filing an issue from a spec/request | [create-issue.md](../workflow/create-issue.md) |
| **Context handoff** | The session is long, context is tight, or work stops mid-phase — **offer it, don't wait to be asked** | [context-handoff.md](../workflow/context-handoff.md) |

`.ai-handoff.md` is intended to be gitignored (local-only). The entry-point files instruct the agent to check for it at session start and ask the user whether to resume.

`context/preferences.md` is likewise gitignored (local-only, per-developer). The entry points read it at session start and apply it silently — it overrides behavioral defaults only, never safety rails, security, or committed-code standards. Its committed catalog is [`../preferences.example.md`](../preferences.example.md).

### Who runs it

Three layers, each with one job: the entry points decide **whether** to use the workflow at all; the
`orchestrator` agent (`.github/agents/agentic/orchestrator.agent.md`) **sequences** the phases and
enforces the gates; the phase agents (`.github/agents/agentic/<phase>.agent.md`) **execute** a single
phase under its prompt. Each phase agent is a thin wrapper: it declares which `context/` docs to read
and adds only role-specific framing — the rules live here and in `context/workflow/`, never
duplicated in the agent file. Splitting execution across agents is the default (keeps context small,
since each specialist loads only its own phase's prompt); running the whole loop in a single thread is
an equivalent, user-selectable alternative — same phases, same gates, same definitions of done.

<!-- >>> FILL IN (optional) — Test-phase sandbox / locked-down identity.

  If your Test phase runs real workloads (jobs, batches, migrations) against shared
  infrastructure, document the identity/permissions cage HERE and keep the operational
  how-to in context/workflow/test.md. A proven setup runs Test as a dedicated, locked-
  down service account that can touch dev but never prod, never modify IAM, and never
  write data — only read it for validation. The KEY IDEAS worth copying:

    - A dedicated, minimal-permission identity for the agent's Test runs (not the
      developer's own credentials).
    - It can read shared data for validation but cannot mutate prod or change permissions.
    - Key-less impersonation: the developer's day-to-day identity is granted "token
      creator" on the agent identity, so no key files exist and the human is not in the loop.
    - A precondition gate in test.md that refuses to run unless the environment and caller
      are exactly what's expected.

  If your Test phase only runs local checks (unit tests, a linter, a local app), you do
  NOT need this section — delete it, and simplify test.md accordingly.
-->

## Modifying the workflow system

| To do this | Edit |
|---|---|
| Change what happens during a workflow phase | `context/workflow/<phase>.md` (the "Definition of done" at the bottom of each prompt is the exit criterion) |
| Add a new workflow phase | Create `context/workflow/<name>.md`, add a row to "The loop" table **in this file only**, update `context/index.md` |
| Add a new project-specific code rule | Create `context/locals/<rule>-overrides.md`, add a row to the doc table in `context/index.md` (don't edit `globals/`) |
| Add a new domain doc | Create `context/locals/<subsystem>.md`, add a row to the doc table in `context/index.md`, and get the user to review it |
| Extend safety rails | Add a row to the table in `CLAUDE.md` AND `.github/copilot-instructions.md` |

## How both AIs read this system

- **Claude Code**: reads `CLAUDE.md` at session start, which points to `context/index.md`. From there
  it follows pointers to `context/workflow/*` (per phase) and `context/locals/*` (per subsystem, plus
  `globals/coding-style.md` and `globals/security.md` before code edits).
- **GitHub Copilot**: reads `.github/copilot-instructions.md` at session start, which points to the
  same `context/index.md` and the same downstream files.

Both AIs read the exact same files via the exact same routing — there is no tool-specific auto-load beyond the entry point. This is why `CLAUDE.md` and `.github/copilot-instructions.md` have nearly identical structure: keeping them in sync is what makes Copilot feel like Claude (and vice versa). If your environment has a per-tool asymmetry (e.g. one tool can open PRs and the other can't), document it explicitly here and in the affected phase prompt (e.g. "step 7 is Copilot-only").

Both AIs delegate the structured workflow the same way, too: to the `orchestrator` agent in
`.github/agents/agentic/`, which reads this file and drives the phases in whichever tool is running.

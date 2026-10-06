# AI Workflow Template

A deprojectified starter kit for the AI-assisted development workflow. It keeps the **structure** —
the router entry points, the always-read navigation index, the org-agnostic `globals/`, the
project-specific `locals/` domain docs, the per-phase `workflow/` prompts, and the thin `orchestrator`
+ phase-agent set — but strips out the project-specific content, leaving fill-in markers and guidance
in its place.

Drop these files into a new repo, fill in the markers, and you have the same
discuss → plan → implement → test → review → update-docs → PR workflow, tuned to your project.

## What's in here

```
.github/agents/agentic/examples/template/
├── CLAUDE.md                          ← Claude Code entry point (router)
├── .github/
│   ├── copilot-instructions.md        ← GitHub Copilot entry point (twin of CLAUDE.md)
│   └── agents/agentic/                ← orchestrator + one thin agent per phase
│       ├── orchestrator.agent.md.template
│       ├── discuss.agent.md.template
│       ├── plan.agent.md.template
│       ├── implement.agent.md.template
│       ├── test.agent.md.template
│       ├── review.agent.md.template
│       └── update-docs.agent.md.template
└── context/
    ├── README.md                      ← this file
    ├── index.md                       ← ALWAYS READ FIRST — navigation router + doc map
    ├── terminology.md                 ← dictionary of business/domain terms (fill in per project)
    ├── preferences.example.md         ← per-developer behavioral overrides (copy to preferences.md)
    ├── globals/                       ← ORG-AGNOSTIC — identical across all projects; copy verbatim
    │   ├── workflows.md               ← the meta-doc: how this whole system fits together
    │   ├── coding-style.md            ← broadly-reusable code rules (adapt examples to your language)
    │   └── security.md                ← broadly-reusable security rules
    ├── locals/                        ← PROJECT-SPECIFIC — "what the codebase IS"
    │   ├── architecture.md            ← the shared mental model (read on every task)
    │   ├── subsystem-template.md      ← COPY once per subsystem, then delete
    │   ├── data-pipelines.md          ← pipeline overlay (ships pre-made — fill the blanks, or delete)
    │   ├── infrastructure.md          ← where/how things run
    │   └── ci-cd.md                   ← quality gates + deployment
    └── workflow/                      ← phase prompts: "what to do at each step"
        ├── discuss.md
        ├── plan.md
        ├── implement.md
        ├── test.md
        ├── review.md
        ├── update-docs.md
        ├── create-pr.md
        ├── create-issue.md
        └── context-handoff.md
```

## The layered model (read `context/globals/workflows.md` first)

The whole thing is a router. Understanding it is the key to filling it in well, so
**read [context/globals/workflows.md](globals/workflows.md) before anything else** — it's the most
reusable file in the kit and it explains the model:

1. **Entry points** (`CLAUDE.md`, `.github/copilot-instructions.md`) — always loaded. They hold no
   project content; they point at `context/index.md`.
2. **Always-read context** — `context/index.md` (navigation) then `context/globals/workflows.md`
   (how the system works).
3. **On-demand context** — `context/globals/*` (org-agnostic rules), `context/locals/*` (project
   domain docs), and `context/workflow/*` (phase prompts).

### globals vs locals — the core contract

- **`globals/`** is the reusable spine. It is **identical across every project** — copy it
  verbatim and do **not** localize it. To bend a global rule for one project, add a
  `locals/<rule>-overrides.md` doc instead of editing the global.
- **`locals/`** is everything specific to *this* project. Agents may add new `locals/*.md` docs over
  time, but each must be **reviewed by the user** and listed in `context/index.md`.

## Conventions used in the templates

Every template file follows the same conventions, so you always know what to do:

- **Top banner** — each file opens with a boxed `<!-- ═══ ... ═══ -->` comment containing a
  **HOW TO USE** note and a `[ ]` **FILL-IN CHECKLIST** listing exactly what that file needs from you.
  Read the banner first; it's your per-file to-do list.
- **`>>> FILL IN`** — the marker for every spot that needs your input. It appears two ways:
  - in a `<!-- >>> FILL IN: ... -->` comment explaining *what* belongs there and why, and
  - as a bold **`>>> FILL IN`** inside the actual content (a table cell, a list item) marking the
    literal place to type. Search the file for `>>> FILL IN` to jump between them.
- **`<angle-bracket placeholders>`** — e.g. `<subsystem-a>`, `<your run command>`. Replace each with
  your value.
- **Delete the scaffolding when done** — every `<!-- ... -->` comment (banners included) is guidance,
  not content. Remove them once the file is filled in.

Two kinds of file:
- **Guidance stubs** (most of `context/locals/`) — the body describes what the file should contain
  (objective + suggested sections), so you (or an agent) can write the real version.
- **Working templates** (entry points, `context/index.md`, `context/workflow/`, `globals/workflows.md`,
  `locals/data-pipelines.md`, `.github/agents/agentic/*.agent.md`) — near-complete files with project-specific
  pockets marked `>>> FILL IN`.

## How to adopt it (suggested order)

1. **Read [context/globals/workflows.md](globals/workflows.md)** end to end. It's the map.
2. **Copy the kit into your repo**: `CLAUDE.md` and `.github/copilot-instructions.md` at the root,
   the whole `context/` folder, and `.github/agents/agentic/` (the orchestrator + phase agents) as-is.
   **Rename every `*.agent.md.template` to `*.agent.md`** as you copy — they ship with the `.template`
   suffix so this repo's own agent picker doesn't treat them as live duplicates of the real agents
   that maintain this kit. (If you use only one AI tool, keep a single entry point — but then update
   the "keep both in sync" references in `globals/workflows.md`.)
3. **Write `context/locals/architecture.md`** — the most important doc, read on every task. Use the
   suggested sections in the stub. You can let an agent draft it.
4. **Write `context/terminology.md`** — a flat dictionary of business/domain terms and
   abbreviations. Keep it separate from `architecture.md` so either can be skimmed on its own.
5. **Decide your subsystems.** For each one, copy `context/locals/subsystem-template.md` to
   `context/locals/<subsystem>.md` and fill it in. Delete the template copy when done.
6. **Keep `globals/` as-is.** `coding-style.md` and `security.md` carry over verbatim (swap only
   language-specific examples if your stack differs); don't fork them per project.
7. **Fill in `locals/data-pipelines.md`, `locals/infrastructure.md`, and `locals/ci-cd.md`** —
   `data-pipelines.md` ships pre-made (almost every data project has pipelines), so fill its blanks
   for your framework/orchestrator. Delete any of the three (and their rows in `index.md` and the
   phase-prompt routing tables) if your project has no pipelines / meaningful infra / CI.
8. **Wire `context/index.md`**: fill the project-context paragraph, list one row per `locals/` doc you
   kept, and adjust the common-multi-file-task examples.
9. **Wire the entry points**: fill the one-paragraph project identity and the safety-rails table. Keep
   `CLAUDE.md` and `copilot-instructions.md` identical except for the `../` path prefix.
10. **Tune the phase prompts** in `context/workflow/`: the routing tables (your subsystems) and — most
    importantly — `test.md`'s trigger table and run/validation mechanics, the most project-specific
    part of the whole kit.
11. **Gitignore `.ai-handoff.md` and `context/preferences.md`** (both local-only). Keep the committed
    `context/preferences.example.md`; align its "Cannot be overridden" list with your safety-rails
    table. Developers copy it to `context/preferences.md` for their personal overrides.
12. **Fill the handful of `>>> FILL IN` lines in `.github/agents/agentic/*.agent.md`** — illustrative
    example bullets only (e.g. discuss's "blast radius", review's stack-specific checks, test's
    shared-environment commands). Don't add new rules here; they belong in `context/`.
13. **Delete every remaining `>>> FILL IN` marker and `<!-- -->` comment** (banners included). A quick
    grep finds anything left: `grep -rn ">>> FILL IN" .` and `grep -rn "<!--" .` — both should return
    nothing when you're done. Also confirm no `.agent.md.template` files remain:
    `grep -rln "\.agent\.md\.template" .` (or just `find . -name "*.agent.md.template"`) should return
    nothing — step 2's rename should have caught them all.

## Notes on what was intentionally left out

- **The `.github/agents/agentic/*.agent.md` set is generic on purpose.** Each agent is a thin
  wrapper — required reading plus a handful of role-specific example lines (tagged `>>> FILL IN`) —
  and carries no rules of its own; the rules live in `context/workflow/` and `context/globals/`.
  Fill the few project-specific example lines (e.g. discuss's "blast radius" bullet, review's
  stack-specific checks, test's shared-environment commands), but resist the urge to add anything
  more — a fattening agent file is a sign a rule belongs in `context/` instead.
- **No framework guide for your pipeline tooling.** `context/locals/data-pipelines.md` covers how
  *your repo* uses its pipeline framework (dbt, Airflow, Dagster, Spark jobs, …). The framework's own
  reference is left out — `data-pipelines.md` links out to its official docs (or a team guide), since
  those are maintained elsewhere.
- **The Test-phase "locked-down identity" pattern** is described (in `globals/workflows.md` and
  `workflow/test.md`) but not pre-built, since the exact identity/permissions are environment-specific.
  Adopt the *idea* if your Test phase touches shared infra; skip it if it only runs local checks.

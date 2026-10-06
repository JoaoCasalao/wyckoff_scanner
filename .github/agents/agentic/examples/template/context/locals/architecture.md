<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — GUIDANCE STUB. This file is read on EVERY task — the most important domain
  doc to get right. Unlike the workflow files, this isn't "fill a few blanks": you WRITE
  the real architecture.md, using the "Suggested sections" below as a guide. You can point
  an agent at this stub — the prose tells it the file's objective and what sections to produce.

  HOW TO USE THIS FILE:
   1. Write your real doc, replacing the "Suggested sections" guidance with actual content.
   2. Fill the line tagged  >>> FILL IN  (the "Where to go next" links).
   3. Delete every  <!-- ... -->  comment and the "Suggested sections" / "Writing notes"
      scaffolding once the real content exists.

  FILL-IN CHECKLIST:
   [ ] What this repo does
   [ ] Subsystems and how they stack (+ a small diagram)
   [ ] Repo map (top-level dirs → purpose)
   [ ] The core pattern (the one repeated shape in your codebase)
   [ ] Environments
   [ ] How to run things (copy-pasteable commands)
   [ ] Gotchas
   [ ] Where to go next (route to subsystem docs)

  NOTE: the domain-term glossary lives in the sibling `context/terminology.md`, not here —
  link out to it instead of duplicating terms.
═════════════════════════════════════════════════════════════════════════════ -->

# Architecture

> **What this file is for** — This is the shared mental model every other doc builds
> on, and it is read first on every task. Its job is to give brief, high-level context
> on all the components of your project and how they interact — enough that someone (human
> or agent) can orient before diving into any subsystem. Keep it a map, not an encyclopedia:
> link out to the subsystem docs for depth. If a section here grows past a screen or two,
> that's a sign it belongs in its own `context/locals/<subsystem>.md`.

## Suggested sections

Write the real `architecture.md` with sections like these (drop the ones that don't apply,
add ones that do):

- **What this repo does** — 1–2 paragraphs. The product, who uses it, the problem it solves.
- **Subsystems and how they stack** — the components and how data/control flows between them.
  A small ASCII diagram of the stack (top-to-bottom or left-to-right) earns its keep here.
- **Repo map** — a table: each top-level directory and what lives there. This is what lets an
  agent find things without guessing.
- **The core pattern** — most codebases have one repeated shape (a pipeline, a request lifecycle,
  a CRUD-per-entity convention). Name it and describe it once here so every subsystem doc can
  refer back instead of re-explaining. (Domain terms and abbreviations go in the sibling
  `context/terminology.md`, not here.)
- **Environments** — what environments exist (local / dev / staging / prod), how they differ, and
  how the code selects between them.
- **How to run things** — the handful of commands to install deps, run the app locally, run a
  single unit of work, and run the tests. Keep it copy-pasteable.
- **Gotchas** — the non-obvious traps: stale config that looks live, intentional misspellings kept
  for compatibility, hardcoded values edited by hand, anything that has bitten someone before. This
  section pays for the whole doc.
- **Where to go next** — a short list routing the reader to the subsystem docs by task.

## Writing notes

- **Document the "why" and the gotchas, not every discoverable value.** Anything an agent can read
  straight from the code (exact function signatures, full column lists, every config key) does not
  belong here — it goes stale and the agent can just read the code. Capture what the code can't tell
  you: intent, history, cross-component contracts, and traps.
- Keep links relative (`[<subsystem>.md](<subsystem>.md)` for a sibling in `locals/`, or `[coding-style.md](../globals/coding-style.md)` for a `globals/` doc) so they work from the repo and on the web.

## Where to go next

<!-- >>> FILL IN: route the reader to your subsystem docs by task. Keep the data-pipelines/infra/ci rows
     (delete any your repo doesn't have). -->
- Business/domain terms → [../terminology.md](../terminology.md)
- Working on a data pipeline / DAG → [data-pipelines.md](data-pipelines.md)
- Working on `<subsystem A>` → [<subsystem-a>.md](<subsystem-a>.md)
- Working on `<subsystem B>` → [<subsystem-b>.md](<subsystem-b>.md)
- Infra, environments, deployment → [infrastructure.md](infrastructure.md)
- CI/CD, quality gates → [ci-cd.md](ci-cd.md)

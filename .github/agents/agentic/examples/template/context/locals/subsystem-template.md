<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — GUIDANCE STUB for a single subsystem / domain doc. (data-pipelines.md is
  the one subsystem doc that ships pre-made; use THIS for your other subsystems.)

  HOW TO USE THIS FILE:
   1. COPY it once per subsystem, renaming to the subsystem (e.g. pipelines.md,
      dashboard.md, api.md, billing.md).
   2. WRITE the real doc, using the "Suggested sections" below as a guide (you can point
      an agent at the copy — the prose tells it the file's objective).
   3. Add a routing row for the new doc in BOTH entry-point files AND in discuss.md /
      update-docs.md / create-pr.md routing tables.
   4. Delete the scaffolding comments when the real content exists.
   5. Delete THIS template file (subsystem-template.md) once you've made all your copies.

  A "subsystem" is a coherent part of the codebase a task can touch on its own (the data
  pipeline, the web UI, the auth layer). One doc per subsystem; split past ~400 lines.

  FILL-IN CHECKLIST (per copy):
   [ ] "read this when…" trigger line (matches its routing-table row)
   [ ] What it does / responsibility (+ boundaries)
   [ ] Where it lives (dirs + key files)
   [ ] The pattern (the repeated shape, shown once)
   [ ] Conventions specific to this subsystem
   [ ] Contracts with other subsystems
   [ ] How to add / change a typical unit here (the highest-value section)
   [ ] Gotchas
   [ ] Where to go next
═════════════════════════════════════════════════════════════════════════════ -->

# <Subsystem name>

> **What this file is for** — Explain what THIS subsystem is and how to work in it, so an
> agent can make a correct change without reading the whole codebase first. Cover the
> structure, the key files, the conventions, the contracts with other subsystems, and the
> traps. Document the *why* and the gotchas — not values an agent can read straight from the
> code (those go stale).

## Suggested sections

Adapt to the subsystem; not all apply to all subsystems:

- **What it does / responsibility** — one paragraph. Where this subsystem starts and stops, and
  what it explicitly is *not* responsible for (boundaries prevent a lot of wrong changes).
- **Where it lives** — the directories and the key files, with a one-line purpose each.
- **The pattern** — the repeated shape within this subsystem (e.g. "every X follows this skeleton").
  Show the skeleton once; describe what each part is for and what must come in what order.
- **Conventions specific to this subsystem** — naming, file layout, anything non-obvious that the
  generic coding-style doc doesn't cover.
- **Contracts with other subsystems** — what it reads from / writes to upstream and downstream, and
  the keys/schemas/interfaces that must stay in sync. Link to the docs on the other side.
- **How to add / change a typical unit here** — a numbered, end-to-end recipe for the most common
  change (add a new endpoint / asset / page / rule). This is the highest-value section.
- **Gotchas** — the subsystem-specific traps.
- **Where to go next** — links to the docs for adjacent subsystems and to `architecture.md`.

## Writing notes

- Open with a one-line "read this when…" trigger that matches the row you add in the entry-point
  routing tables — so the agent knows when this file applies.
- Call out **multi-file tasks** near the top: "if you touch X here, also read `<other>.md`." Most
  real tasks span 2–3 subsystems; saying so up front is what makes the agent read enough.

## Where to go next

<!-- >>> FILL IN: link to architecture and the docs for adjacent subsystems. -->
- System overview, glossary → [architecture.md](architecture.md)
- `<Adjacent subsystem>` → [<other-subsystem>.md](<other-subsystem>.md)

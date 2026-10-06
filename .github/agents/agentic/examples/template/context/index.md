<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — the navigation router. ALWAYS READ FIRST by the agent. This file holds the
  per-subsystem doc routing table and the common-multi-file-task table that used to live in
  the entry points.

  FILL-IN CHECKLIST:
   [ ] Project context — one short paragraph (mirror the entry points' summary)
   [ ] locals/ table — one row per domain doc your project has (rename the <subsystem-X> rows)
   [ ] Common multi-file tasks — 3–5 cross-cutting tasks (or delete the section)
   [ ] Related repositories — heuristic prose ships AS-IS; only fill in the org convention and the Exceptions table (or leave its template row)

  KEEP as-is: the globals/ table, the workflow/ list (links to globals/workflows.md, the single
  source of the phase table — don't turn this back into a duplicate table), the maintenance rules,
  and the always-read ordering (index.md → globals/workflows.md → locals/architecture.md).

  Delete every  <!-- ... -->  comment (including this banner) when done.
═════════════════════════════════════════════════════════════════════════════ -->

# Context index

**Always read this file first**, before opening any other doc. It is the navigation router for all
AI context in this repo. Then read [globals/workflows.md](globals/workflows.md) to understand how the
workflow itself operates. For any code task, read [locals/architecture.md](locals/architecture.md)
(the project map) before exploring source. For unfamiliar business/domain words, check
[terminology.md](terminology.md).

<!-- >>> FILL IN: One short paragraph — what the product does, for whom, and the core stack.
     Mirror the one-paragraph summary from the entry points. -->
**>>> FILL IN — one-paragraph project summary: what it does, for whom, and the core stack.**

## How context is organized

```
context/
├── index.md          ← you are here (always read first)
├── README.md         ← template usage guide (not project context — for whoever adopts this kit)
├── terminology.md    ← dictionary of business/domain terms
├── preferences.md    ← personal behavioral overrides (gitignored, optional)
├── globals/          ← ORG-AGNOSTIC — identical across all projects
├── locals/           ← PROJECT-SPECIFIC — what this codebase IS
└── workflow/         ← PHASE PROMPTS — what to do at each step
```

- **globals/** is the reusable spine — never localize it. To bend a global rule for this project, add
  an overrides doc in `locals/` instead.
- **locals/** holds everything project-specific. Read the matching `locals/*.md` for every subsystem a
  task touches (usually 2–3, not just the closest one).
- **workflow/** holds the phase prompts; pull the one for the phase you're in.

## globals/ — org-agnostic (always the same across projects)

| Doc | When to read |
|---|---|
| [globals/workflows.md](globals/workflows.md) | **Always, 2nd** — how the whole AI-context system and workflow fit together |
| [globals/coding-style.md](globals/coding-style.md) | Before writing or editing any application code |
| [globals/security.md](globals/security.md) | Before writing or editing any code, regardless of language |

## locals/ — project-specific

<!-- >>> FILL IN: rename the <subsystem-X> rows to your real subsystems and adjust the
     "when to read" text. KEEP architecture.md (always first), and data-pipelines/
     infrastructure/ci-cd if your project uses them (else delete the row and the doc). -->

| Doc | When to read |
|---|---|
| [locals/architecture.md](locals/architecture.md) | **First, on every code task** — business model, subsystem map, repo map, glossary, core patterns, environments, run commands, gotchas |
| [locals/&lt;subsystem-a&gt;.md](locals/<subsystem-a>.md) | **>>> FILL IN** — when to read this subsystem doc |
| [locals/&lt;subsystem-b&gt;.md](locals/<subsystem-b>.md) | **>>> FILL IN** |
| [locals/&lt;subsystem-c&gt;.md](locals/<subsystem-c>.md) | **>>> FILL IN** |
| [locals/data-pipelines.md](locals/data-pipelines.md) | Adding/modifying a pipeline step, wiring a DAG/schedule, output-schema changes |
| [locals/infrastructure.md](locals/infrastructure.md) | Infra, environments, deployment targets, service accounts |
| [locals/ci-cd.md](locals/ci-cd.md) | Pre-commit hooks, PR quality gates, deployment workflows |

### Common multi-file tasks

<!-- >>> FILL IN: 3–5 of the most common tasks in your project that span multiple
     subsystems, and which docs to read for each. Teaches the agent that tasks rarely
     touch one file. Delete this subsection if single-doc tasks are the norm. -->

| Task | Docs to read |
|---|---|
| **>>> FILL IN** — a common cross-cutting task | [locals/&lt;doc-a&gt;.md](locals/<doc-a>.md) + [locals/&lt;doc-b&gt;.md](locals/<doc-b>.md) |
| **>>> FILL IN** | [locals/&lt;doc-a&gt;.md](locals/<doc-a>.md) + [locals/&lt;doc-c&gt;.md](locals/<doc-c>.md) |

## workflow/ — phase prompts

The phases, their order, and their entry conditions are defined in **one place**:
[globals/workflows.md](globals/workflows.md). Don't restate them here or anywhere else — this is
just the file list. Pull a prompt when you enter its phase.

- [workflow/discuss.md](workflow/discuss.md)
- [workflow/plan.md](workflow/plan.md)
- [workflow/implement.md](workflow/implement.md)
- [workflow/test.md](workflow/test.md)
- [workflow/review.md](workflow/review.md)
- [workflow/update-docs.md](workflow/update-docs.md)
- [workflow/create-pr.md](workflow/create-pr.md)
- [workflow/create-issue.md](workflow/create-issue.md)
- [workflow/context-handoff.md](workflow/context-handoff.md)

<!-- >>> FILL IN: this section is mostly heuristic prose that ships AS-IS — do not rewrite it per
     repo. Per repo you only: (1) fill in the org convention in step 1 (where companion repos live and
     how an upstream reference maps to a repo name) or state that there is none; (2) replace the
     template row in the Exceptions table with real exceptions, or leave it if there are none. Never
     hand-list repos the heuristic resolves. -->

## Related repositories

Some products are split across multiple repos — for example a Data Science repo and a separate Data
Engineering repo for the same product — and this repo may also read from upstream data products owned
by other teams. Rather than keeping a hand-maintained list, derive *which* repo produces an input from
the references this repo already contains.

### 1. Identify the source repo (heuristic)

Pipeline configuration usually names every upstream input — a source table, dataset, schema, bucket,
or cloud project (see [locals/data-pipelines.md](locals/data-pipelines.md)). Most organisations name
those resources after the repo that produces them, so the reference can be mapped back to a repo.

<!-- >>> FILL IN: describe YOUR org's convention, with one or two real examples, e.g.
       "Input tables live in a project/database named `<slug>-<env>`; drop the `-<env>` suffix and
        the producing repo is `github.com/<your-org>/<slug>` — so `sales-etl-prod` →
        `github.com/<your-org>/sales-etl`."
     If no such convention exists, say so here and rely on the Exceptions table instead. -->
**Convention in this org:** **>>> FILL IN** — where companion repos live
(`github.com/<your-org>/…`) and how an upstream reference maps to a repo name, with an example.

This is an **inference**, not a registry lookup. If the inferred repo doesn't exist, is archived, or
clearly isn't the producer (for example the data comes from a managed/vendor product that has no
repo), treat it as an **exception**: stop, tell the user which reference you hit and that the
heuristic didn't resolve it, and ask them to add a row to the Exceptions table below. **Never silently
guess a different name.**

### 2. Read the docs before the code

Before analysing a companion repo's source, in order: (a) read this repo's `context/` docs for the
task; (b) read any in-repo contract docs (e.g. data contracts or schema docs for the shared tables);
(c) read the companion repo's own `context/` folder; (d) only then read its source. If the companion
repo has no `context/` folder, tell the user: *"This repo isn't set up yet — set it up first (via the
`agentic-setup` agent) to reduce token usage,"* and search its remaining files only as a last resort,
never as the default.

### 3. Access a companion repo (tiered)

Reaching an org repo is an authorization question, not a capability one — use the lightest tier that
works:

1. **Built-in GitHub search tools** (e.g. `github_repo`, `github_text_search`) — good for "what
   produces table X" or "where is Y defined." **Requires** (a) the tools to be **enabled/available in
   your chat's tool set** — depending on the client this may sit under a tools or *web tools* toggle —
   and (b) your GitHub login to have access to the repo. **Before using this tier, confirm the tools
   are available; if they're not, ask the user to activate them and proceed, otherwise fall back to
   tier 2 or 3.**
2. **GitHub MCP server** *(recommended for whole-file reads)* — add an MCP config (e.g.
   `.vscode/mcp.json`) pointing at the official GitHub MCP server (remote via OAuth, or local Docker
   `ghcr.io/github/github-mcp-server` with a token scoped to `repo`). Gives structured file and
   directory reads of private repos your token can access, with no clone.
3. **Local clone** *(deep-dive / offline fallback)* — clone the repo next to this one (`../<slug>`).
   When a task needs repo X: check whether `../<slug>` already exists; if it does, pull the default
   branch before reading; if it doesn't, ask the user to clone it.

### Exceptions and special handling

Only references that **don't** follow the heuristic — or that resolve but need special handling (a
renamed, moved, or archived repo; a managed/vendor product with no repo; or a companion repo with a
contract doc to read first) — belong here. The heuristic covers everything else, so don't enumerate
repos it already resolves. **Installed libraries are never exceptions** — the agent can already read
installed packages, so don't list a pip- or git-installed dependency here.

**Flag likely exceptions — never work around them silently.** When an upstream reference doesn't
resolve to a real repo, or resolves but you have good reason to think it needs special handling,
**stop and tell the user**: give the reference, the repo the heuristic produced (or "none"), and why
you think it's an exception, then ask them to confirm before adding a row here. Never silently guess a
name or silently proceed.

Add rows in the format of the template row below — replace it, don't ship the placeholder:

| Reference | Resolves to | Notes / read first |
|---|---|---|
| `<upstream reference>` _(template — replace)_ | `github.com/<your-org>/<repo>` — or `—` if there's no repo | One line: **why it's an exception** — a heuristic miss (renamed / moved / archived / not a repo) **or** the **special handling** it needs (e.g. read `<doc>.md` first). |

## Personal preferences

An optional, gitignored `context/preferences.md` holds per-developer **behavioral** overrides
(interaction style, ceremony, delegation, tooling). The full catalog is
[preferences.example.md](preferences.example.md). Personal prefs never override the safety rails, the
security rules, or the committed-code standards.

## Maintenance rules

- **Keep this index in sync** with every meaningful doc under `context/`. Add a row when a doc is
  added; remove it when a doc is deleted.
- **Agents may add new `locals/*.md`** to capture project knowledge for future sessions — but every
  new or changed local doc **must be reviewed by the user** and reflected here.
- **Never edit `globals/`** to fit this project; add a `locals/*-overrides.md` doc instead and list it
  above.
- **Keep the Related repositories section current** — the heuristic prose is the source of truth; only
  the Exceptions table needs upkeep (add/remove rows as references stop or start following the rule).

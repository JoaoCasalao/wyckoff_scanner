<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — Data-pipelines overlay doc. Almost every data project has pipelines, so
  this file ships with the kit. It documents how YOUR repo builds and runs them — the
  framework/orchestrator in use (dbt, Airflow, Dagster, Prefect, Spark jobs, plain
  scripts, …), the conventions, the pipeline/model inventory, the schedules, and the
  how-to-add recipe — on top of the framework's own documentation.

  This is a GUIDANCE STUB: the headings and the generic prose are reusable as-is; the
  project-specific content (framework, job names, layout, schedules, gotchas) is marked
  >>> FILL IN.  Keep the structure, fill the blanks, delete the comments.

  If your repo has no data pipelines, delete this file and its rows in context/index.md,
  workflow/discuss.md, workflow/update-docs.md, and locals/architecture.md.

  FILL-IN CHECKLIST:
   [ ] Framework / orchestrator — what you use, and a link to its docs
   [ ] Project layout — where pipelines live
   [ ] Repo-specific conventions on top of the framework
   [ ] Pipeline / model inventory — grouped by stage/layer
   [ ] Naming tokens used in job/table names
   [ ] Schedules / DAGs — cadence, dependencies, publishing flow
   [ ] How to add a new pipeline step (adapt the recipe)
   [ ] Gotchas
═════════════════════════════════════════════════════════════════════════════ -->

# Data pipelines (this repo's overlay)

> **What this file is for** — the **repo-specific overlay** on your pipeline framework. It covers
> what's different or non-obvious about how *this repo* builds, schedules, and runs pipelines — not
> the generic framework. For framework concepts (APIs, config reference, CLI commands, operators),
> consult the framework's own documentation.

<!-- >>> FILL IN: name the framework(s)/orchestrator(s) in use and link their docs (or an
     in-repo/team guide if you keep one). -->
> Framework / orchestrator: **>>> FILL IN** — e.g. dbt + Airflow, Dagster, Spark jobs on a scheduler
> → `<link to the framework / team guide>`

**Workflow**: start here; follow links out to the framework docs when you need depth. Read the
business-logic doc(s) for the transformation code itself.

## Project layout

<!-- >>> FILL IN: where pipelines live and how they're organised. Show the tree. A repo may
     hold one pipeline project or several side-by-side; describe what's true here. The tree
     below is only an illustration. -->

```
pipelines/
├── <config>                  # project/framework config (e.g. dbt_project.yml, settings)
├── jobs/ | models/           # pipeline steps (one folder/file per step)
├── dags/                     # orchestration definitions (schedules, dependencies)
└── lib/                      # shared business logic imported by the steps
```

## Repo-specific conventions on top of the framework

<!-- >>> FILL IN: the patterns YOUR repo repeats in every pipeline step that are NOT part of
     the framework itself. Common examples — verify each applies, edit or delete:
       1. a shared base class / macro every step uses,
       2. how shared code is packaged and shipped to workers/executors,
       3. how input and output schemas are declared (and whether they're handwritten or
          generated — note it if a generator can't be trusted),
       4. how environments (dev / prod / sandbox) are selected at runtime.
     Document the ones true for your repo, with the WHY (gotchas), not just the what. -->

These are patterns in this repo that are *not* part of the generic framework:

- **>>> FILL IN** — convention 1 (what it is, why it exists, when it applies)
- **>>> FILL IN** — convention 2
- **>>> FILL IN** — convention 3

### Configuration patterns in this repo

<!-- >>> FILL IN: the distinct config shapes your pipeline steps use (e.g. steps that read
     external/source tables vs. steps that read upstream outputs). Note any wiring rule (how
     an upstream output name must match a downstream input). -->
**>>> FILL IN** — the input/output configuration patterns this repo uses.

## Pipeline inventory

<!-- >>> FILL IN: list the pipeline steps / models grouped by stage or layer (e.g. raw →
     staging → marts, or ingestion → features → scoring → reporting), so an agent can see the
     whole tree at a glance. Mark any folders that exist but are NOT wired in, so nobody
     chases them. -->

| Stage / layer | Steps / models |
|---|---|
| <stage 1 — e.g. ingestion> | `<step-a>`, `<step-b>` |
| <stage 2 — e.g. features> | `<step-c>` |
| <outputs — e.g. reporting> | `<step-d>` |

## Naming tokens

<!-- >>> FILL IN: the tokens that recur in job and output-table names in this repo, and what
     each means. This is what lets an agent parse a name without reading the code. -->

| Token | Meaning |
|---|---|
| `<token>` | **>>> FILL IN** |

## Schedules / DAGs

<!-- >>> FILL IN: each DAG / schedule, its cadence, and what it contains. If schedules are
     staggered or gated by sensors/upstream availability, explain WHY — that reasoning is the
     valuable part. -->

| DAG / schedule | Cadence | Contents |
|---|---|---|
| `<dag-name>` | `<cron>` | **>>> FILL IN** |

### Publishing flow

<!-- >>> FILL IN: how pipeline/DAG changes reach the orchestrator in your setup (CI deploy on
     merge, image build, sync to a central repo, …) — and the implication that editing a DAG
     locally doesn't change what's scheduled until it's deployed. -->
**>>> FILL IN** — how a pipeline change reaches the scheduler (push → deploy mechanism), and the
implication for local runs.

## How to add a new pipeline step in this repo

<!-- >>> FILL IN: keep this end-to-end recipe but adapt it to your framework and conventions.
     The skeleton below is the common shape — edit it to match. -->

End-to-end for a new `my_new_step`:

1. **Create the step** following this repo's skeleton (see the conventions above).
2. **Declare its inputs** following the matching configuration pattern.
3. **Declare its output schema** — if your framework can generate one, check it by hand before
   trusting it; type inference is a common source of silent drift.
4. **Register / wire it** into the pipeline (registry, DAG, `ref()` graph, …) — an unregistered step
   is silently ignored.
5. **Run it locally / against a sandbox** so you're not writing to shared tables.
6. **Push** to trigger the deploy/publish flow.

## Gotchas

<!-- >>> FILL IN: the non-obvious pipeline traps in THIS repo — stale config that looks live,
     intentional misspellings kept for table compatibility, partitioned tables that reject
     unfiltered queries, hardcoded values edited by hand, env-specific connection quirks, etc. -->
- **>>> FILL IN** — a repo-specific pipeline gotcha.

## Where to go next

<!-- >>> FILL IN: route to your business-logic doc, infra doc, and the framework docs. -->
- Business logic used by the pipelines → [<your business-logic doc>.md](<...>.md)
- Environments, compute, scheduler infrastructure → [infrastructure.md](infrastructure.md)
- System overview, glossary → [architecture.md](architecture.md)
- Framework-level depth → `<the framework / team guide>`

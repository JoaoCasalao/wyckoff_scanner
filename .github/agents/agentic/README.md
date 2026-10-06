# Agentic AI Guide

**This file is for humans.** It explains the agentic AI kit for data projects (data science, analytics,
and data engineering repos) — agents don't need
to read it, and shouldn't: everything they need is routed from [context/index.md](../../../context/index.md).
Read this to understand the system; read `context/index.md` to work inside it.

It covers:

- What was added
- How the folder structure is organized
- How the system works end to end
- How to set it up and use it day to day

## Features (Why Reuse This in Other Projects)

### Onboarding and context

- Faster onboarding with a clear entry path (`CLAUDE.md` / Copilot instructions -> context index ->
  workflow phases)
- Session continuity via structured AI handoff state (`.ai-handoff.md`) so work can resume without
  context loss — the agent offers to write it when a session runs long or stops mid-phase, and reads
  it back at the next session's startup
- Per-developer behavior overrides via `context/preferences.md` (gitignored), without weakening
  safety or committed-code standards
- Documentation-first exploration guardrails: read relevant context docs before source-level
  exploration
- A dedicated business/domain terminology dictionary (`context/terminology.md`) that exists in every
  project, with content tailored to that project
- Evidence-based terminology building with mandatory user validation: scans the whole project for
  concrete vocabulary sources
- Domain-aware decisions via layered context (`globals/`, `locals/`, `workflow/`)
- Cross-repo context awareness for multi-repo products (e.g. paired Data Science / Data Engineering
  repos), checking companion repos' `context/` folders first and falling back to their source only
  when necessary
- GitHub wiki reuse during setup: the scaffolder checks for an existing wiki and links/reuses useful
  pages instead of re-documenting them

### Workflow and agents

- Predictable AI behavior through explicit phases (`discuss -> plan -> implement -> test -> review
  -> update-docs -> PR`)
- **One definition of the workflow.** The phases, their order, and their entry conditions live in a
  single file (`context/globals/workflows.md`); entry points, the context index, and every agent link
  to it instead of restating it, so the workflow changes in one place
- **Agents are thin wrappers.** Each agent declares which `context/` docs to read and adds only
  role-specific framing — no checklists, no rules, nothing duplicated from `context/`
- **Split-agent execution keeps context small.** Each phase loads only its own prompt plus the
  `locals/` docs it needs and drops them on exit, so the whole workflow is never resident at once
- The entry point decides *whether* to run the workflow, and must say so and justify it before
  switching — no silent mode changes
- Better quality gates by design (acceptance criteria first, routed testing, structured review)
- Documentation freshness because docs update is part of the delivery flow, not an afterthought
- Continuous hygiene checks for code and docs: detect monolith refactor opportunities, duplicated
  or contradictory documentation, and propose restructuring

### Safety and reuse

- Safer operations with built-in safety rails for high-risk actions
- Optional delegation of framework-specific work (e.g. a dbt or Airflow expert agent) for areas
  where a specialist is safer than a generic agent
- Operational acceleration through reusable skills (validation flows, issue/PR automation, setup utilities, documentation generation)
- Portability across teams/repos through the AI kit template and scaffolder model

## Purpose

The goal is to make AI-assisted development consistent, safe, and easier to onboard.

Instead of a single generic assistant behavior, a repo with this kit installed has:

- Router entry points that define how AI sessions should start
- Structured project context (`context/`) for domain-aware decisions
- A phase workflow (`discuss -> plan -> implement -> test -> review -> update-docs -> PR`), defined
  once and executed by an `orchestrator` that delegates each phase to a matching specialist agent
- Reusable skills for common team workflows (validation flows, issue/PR workflows, setup utilities, etc.)

## High-Level Architecture

The setup follows a routing model:

1. AI session starts at entry instructions
2. Entry instructions decide whether the task needs the structured workflow
3. `context/index.md` routes to the relevant local subsystem docs
4. Workflow phase prompts drive behavior by phase, one phase at a time
5. Each phase runs in its own specialist agent; skills cover repeatable operational tasks

This makes AI behavior predictable and easier to govern.

## Folder Structure

Main agentic AI surfaces in a repo with the kit installed:

```text
.github/
  copilot-instructions.md
  agents/
    agentic/
      README.md
      orchestrator.agent.md
      discuss.agent.md
      plan.agent.md
      implement.agent.md
      test.agent.md
      review.agent.md
      update-docs.agent.md
      agentic-setup.agent.md
      examples/
        template/             # source of truth for the scaffolder
        <filled-example>/     # optional — add filled kits from your own projects to study
  skills/                     # optional — your repo's reusable skills, e.g.
    create-github-issue/SKILL.md
    create-pull-request/SKILL.md
    run-pipeline/SKILL.md
  prompts/                    # optional — repeatable structured prompts

context/
  index.md
  terminology.md
  preferences.example.md
  preferences.md          # local-only, gitignored
  globals/
    workflows.md
    coding-style.md
    security.md
  locals/
    architecture.md
    data-pipelines.md     # pipeline framework overlay (dbt, Airflow, Spark, ...)
    <subsystem>.md        # one per subsystem — e.g. ingestion.md, features.md,
                          # ml-training.md, serving.md, dashboard.md
    infrastructure.md
    ci-cd.md
  workflow/
    discuss.md
    plan.md
    implement.md
    test.md
    review.md
    update-docs.md
    create-pr.md
    create-issue.md
    context-handoff.md

CLAUDE.md
```

## Core Concepts

### 1) Router Entry Points

The AI entry points are thin routers, not full documentation bundles.

- `CLAUDE.md`
- `.github/copilot-instructions.md`

They primarily tell the assistant to start at `context/index.md` and follow the staged workflow.

### 2) Context Layers

`context/` is split into three layers:

- `globals/`: reusable org-agnostic rules and standards
- `locals/`: project-specific architecture and subsystem docs
- `workflow/`: phase prompts that describe what to do at each step

The intended read order is:

1. `context/index.md`
2. `context/globals/workflows.md`
3. `context/locals/architecture.md`
4. Additional subsystem docs based on task scope

`context/terminology.md` sits alongside `index.md` — a flat dictionary of business/domain terms and
abbreviations, read on demand whenever an unfamiliar term shows up rather than as part of the fixed
read order.

### 3) Workflow Phases

The lifecycle is intentionally explicit — discuss → plan → implement → test → review → update docs →
create PR, plus two on-demand phases (create issue, context handoff).

**The phases, their order, and their entry conditions are defined in exactly one place:**
`context/globals/workflows.md`. The entry points, the context index, and the `orchestrator` agent all
link to it rather than restating it, so a change to the workflow happens in a single file.

Benefits:

- Better scoping and acceptance criteria
- Safer changes in multi-service areas
- Cleaner handoffs and PR quality

#### Who runs it

Three layers, each with one job:

| Layer | Decides / does |
|---|---|
| Entry point (`CLAUDE.md`, `copilot-instructions.md`) | **Whether** to use the workflow at all |
| `orchestrator` agent | **Sequences** the phases, enforces the gates, delegates each one |
| Phase agents | **Execute** a single phase under its prompt |

The workflow is for development work — a new feature, a multi-file bug fix, a schema or
architectural change, anything you would open a PR for. It is deliberately **not** used for quick
questions about how the code works, single-line fixes, config values, typos, or non-development
tasks (writing an issue, summarizing a PR, generating a deck, analyzing data). If a developer asks
for it explicitly, it is used regardless of size.

When the agent decides to switch into the workflow it must **say so and give the reason** before
starting — naming the agent and the one-line justification. Silent mode switches are not allowed.

### 4) Data Pipelines and Framework Delegation

Most data projects have pipelines — dbt models, Airflow/Dagster DAGs, Spark jobs, or scheduled
scripts. The kit ships `context/locals/data-pipelines.md`, an overlay doc describing how *this* repo
builds, schedules, and runs them (layout, conventions, inventory, schedules, how to add a step,
gotchas), and `context/workflow/test.md` defaults to the common data-project shape: run a pipeline
step for a date/partition, then validate the output with pass/fail SQL checks.

If your team has a dedicated expert agent for a framework (for example a dbt or Airflow agent), the
work can be delegated to it:

- Name the agent and the paths it owns in `context/index.md`; the `orchestrator` and `test` agents
  hand that area off to it in any phase.
- Pipeline runs against shared dev/prod tables belong in the safety-rails table, so they are never
  executed blindly from a generic agent flow.

This keeps pipeline changes aligned with framework conventions and reduces risk in data operations.

### 5) Specialized Agents

Custom agents define role-specialized behavior. Each one is a **thin wrapper**: it declares which
`context/` docs to read (its workflow phase prompt plus the relevant `locals/` docs) and adds only
role-specific framing. The rules themselves live in `context/`, never duplicated in the agent file —
so the same behavior applies whether the workflow runs across specialists or in a single thread.

Every phase maps to exactly one executor, named after the phase itself:

| Phase | Executor |
|---|---|
| Discuss | `discuss` |
| Plan | `plan` |
| Implement | `implement` |
| Test | `test` |
| Review | `review` |
| Update docs | `update-docs` |
| Create PR | `create-pull-request` skill |

Plus the agents that sit outside the sequence:

- `orchestrator`: sequences the phases, enforces the gates, delegates each one
- `agentic-setup`: bootstraps this full model into a repo, using
  `.github/agents/agentic/examples/template/` as source of truth. Any other folder under `examples/`
  is treated as a filled reference kit to study alongside it — add your own once a project is set up
- (optional) framework expert agents your team already has, delegated to via `context/index.md`

What lives in an agent file: its required reading, its role framing, its output shape, and its
boundaries. What never lives there: the phase list, checklists, coding rules, security rules, or
anything else already written in `context/`.

### 6) Why Split Agents

Running each phase in its own agent is primarily a **context-cost** decision. A specialist loads one
phase prompt and the two or three `locals/` docs that phase needs, then drops them when it hands off.
A single agent carrying all seven phases plus every rule pays for the whole workflow on every turn,
including the turns that only need one part of it.

The trade-off is more handoffs, and state that has to be passed forward explicitly — the agreed
approach and acceptance criteria into Plan, the approved plan into Implement, the criteria into Test,
the final diff into Review.

Splitting is the **default, not a requirement**. When delegation isn't available, or a developer
simply prefers one thread, the orchestrator runs the phases itself: same order, same gates, same
definitions of done — only the executor changes. That choice is a behavioral preference, so it can be
set permanently in `context/preferences.md` (see *Delegation → Execution mode* in
`context/preferences.example.md`).

### 7) Related Repositories (Cross-Repo Context)

Some products span multiple repos — for example a Data Science repo and a separate Data Engineering
repo for the same product, where each repo benefits from knowing what the other does.

Rather than keeping a hand-maintained list, `context/index.md` derives companion repos by **heuristic**
from the upstream references the repo already contains: pipeline config names its source tables,
datasets, schemas, or cloud projects, and most organisations name those after the repo that produces
them. Each repo records its org's convention once (e.g. `sales-etl-prod` →
`github.com/<your-org>/sales-etl`).

The section spells out three things for an agent that needs a companion repo:

- **Identify** the source repo from the pipeline config (the heuristic above), treating any reference
  that doesn't resolve to a real repo as an *exception* to raise with the user
- **Read docs before code** — this repo's `context/`, then in-repo contract docs, then the companion
  repo's own `context/` folder, and only then its source; if it has no `context/`, tell the user it
  isn't set up yet (to reduce token usage)
- **Access tiers** — built-in GitHub search tools, then a GitHub MCP server, then cloning on the VM

Only genuine exceptions are hand-listed (renamed/moved/archived repos, managed-catalog products with no
repo, or repos with a contract doc to read first). **Installed libraries are never listed** — the
agent can already read them. During setup, the `agentic-setup` agent asks for the org convention,
explains the derivation, and asks only for those exceptions instead of collecting a full repo list.

### 8) Skills and Prompts

Skills are reusable operational procedures:

- Run project-specific validation flows
- Automate issue and PR preparation
- Bootstrap or sync the agentic AI kit
- Create GitHub issue from spec
- Generate documentation or presentation artifacts

Prompts support repeatable, structured tasks where needed.

## Safety and Governance

Safety rails are built into entry instructions and workflow docs.

Examples of guarded operations:

- Editing infrastructure in live environments
- Running risky shared-environment tests
- Destructive git operations (force push, hard reset, risky rebases)

This prevents accidental impact on shared services and environments.

## Setup and Use

### 1) Day-0 onboarding (for developers)

1. Clone the repo
2. Open in VS Code with Copilot/agent enabled
3. Copy this `agentic/` folder to `.github/agents/agentic/` in the target repo (if it isn't there
   already), then add `.github/agents/agentic` to the `chat.agentFilesLocations` setting in `.vscode/settings.json`
   (VS Code only auto-discovers `.agent.md` files directly under `.github/agents`, not subfolders),
   and enable organization custom agents:
   ```json
   {
       "chat.agentFilesLocations": {
           ".github/agents/agentic": true
       },
       "github.copilot.chat.organizationCustomAgents.enabled": true
   }
   ```
   Then reload the window so the agents in this folder show up in the agent dropdown
4. Use the `agentic-setup` agent to set up (or sync/update) the agentic AI kit in the repository through its interview -> generate -> verify -> review flow. It also checks for an existing GitHub wiki and reuses/links any useful pages instead of re-documenting them.

### 2) Typical dev flow

1. Describe the task. For development work the agent announces that it is switching to the
   `orchestrator` and why — or you invoke it yourself
2. Discuss the approach and confirm acceptance criteria
3. Plan impacted files and tests
4. Implement changes
5. If a framework area has a dedicated expert agent, delegate framework-specific actions to it
6. Test based on touched areas (for example unit tests, pipeline runs + SQL checks, notebooks)
7. Review and fix findings
8. Update affected docs in `context/locals/`
9. Commit and open PR

For a quick question, a one-line fix, or a non-development task, none of this applies — the agent
answers directly.

## How This Helps the Team

- Faster onboarding: structured docs and predictable flow
- Better quality: planning, testing, and review are explicit
- Lower risk: safety rails for destructive/shared actions
- Better maintainability: docs update step is part of workflow
- Reusability: AI-kit template can scaffold same model elsewhere

## Recommended Team Adoption

1. Use the structured workflow for development work; skip it for questions and one-liners
2. Keep `context/locals/` synced with real code changes
3. Use skills for repeatable operational tasks
4. Keep safety rails strict for shared environments
5. Regularly review agent definitions for drift — an agent should never accumulate rules that belong
   in `context/`

## Quick Reference

- Entry routing: `CLAUDE.md`, `.github/copilot-instructions.md`
- Context map: `context/index.md`
- Terminology: `context/terminology.md`
- Workflow definition: `context/globals/workflows.md`
- Phase prompts: `context/workflow/<phase>.md`
- Phase agents: `.github/agents/agentic/<phase>.agent.md` (`discuss`, `plan`, `implement`, `test`,
  `review`, `update-docs`) driven by `orchestrator`
- Personal overrides: `context/preferences.example.md` (copy to `context/preferences.md`)
- Domain map: `context/locals/architecture.md`
- Operational automation: `.github/skills/`

## Notes

- This guide is descriptive; it does not replace subsystem technical docs.
- For pipeline-specific execution, follow `context/locals/data-pipelines.md` and
  `context/workflow/test.md`.
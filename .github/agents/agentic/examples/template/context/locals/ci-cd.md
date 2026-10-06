<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — GUIDANCE STUB. Write the real ci-cd.md using the "Suggested sections" below
  as a guide (you can point an agent at this stub). Delete the scaffolding comments when
  the real content exists.

  FILL-IN CHECKLIST:
   [ ] The quality system at a glance (where enforcement happens)
   [ ] Pre-commit hooks (inventory + the auto-fix-and-abort commit flow)
   [ ] PR checks — which BLOCK the merge vs. which are advisory (most useful section)
   [ ] Tool configuration (pointer + non-obvious choices with reasons)
   [ ] Deployment workflows (trigger → action → target env)
   [ ] Secrets / auth used by CI (names only)
   [ ] Where to go next
═════════════════════════════════════════════════════════════════════════════ -->

# CI/CD — Code Quality & Deployment

> **What this file is for** — Explain how quality is enforced and how code reaches each
> environment: the pre-commit hooks, the PR checks (what blocks a merge vs. what's advisory),
> and the deploy/publish workflows. Read this when modifying the CI pipeline, adding a quality
> tool, or debugging a failing check. Document how the pieces fit and which gates block — not a
> line-by-line restatement of YAML the agent can read.

## Suggested sections

- **The quality system at a glance** — where enforcement happens (local hooks, CI, or both) and the
  intent of each layer. If layers overlap on purpose, say why.
- **Pre-commit hooks** — the inventory: each hook, what it checks, whether it auto-fixes. Crucially:
  document the *commit flow* when a hook auto-fixes and aborts (so the agent re-stages and retries
  instead of fighting it). Note any "do NOT run the full hook suite as a verification step" caveats if
  your repo carries lint debt.
- **PR checks** — which checks run on a PR, and **which ones actually block the merge** vs. which are
  reported but advisory. This distinction is the single most useful thing in the file.
- **Tool configuration** — where each tool's settings live (one pointer), and any non-obvious choices
  (ignored rules, exclusions) with the reason.
- **Deployment workflows** — each deploy/publish workflow: its trigger (branch, path filter, tag), what
  it does, and which environment it targets. A trigger-summary table at the end is handy.
- **Secrets / auth used by CI** — which secret each workflow needs (names only).
- **Where to go next** — link to `infrastructure.md` for the resources these workflows deploy to.

## Writing notes

- Tell agents plainly which commands are safe to run locally as a verification step and which will
  rewrite unrelated files or waste time. This prevents a class of messy diffs.

## Where to go next

<!-- >>> FILL IN: keep these two; add links to anything else relevant. -->
- Infra, environments, deploy targets → [infrastructure.md](infrastructure.md)
- System overview → [architecture.md](architecture.md)

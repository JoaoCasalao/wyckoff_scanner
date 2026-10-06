<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — GUIDANCE STUB. Write the real infrastructure.md using the "Suggested
  sections" below as a guide (you can point an agent at this stub).

  If your project has NO meaningful infra (a library, a script, a local app), delete
  this file entirely and remove its routing row from the entry points and routing tables.

  Delete the scaffolding comments when the real content exists.

  FILL-IN CHECKLIST:
   [ ] Environments (project/account, branch → env, where config lives)
   [ ] Infrastructure-as-code layout
   [ ] Resources provisioned (shared vs per-env)
   [ ] Runtime / compute config (with the WHY for non-obvious settings)
   [ ] Service accounts / identities and IAM (+ how CI/agent auth, key-lessly)
   [ ] Secrets (names + consumer, never values)
   [ ] Gotchas
   [ ] Where to go next
═════════════════════════════════════════════════════════════════════════════ -->

# Infrastructure

> **What this file is for** — Document where and how things run: environments, the
> infrastructure-as-code layout, deployment targets, service accounts / identities, secrets,
> and scheduling. Read this when changing *where or how* things run, as opposed to *what* the
> code does. Capture the wiring and the gotchas, not values an agent can read from the config.

## Suggested sections

- **Environments** — a table of the environments (local / dev / staging / prod): which project/account
  each maps to, which branch deploys to it, and where the authoritative config values live.
- **Infrastructure-as-code layout** — the directory tree of your Terraform / Pulumi / CloudFormation /
  k8s manifests, and which module provisions what.
- **Resources provisioned** — the main resources (compute, storage, databases, queues, load balancers)
  and any that are shared vs per-environment.
- **Runtime / compute config** — how workloads are sized and scheduled (containers, serverless, cron,
  DAGs). If there are non-obvious settings (memory, parallelism, schedule staggering), explain *why*.
- **Service accounts / identities and IAM** — a table of the identities and their roles, plus how the
  agent (and CI) authenticate. Prefer key-less auth; document it.
- **Secrets** — where secrets live (secret manager, CI secrets) and which thing uses each. Never put
  the secret values here.
- **Gotchas** — version skews, resources that only update on push (not PR), things that look shared but
  aren't, etc.
- **Where to go next** — links back to architecture and to the deployment side in `ci-cd.md`.

## Where to go next

<!-- >>> FILL IN: keep these two; add links to any subsystem docs that own runtime config. -->
- CI/CD, deployment workflows → [ci-cd.md](ci-cd.md)
- Pipelines, DAGs, scheduler config → [data-pipelines.md](data-pipelines.md)
- System overview → [architecture.md](architecture.md)

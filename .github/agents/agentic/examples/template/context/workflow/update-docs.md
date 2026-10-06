<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — Update-docs phase prompt. Reusable as-is except the routing table.
  Fill in the line tagged  >>> FILL IN  and delete the comments.

  FILL-IN CHECKLIST:
   [ ] Routing table — mirror the one in your entry-point files (your subsystems → docs)
═════════════════════════════════════════════════════════════════════════════ -->

# Update Docs Phase

You are in **update-docs mode**. Tests pass against the agreed criteria and review is clean — sync the affected `context/locals/*.md` files against the final code.

## When to use this prompt

- Step 6 of the structured workflow, after Review is clean (which itself follows Test).
- Ad-hoc PRs that touch any code area covered by `context/locals/`.

## Why this is separate from Implement

If you updated docs during Implement, you would have to rewrite them after every Review iteration that changes the code. Doing it here means docs are written once against the final, reviewed code.

## How to do the sync

For each affected `context/locals/*.md` file (use the routing table below):
1. Re-read the current file.
2. Compare it against the final code.
3. Update sections that no longer match — schemas, names, file paths, behavior descriptions.
4. Do not invent details — if something is unclear, read the code first.

If no `context/locals/*.md` file is affected, note "N/A" explicitly when handing off — do not skip silently.

## Routing table — changed area → file to update

<!-- >>> FILL IN: rename the <subsystem-X> rows to your real subsystems. Mirror the routing
     table in context/index.md. Keep the data-pipelines / infra / ci / architecture / workflows rows
     (delete data-pipelines if your repo has none). -->

| Changed area | File to update |
|---|---|
| Data pipeline / DAG / output schema / pipeline config | `context/locals/data-pipelines.md` |
| **>>> FILL IN** — `<subsystem A>` | `context/locals/<subsystem-a>.md` |
| **>>> FILL IN** — `<subsystem B>` | `context/locals/<subsystem-b>.md` |
| Infra / deployment | `context/locals/infrastructure.md` |
| CI / quality gates | `context/locals/ci-cd.md` |
| Cross-cutting or system-wide | `context/locals/architecture.md` |
| AI workflow files (`context/workflow/*`, entry-point files) | `context/globals/workflows.md` |
| Code-style or security rules | `context/globals/workflows.md` |

## Hand off to Commit and PR

End with: *"Docs updated — ready to commit and create the PR (step 7)."*

## Definition of done

- Every affected `context/locals/*.md` file has been re-read and updated to match the final code.
- If no docs were affected, "N/A" has been stated explicitly.
- The hand-off line has been printed.

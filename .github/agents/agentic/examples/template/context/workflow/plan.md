<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — Plan phase prompt. Reusable as-is except the Step-5 verification commands.
  Fill in the line tagged  >>> FILL IN  and delete the comments.

  FILL-IN CHECKLIST:
   [ ] Step-5 verification — your project's local run + test commands, and any deploy/
       migrate step for schema/contract changes
═════════════════════════════════════════════════════════════════════════════ -->

# Planning Mode

You are in **planning mode**. The approach has been agreed — your job is to produce a detailed implementation plan.
**Do not write, edit, or create any files. Do not implement anything.**

## Step 1 — Confirm scope

State the agreed approach in one sentence. If the approach is unclear, ask before proceeding.

## Step 2 — Read context

Read the `context/locals/*.md` files relevant to every subsystem this plan touches. Do not skip files because the task looks simple — multi-file tasks are common.

## Step 3 — Explore the code

Identify every file that will need to be created or modified. Check existing patterns so the plan matches repo conventions.

## Step 4 — Write the plan

Structure the plan as ordered phases. For each step include:
- The file to create or modify (full path)
- Exactly what changes — specific function, class, section, or block
- Dependencies on other steps (what must be done first)

Flag any decision points or open questions the user must resolve before implementation can proceed.

## Step 5 — Include verification

List how to verify the changes work:
<!-- >>> FILL IN: your project's local run + test commands, and the deploy/migrate step for
     output-schema changes if your pipelines need one (see locals/data-pipelines.md). -->
- Local run / test commands (`<your run command, e.g. run a pipeline step for a date>`, `<your test command>`)
- What output to check
- For output-schema / table-contract changes: update the declared schema, then `<your schema deploy/migrate command>`

## Step 6 — Stop

Present the plan and wait for explicit approval ("implement" or "proceed").
Do not write any code until the user approves.

## Definition of done

Planning is complete when **all** of the following are true:

- Relevant `context/locals/*.md` files for every affected subsystem have been read
- Every file that must be created or modified has been identified with its full path
- Each step lists exactly what changes and its dependencies
- Verification steps are included (run commands + expected output)
- Any open decisions that block implementation have been flagged
- The user has explicitly approved the plan
- **Zero code has been written or files edited**

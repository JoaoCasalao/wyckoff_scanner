<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — Implement phase prompt. Reusable as-is — no placeholders to fill.

  ONE DECISION to confirm (tagged >>> FILL IN below): the "don't run linters/formatters
  here" rule assumes a pre-commit hook auto-fixes them at commit time (step 7). If your
  project has NO such hook, delete that paragraph and run your formatter/linter here instead.

  Delete the comments when done.
═════════════════════════════════════════════════════════════════════════════ -->

# Implementation Phase

You are in **implementation mode**. The plan has been approved — execute it.

## When to use this prompt

Step 3 of the structured workflow, after the plan was approved in step 2.

## Step 1 — Read code-style and security rules

Before editing any file, read [`globals/coding-style.md`](../globals/coding-style.md) and [`globals/security.md`](../globals/security.md). These set the bar for every code change in this repo.

## Step 2 — Execute the approved plan

- Code only.
- **Do not** update `context/locals/*.md` files in this step — that is step 6 (Update docs), separated so docs are written once against final code.
- **Do not** commit — that is step 7 (Commit and PR).

<!-- >>> FILL IN (decision): this paragraph assumes a pre-commit hook auto-fixes lint/format
     at commit time (step 7). If you DON'T have such a hook, delete it and run your
     formatter/linter here instead. -->
**Do not run any linter, formatter, or pre-commit hook in this phase.** The git pre-commit hook in step 7 (Commit and PR) handles all of this and auto-fixes most of it. Running them here either wastes time (the hook will re-run them) or rewrites unrelated files if the repo carries pre-existing lint debt. Trust the hook.

## Step 3 — Hand off to Test

Implementation is code-only. **Do not** stage the test run here — deriving the run plan (what to run, the
run parameters, and the validation checks proving the agreed acceptance criteria) is the **first step of
the Test phase**, where [`test.md`](test.md) is in context and its rules apply. This is the phase boundary:
Implement owns code, Test owns the run plan.

End with: *"Implementation complete — moving to Test (step 4) to derive and validate the run plan."*

## Definition of done

- `globals/coding-style.md` and `globals/security.md` have been read.
- Every step in the approved plan has been executed.
- Focused verification commands have run and reported the expected output.
- **No linter, formatter, or pre-commit hook was run** (if your project defers them to commit time).
- No `context/locals/*.md` file has been edited.
- No test runbook or validation checks were produced here — that is the Test phase's first step.
- No commit has been made.
- The hand-off line has been printed.

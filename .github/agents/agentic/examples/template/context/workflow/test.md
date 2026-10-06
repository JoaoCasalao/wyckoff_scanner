<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — Test phase prompt. The MOST project-specific phase: "running the change"
  differs per project. The reusable SHAPE (keep it) is:
    Step 1  derive run plan from the diff + draft validation checks → get go-ahead
    Step 2  precondition gate + assume the safe test identity (if you use one)
    Step 3  run the unit(s) of work, honoring ordering
    Step 4  wait to finish (poll, don't block)
    Step 5  validate against the AGREED criteria
    Step 6  on failure: notify → propose fix → discuss → loop to Implement on approval
    Step 7  report pass/fail with real output; clean up

  The defaults below are written for a typical data project (pipeline steps run against a
  date/partition, results checked with SQL), so much of it works out of the box. Adjust the
  marked bits to your repo's pipelines/commands.

  FILL-IN CHECKLIST:
   [ ] Step-1 trigger table — your pipelines/commands (generic defaults provided; tune them)
   [ ] Step-1 validation-check example — your check format + known gotchas
   [ ] Step-2 precondition gate / safe test identity — your env + identity (or delete if
       you only run LOCAL checks)
   [ ] Step-4 polling — keep for async/remote jobs (cluster batches, orchestrator runs);
       delete if your runs are synchronous

  If your Test phase only runs LOCAL checks (unit tests, a local app), this file collapses
  to: Step 1 (what to run + checks → go-ahead) → run → validate → report. Drop Steps 2 & 4.
  Delete the comments when done.
═════════════════════════════════════════════════════════════════════════════ -->

# Test Phase

You are in **test mode**. Implementation is complete — now **derive the run plan from the diff, get
the user to validate it**, run the change yourself, and validate the result against the **agreed**
acceptance criteria, before Review.

## When to use this prompt

Step 4 of the structured workflow, after Implement (step 3) and before Review (step 5). This phase
**derives** the run plan from the diff itself — Implement does not pre-stage it. If the diff touches
nothing runnable (only docs, config, etc.), there is nothing to run — Step 1 says so and skips straight
to Review. (If the user explicitly chose to skip testing in Discuss, skip this phase entirely.)

## The agreed-criteria rule

This phase **drafts** the validation checks from the acceptance criteria agreed in Discuss, gets the
user to validate them, then **executes** them. It does **not** invent new success criteria after seeing
results (that is how an agent rationalizes whatever output it produced), and it does **not** change
*what* is being tested — it only translates the **already-agreed** criteria into runnable checks. Run
the checks the user approved and report pass/fail against them. If a criterion turns out to be wrong or
insufficient, say so and stop — do not silently substitute your own.

## Step 1 — Derive and propose the run plan, get the user's go-ahead

Read the diff and build the run plan yourself. Then present it and **wait for the user to validate
before anything is run.**

### Decide what to run

Walk the diff and apply a trigger table that maps "what changed" → "what to run".

<!-- >>> FILL IN: the rows below are generic data-project defaults — replace the paths and
     commands with your repo's layout and tooling (see locals/data-pipelines.md). Keep the
     "only X → skip" row. -->

| Diff touched | Run |
|---|---|
| Library / module code covered by unit tests (`<src>/**`, `<tests>/**`) | `<your unit-test command, e.g. pytest tests/<area>>` |
| Output schema of an existing pipeline step | `<your schema deploy/migrate command>` against the sandbox/dev env, then run the step |
| New pipeline step (code + registration + schema) | Deploy its schema (if needed), then `<your run command> <step> <DATE>` |
| Logic or config of an existing pipeline step | `<your run command> <step> <DATE>` |
| Shared transformation code imported by several steps | list every step that imports it — the user picks which subset to actually run |
| Notebook / analysis code | Re-execute the affected notebook(s) top to bottom (e.g. `<jupyter nbconvert --execute ...>`) |
| `<your non-runnable paths — e.g. dags/, docs/, infrastructure/, .github/>` only | Nothing to run — say so and **skip straight to Review (step 5)** |

### Ask for any run parameters

<!-- >>> FILL IN: many pipelines run against a date/partition (YYYYMMDD). Confirm this is your
     run parameter, or replace with whatever yours need (an env, an input id, a sample size). -->
Ask the user: *"What date should the runbook use? (default: today, YYYYMMDD)"* and wait. If they accept
the default or don't reply with a date, use today's date.

### Draft the validation checks

Translate each acceptance criterion **agreed in Discuss** into a runnable check whose result is
trivially pass/fail — do not re-derive new criteria. Write them runnable the first time:

<!-- >>> FILL IN: the example below is a SQL check against a warehouse table — replace the
     query client and the table prefix with yours, and keep/adjust the partition-filter gotcha.
     If your checks aren't SQL (an HTTP request, a script that exits 0/1, an assertion on a file,
     a metric threshold), swap the example. -->

- Make each check's result a single pass/fail value (a count, a boolean, an exit code, a status).
- **Bake in known gotchas** so the check doesn't fail for the wrong reason. For example, partitioned
  warehouse tables often **require a partition filter** — an unfiltered query may be *rejected* or
  scan far more data than intended. Filter on the run's partition and fully-qualify the table name.

```bash
# Criterion: <table> has 0 rows where <condition>
<your SQL client — e.g. bq query, snowsql, psql, duckdb> \
  'SELECT COUNT(*) AS violations
   FROM <project_or_catalog>.<schema>.<table>
   WHERE <condition> AND <partition_column> = "<run-date>"'
# PASS when violations = 0
```

### Present the plan and get the go-ahead

Group the run commands into numbered steps:
- **Within a step**: commands are independent and run in parallel.
- **Between steps**: commands are sequential — Step N+1 waits for Step N to finish (because N+1 reads
  what N produced).

Present the runbook **and** the validation checks to the user and **wait for explicit go-ahead.** Only
after the user validates do you proceed. Do not invent new criteria here — you are confirming and
de-risking the agreed ones.

## Step 2 — Precondition gate (and safe test identity, if used)

<!-- >>> FILL IN (or DELETE this whole step if your Test phase runs only local checks):
     Gate any run that touches shared infra. Refuse to proceed unless the environment and caller are
     exactly what you expect (e.g. the target-environment variable is dev/sandbox, never prod; the
     caller is the expected dev identity). If you use a dedicated locked-down test identity
     (recommended — its roles/limits belong in context/globals/workflows.md), assume it here
     key-lessly and verify it took before running. Put the exact credential / impersonation / profile
     commands for your cloud here. -->

Abort the phase unless your preconditions hold (e.g. target environment is **not** production; the
caller is the expected identity). If you use a dedicated, locked-down test identity, assume it here and
verify it took before running anything.

## Step 3 — Run, honoring the step structure

You presented the runbook as numbered steps in Step 1. **The step structure is the test** — get it
wrong and the run is meaningless:

- **Within a step**: commands are independent. Start them all, then collect their handles/IDs.
- **Between steps**: steps are sequential. **Step N+1 must not start until every command in step N has
  finished.** Step N+1 reads what step N produced — starting early reads stale or missing data.

<!-- >>> FILL IN: if your run command is async (it submits a cluster batch or orchestrator run,
     prints an ID, and returns while the job keeps running for minutes), parse and record each
     job/run ID so you can poll it in Step 4. If your runs are synchronous, delete this note and
     skip Step 4. -->

## Step 4 — Wait for completion (poll, don't block)

<!-- >>> FILL IN (delete if your runs are synchronous): poll each batch to a terminal state. Do NOT
     foreground-sleep in a long loop — use the harness's scheduled-wakeup so the session doesn't wedge.
     Put your status command here, e.g.:
       <your job-status command> <job-id>   # prints the job's state only
     Seed the first wakeup from a realistic duration for the slowest step, then short re-checks (~90s)
     until terminal. Build a per-step duration table (median/p90) from a few runs to size the first
     wakeup well — it's pure project data, so start with a rough estimate and refine. -->

Poll each running unit to a terminal state. Only when **all** units in a step are terminal do you move
to the next step (or to Step 5 if it was the last). Any failure → Step 6.

## Step 5 — Validate (on success)

Run the validation checks **exactly as the user approved them in Step 1**. Capture the actual output.
Do not edit the checks now — any fixes were already applied and approved in Step 1. If a check errors
instead of returning pass/fail, that is a check defect, not a verdict: surface it, get a corrected check
approved, and re-run — never silently rewrite it to make it pass.

## Step 6 — On failure: notify, propose, discuss

A failure is either a unit that ended in an error **or** a validation check that came back fail. Do
**not** loop back to Implement automatically. Instead:

1. Fetch the error and surface it verbatim.
2. **Notify the user** that the test failed, with the actual error / failing criterion.
3. **Propose a fix** and discuss it with the user.
4. **Only once the user approves the fix**, loop back to Implement (step 3) to apply it. Then return
   here and re-run.

## Step 7 — Report and clean up

- Report **each** approved criterion as **pass/fail** with the actual command output beside it.
- Clean up anything the run set up (e.g. unset impersonation) so the user's shell is left clean.

## Hand off to Review

Once every approved criterion passes, end with:
*"Tests pass against the agreed criteria — moving on to Review (step 5)."*

## Definition of done

- The run plan was derived from the diff and presented to the user — what to run + the validation
  checks — and the user gave explicit go-ahead **before** anything ran (Step 1).
- The precondition gate passed (and the safe test identity was assumed, if used).
- The runbook's step structure was honored: units within a step run together, every unit in a step
  finished before the next step started.
- Async runs were polled via scheduled wakeup, never a foreground `sleep`.
- The user-approved validation checks were run — no new criteria invented after seeing results.
- On any failure, the user was notified, a fix proposed and discussed, and Implement re-entered only
  after the user approved.
- Each criterion was reported pass/fail with actual output.
- Any run-time setup was cleaned up.
- The hand-off line was printed (or the phase was skipped because the diff has nothing runnable, or the
  user chose to skip testing).

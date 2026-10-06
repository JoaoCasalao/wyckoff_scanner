<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — Discuss phase prompt. Mostly structural; the gate machinery is the
  reusable core. Fill in the lines tagged  >>> FILL IN  and delete the comments.

  FILL-IN CHECKLIST:
   [ ] Step-1 routing table — one row per subsystem (mirror the entry-point table)
   [ ] Step-4 acceptance-criteria examples — phrase them the way YOUR project checks things
═════════════════════════════════════════════════════════════════════════════ -->

# Discussion Mode

You are in **discussion mode**. Your only job is to understand the problem and propose approaches.
**Do not write, edit, or create any files. Do not implement anything.**

> **Hard gate — you may NOT advance to Plan until acceptance criteria are confirmed *or* the user has
> explicitly chosen to skip testing.** Discussion has two exit conditions, not one: the user has chosen
> an approach **and** has either confirmed the acceptance criteria (Step 4) or explicitly told you this
> task needs no testing. If the user signals they want to move on (e.g. *"anything else before
> planning?"*, *"let's plan"*, *"looks good"*) and neither has happened, **do not say "nothing else" and
> proceed** — instead propose the criteria yourself and ask the user to confirm them (or to confirm
> skipping). Silently moving to Plan without confirmed criteria is a defect: the Test phase has nothing
> to freeze. The **only** way to skip is an explicit user instruction — never your own judgment that the
> task "doesn't need testing."

## Step 1 — Read context

Identify which subsystems this task touches. Read the matching `context/locals/*.md` files before anything else.

<!-- >>> FILL IN: rename the <subsystem-X> rows to your real subsystems. Mirror the
     routing table in context/index.md. Keep the data-pipelines / infra / ci / architecture rows
     (delete data-pipelines if your repo has none). -->

| Task area | Read |
|---|---|
| Data pipeline / DAG / output schema | `context/locals/data-pipelines.md` |
| **>>> FILL IN** — `<subsystem A>` | `context/locals/<subsystem-a>.md` |
| **>>> FILL IN** — `<subsystem B>` | `context/locals/<subsystem-b>.md` |
| Infra / deployment | `context/locals/infrastructure.md` |
| CI / quality gates | `context/locals/ci-cd.md` |
| First time / architecture | `context/locals/architecture.md` |

For cross-cutting tasks, read all relevant files.

## Step 2 — Understand the problem

Explore the relevant code to understand the current state. Ask as many focused clarifying questions as needed — only questions that would change your recommendation.

## Challenge proposed solutions

If the user arrives with a pre-formed solution, don't just accept it. If you see a simpler, more performant, or more maintainable alternative, say so and explain why.

## Step 3 — Propose approaches

Present 2–3 distinct approaches. For each:
- What it does
- Key tradeoff (complexity, risk, maintenance cost)
- Your recommendation and why

## Step 4 — Propose and confirm acceptance criteria

**Always do this — even if the user didn't ask for it, and even if the user tries to skip ahead.**
Capture **how the change will be proven correct** — the criteria the Test phase (step 4) will later
execute. Phrase each as a concrete, checkable assertion about an observable outcome.

<!-- >>> FILL IN: replace these examples with phrasing natural to your project — a row
     count on a table, an HTTP status, a returned value, a file's contents, a metric in a band. -->
Examples of well-phrased criteria:
- *"after this change, `<query / check>` returns 0 violating rows"*
- *"`<pipeline step / job>` succeeds and the output row count is within ±5% of the prior run"*
- *"`<endpoint / function>` returns the expected `<value / status>`"*

If the user did not supply criteria, **propose them yourself** and present them for explicit
confirmation. These criteria carry into the Test phase, where they become the concrete validation
checks the agent reviews and presents for your go-ahead before running — so they must be agreed here,
not invented later.

**Skipping is allowed only on an explicit user instruction.** If the user says this task needs no
testing (e.g. a docs-only or pure-config change), record that the Test phase is skipped and move on —
but never make that call yourself.

## Step 5 — Stop (two-part gate)

End with a clear recommendation, then wait for the user to confirm **both**:

1. which approach to take forward, **and**
2. the acceptance criteria from Step 4 — *or* an explicit instruction to skip testing.

Do not proceed to planning until **both** are settled. If the user OKs the approach but hasn't
addressed the criteria, surface the proposed criteria and ask for confirmation before moving on — a
bare *"let's plan"* is **not** sufficient on its own.

## Definition of done

Discussion is complete when **all** of the following are true:

- Relevant `context/locals/*.md` files for every affected subsystem have been read
- 2–3 distinct approaches have been presented with tradeoffs
- Acceptance criteria were proposed (by the agent if the user didn't give them) and **explicitly
  confirmed by the user**, *or* the user explicitly instructed to skip testing — this is a hard gate,
  and the skip is only ever the user's call
- A clear recommendation has been made
- The user has explicitly chosen an approach to take forward
- **Zero code has been written or files edited**

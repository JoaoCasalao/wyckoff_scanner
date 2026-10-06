<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — Commit-and-PR phase prompt. The STRUCTURE is reusable (conventional commits,
  pre-commit flow, body template, check-for-existing-PR). Fill in the lines tagged
  >>> FILL IN and delete the comments.

  FILL-IN CHECKLIST:
   [ ] Tool-restriction banner — can your agent open PRs? (keep/edit/delete the banner below)
   [ ] GitHub tool — name the ONE tool to use (gh CLI vs MCP GitHub server) and the one to avoid
   [ ] Pre-commit-hook block — keep if you have a hook that auto-fixes + aborts; delete if not
   [ ] Step-3 docs-sync table — mirror update-docs.md's routing table
   [ ] Step-4 CI blocking checks — the exact checks that block a merge (from ci-cd.md)
   [ ] Step-6 target branch — your default (e.g. `main` or `dev`)
═════════════════════════════════════════════════════════════════════════════ -->

<!-- >>> FILL IN or DELETE this banner depending on your tooling:
> **This phase may be tool-restricted.** If one AI tool cannot create PRs (e.g. org SAML
> restrictions), it hands off to the human after step 6 and another tool runs this phase.
> If all your tools can open PRs, delete this banner.
-->

# Commit and PR Phase

You are in **commit-and-PR mode**. Code is final, review is clean, docs are updated — commit the work and open the PR.

## When to use this prompt

Step 7 of the structured workflow, after step 6 (Update docs).

**Also use this prompt when asked to modify an existing PR** (edit its title or description). In that case skip the commit/docs-sync/lint steps and go straight to **Step 5 (title and body standards)** to draft the new text, then apply it to the existing PR. The title and body-format rules are mandatory for edits too.

<!-- >>> FILL IN: name the ONE tool you use for GitHub ops and stick to it (e.g. an MCP GitHub
     server if `gh` hits SAML denials in your org, or the reverse). Tell the agent not to waste
     turns falling back to the other. -->
**Use `<your GitHub tool — the gh CLI, or an MCP GitHub server>` for all GitHub operations.**
Don't fall back to the other tool on failure — if the chosen tool genuinely errors, surface it.

## Step 1 — Commit

### Conventional commit format

`<TYPE>: <description>` — **the TYPE prefix MUST be UPPERCASE.** This is non-negotiable.

Types (always uppercase): `FEAT`, `FIX`, `REFACTOR`, `DOCS`, `TEST`, `CHORE`, `PERF`, `CI`

Good: `FEAT: add silence trimming step`, `FIX: handle empty segment list`
Bad: `feat: add silence trimming step`, `Fix: handle empty segment list`

### When the pre-commit hook fires

<!-- >>> FILL IN (decision): this assumes a pre-commit hook that auto-fixes and aborts. If you
     don't have one, delete this block. -->
The git pre-commit hook auto-fixes most lint/format issues and then aborts the commit. The expected flow is:

1. Run `git commit`. If it aborts because hooks modified files, re-stage them (`git add <files>`) and run `git commit` again.
2. The second commit usually succeeds — the auto-fixes are now staged.
3. **Only if the second commit also fails** should you read the hook output and fix issues by hand.

**Never use `--no-verify`** unless the user explicitly asks. Trust the hook; intervene only when it surfaces something it can't fix itself.

## Step 2 — Understand the change set

```
git diff <base>...HEAD --stat
git log <base>...HEAD --oneline
```

Identify which subsystems changed.

## Step 3 — Docs-sync verification

<!-- >>> FILL IN: mirror the routing table from update-docs.md (your subsystems → docs). -->
For each changed subsystem, verify its `context/locals/*.md` doc was updated in step 6 (e.g. a pipeline change → `context/locals/data-pipelines.md`).

> When this PR comes out of the structured workflow, docs were already updated in step 6 and this step is a quick verification only. For ad-hoc PRs, this step does the actual work.

If no `context/locals/` file is affected, note "N/A" explicitly in the PR body — don't skip silently.

## Step 4 — Verify CI blocking gates locally

<!-- >>> FILL IN: the exact checks that BLOCK a merge in your CI (from ci-cd.md). Run them and fix failures. -->
Run the checks that block merge in your CI (e.g. `<lint command>`, `<format --check command>`) and fix any failures before proceeding.

## Step 5 — Draft title and body

**Title**: `<TYPE>: <description>` — max ~70 characters. **TYPE MUST be UPPERCASE.**

**Body**:

```
## What changed
<1–3 bullet points — what and where in the codebase>

## Why
<Motivation — business requirement, bug, tech debt, or correctness>

## How to test
<Steps to verify. Include any run parameters used and which unit(s) to run.>

## Docs updated
<Which context/locals/*.md files were updated, or "N/A — no docs-relevant changes in this PR">
```

## Step 6 — Create the PR

<!-- >>> FILL IN: your default target branch (e.g. `main`, or `dev` if you promote dev → prod). -->
Default target branch: `<dev | main>`.

### Step 6a — Check for an existing open PR

**Before doing anything else**, list open PRs for `head: <current branch>`, `base: <target branch>`.

- **None** → proceed to 6b and create a new PR.
- **Any result** → stop, tell the user `There's an open PR from this branch — #NNN: <title>. Update it or open a new one?`, and wait for their answer.

Rely only on a real PR-list query — ignore branch-name guesses or stale sidebar info.

### Step 6b — Create the PR

Create the PR with `base: <target>`, `head: <current branch>`, the title and body above. Return the PR URL.

## Definition of done

- Commit(s) created with conventional format; pre-commit hooks passed (or auto-fixed and re-staged)
- Change set identified (`git diff`, `git log`)
- Every affected `context/locals/*.md` file verified or "N/A" noted explicitly
- CI blocking checks pass locally
- PR title follows `<TYPE>: <description>` (uppercase prefix) and is within the length limit
- PR body includes all four sections: What changed, Why, How to test, Docs updated
- Open PRs for this branch were listed before any PR write
- Either the PR was created (URL returned), or the user was asked about an existing open PR and chose the next action

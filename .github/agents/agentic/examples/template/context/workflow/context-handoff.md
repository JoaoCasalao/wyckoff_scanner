<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — Context-handoff phase prompt. FULLY REUSABLE — no >>> FILL IN markers.
  Nothing project-specific to change.

  ONE SETUP STEP (outside this file): gitignore `.ai-handoff.md` in your repo so the
  handoff stays local-only.

  Delete this comment when done.
═════════════════════════════════════════════════════════════════════════════ -->

# Context Handoff

You are writing a structured handoff so the next AI session can resume seamlessly.
**Do not implement anything. Do not edit any source files.** Only write `.ai-handoff.md`.

## Step 1 — Collect state

Gather the following without asking the user (use `git` and file reads):

- Current branch and last 5 commits (`git log --oneline -5`)
- Uncommitted changes (`git status --short`, `git diff --stat`)
- Which `context/locals/*.md` files are relevant to the current work
- What was being built or fixed (infer from branch name, commits, and conversation)

## Step 2 — Summarise the conversation

From the current conversation, extract:

- **Goal**: What the user is trying to achieve (one sentence)
- **Approach chosen**: Which option was selected during Discuss/Plan (if applicable)
- **Progress**: What has been implemented so far (bullet list of completed steps)
- **Remaining work**: What is still to do (ordered list — most important first)
- **Open decisions**: Any questions or blockers not yet resolved
- **Key file paths**: Every file created or modified in this session

## Step 3 — Write `.ai-handoff.md`

Write the file to the repo root using this exact structure:

```markdown
# AI Handoff — <branch-name> — <YYYY-MM-DD>

## Goal
<one-sentence description of what is being built or fixed>

## Approach
<which option was chosen and why — from the Discuss/Plan phase if used>

## Status
<overall progress: percentage or "X of Y steps done">

## Completed
- <step 1>
- <step 2>
...

## Remaining
1. <next step — most important first>
2. <step after that>
...

## Open decisions
- <question or blocker, if any — otherwise "None">

## Key files
- `<path>` — <one-line description of what changed>
...

## Docs context
- Read before starting: <list of context/locals/*.md files relevant to this work>

## Resume instruction
Pick up at: <exact next action — e.g. "Add definition of done to context/workflow/plan.md">
```

## Step 4 — Confirm

Tell the user: "Handoff written to `.ai-handoff.md`. Open a new session or paste the file contents into your other AI tool to resume."

## Definition of done

- `.ai-handoff.md` exists at the repo root
- All sections are filled in (no placeholders left)
- "Resume instruction" names the exact next action unambiguously
- **No source files have been edited**

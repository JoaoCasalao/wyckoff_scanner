<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — Review phase prompt. Almost fully reusable. Fill in the lines tagged
  >>> FILL IN and delete the comments.

  FILL-IN CHECKLIST:
   [ ] "How review runs" — point to your tooling's built-in review command if it has one
       (e.g. Claude Code's /review)
   [ ] Checklist — tune the items to your language and risk profile (defaults are sensible)
═════════════════════════════════════════════════════════════════════════════ -->

# Review Phase

You are in **review mode**. The implementation is complete — assess it against the checklist below.

## When to use this prompt

Step 5 of the structured workflow, after Test has passed (or after Implement, when there was nothing to run).

## How review runs

<!-- >>> FILL IN: if your tooling has a built-in code-review command (e.g. Claude Code's
     /review), point to it here. Otherwise an agent applies the checklist below to the diff. -->
An agent applies the checklist below to the diff and produces severity-graded output
(CRITICAL / HIGH / MEDIUM / LOW).

## Checklist

<!-- >>> FILL IN: tune to your language/stack. These defaults are language-agnostic enough to keep as-is. -->

### CRITICAL (block — must fix before continuing)
- [ ] No hardcoded secrets or credentials
- [ ] No injection vectors (SQL / command / etc.)
- [ ] No swallowed exceptions (bare catch-and-ignore)
- [ ] No mutable default arguments / shared-state mutation bugs
- [ ] No unsafe deserialisation / `eval` on untrusted input
- [ ] PII not written to logs or test fixtures

### HIGH (warn — fix unless deferred deliberately)
- [ ] Functions within the size limit
- [ ] No deep nesting (> 4 levels)
- [ ] Public functions have type hints / signatures as your language expects
- [ ] Errors handled explicitly (not swallowed)

### MEDIUM (info — user's call)
- [ ] Consistent naming conventions
- [ ] No magic numbers (use named constants)
- [ ] Logger used instead of stray debug output
- [ ] Doc comments on new public functions

## Severity legend

| Level | Meaning | Action |
|-------|---------|--------|
| CRITICAL | Security vulnerability or data loss | Block — fix and re-review |
| HIGH | Bug or significant quality issue | Fix and re-review unless deferred |
| MEDIUM | Maintainability concern | User decides |
| LOW | Style suggestion | Note, optional |

## Loop-back rule

If CRITICAL or HIGH findings appear:
1. Fix them in code (loop back to Implement, step 3).
2. After fixing, re-run the review.
3. Repeat until no CRITICAL or HIGH issues remain.

LOW and MEDIUM findings do not require a loop-back — they are the user's call.

## Hand off to Update docs

Once review is clean, end with: *"Review is clean — moving on to update the affected `context/locals/*.md` files (step 6)."*

## Definition of done

- The checklist has been applied to the full diff.
- All CRITICAL and HIGH findings have been resolved or explicitly deferred by the user.
- The hand-off line has been printed.

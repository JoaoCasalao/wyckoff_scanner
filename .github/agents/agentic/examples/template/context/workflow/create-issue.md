<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — Create-issue phase prompt. Reusable structure. Fill in the lines tagged
  >>> FILL IN and delete the comments.

  FILL-IN CHECKLIST:
   [ ] Tool-restriction note — same decision as create-pr.md (can your agent open issues?)
   [ ] GitHub tool — name the ONE tool to use
   [ ] Metadata — your project board, milestone defaults, and approved label list
═════════════════════════════════════════════════════════════════════════════ -->

<!-- >>> FILL IN or DELETE: same tool-restriction note as create-pr.md, if your agent can't open issues. -->

# Create Issue from Specification

Create an issue for the specification.
Do not change code — this is supposed to create an issue only.

<!-- >>> FILL IN: name the GitHub tool to use (and the one to avoid), same as create-pr.md. -->
**Use `<your GitHub tool>` for all operations.** Don't fall back to the other tool on failure.

## Process

1. Analyze the specification to extract requirements.
2. Check existing issues to avoid duplicates (search by keywords).
3. Create the new issue (or update an existing one if it already covers this).
4. Use your repo's issue template if it has one (fallback to default).

## Requirements

- Single issue for the complete specification.
- Clear title identifying the specification.
- Include only changes required by the specification.
- Verify against existing issues before creation.
- Clear, concise description that any team member can understand.
- List the steps needed to implement the feature.
- Clear deliverables.
- Markdown formatting for readability.
- Do not include implementation details or extensive technical information.
- Do not add extensive acceptance criteria unless necessary.
- Add relevant labels (only from your project's approved list).

## Issue content

- **Title**: feature name from the specification.
- **Description**: Context, Goal, and Acceptance Criteria.

## Metadata

<!-- >>> FILL IN: your project board, milestone defaults, assignee defaults, and the approved label list. -->
- Project board → `<your project board>`
- Milestone → `<default milestone or "No Milestone">`
- Assignees → none unless specified
- Labels → from the approved list: `<label-a>`, `<label-b>`, `<label-c>` (as appropriate)

## Definition of done

- Existing issues searched to avoid duplicates
- Title clearly identifies the feature or bug
- Description includes: Context, Goal, and Acceptance Criteria
- Implementation steps listed
- Deliverables clearly stated
- Labels applied from the approved list
- Issue added to the project board (if applicable)
- **No code has been written or files edited**

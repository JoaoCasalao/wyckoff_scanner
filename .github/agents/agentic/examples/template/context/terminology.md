<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — GUIDANCE STUB. Lives at `context/terminology.md`, a sibling of `index.md` — it
  exists in every project adopting this kit, but its content is entirely project-specific.

  HOW TO USE THIS FILE:
   1. Write the real doc: a flat dictionary of the business/domain terms and abbreviations
      that show up in this repo's code, tests, docs, table/column names, and conversations
      with the business. Not a subsystem doc — just terms and one-line meanings.
   2. Delete every  <!-- ... -->  comment (including this banner) once the real content exists.
   3. Reference it from `context/index.md`'s "How context is organized" tree (already wired
      in the working template) and from `locals/architecture.md`'s "Where to go next".

  FILL-IN CHECKLIST:
   [ ] Business & domain terms table (Term | Meaning) — one row per term
   [ ] A short maintenance note on how new terms get added
═════════════════════════════════════════════════════════════════════════════ -->

# Terminology

A dictionary of the business and domain terms used throughout this repo — in code, tests, docs,
table/column names, and conversations with the business. Read this whenever an unfamiliar term shows
up; see [locals/architecture.md](locals/architecture.md) for how these terms fit into the system.

## Business & domain terms

<!-- >>> FILL IN: one row per term. Favor business/domain vocabulary (the words a product
     owner or analyst would use) over pure code internals — those belong in the relevant
     locals/<subsystem>.md instead. Don't rely on interview answers alone — scan the whole
     project for concrete sources of this vocabulary. Model feature/metric names and dashboard
     KPI/page names are just two examples; also check config/schema field names, table/column
     names, CLI/API argument names, and anything else that recurs across the codebase.
     Before writing a row, have the user validate or correct your best-guess meaning for each
     mined term — terms are easy to misread out of context, and a wrong definition is worse
     than a missing one. -->

| Term | Meaning |
|---|---|
| **&lt;Term&gt;** | **>>> FILL IN** — one-line meaning |

## Maintenance

Add a term here whenever a new abbreviation or business concept enters the codebase or a
conversation with the business. Keep entries to one line each. **Have the user validate or
correct any mined or inferred meaning before adding it** — it's easy to misread a term out of
context.

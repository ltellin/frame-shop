---
description: Create a new Architecture Decision Record from the template
argument-hint: <short-kebab-title>
---
Create a new ADR for: **$ARGUMENTS**

1. Find the highest-numbered file in `docs/architecture/decisions/` and use the
   next number, zero-padded to 4 digits (e.g. after `0011-…` comes `0012-…`).
2. Create `docs/architecture/decisions/<NNNN>-$ARGUMENTS.md` by copying
   `docs/architecture/decisions/0000-template.md` and filling in:
   - the title and today's date,
   - **Context** — the forces in play, drawing on our current discussion and the
     project brief,
   - **Decision** — what we're doing, plainly,
   - **Consequences** — what it commits us to, including any "you may not X
     without revisiting this ADR" lines,
   - **Alternatives considered** — briefly.
3. Add a row to the table in `docs/architecture/decisions/README.md`.
4. If this decision supersedes an earlier ADR, set that one's Status to
   "superseded by ADR-<NNNN>" and note it here.

Show me the finished ADR.

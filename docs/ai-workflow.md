# Working on this project with AI coding agents

This project is built with Claude Code. This doc explains the conventions so a
session doesn't have to relearn them and so we don't rely on one long chat as the
project's memory.

## The layers of project memory

| File | Loaded | Purpose |
|---|---|---|
| `CLAUDE.md` (root) | automatically, every session | Lean orientation: what this is, how to run it, the hard architecture rules, pointers to `docs/`. |
| `backend/CLAUDE.md`, `frontend/CLAUDE.md` | automatically, when working in that subtree | Area-specific rules (layering, "no business logic in the client", commands). |
| `docs/brief.md` | on demand | The original intent, verbatim. Source of truth for *what we're building*. |
| `docs/architecture/overview.md` | on demand | As-built architecture. Source of truth for *how it's built*. |
| `docs/architecture/domain-model.md` | on demand | Entities, relationships, derived state. |
| `docs/architecture/decisions/` | on demand | One ADR per decision — *why* it's built this way and what it commits us to. |
| `docs/roadmap.md` | on demand | *Where we are, what's next, known risks.* Update this as work lands. |

**Rule of thumb:** if you're about to explain a decision or constraint in chat
for the second time, it belongs in a file — a `CLAUDE.md` line if it's a rule, an
ADR if it's a decision, `roadmap.md` if it's status.

Keep `CLAUDE.md` files short. They cost context tokens on every turn. Depth goes
in `docs/`, which is read only when relevant.

## Decisions go in ADRs, not chat

When we make an architectural choice (or revisit one), record it:

```
/new-adr short-title-here
```

This creates the next-numbered file in `docs/architecture/decisions/` from the
template and adds it to that folder's `README.md` index. Fill in Context /
Decision / Consequences. Don't edit a shipped ADR — add a new one that supersedes
it and flip the old one's status.

## Slash commands

Defined in `.claude/commands/`. Type `/` in Claude Code to see them.

| Command | Does |
|---|---|
| `/checks` | The full verification gate: backend `pytest` + `ruff check`, frontend `tsc -b` + `npm run build`, Alembic `upgrade`→`downgrade` round-trip. **Run before calling any change done.** |
| `/new-adr <title>` | Scaffold a new ADR (see above). |
| `/add-component-kind <key>` | Guided walkthrough for adding a framing component type — touches the kind registry, seed data, a pricing rule, and tests. |

## Automated checks

- **PostToolUse hook** (`.claude/hooks/format.sh`, wired in
  `.claude/settings.json`): after any `Edit`/`Write`, if the file is `*.py` it's
  run through `ruff format` + `ruff check --fix`. Non-Python files: no-op. The
  hook never blocks an edit.
- **`.claude/settings.json`** (committed): the format hook + a permission
  allowlist for safe, common commands (`pytest`, `ruff`, `alembic`, `uvicorn`,
  `npm run`, `tsc`, `curl localhost`). Shared by everyone.
- **`.claude/settings.local.json`** (gitignored): your personal overrides —
  extra permissions, local env. Never committed.

## Subagents — what they are, and how to add one

A **subagent** is a separate Claude instance with its own fresh context window,
its own system prompt, and optionally a restricted tool set or a different model.
The main session hands it a task; it works in isolation and reports back. Claude
Code ships general ones (an explore/search agent, a planning agent, a
general-purpose agent).

You define a **project-specific** subagent as a Markdown file in
`.claude/agents/<name>.md`:

```markdown
---
name: architecture-reviewer
description: >
  Use before merging a backend change. Reviews a diff against this project's
  architectural principles (docs/architecture/decisions/) and flags schema
  lock-in risks. Read-only.
tools: Read, Grep, Glob, Bash       # optional — omit to inherit all tools
model: sonnet                        # optional
---

You are reviewing a change to the Frame Shop codebase. Read
docs/architecture/decisions/ and docs/architecture/overview.md first. For the
given diff, check: does domain/ stay free of fastapi/sqlalchemy imports? Are new
component behaviours in the kind registry rather than new columns? Does pricing
stay in domain/pricing? ... Report findings as a short list, most serious first.
```

The frontmatter fields:

- `name` — the identifier you invoke (`@architecture-reviewer`, or the Agent
  tool's `subagent_type`).
- `description` — **when to use it**. Claude reads this to decide whether to
  delegate automatically. Be specific about the trigger.
- `tools` — optional allowlist. Omit to inherit everything. Restrict for
  safety (a reviewer gets no `Edit`/`Write`) or focus.
- `model` — optional per-agent model override.

**When a subagent earns its place:**

- a **narrow, repeatable** job with a clear trigger (review this kind of change;
  do this kind of migration);
- you want **tool restriction** (read-only reviewer) or **isolation** (a big
  search that would bloat the main context);
- you want a **different model / effort level** for a sub-task.

**When it doesn't:** one-off work, or anything that needs the full conversation
context — a cold subagent re-derives what the main session already knows, which
is slower and more expensive.

**This project has no custom subagents yet** — `CLAUDE.md` + `docs/` carry the
rules and the codebase is small enough for the main session to hold. Add one when
a repeated, well-bounded task actually shows up (a likely first candidate: the
read-only architecture reviewer sketched above, once slice 2 adds more surface
area).

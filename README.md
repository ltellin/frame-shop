# Frame Shop

A browser-based ERP / order-management / production system for a custom
picture-framing shop.

**Restarting deliberately.** The project was reset to build the domain model
first, one concept at a time, with implementation kept behind understanding.
Nothing is implemented yet.

## What's here

| Path | |
|---|---|
| [`AGENTS.md`](AGENTS.md) | how coding agents (and people) should work in this repo |
| [`docs/domain/overview.md`](docs/domain/overview.md) | relationship map + glossary — read first |
| [`docs/domain/`](docs/domain/) | one file per domain concept; `moulding`, `material`, `lumber`, `offering`, `design-moulding` have first-pass specs, the rest are stubs |
| [`docs/decisions/`](docs/decisions/) | settled decisions — ADRs 0001 (moulding geometry + tooling work), 0002 (material + bare moulding cost) |
| [`docs/OPEN_QUESTIONS.md`](docs/OPEN_QUESTIONS.md) | what is deliberately undecided |
| [`docs/architecture/overview.md`](docs/architecture/overview.md) | known technical direction, kept high-level |
| [`docs/roadmap/roadmap.md`](docs/roadmap/roadmap.md) | the domain-development sequence |
| [`frontend/schematic-visualizer/`](frontend/schematic-visualizer/) | preserved prototype of the framing schematic — do not modify; see its `NOTES.md` |

## The previous prototype

A full working prototype (FastAPI + React) was built and then set aside. It's in
git history:

```
git checkout prototype-v0      # the complete prior app
git checkout main              # back to here
```

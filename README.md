# Frame Shop

Software for running a custom picture-framing shop. **Restarting** — the project
was reset to re-plan from a cleaner base. Nothing is currently implemented.

## What's here

| Path | |
|---|---|
| `backend/functionality.yaml` | every backend requirement / decision reached before the reset — the domain model, the shop scenarios, pricing, catalog + SKU conventions, deferred work, open risks |
| `frontend/functionality.yaml` | the UI/UX decisions — the design-page workflow, editor panels, the "make a design with no upfront info" flow |
| `schematic-visualizer/` | a preserved, standalone copy of the framing schematic (the signature visualizer) with a spec in `NOTES.md`, to rebuild into the next version |

## The previous prototype

A full working prototype (FastAPI + React) built all of the above. It's kept in
git history:

```
git checkout prototype-v0      # the complete prior app
git checkout main              # back to this skeleton
```

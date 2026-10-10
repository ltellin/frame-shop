# Frame Shop

A browser-based ERP / order-management / production system for a custom
picture-framing shop.

**Restarting deliberately.** The project was reset to build the domain model
first, one concept at a time, with implementation kept behind understanding.
The moulding-pricing slice (docs Phases 1–6) is now implemented as a
standalone package — see `backend/frameshop_pricing/` — with the rest of the domain
still docs-only.

## What's here

| Path | |
|---|---|
| [`AGENTS.md`](AGENTS.md) | how coding agents (and people) should work in this repo |
| [`backend/frameshop_pricing/`](backend/frameshop_pricing/) | **implemented**: the moulding pricing engine (Phases 1–6) — `models.py`, `geometry.py`, `pricing_context.py`, `engine.py`, `data/shop_pricing_data.py` (real lumber prices + example rates), tests in `backend/tests/`. Decoupled from Design/DesignMoulding via `MouldingLineInput` since those aren't specified yet |
| [`docs/domain/overview.md`](docs/domain/overview.md) | relationship map + glossary — read first |
| [`docs/domain/`](docs/domain/) | one file per domain concept; `moulding`, `material`, `lumber`, `finish`, `extra`, `offering`, `design-moulding` have first-pass specs, the rest are stubs |
| [`docs/decisions/`](docs/decisions/) | settled decisions — ADRs 0001 (moulding geometry + tooling work), 0002 (material + bare moulding cost), 0003 (milling orientation + lumber-table keying), 0004 (finish + extra pricing), 0005 (offering pricing + non-offering labor charge), 0006 (pricing context + tooling labor + joinery + markup), 0007 (source lumber size), 0008 (finish two-rate pricing) |
| [`docs/OPEN_QUESTIONS.md`](docs/OPEN_QUESTIONS.md) | what is deliberately undecided |
| [`docs/architecture/overview.md`](docs/architecture/overview.md) | known technical direction, kept high-level |
| [`docs/roadmap/roadmap.md`](docs/roadmap/roadmap.md) | the domain-development sequence — see its 2026-09-17 note on the deliberate sequence deviation to implement pricing early |
| [`frontend/schematic-visualizer/`](frontend/schematic-visualizer/) | preserved prototype of the framing schematic — do not modify; see its `NOTES.md` |

## Using the pricing engine from another repo

`backend/frameshop_pricing/` is a self-contained package with no dependency on
the rest of this repo (or on any web framework) — it's meant to be imported
directly from a separate app, e.g. a website that sells these mouldings.

```bash
# local editable install — day-to-day dev, same machine, always reads live
# source (no reinstall needed as frame-shop changes)
pip install -e /path/to/frame-shop/backend

# git-based install, pinned to a release tag — what the website should
# actually depend on. Not "always latest" on purpose: pin to an explicit,
# tested version, bump it deliberately — see "Releasing a new version" below.
pip install "frameshop-pricing @ git+https://github.com/ltellin/frame-shop.git@v0.1.0#subdirectory=backend"
```

```python
from frameshop_pricing import get_moulding, PricingContext, MouldingLineInput, price_moulding_line

ctx = PricingContext.load_default()
moulding = get_moulding(2001)
line = MouldingLineInput(
    moulding=moulding, material="walnut", finish="oil", extras=(),
    finished_width_in=8.0, finished_height_in=10.0,
)
price_moulding_line(line, ctx)  # -> an itemized price breakdown dict
```

Lumber prices, Finish/Extra/joinery rates, tooling-work rate, and markup all
live in `backend/frameshop_pricing/data/shop_pricing_data.py` — edit that file
directly for your shop's real numbers; `get_moulding(id)` reads from
`backend/frameshop_pricing/data/moulding_catalog.py`, same pattern.

### Releasing a new version

The website pins to a tag, not to `main` — a dependency that changes under a
consuming app without anyone deciding to bump it is a reproducibility hazard,
not a convenience. To ship a frame-shop change to the website:

1. Make the change; CI (`.github/workflows/test.yml`) runs the test suite on
   every push — only tag a commit where it's green.
2. Bump `version` in `backend/pyproject.toml` (semver) and add an entry to
   `backend/CHANGELOG.md`.
3. `git tag vX.Y.Z && git push origin vX.Y.Z`.
4. In the website repo, bump the pinned tag in its dependency file and
   reinstall — a deliberate, reviewable one-line diff, not implicit drift.

## The previous prototype

A full working prototype (FastAPI + React) was built and then set aside. It's in
git history:

```
git checkout prototype-v0      # the complete prior app
git checkout main              # back to here
```

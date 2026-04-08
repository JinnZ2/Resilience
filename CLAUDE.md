# CLAUDE.md

Quick-start guide for AI assistants. **Read `sim/INDEX.json` for the full module registry.**

## What This Is

**Resilience** — simulation framework for systemic resilience across food, energy, logistics, institutions, and cognition. Built by a long-haul truck driver (Superior, WI → Tomah, WI) from direct observation.

- **License:** CC0 (public domain)
- **Language:** Python 3, stdlib only (no pip dependencies)
- **Modules:** 68 Python files, ~29,700 lines
- **Entry point:** `python -m sim.run`

## Quick Navigation

| Need to... | Read this |
|------------|-----------|
| Find a module | `sim/INDEX.json` — every module with tier, deps, run command |
| Understand architecture | `docs/ARCHITECTURE.md` — 5-layer model, import chain, data structures |
| Work with linked repos | `docs/ECOSYSTEM.md` — 10 connected repos, entity flow, fieldlink protocol |
| See cross-repo deps | `fieldlink.json` — machine-readable federation manifest |
| Grep module metadata | `grep "^# MODULE:" sim/*.py` — parseable headers on every file |

## Module Header Format

Every `.py` file has a standardized header:
```
# MODULE: sim/seed_protocol.py
# PROVIDES: SEED.STDLIB_PROTOCOL, SEED.MESH_SIMULATION
# DEPENDS: stdlib-only
# RUN: python -m sim.seed_protocol
# TIER: core
# Stdlib-only octahedral seed expansion, 21-byte packets, mesh networking
```

## Tiers (from INDEX.json)

- **core** — Entry point + shared data structures (always relevant)
- **domain** — Standalone domain models (topic-specific)
- **bridge** — Cross-repo/cross-package connectors
- **tool** — Utilities and analyzers
- **demo** — Example scenarios and city models

## Conventions

- **Stdlib only** — no external dependencies (one exception: `Models/Time-resource.py` uses NumPy)
- **Dataclasses** for schemas, **Enums** for categoricals
- **CC0 headers** on all source files
- **Physics-first** — all claims grounded in thermodynamic constraints
- **Graceful degradation** — `try/except` for optional sibling imports

## When Making Changes

- Keep code self-contained (stdlib only)
- Preserve coupling terms between domains
- Add CC0 header + MODULE header to new files
- Update `sim/INDEX.json` when adding/removing modules
- Run `python -m sim.run` to verify
- See `docs/ARCHITECTURE.md` for design principles

## Deep References

- `SYSTEM_MAP.md` — 5-layer architecture diagram
- `Sovereign.md` — foundational framework (39KB)
- `README.md` — master overview (28KB)
- `game-theory-proofs.md` — 13 axiom failure proofs

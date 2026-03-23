# CLAUDE.md

Guide for AI assistants working in this repository.

## Project Overview

**Resilience** is a simulation framework and knowledge system for modeling systemic resilience across food, energy, logistics, institutions, and cognition. Built by a long-haul truck driver operating the Upper Midwest corridor (Superior, WI → Tomah, WI) from direct observation of the systems being modeled.

- **License:** CC0 (public domain)
- **Primary language:** Python 3 (stdlib only, no external dependencies)
- **Secondary:** React/JSX (standalone interactive visualizations)
- **Documentation:** Extensive Markdown (21+ files)

## Repository Structure

```
Resilience/
├── sim/                          # Core simulation framework
│   ├── run.py                    # Entry point: python sim/run.py
│   ├── core.py                   # Dataclasses, enums (StressScenario, Season, etc.)
│   ├── engine.py                 # Simulation engine (run_city_assessment, print_report)
│   ├── schema_v2.py              # Domain schema definitions
│   ├── economics.py              # Economic modeling
│   ├── survival_engineering.py   # Shuttle/submarine criticality tiers
│   ├── energy_games.py           # Energy system game theory
│   ├── city_thermodynamics.py    # City-level thermodynamic analysis
│   ├── city_optimization.py      # City optimization routines
│   ├── thermodynamic_impact.py   # Impact assessment
│   ├── resilience_offset.py      # Offset calculations
│   ├── purpose_deviation.py      # Purpose drift detection
│   ├── phi_growth.py             # Growth modeling
│   ├── institution_registry.py   # Institution tracking
│   ├── intituitional_first_principles.py  # Institutional analysis
│   ├── datacenter_net_zero.py    # Data center energy modeling
│   ├── cities/
│   │   ├── madison_wi.py         # Madison, WI city model (build_madison())
│   │   └── coupling.py           # Cross-domain coupling terms
│   ├── domains/
│   │   ├── soil_regeneration.py  # Soil health modeling
│   │   ├── incentive_alignment.py # Incentive structure analysis
│   │   └── triage_layer.py       # Triage/priority framework
│   ├── visualizations/
│   │   └── energy_topology.jsx   # Energy topology React visualization
│   ├── docs/
│   │   ├── physics.py            # Physics constraint utilities
│   │   └── prayer_index.md       # Supporting documentation
│   ├── Charter.md                # Layer Zero Charter (system requirements)
│   ├── Purpose.md                # Criticality tier framework
│   └── Urban_Resilience.md       # Framework summary
├── Models/
│   ├── food-resilience.py        # Food system model
│   ├── Time-resource.py          # Time-resource modeling
│   ├── README.md                 # Food system model docs
│   ├── Community.md              # Community model docs
│   ├── Physics-First-AI.md       # Physics-first AI approach
│   └── Simulation.md             # Simulation documentation
├── Dashboard/
│   ├── Routing-ops.md            # Routing operations (30KB)
│   └── Routing-resilience.md     # Routing resilience (38KB)
├── PhysicsGuard/
│   └── README.md                 # Semantic-to-physical constraint translator
├── Food-resiliency.jsx           # Interactive food resilience simulation
├── NVC-game theory-sim.jsx       # NVC game theory simulation
├── README.md                     # Master overview (28KB)
├── SYSTEM_MAP.md                 # 5-layer architecture diagram
├── Sovereign.md                  # Foundational framework (39KB)
├── Field-manual.md               # Practical field manual
└── [other .md files]             # Thematic documentation
```

## Running the Simulation

```bash
cd sim
python run.py
```

This creates a Madison, WI city model and runs stress scenarios (grid failure, supply chain disruption) through the simulation engine.

## Architecture

The project follows a **5-layer architecture** (see `SYSTEM_MAP.md`):

- **Layer 0 — Ground Truth:** Direct physical observation (the sensor)
- **Layer 1 — Dynamic Models:** Food system, nutrient cascade, institutional behavior
- **Layer 2 — Structural Analysis:** Thermodynamic analysis, game theory proofs
- **Layer 3 — Tools:** PhysicsGuard, Combine Cognition
- **Layer 4 — Ground Application:** Corridor mapping (Superior→Tomah)
- **Layer 5 — Meta:** Relational knowledge encoding

### Core thesis

`T_drive < τ_adapt` — external forcing frequency exceeds internal adaptation timescale, and the gap is widening. This is modeled as a thermodynamic trap.

## Code Conventions

- **Python stdlib only** — no external dependencies (intentional design for resilience)
- **Dataclasses** for all schema definitions (`@dataclass` extensively in `core.py`, `schema_v2.py`)
- **Enums** for state variables and categorical types
- **Type hints** throughout (`typing.Optional`, `typing.List`, `typing.Dict`)
- **CC0 headers** on all source files
- **Physics-first modeling** — all claims must be grounded in thermodynamic constraints
- **React hooks pattern** in JSX files (useState, useCallback, useMemo)

## Key Design Principles

1. **Preserve coupling terms.** The connections between domains (food↔energy↔logistics↔nutrition↔cognition) are the primary contribution. Never model domains in isolation.
2. **Physics constraints are non-negotiable.** Energy balance, conservation laws, and thermodynamic limits are enforced explicitly. Use `PhysicsGuard/` concepts and `sim/docs/physics.py`.
3. **No external dependencies.** The codebase is designed to function in degraded infrastructure scenarios. Do not add pip packages.
4. **Relational knowledge over propositional.** Knowledge is stored as relationships between systems, not isolated facts. Preserve cross-references and coupling terms.
5. **Ground truth calibration.** Models stay coupled to physical reality through direct observation data.

## Testing

There is no formal test suite. Validation is done through:
- Physical/thermodynamic constraint checking (PhysicsGuard approach)
- Running simulation scenarios via `sim/run.py`
- Manual verification against ground-truth observations

## No CI/CD

No GitHub Actions or automated pipelines. Changes are verified manually.

## When Making Changes

- Read `SYSTEM_MAP.md` first to understand how components connect
- Maintain coupling terms between domains — don't break cross-references
- Keep code self-contained (stdlib only)
- Add CC0 headers to new source files
- Follow existing patterns: dataclasses for schemas, enums for categoricals
- Documentation files are substantial and interconnected — update cross-references when renaming or moving content
- The `sim/` directory is the active codebase; root-level `.md` files are documentation/theory

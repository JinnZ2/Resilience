# CLAUDE.md

Guide for AI assistants working in this repository.

## Project Overview

**Resilience** is a simulation framework and knowledge system for modeling systemic resilience across food, energy, logistics, institutions, and cognition. Built by a long-haul truck driver operating the Upper Midwest corridor (Superior, WI → Tomah, WI) from direct observation of the systems being modeled.

- **License:** CC0 (public domain)
- **Primary language:** Python 3 (stdlib only, no external dependencies)
- **Secondary:** React/JSX (standalone interactive visualizations)
- **Documentation:** Extensive Markdown (25+ files)
- **Total Python:** ~11,300 lines across 22 modules

## Repository Structure

```
Resilience/
├── sim/                            # Core simulation framework (Python package)
│   ├── run.py                      # Entry point (38 lines)
│   ├── core.py                     # Dataclasses, enums — StressScenario, Season, CityNode, etc. (488 lines)
│   ├── engine.py                   # Simulation engine — run_city_assessment(), print_report() (193 lines)
│   ├── schema_v2.py                # Domain schema definitions (749 lines)
│   ├── economics.py                # Economic modeling (860 lines)
│   ├── survival_engineering.py     # Shuttle/submarine criticality tiers (918 lines)
│   ├── energy_games.py             # Energy system game theory (964 lines)
│   ├── city_thermodynamics.py      # City-level thermodynamic analysis (560 lines)
│   ├── city_optimization.py        # City optimization routines (478 lines)
│   ├── thermodynamic_impact.py     # Impact assessment (626 lines)
│   ├── resilience_offset.py        # Offset calculations (39 lines)
│   ├── purpose_deviation.py        # Purpose drift detection (589 lines)
│   ├── phi_growth.py               # Growth modeling (380 lines)
│   ├── institution_registry.py     # Institution tracking (410 lines)
│   ├── institutional_first_principles.py  # Institutional analysis (322 lines)
│   ├── datacenter_net_zero.py      # Data center energy modeling (621 lines)
│   ├── cities/
│   │   ├── madison_wi.py           # Madison, WI city model — build_madison() (360 lines)
│   │   └── coupling.py             # Cross-domain coupling terms (469 lines)
│   ├── domains/
│   │   ├── soil_regeneration.py    # Soil health modeling (837 lines, largest domain)
│   │   ├── incentive_alignment.py  # Incentive structure analysis (447 lines)
│   │   └── triage_layer.py         # Triage/priority framework (527 lines)
│   ├── visualizations/
│   │   ├── energy_topology.jsx     # Energy topology React visualization
│   │   └── README.md
│   ├── docs/
│   │   ├── physics.py              # Physics constraint utilities (175 lines)
│   │   └── prayer_index.md
│   ├── Charter.md                  # Layer Zero Charter
│   ├── Purpose.md                  # Criticality tier framework
│   ├── Urban_Resilience.md         # Framework summary
│   ├── suburban_tax_flow.md        # Suburban tax flow analysis
│   ├── madison_austin_comparison.md # City comparison
│   └── datacenter_net0.md          # Data center net-zero docs
├── Models/
│   ├── food-resilience.py          # Food system model — Michaelis-Menten yield + ENSO forcing (174 lines)
│   ├── Time-resource.py            # Time-resource modeling — REQUIRES NumPy (76 lines)
│   ├── README.md                   # Food system model docs
│   ├── Community.md                # Community model docs
│   ├── Physics-First-AI.md         # Physics-first AI approach
│   └── Simulation.md              # Simulation documentation
├── Dashboard/
│   ├── Routing-ops.md              # Routing operations (30KB)
│   └── Routing-resilience.md       # Routing resilience (38KB)
├── PhysicsGuard/
│   └── README.md                   # Semantic-to-physical constraint translator
├── Food-resiliency.jsx             # Interactive food resilience simulation
├── NVC-game theory-sim.jsx         # NVC game theory simulation
├── README.md                       # Master overview (28KB)
├── SYSTEM_MAP.md                   # 5-layer architecture diagram
├── Sovereign.md                    # Foundational framework (39KB)
├── Field-manual.md                 # Practical field manual
├── nutrient-cascade.md             # Nutrient cascade model
├── combine-cognition.md            # Combine cognition framework
├── game-theory-proofs.md           # 13 game theory axiom failure proofs
├── thermodynamics-institutional-analysis.md
├── communication-infrastructure.md # CB/LoRa/HAM mesh network design
├── Camouflage-network.md           # Network camouflage concepts
├── Fats-communication.md           # Fats and communication systems
├── Calories_and_water.md           # Caloric and water modeling
└── Urban_food_resilience.md         # Urban food resilience
```

## Running the Simulation

```bash
# From the repository root:
python -m sim.run
```

All imports use absolute paths (`from sim.core import ...`). The `sim/` directory is a proper Python package with `__init__.py` files.

## Import Chain

```
sim/run.py
  ├── sim.core (StressScenario, StressType, Season)
  ├── sim.engine (run_city_assessment, print_report)
  │   └── sim.core (CityNode, ResilienceFoundation, InfrastructureLayers, StressScenario, RedundancyLevel)
  └── sim.cities.madison_wi (build_madison)
      └── sim.core (wildcard import)

sim/docs/physics.py
  └── sim.energy_games
```

Most other modules are self-contained domain models not imported by the entry point. Several use `try/except` sibling imports for optional integration:

```
Standalone domain modules (define models independently):
  economics.py           — substrate accounting (replaces GDP)
  schema_v2.py           — v2 schema with explicit formulas + build_madison_v2()
  city_thermodynamics.py — institutions as heat engines + build_city_1000()
  city_optimization.py   — cross-domain upgrade testing (2x purpose / 0.5x energy rule)
  thermodynamic_impact.py — replaces IMPLAN with thermodynamic reality
  survival_engineering.py — shuttle/submarine criticality tiers (T1-T4)
  purpose_deviation.py   — drift detection via ungameable signals
  phi_growth.py          — golden ratio as thermodynamic scaling law
  institution_registry.py — unified scoring across institution types
  datacenter_net_zero.py — data centers as thermodynamic institutions
  resilience_offset.py   — entropy offset mechanism
  institutional_first_principles.py — operator substitutability
  cities/coupling.py     — multi-domain shock propagation + knowledge decay clocks
  domains/soil_regeneration.py — soil as substrate; knowledge holder age as countdown
  domains/incentive_alignment.py — incentives as infrastructure
  domains/triage_layer.py — financial vs thermodynamic triage comparison
```

All subdirectories have `__init__.py` files for proper Python package structure.

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

- **Python stdlib only** — no external dependencies (intentional design for resilience). One exception: `Models/Time-resource.py` uses NumPy.
- **Dataclasses** for all schema definitions (`@dataclass` extensively in `core.py`, `schema_v2.py`)
- **Enums** for state variables and categorical types (`Season`, `StressType`, `DensityType`, `RedundancyLevel`, `ZoneType`)
- **Type hints** throughout (`typing.Optional`, `typing.List`, `typing.Dict`)
- **CC0 headers** on all source files (format: `CC0 public domain — github.com/JinnZ2/urban-resilience-sim`)
- **Physics-first modeling** — all claims must be grounded in thermodynamic constraints
- **Graceful degradation** — higher-level modules (`survival_engineering.py`, `thermodynamic_impact.py`, `datacenter_net_zero.py`, `purpose_deviation.py`) use `try/except` for sibling imports so they function even if dependencies are missing
- **Method-rich dataclasses** — domain logic lives on the objects (e.g., `entropy_risk()`, `survival_window_hours()`, `thermodynamic_value()`)
- **React hooks pattern** in JSX files (useState, useCallback, useMemo)
- **No linting or formatting tools** configured — code follows PEP 8 informally

## Key Data Structures (sim/core.py)

| Class | Purpose |
|-------|---------|
| `Season` (Enum) | WINTER, SPRING, SUMMER, FALL |
| `StressType` (Enum) | GRID_FAILURE, SUPPLY_CHAIN_DISRUPTION, POPULATION_INFLUX, etc. |
| `RedundancyLevel` (Enum) | NONE(0) through TRIPLE(3) |
| `StressScenario` (dataclass) | Defines a stress test: type, severity, duration, season, notes |
| `CognitiveReadinessLayer` (dataclass) | Human cognitive capacity as infrastructure |
| `CityNode` (dataclass) | Top-level city model with zones and infrastructure |
| `ResilienceFoundation` (dataclass) | Foundation layers for resilience assessment |
| `InfrastructureLayers` (dataclass) | Infrastructure redundancy and capacity |
| `DecisionAuthorityNode` (dataclass) | Who decides during crisis; absentee ownership tracking |

## Key Design Principles

1. **Preserve coupling terms.** The connections between domains (food↔energy↔logistics↔nutrition↔cognition) are the primary contribution. Never model domains in isolation.
2. **Physics constraints are non-negotiable.** Energy balance, conservation laws, and thermodynamic limits are enforced explicitly. Use `PhysicsGuard/` concepts and `sim/docs/physics.py`.
3. **No external dependencies.** The codebase is designed to function in degraded infrastructure scenarios. Do not add pip packages.
4. **Relational knowledge over propositional.** Knowledge is stored as relationships between systems, not isolated facts. Preserve cross-references and coupling terms.
5. **Ground truth calibration.** Models stay coupled to physical reality through direct observation data.

## Known Issues

1. **Many modules are standalone:** Most Python files beyond the core import chain define models but are not wired into the simulation entry point. Several have their own builder functions (e.g., `build_madison_v2()`, `build_city_1000()`, `build_madison_economics()`, `build_madison_coupled_system()`).
2. **`Models/Time-resource.py` uses NumPy:** The only file in the repo with an external dependency (`import numpy`). All other Python is stdlib-only.

## Testing

There is no formal test suite. Validation is done through:
- Physical/thermodynamic constraint checking (PhysicsGuard approach)
- Running simulation scenarios via `python -m sim.run`
- Manual verification against ground-truth observations

## No CI/CD

No GitHub Actions, no automated pipelines, no pre-commit hooks, no linter config. Changes are verified manually.

## When Making Changes

- Read `SYSTEM_MAP.md` first to understand how components connect
- Maintain coupling terms between domains — don't break cross-references
- Keep code self-contained (stdlib only)
- Add CC0 headers to new source files
- Follow existing patterns: dataclasses for schemas, enums for categoricals
- Run from repo root: `python -m sim.run`
- Documentation files are substantial and interconnected — update cross-references when renaming or moving content
- The `sim/` directory is the active codebase; root-level `.md` files are documentation/theory
- Many modules are standalone domain models — adding new ones does not require modifying existing imports

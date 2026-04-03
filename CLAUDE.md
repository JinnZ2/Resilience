# CLAUDE.md

Guide for AI assistants working in this repository.

## Project Overview

**Resilience** is a simulation framework and knowledge system for modeling systemic resilience across food, energy, logistics, institutions, and cognition. Built by a long-haul truck driver operating the Upper Midwest corridor (Superior, WI → Tomah, WI) from direct observation of the systems being modeled.

- **License:** CC0 (public domain)
- **Primary language:** Python 3 (stdlib only, no external dependencies)
- **Secondary:** React/JSX (standalone interactive visualizations)
- **Documentation:** Extensive Markdown (30+ files)
- **Total Python:** ~29,700 lines across 50+ modules

## Repository Structure

```
Resilience/
├── sim/                            # Core simulation framework (Python package)
│   ├── run.py                      # Entry point
│   ├── core.py                     # Dataclasses, enums — StressScenario, Season, CityNode, etc.
│   ├── engine.py                   # Simulation engine — run_city_assessment(), print_report()
│   ├── schema_v2.py                # Domain schema definitions
│   ├── economics.py                # Economic modeling — substrate accounting
│   ├── survival_engineering.py     # Shuttle/submarine criticality tiers (T1-T4)
│   ├── energy_games.py             # Energy system game theory
│   ├── city_thermodynamics.py      # Institutions as heat engines
│   ├── city_optimization.py        # Cross-domain upgrade testing
│   ├── thermodynamic_impact.py     # Replaces IMPLAN with thermodynamic reality
│   ├── resilience_offset.py        # Entropy offset mechanism
│   ├── purpose_deviation.py        # Drift detection via ungameable signals
│   ├── phi_growth.py               # Golden ratio as thermodynamic scaling law
│   ├── institution_registry.py     # Unified scoring across institution types
│   ├── institutional_first_principles.py  # Operator substitutability
│   ├── datacenter_net_zero.py      # Data centers as thermodynamic institutions
│   ├── seed_protocol.py            # Stdlib-only octahedral seed expansion, 21-byte packets, mesh
│   ├── seed_mesh.py                # City resilience mesh bridge — grid failure simulation
│   ├── field_system.py             # Rule-field engine — regen capacity, drift, ecological coupling
│   ├── ai_delusion_checker.py      # Systemic assumption detector — Six Sigma audit, S_e=0 forcing
│   ├── crisis_geology.py           # Crisis geology modeling — rock formation as constraint
│   ├── crisis_topology.py          # Network failure cascades and topological resilience
│   ├── dissipative_systems.py      # Prigogine-inspired dissipative structure modeling
│   ├── energy_taxonomy.py          # Energy type classification
│   ├── fidelity_accounting.py      # Fidelity-based accounting
│   ├── geometric_coupling_optimizer.py  # Geometric coupling optimization
│   ├── geometric_exploration.py    # Octahedral field structure exploration
│   ├── innovation_engine.py        # Innovation engine modeling
│   ├── innovation_engine_recycling.py      # Recycling-focused innovation
│   ├── innovation_engine_recycling_full.py # Full recycling innovation engine
│   ├── inversion_tools.py          # Inversion analysis tools
│   ├── physical_coupling_matrix.py # Cross-domain interaction strengths
│   ├── resource_flow_dynamics.py   # Resource flow modeling
│   ├── system_weaver.py            # System integration weaver
│   ├── urban_grid.py               # Urban grid spatial network modeling
│   ├── cities/
│   │   ├── madison_wi.py           # Madison, WI city model — build_madison()
│   │   └── coupling.py             # Cross-domain coupling terms + knowledge decay clocks
│   ├── domains/
│   │   ├── soil_regeneration.py    # Soil as substrate; knowledge holder age as countdown
│   │   ├── incentive_alignment.py  # Incentives as infrastructure
│   │   └── triage_layer.py         # Financial vs thermodynamic triage comparison
│   ├── visualizations/
│   │   ├── energy_topology.jsx     # Energy topology React visualization
│   │   └── README.md
│   ├── docs/
│   │   ├── physics.py              # Physics constraint utilities
│   │   └── prayer_index.md
│   ├── Charter.md                  # Layer Zero Charter
│   ├── Purpose.md                  # Criticality tier framework
│   ├── Urban_Resilience.md         # Framework summary
│   ├── suburban_tax_flow.md        # Suburban tax flow analysis
│   ├── madison_austin_comparison.md # City comparison
│   └── datacenter_net0.md          # Data center net-zero docs
├── KnowledgeDNA/                   # Knowledge ancestry and substrate reasoning
│   ├── knowledge_dna.py            # Knowledge as field propagation — channel coupling, dormancy
│   ├── equation_field.py           # 14 equations × 15 domains, overlap scoring, bridge discovery
│   ├── substrate.py                # Substrate-first reasoning — decompose to physics
│   ├── geobin_bridge.py            # GEIS vertex bits ↔ substrate properties bridge
│   ├── living_intelligence.py      # Living Intelligence Database connector — 38 teachers
│   └── seed_data.csv               # Seed reference data
├── GoatHerd/                       # Village goat herding assistant
│   └── herd.py                     # Logistic growth, zone scoring, grazing rotation
├── Rescue/                         # Rescue coordination
│   ├── rescue.py                   # Resource allocation under crisis
│   └── energy_efficient_ai.py      # Energy-efficient AI for rescue operations
├── SAR/                            # Search and Rescue drone coordination
│   ├── workflow_bridge.py          # Stdlib-only geometric swarm with 3D allocation
│   ├── mobius_swarm.py             # Möbius swarm coordination
│   ├── swarm_bridge.py             # Swarm-to-system bridge
│   └── SeaFrost/                   # Maritime firefighting digital twin
│       ├── digital_twin.py         # Ship digital twin engine
│       └── maersk_fire_test.py     # Maersk C204 fire scenario test
├── octahedral-nfs/                 # Octahedral number field sieve
│   ├── src/                        # NFS pipeline (factor base, matrix, nullspace, etc.)
│   ├── examples/                   # Example factorizations
│   └── hardware/                   # Hardware detection for phone-optimized scaling
├── Models/
│   ├── food-resilience.py          # Michaelis-Menten yield + ENSO forcing
│   ├── Time-resource.py            # Time-resource modeling — REQUIRES NumPy
│   └── *.md                        # Food system, community, physics-first AI docs
├── Dashboard/
│   ├── Routing-ops.md              # Routing operations (30KB)
│   └── Routing-resilience.md       # Routing resilience (38KB)
├── PhysicsGuard/
│   └── README.md                   # Semantic-to-physical constraint translator
├── fieldlink.json                  # Cross-repo dependency manifest (TRDAP, Seed-physics, SOMS, G2B, etc.)
├── irony.py                        # "Too complex" irony demonstration
├── run.py                          # Root-level run script
├── Food-resiliency.jsx             # Interactive food resilience simulation
├── NVC-game theory-sim.jsx         # NVC game theory simulation
├── README.md                       # Master overview (28KB)
├── SYSTEM_MAP.md                   # 5-layer architecture diagram
├── Sovereign.md                    # Foundational framework (39KB)
├── Field-manual.md                 # Practical field manual
├── Fix.md                          # Fix documentation
├── GPU.md                          # GPU considerations
├── nutrient-cascade.md             # Nutrient cascade model
├── combine-cognition.md            # Combine cognition framework
├── game-theory-proofs.md           # 13 game theory axiom failure proofs
├── thermodynamics-institutional-analysis.md
├── communication-infrastructure.md # CB/LoRa/HAM mesh network design
├── Camouflage-network.md           # Network camouflage concepts
├── Fats-communication.md           # Fats and communication systems
├── Calories_and_water.md           # Caloric and water modeling
└── Urban_food_resilience.md        # Urban food resilience
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
  seed_protocol.py       — stdlib-only octahedral seed expansion + 21-byte mesh packets
  seed_mesh.py           — city resilience mesh bridge — grid failure simulation
  field_system.py        — rule-field engine: regen capacity, drift, g(k) coupling
  ai_delusion_checker.py — systemic assumption detection + Six Sigma audit (S_e=0)
  crisis_geology.py      — geological substrate as infrastructure constraint
  crisis_topology.py     — network failure cascades + topological resilience
  dissipative_systems.py — Prigogine dissipative structure modeling
  energy_taxonomy.py     — energy type classification
  fidelity_accounting.py — fidelity-based accounting
  geometric_coupling_optimizer.py — geometric coupling optimization
  geometric_exploration.py — octahedral field exploration
  innovation_engine.py   — innovation modeling engine
  inversion_tools.py     — inversion analysis tools
  physical_coupling_matrix.py — cross-domain coupling strengths
  resource_flow_dynamics.py — resource flow modeling
  system_weaver.py       — system integration weaver
  urban_grid.py          — urban grid spatial network
  cities/coupling.py     — multi-domain shock propagation + knowledge decay clocks
  domains/soil_regeneration.py — soil as substrate; knowledge holder age as countdown
  domains/incentive_alignment.py — incentives as infrastructure
  domains/triage_layer.py — financial vs thermodynamic triage comparison

Top-level packages (outside sim/):
  KnowledgeDNA/          — knowledge ancestry, equation fields, substrate reasoning, geobin bridge
  GoatHerd/              — village goat herding assistant (logistic growth, zone scoring)
  Rescue/                — rescue coordination + energy-efficient AI
  SAR/                   — search & rescue drone coordination, SeaFrost maritime digital twin
  octahedral-nfs/        — number field sieve via octahedral geometry
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

## Cross-Repository Ecosystem

This repo is part of a connected ecosystem managed via `fieldlink.json`. Key connections:

| Repo | Relation | Shared Entities |
|------|----------|----------------|
| [Seed-physics](https://github.com/JinnZ2/Seed-physics) | NumPy reference for seed expansion | `SEED.EXPANSION_RULES`, `SEED.OCTAHEDRAL_DIRS` |
| [SOMS](https://github.com/JinnZ2/Sovereign-Octahedral-Mandala-Substrate-SOMS-) | Octahedral substrate compute | `SOMS.OCTAHEDRAL_PHYSICS`, `SOMS.PHI_CALCULATOR`, `SOMS.FRET_COUPLING` |
| [Geometric-to-Binary](https://github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge) | GEIS encoding bridge | `GEIS.ENCODING`, `SHAPE.OCTA`, `CONST.PHI` |
| [TRDAP](https://github.com/JinnZ2/TRDAP) | Transport resilience protocol | `TRDAP.CORRIDOR_DATA`, `TRDAP.ROUTE_OBSERVATION` |
| [BE2-communication](https://github.com/JinnZ2/BE2-communication) | BT/BLE mesh transport | `BE2.BLE_MESH_TRANSPORT`, `BE2.EMERGENCY_REACH` |
| [Living-Intelligence-Database](https://github.com/JinnZ2/Living-Intelligence-Database) | Knowledge teacher ontology | `INTELLIGENCE.*` (38 teachers) |
| [Universal-Redesign-Algorithm](https://github.com/JinnZ2/Universal-Redesign-Algorithm-) | Bio-hybrid redesign | `URA.REDESIGN_SCHEMA`, `URA.STRESS_POINTS` |
| [Mandala-Computing](https://github.com/JinnZ2/Mandala-Computing) | Mandala computation | `SHAPE.OCTA`, `CONST.PHI` |
| [Rosetta-Shape-Core](https://github.com/JinnZ2/Rosetta-Shape-Core) | Shape ontology | `SHAPE.OCTAHEDRON`, `BRIDGE.ROSETTA` |

### Key Bridges

- **sim/seed_protocol.py** is the stdlib port of Seed-physics (no NumPy)
- **KnowledgeDNA/geobin_bridge.py** bridges Geometric-to-Binary ↔ substrate properties
- **octahedral-nfs/** extends SOMS octahedral concepts to number field sieve factorization
- **sim/field_system.py** + **sim/ai_delusion_checker.py** provide the rule-field engine and Six Sigma audit referenced in the ecological coupling analysis

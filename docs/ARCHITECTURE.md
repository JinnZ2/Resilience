# Architecture

Deep design reference. Read this when making structural changes.

## 5-Layer Architecture (see `SYSTEM_MAP.md`)

- **Layer 0 — Ground Truth:** Direct physical observation (the sensor)
- **Layer 1 — Dynamic Models:** Food system, nutrient cascade, institutional behavior
- **Layer 2 — Structural Analysis:** Thermodynamic analysis, game theory proofs
- **Layer 3 — Tools:** PhysicsGuard, Combine Cognition
- **Layer 4 — Ground Application:** Corridor mapping (Superior→Tomah)
- **Layer 5 — Meta:** Relational knowledge encoding

## Core Thesis

`T_drive < τ_adapt` — external forcing frequency exceeds internal adaptation timescale, and the gap is widening. This is modeled as a thermodynamic trap.

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

Most other modules are self-contained domain models not imported by the entry point. Several use `try/except` sibling imports for optional integration.

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

## Design Principles

1. **Preserve coupling terms.** The connections between domains (food↔energy↔logistics↔nutrition↔cognition) are the primary contribution. Never model domains in isolation.
2. **Physics constraints are non-negotiable.** Energy balance, conservation laws, and thermodynamic limits are enforced explicitly. Use `PhysicsGuard/` concepts and `sim/docs/physics.py`.
3. **No external dependencies.** The codebase is designed to function in degraded infrastructure scenarios. Do not add pip packages.
4. **Relational knowledge over propositional.** Knowledge is stored as relationships between systems, not isolated facts. Preserve cross-references and coupling terms.
5. **Ground truth calibration.** Models stay coupled to physical reality through direct observation data.

## Module Tiers

- **core** — Entry point and shared data structures — always relevant
- **domain** — Standalone domain models — topic-specific, run independently
- **bridge** — Cross-repo or cross-package connectors
- **tool** — Utilities and analyzers
- **demo** — Example scenarios and city models

See `sim/INDEX.json` for the complete machine-readable module registry.

## Known Issues

1. **Many modules are standalone:** Most Python files beyond the core import chain define models but are not wired into the simulation entry point. Several have their own builder functions (e.g., `build_madison_v2()`, `build_city_1000()`, `build_madison_economics()`).
2. **`Models/Time-resource.py` uses NumPy:** The only file in the repo with an external dependency (`import numpy`). All other Python is stdlib-only.

## Testing

There is no formal test suite. Validation is done through:
- Physical/thermodynamic constraint checking (PhysicsGuard approach)
- Running simulation scenarios via `python -m sim.run`
- Manual verification against ground-truth observations
- Runnable modules have `if __name__ == "__main__"` demos

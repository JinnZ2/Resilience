# Cross-Repository Ecosystem

This repo is part of a connected ecosystem managed via `fieldlink.json`.

## Linked Repositories

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
| [BioGrid2.0](https://github.com/JinnZ2/BioGrid2.0) | Biological grid patterns | `BIOGRID.ATLAS` |

## Key Bridges

- **sim/seed_protocol.py** is the stdlib port of Seed-physics (no NumPy)
- **KnowledgeDNA/geobin_bridge.py** bridges Geometric-to-Binary ↔ substrate properties
- **octahedral-nfs/** extends SOMS octahedral concepts to number field sieve factorization
- **sim/field_system.py** + **sim/ai_delusion_checker.py** provide the rule-field engine and Six Sigma audit

## Entity Flow Direction

```
Seed-physics ──SEED.EXPANSION_RULES──▶ sim/seed_protocol.py (stdlib port)
SOMS ──SOMS.OCTAHEDRAL_PHYSICS──▶ octahedral-nfs/, sim/geometric_exploration.py
G2B ──GEIS.ENCODING──▶ KnowledgeDNA/geobin_bridge.py ──▶ SUBSTRATE.PROPERTY_VECTOR
TRDAP ──CORRIDOR_DATA──▶ sim/cities/madison_wi.py (ground truth calibration)
Living-Intelligence ──INTELLIGENCE.*──▶ KnowledgeDNA/living_intelligence.py
```

## Fieldlink Protocol

The `fieldlink.json` file defines:
- **sources**: external repos with direction (bidirectional/inbound)
- **local_modules**: what this repo provides
- **entity_map**: how external entities map to local substrate properties
- **merge order**: priority for deep-merge conflict resolution
- **consent**: licensing and sharing permissions

To clone external sources for full integration:
```bash
git clone https://github.com/JinnZ2/Seed-physics.git
git clone https://github.com/JinnZ2/Sovereign-Octahedral-Mandala-Substrate-SOMS-.git
git clone https://github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge.git
git clone https://github.com/JinnZ2/TRDAP.git
```

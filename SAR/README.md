# SAR — Search and Rescue Coordination System

Geometric swarm coordination for search and rescue operations.
Icosahedral state encoding, dodecahedral parity checking, and nautilus
spiral resource allocation.

CC0 public domain.

## Overview

This module provides three layers:

1. **WorkflowBridge** — generic geometric pipeline for any vectorized input
2. **SARSwarm** — drone swarm adapter for blizzard/rubble SAR operations
3. **SeaFrostWolfPack** — 4-drone wolf pack for maritime lithium battery fires

The core idea: map high-dimensional sensor data to discrete states on an
icosahedron (12 vertices, 30 edges). Transitions between non-adjacent
vertices are forbidden. Sequences are validated against the dual
dodecahedron. Invalid state trajectories trigger backtrack recovery.
Resource allocation uses a golden-angle nautilus spiral.

## Files

```
SAR/
├── workflow_bridge.py        # Stdlib-only core (no dependencies)
├── swarm_bridge.py           # MAVLink adapter (requires pymavlink)
├── mobius_swarm.py            # Tension-protected swarm (requires numpy)
├── SeaFrost/
│   ├── digital_twin.py       # Ship blueprint parser (stdlib only)
│   ├── maersk_fire_test.py   # Maersk C-204 fire suppression test
│   ├── sitl_seafrost.sh      # ArduPilot SITL launch script
│   └── README.md             # SeaFrost technical details
└── Claude-todo.md            # Design notes and future work
```

## Quick Start

The stdlib version runs anywhere Python 3 is available:

```bash
python SAR/workflow_bridge.py
```

This runs three demos:
- Core abstraction: 4 test vectors through the geometric pipeline
- Blizzard SAR: 50-drone simulation with 3% dropout rate
- SeaFrost: wolf pack fire suppression sequence

The SeaFrost integration test:

```bash
python SAR/SeaFrost/maersk_fire_test.py
```

## Architecture

### Geometric Pipeline

```
Input Vector (any dimension)
    |
    v
Icosahedral Projection (nearest of 12 vertices)
    |
    v
Adjacency Check (only neighbor transitions allowed)
    |
    v
Nibble Encoding (4-bit state code)
    |
    v
Dodecahedral Parity (5-nibble closed walk check)
    |                              |
    v                              v
  VALID                         ERROR
    |                              |
    v                              v
Spiral Allocation             Backtrack Recovery
(golden-angle placement)    (restore last known good state)
```

### State Encoding

Each input vector maps to one of 12 icosahedral vertices. The 4-bit
nibble identifies which vertex. Adjacency constrains transitions:
vertex 0 connects to [1, 2, 4, 6, 8], vertex 1 connects to
[0, 2, 5, 6, 7], and so on. A transition to a non-adjacent vertex
is redirected to the nearest valid neighbor.

### Parity Checking

Every 5 transitions, the nibble sequence is validated as a walk on the
dodecahedron (dual of the icosahedron). If the walk returns to its
starting face, the sequence is valid. If not, the state trajectory
contains an inconsistency.

Parity is a health metric, not a gate. Single failures are normal with
diverse inputs. Three consecutive failures trigger backtrack recovery.

### Nautilus Spiral Allocation

Resources (drone waypoints, task slots, scan positions) are placed using
a golden-angle spiral. The golden angle (137.5 degrees) ensures uniform
coverage without overlap. Load-aware scaling contracts the spiral under
high stress. Survivor detection expands local coverage.

### Fault Tolerance

Before every state transition, the engine snapshots its current state
(position, last vertex, parity buffer) onto a backtrack stack. On
sustained parity failure, the engine pops the stack and restores the
last known good state. This is how the system achieves recovery under
drone dropout: the geometry remembers where you were.

## SAR Telemetry Format

The SARSwarm adapter expects a 5-element vector per drone per cycle:

| Index | Field        | Range | Meaning                   |
|-------|-------------|-------|---------------------------|
| 0     | health      | 0-1   | 0 = dropout, 1 = nominal  |
| 1     | alt_norm    | 0-1   | Normalized altitude        |
| 2     | battery     | 0-1   | Remaining charge           |
| 3     | thermal     | 0-1   | >0.7 = potential survivor  |
| 4     | wind_load   | 0-1   | Wind stress on formation   |

Short vectors are zero-padded automatically.

## SeaFrost Wolf Pack

Four-drone formation for lithium battery fire suppression on ships:

| Drone | Role   | Payload      | Sequence       |
|-------|--------|-------------|----------------|
| 0     | Alpha  | Thermal scan | T+0s: recon    |
| 1     | Beta1  | CO2 burst    | T+15s: pre-cool |
| 2     | Beta2  | CO2 burst    | T+15s: pre-cool |
| 3     | Gamma  | LN2 flood    | T+30s: kill    |

Staged cooling: 1000C -> 400C (CO2) -> -20C (LN2) in 45 seconds.
Ship digital twin pre-calculates flight paths from vessel blueprints.

## Dependencies

| File               | Dependencies          | Notes                          |
|--------------------|-----------------------|--------------------------------|
| workflow_bridge.py | None (stdlib only)    | Core logic, runs anywhere      |
| digital_twin.py    | None (stdlib only)    | Ship blueprint parser          |
| maersk_fire_test.py| None (stdlib only)    | Uses workflow_bridge + digital_twin |
| swarm_bridge.py    | pymavlink             | Live MAVLink telemetry         |
| mobius_swarm.py     | numpy                 | Tension-protected formation    |

The stdlib files run on any system with Python 3.
The MAVLink and numpy files are for hardware integration.

## Simulation Results

50-drone blizzard SAR, 500 cycles, 3% dropout rate:

```
24,237 nodes allocated
1,924 survivor detections
8,077 backtrack recoveries
```

SeaFrost Maersk C-204 test:

```
45 seconds alarm-to-suppression
4 drones, staged cooling
Pre-calculated paths from ship digital twin
```

## Waypoint Export

Two output formats for integration with flight controllers:

- **CSV**: `index,x_meters,y_meters,alt_meters,load` — for any tool
- **QGC WPL 110**: Mission Planner / QGroundControl native format

```python
swarm.export("mavlink", origin_lat=44.76, origin_lon=-89.13,
             filename="mission.txt")
```

## Known Limitations

- Parity check returns low pass rates when all inputs are similar
  (expected: uniform inputs produce uniform walks that rarely close).
  Real deployments with spatial diversity produce higher parity.
- MAVLink adapter (`swarm_bridge.py`) has not been tested against
  live ArduPilot hardware.

## Related Modules

- `sim/seed_protocol.py` — seed encoding and mesh networking (stdlib only)
- `sim/seed_mesh.py` — city resilience mesh bridge for grid failure
- `sim/cities/coupling.py` — cross-domain shock propagation model

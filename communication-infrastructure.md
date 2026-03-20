# Communication Infrastructure: Corridor Mesh Network

CB radio, LoRa, and HAM mesh network design for the Superior-to-Tomah corridor.
Provides communication continuity when cellular and internet infrastructure degrades.

## Why This Exists

```
CURRENT CORRIDOR COMMUNICATION:

  Cell towers ──► single provider in many areas
  Internet   ──► cable/DSL, single path in rural zones
  Emergency  ──► 911 depends on cell/landline
  
  ALL THREE share failure modes:
    - grid power dependency
    - backhaul fiber cuts
    - tower site access in severe weather
    - carrier business decisions (tower decommission)

  One ice storm or one business decision
  can take out communication for thousands.
```

## Three-Layer Mesh Design

```
LAYER 1: CB RADIO (immediate, no infrastructure)
  - Range: 5-15 miles (terrain dependent)
  - Power: 12V vehicle battery, 4W
  - License: none required
  - Deployment: every truck, farm, residence with radio
  - Role: emergency coordination, local awareness

LAYER 2: LoRa MESH (data, low power, long range)
  - Range: 5-10 miles per node (rural line-of-sight)
  - Power: solar + battery, <1W
  - License: ISM band, no license
  - Deployment: fixed nodes at identified locations
  - Role: text messaging, sensor data, status reporting

LAYER 3: HAM RADIO (regional, high power, skilled operators)
  - Range: 50+ miles (HF: continental)
  - Power: 12V-48V, 5-100W
  - License: FCC amateur license required
  - Deployment: identified operators in corridor
  - Role: regional coordination, external communication
```

## Identified Node Locations

Ground-surveyed locations along the corridor optimized for:
- Terrain elevation (radio propagation)
- Power availability (grid + solar potential)
- Physical access in severe weather
- Proximity to population centers
- Redundancy (overlapping coverage)

Specific locations documented through driving observation.

## Connection to Repository

Communication is the nervous system of the corridor.
Without it, the food system model's adaptation mechanisms (D_t feedback,
price signals, coordination) cannot function. The institutional analysis
shows which entities can coordinate response — but only if they can
communicate. The knowledge holders can only share knowledge if
transmission paths exist.

This layer is infrastructure for everything else in the repository.

CC0. No rights reserved.

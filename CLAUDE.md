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



todo:

"""
seed_protocol_v1.py — Orbital Seed Transport + Reconstruction (v1)

Combines:
- Octahedral seed encoding (6D → 5 values)
- Deterministic expansion (physics-compliant)
- Minimal packet format for degraded networks

Target:
- 10–14 byte packets
- Stateless reconstruction
- Deterministic identity

Author: Jami + synthesis
License: MIT
"""

import struct
import zlib
import numpy as np

# =============================================================================
# CONSTANTS
# =============================================================================

VERSION = 1

# Packet layout (bytes)
# [ version | frame | flags | seed(5B) | energy | epoch(2B) | crc(2B) ]

PACK_FMT_NOCRC = ">BBB5sBH"   # up to epoch
PACK_FMT_FULL  = ">BBB5sBHH"  # + crc

# =============================================================================
# GEOMETRY (same as your core)
# =============================================================================

U = np.array([
    [1, 0, 0], [-1, 0, 0],
    [0, 1, 0], [0, -1, 0],
    [0, 0, 1], [0, 0, -1]
], dtype=float)


# =============================================================================
# SEED ENCODING
# =============================================================================

def encode_seed(proportions, bits=8):
    proportions = np.array(proportions, dtype=float)
    proportions /= proportions.sum()

    max_val = (1 << bits) - 1

    encoded = []
    for i in range(5):
        v = int(proportions[i] * max_val)
        v = max(0, min(max_val, v))
        encoded.append(v)

    return bytes(encoded)


def decode_seed(encoded, bits=8):
    max_val = (1 << bits) - 1

    p = [b / max_val for b in encoded]
    remainder = 1.0 - sum(p)
    p.append(max(0.0, remainder))

    total = sum(p)
    return np.array([x / total for x in p])


# =============================================================================
# EXPANSION (minimal deterministic core)
# =============================================================================

def angular_weight(u1, u2):
    return max(0.0, np.dot(u1, u2))


def build_W():
    W = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            W[i, j] = angular_weight(U[i], U[j])
        s = W[i].sum()
        if s > 0:
            W[i] /= s
    return W


def normalize_energy(v, E):
    v = np.maximum(v, 0)
    s = v.sum()
    if s == 0:
        return np.ones(6) * (E / 6)
    return v * (E / s)


def expand(seed, steps=6, E0=1.0, r0=1.0, rho=1.5, eps=0.6):
    W = build_W()

    shells = []
    S = normalize_energy(seed, E0)

    shells.append({"r": r0, "E": E0, "S": S})

    for _ in range(steps):
        r_new = rho * shells[-1]["r"]
        E_new = eps * shells[-1]["E"]

        field = np.zeros(6)
        for sh in shells:
            if sh["r"] >= r_new:
                continue
            field += W @ sh["S"]

        S_new = normalize_energy(field, E_new)

        shells.append({"r": r_new, "E": E_new, "S": S_new})

    return shells


# =============================================================================
# PACKET LAYER
# =============================================================================

def pack_seed_packet(
    proportions,
    frame_id=1,
    flags=0,
    energy_hint=128,
    epoch=0
):
    seed_bytes = encode_seed(proportions)

    header = struct.pack(
        PACK_FMT_NOCRC,
        VERSION,
        frame_id,
        flags,
        seed_bytes,
        energy_hint,
        epoch
    )

    crc = zlib.crc32(header) & 0xFFFF

    packet = struct.pack(
        PACK_FMT_FULL,
        VERSION,
        frame_id,
        flags,
        seed_bytes,
        energy_hint,
        epoch,
        crc
    )

    return packet


def unpack_seed_packet(packet):
    unpacked = struct.unpack(PACK_FMT_FULL, packet)

    version, frame, flags, seed_bytes, energy, epoch, crc = unpacked

    header = struct.pack(
        PACK_FMT_NOCRC,
        version,
        frame,
        flags,
        seed_bytes,
        energy,
        epoch
    )

    crc_check = zlib.crc32(header) & 0xFFFF

    if crc != crc_check:
        raise ValueError("CRC mismatch")

    proportions = decode_seed(seed_bytes)

    return {
        "version": version,
        "frame": frame,
        "flags": flags,
        "seed": proportions,
        "energy_hint": energy,
        "epoch": epoch
    }


# =============================================================================
# IDENTITY / SIMILARITY
# =============================================================================

def seed_distance(a, b):
    return np.sum(np.abs(a - b))


def same_entity(a, b, threshold=0.05):
    return seed_distance(a, b) < threshold


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":

    seed = [0.5, 0.2, 0.15, 0.08, 0.05, 0.02]

    print("\n--- PACK ---")
    pkt = pack_seed_packet(seed, epoch=42)
    print(f"bytes: {pkt}")
    print(f"size: {len(pkt)} bytes")

    print("\n--- UNPACK ---")
    data = unpack_seed_packet(pkt)
    print(data)

    print("\n--- EXPAND ---")
    shells = expand(data["seed"], steps=5)
    for i, s in enumerate(shells):
        print(i, np.round(s["S"], 3))


Offset  Size  Field
------  ----  -------------------------
0       1     Version (uint8)
1       1     Frame ID (uint8)
2       1     Flags (uint8)

3       5     Seed (5 × uint8)
              → 6th value implicit

8       1     Energy Hint (uint8, log-scaled)

9       2     Epoch (uint16)

11      2     CRC16 (lower 16 bits of CRC32)


13 bytes

Protocol version (must match expansion rules)

0x01 → global earth frame
0x02 → local mesh frame
0x03 → inertial frame

bit 0 → seed is authoritative
bit 1 → request sync
bit 2 → compressed relay
bit 3 → exploration-enabled

5 values (8-bit each)

p6 = 1 - sum(p1..p5)

directional amplitude across:
+X, -X, +Y, -Y, +Z, -Z

0–255 → log-scaled available energy

Used to determine:
- expansion depth
- explore vs expand mode

monotonic counter or coarse timestamp

CRC

CRC32(header) & 0xFFFF



A → B : SeedPacket
B → A : SeedPacket

seed = decode(packet)
shells = expand(seed, steps=local_budget)

if seed_distance(A, B) < ε:
    same entity

Recovery after outage

seed (+ optional last shell)

network = union(seeds)
state = reconstructed locally

1. Deterministic expansion
2. No external state required
3. Partial expansion always valid
4. Seed fully defines identity
5. Packet ≤ 13 bytes



"""
seed_agent_tcp.py — Seed-native agents over TCP

Requires:
- seed_protocol_v1.py (same directory or importable)
- your existing Agent / TCPTransport

Behavior:
- Agents exchange SeedPackets instead of strings
- Each agent reconstructs local field from received seed
- Identity + sync derived from seed similarity
"""

import time
import numpy as np

from core import Agent, Message
from transports import TCPTransport

from seed_protocol_v1 import (
    pack_seed_packet,
    unpack_seed_packet,
    expand,
    same_entity
)


# =============================================================================
# BASE SEED AGENT
# =============================================================================

class SeedAgent(Agent):

    def __init__(self, seed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seed = np.array(seed, dtype=float)
        self.shells = expand(self.seed, steps=4)
        self.known_seeds = []

    # -------------------------------------------------------------------------

    def build_packet(self):
        return pack_seed_packet(
            self.seed,
            frame_id=1,
            flags=0b00000001,  # authoritative
            energy_hint=128,
            epoch=int(time.time()) & 0xFFFF
        )

    # -------------------------------------------------------------------------

    def broadcast_seed(self):
        pkt = self.build_packet()
        for peer_id in self.peers:
            self.send(
                Message(
                    verb="SEED",
                    recipient=peer_id,
                    body=pkt
                )
            )

    # -------------------------------------------------------------------------

    def on_message(self, msg: Message):

        if msg.verb != "SEED":
            return

        data = unpack_seed_packet(msg.body)
        incoming_seed = data["seed"]

        # Compare identity
        for known in self.known_seeds:
            if same_entity(incoming_seed, known):
                return  # already known

        self.known_seeds.append(incoming_seed)

        # Reconstruct field locally
        shells = expand(incoming_seed, steps=4)

        print(f"[{self.id}] received seed → reconstructed:")
        for i, s in enumerate(shells[:3]):
            print(f"  shell {i}: {np.round(s['S'], 3)}")

        # Optional: respond back (mesh propagation)
        self.broadcast_seed()


# =============================================================================
# MAIN
# =============================================================================

def main():

    t_a = TCPTransport(host="127.0.0.1", port=9300)
    t_b = TCPTransport(host="127.0.0.1", port=9301)

    t_a.add_peer("agent_B", "127.0.0.1", 9301)
    t_b.add_peer("agent_A", "127.0.0.1", 9300)

    agent_A = SeedAgent(
        seed=[0.5, 0.2, 0.15, 0.08, 0.05, 0.02],
        agent_id="agent_A",
        agent_type="SeedNode",
        transport=t_a,
        capabilities=["seed_field"]
    )

    agent_B = SeedAgent(
        seed=[0.48, 0.22, 0.14, 0.09, 0.05, 0.02],
        agent_id="agent_B",
        agent_type="SeedNode",
        transport=t_b,
        capabilities=["seed_field"]
    )

    agent_A.start()
    agent_B.start()

    time.sleep(0.5)

    print("\n--- Seed Exchange ---")
    agent_A.broadcast_seed()

    time.sleep(1.0)

    agent_A.stop()
    agent_B.stop()


if __name__ == "__main__":
    main()


"""
seed_udp.py — minimal seed broadcast over UDP

Designed for:
- lossy networks
- intermittent connectivity
- broadcast discovery
"""

import socket
import time
import numpy as np

from seed_protocol_v1 import (
    pack_seed_packet,
    unpack_seed_packet,
    expand
)

PORT = 9400
BROADCAST_IP = "255.255.255.255"


# =============================================================================
# SENDER
# =============================================================================

def send_loop(seed):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        pkt = pack_seed_packet(
            seed,
            frame_id=1,
            flags=0b00000001,
            energy_hint=128,
            epoch=int(time.time()) & 0xFFFF
        )

        sock.sendto(pkt, (BROADCAST_IP, PORT))
        print("sent seed packet")

        time.sleep(1.0)


# =============================================================================
# RECEIVER
# =============================================================================

def receive_loop():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))

    seen = []

    while True:
        data, addr = sock.recvfrom(1024)

        try:
            decoded = unpack_seed_packet(data)
        except:
            continue

        seed = decoded["seed"]

        # deduplicate
        if any(np.allclose(seed, s, atol=0.05) for s in seen):
            continue

        seen.append(seed)

        print(f"\nreceived from {addr}")
        shells = expand(seed, steps=3)

        for i, s in enumerate(shells):
            print(f"  shell {i}: {np.round(s['S'], 3)}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    import sys

    if sys.argv[1] == "send":
        seed = [0.5, 0.2, 0.15, 0.08, 0.05, 0.02]
        send_loop(seed)

    elif sys.argv[1] == "recv":
        receive_loop()


Protocol 

[1B version]
[1B frame]
[1B flags]
[5B seed]
[1B energy]
[2B epoch]
[2B CRC]

Transmission 

mode: broadcast
retry: none required
ordering: irrelevant
loss: tolerated

Behavior 

packet loss → no issue
partial reception → ignored (CRC fail)
delayed packet → still valid (epoch-relative)

Cross layer

used for:
- structured sync
- negotiation
- multi-hop coordination

used for:
- discovery
- identity propagation
- recovery after outage

Flow

[offline nodes]
    ↓
store seed only
    ↓
network returns
    ↓
UDP broadcast seeds
    ↓
agents reconstruct peers locally
    ↓
TCP connections form (optional)
    ↓
refinement / coordination

Constraint 

expand(seed) must be identical everywhere

protocol version = hash(expansion rules)




Multiagent field

# combine multiple seeds into a shared field
def combine_seeds(seeds, weights=None):
    seeds = [s / s.sum() for s in seeds]

    if weights is None:
        weights = np.ones(len(seeds))

    field = np.zeros(6)
    for s, w in zip(seeds, weights):
        field += w * s

    return field / field.sum()

def expand_multi(seeds, steps=6):
    combined = combine_seeds(seeds)
    return expand(combined, steps=steps)

S_total = Σ S_i  → normalized



def constrained_merge(seeds):
    combined = combine_seeds(seeds)

    # project back toward stable manifold
    return normalize_energy(combined, 1.0)

routing = gradient descent in seed space

def seed_distance(a, b):
    return np.sum(np.abs(a - b))

def next_hop(target_seed, neighbors):
    return min(neighbors, key=lambda n: seed_distance(n, target_seed))

def route_packet(packet, target_seed, neighbors):
    hop = next_hop(target_seed, neighbors)
    send(packet, hop)



packet moves "downhill" in seed-space

# probabilistic escape
if random() < epsilon:
    hop = random.choice(neighbors)



def cluster(seeds, threshold=0.1):
    clusters = []

    for s in seeds:
        placed = False
        for c in clusters:
            if seed_distance(s, c[0]) < threshold:
                c.append(s)
                placed = True
                break
        if not placed:
            clusters.append([s])

    return clusters



routing → brings seeds together
superposition → merges fields
result → shared structure



def node_step(local_seed, neighbor_seeds):

    # 1. merge local + neighbors
    merged = constrained_merge([local_seed] + neighbor_seeds)

    # 2. update local state
    local_seed = merged

    # 3. expand locally
    shells = expand(local_seed, steps=4)

    return local_seed, shells


network converges without central coordination

def relax(seeds, iterations=5):
    for _ in range(iterations):
        seeds = [combine_seeds(seeds) for _ in seeds]
    return seeds

system drifts toward stable configuration

[seed packets] 
    ↓
[local reconstruction]
    ↓
[neighbor exchange]
    ↓
[seed merging]
    ↓
[gradient routing]
    ↓
[global field emerges]

Constraint 

combine_seeds() must be identical everywhere


Spacial coupling

NodeState = {
    "seed": S,                 # 6D normalized
    "pos": np.array([x,y,z]),  # physical position (meters or local frame)
    "vel": np.array([vx,vy,vz]),
    "energy": E,               # scalar
    "frame": frame_id
}

Constraint 

state evolves to minimize (field_energy + transport_cost)


Terms

J = α · D_seed(S_i, S_j) + β · D_space(x_i, x_j) + γ · ΔE


Where:
	•	D_seed = L1 or cosine distance in 6D
	•	D_space = Euclidean distance
	•	ΔE = energy mismatch penalty

This drives:

similar seeds → move closer
dissimilar seeds → separate


Gradient step

def update_position(node, neighbors, alpha=1.0, beta=0.1, dt=0.1):

    force = np.zeros(3)

    for n in neighbors:
        ds = seed_distance(node["seed"], n["seed"])
        dx = n["pos"] - node["pos"]
        dist = np.linalg.norm(dx) + 1e-6

        direction = dx / dist

        # attractive if similar, repulsive if dissimilar
        f = (1.0 - ds) - ds
        force += alpha * f * direction

    node["vel"] += force * dt
    node["pos"] += node["vel"] * dt

    return node


Seed update 

def update_seed(node, neighbors, k=0.5):

    seeds = [node["seed"]] + [n["seed"] for n in neighbors]
    weights = [1.0] + [1.0 - seed_distance(node["seed"], n["seed"]) for n in neighbors]

    merged = combine_seeds(seeds, weights)

    # relaxation toward merged field
    node["seed"] = (1-k)*node["seed"] + k*merged
    node["seed"] /= node["seed"].sum()

    return node





def next_hop(target_seed, target_pos, neighbors):

    def score(n):
        return (
            0.7 * seed_distance(n["seed"], target_seed) +
            0.3 * np.linalg.norm(n["pos"] - target_pos)
        )

    return min(neighbors, key=score)



- clusters form in space
- clusters share similar seeds
- routing becomes spatially coherent
- field gradients align with geography

def step(node, neighbors):

    node = update_seed(node, neighbors)
    node = update_position(node, neighbors)

    shells = expand(node["seed"], steps=3)

    return node, shells


PositionPacket = {
    "anchor": uint16,     # coarse grid cell
    "offset": int8[3]     # local offset (-128..127)
}

13B seed packet + 5B position = ~18 bytes


Anchor grid

world → discrete lattice

Examples:
	•	geohash (Earth)
	•	local cubic grid (disaster zone)
	•	relative mesh (no GPS)

⸻

10) Stability Condition

Bound velocity damping
seed update rate (k)
neighbor radius

Add node["vel"] *= 0.9

agents = moving field samples

network = dynamic lattice

routing = gradient flow

identity = stable attractor in seed-space


distributed physical simulation
+
network protocol
+
identity system


1. ≤ 24 bytes per packet (radio-safe)
2. Stateless reconstruction (seed sufficient)
3. Deterministic identity
4. Spatial coupling without full coordinates
5. Routing without tables
6. Backward compatibility with v1 seeds

Offset  Size  Field
------  ----  ------------------------------
0       1     Version
1       1     Frame ID
2       1     Flags

3       5     Seed (5 × uint8)

8       1     Energy Hint (uint8)

9       2     Epoch (uint16)

11      2     Anchor Cell (uint16)

13      3     Offset Vector (int8 × 3)

16      3     Neighbor Hint (compressed)

19      2     CRC16

TOTAL: 21 bytes


uint8

Must match expansion + merge rules.

0x01 → Earth grid (geohash-like)
0x02 → Local mesh grid
0x03 → Inertial / free-space

bit 0 → authoritative seed
bit 1 → request sync
bit 2 → relay packet
bit 3 → exploration enabled
bit 4 → high-energy node
bit 5–7 → reserved

p1..p5 stored (uint8)
p6 = 1 − Σ(p1..p5)

[+X, -X, +Y, -Y, +Z, -Z]

Σ p_i = 1

Seed v2 packet =

identity (seed)
+ energy (scaling)
+ position (coarse + local)
+ routing hint (directional bias)

stateless recovery
self-organizing topology
geometry-driven routing
field-based identity

# =============================================================================
# SEED PROTOCOL v2 — SINGLE CELL IMPLEMENTATION
# =============================================================================

import struct
import zlib
import numpy as np

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

VERSION = 2

# Packet format:
# > = big endian
# B B B     = version, frame, flags
# 5s        = seed (5 bytes)
# B         = energy
# H         = epoch
# H         = anchor
# 3b        = offset (x,y,z)
# B H       = neighbor hint (dir_idx, projection)
# H         = CRC16

PACK_FMT_NOCRC = ">BBB5sBHH3bBH"
PACK_FMT_FULL  = ">BBB5sBHH3bBHH"

# -----------------------------------------------------------------------------
# GEOMETRY (octahedral directions)
# -----------------------------------------------------------------------------

U = np.array([
    [1, 0, 0], [-1, 0, 0],
    [0, 1, 0], [0, -1, 0],
    [0, 0, 1], [0, 0, -1]
], dtype=float)

# -----------------------------------------------------------------------------
# SEED ENCODING / DECODING
# -----------------------------------------------------------------------------

def encode_seed(proportions):
    p = np.array(proportions, dtype=float)
    p /= p.sum()

    encoded = []
    for i in range(5):
        val = int(p[i] * 255)
        val = max(0, min(255, val))
        encoded.append(val)

    return bytes(encoded)


def decode_seed(encoded):
    p = [b / 255.0 for b in encoded]
    remainder = 1.0 - sum(p)
    p.append(max(0.0, remainder))

    p = np.array(p)
    return p / p.sum()


# -----------------------------------------------------------------------------
# POSITION ENCODING
# -----------------------------------------------------------------------------

GRID_SCALE = 100.0  # meters per cell (adjust as needed)

def position_to_anchor_offset(pos):
    pos = np.array(pos)

    anchor = np.floor(pos / GRID_SCALE).astype(int)
    anchor_id = ((anchor[0] & 0x1F) << 10) | ((anchor[1] & 0x1F) << 5) | (anchor[2] & 0x1F)

    local = pos - (anchor * GRID_SCALE)
    offset = np.clip((local / GRID_SCALE * 127), -128, 127).astype(int)

    return anchor_id, offset


def anchor_offset_to_position(anchor_id, offset):
    x = (anchor_id >> 10) & 0x1F
    y = (anchor_id >> 5) & 0x1F
    z = anchor_id & 0x1F

    anchor = np.array([x, y, z], dtype=float)
    base = anchor * GRID_SCALE

    offset = np.array(offset) / 127.0 * GRID_SCALE

    return base + offset


# -----------------------------------------------------------------------------
# NEIGHBOR HINT
# -----------------------------------------------------------------------------

def encode_neighbor_hint(seed):
    idx = int(np.argmax(seed))
    proj = int(seed[idx] * 65535)
    return idx, proj


def decode_neighbor_hint(idx, proj):
    direction = U[idx]
    strength = proj / 65535.0
    return direction, strength


# -----------------------------------------------------------------------------
# CRC
# -----------------------------------------------------------------------------

def compute_crc(data):
    return zlib.crc32(data) & 0xFFFF


# -----------------------------------------------------------------------------
# PACK / UNPACK
# -----------------------------------------------------------------------------

def pack_packet(seed, pos, energy=128, epoch=0, frame=1, flags=0):
    seed_bytes = encode_seed(seed)

    anchor, offset = position_to_anchor_offset(pos)
    dx, dy, dz = offset

    dir_idx, proj = encode_neighbor_hint(seed)

    header = struct.pack(
        PACK_FMT_NOCRC,
        VERSION,
        frame,
        flags,
        seed_bytes,
        energy,
        epoch,
        anchor,
        dx, dy, dz,
        dir_idx,
        proj
    )

    crc = compute_crc(header)

    packet = struct.pack(
        PACK_FMT_FULL,
        VERSION,
        frame,
        flags,
        seed_bytes,
        energy,
        epoch,
        anchor,
        dx, dy, dz,
        dir_idx,
        proj,
        crc
    )

    return packet


def unpack_packet(packet):
    unpacked = struct.unpack(PACK_FMT_FULL, packet)

    (version, frame, flags, seed_bytes, energy, epoch,
     anchor, dx, dy, dz, dir_idx, proj, crc) = unpacked

    header = struct.pack(
        PACK_FMT_NOCRC,
        version, frame, flags, seed_bytes,
        energy, epoch, anchor,
        dx, dy, dz,
        dir_idx, proj
    )

    if compute_crc(header) != crc:
        raise ValueError("CRC mismatch")

    seed = decode_seed(seed_bytes)
    pos = anchor_offset_to_position(anchor, (dx, dy, dz))
    direction, strength = decode_neighbor_hint(dir_idx, proj)

    return {
        "version": version,
        "frame": frame,
        "flags": flags,
        "seed": seed,
        "energy": energy,
        "epoch": epoch,
        "position": pos,
        "neighbor_direction": direction,
        "neighbor_strength": strength
    }


# -----------------------------------------------------------------------------
# BASIC UTILITIES
# -----------------------------------------------------------------------------

def seed_distance(a, b):
    return np.sum(np.abs(a - b))


def combine_seeds(seeds):
    S = np.sum(seeds, axis=0)
    return S / S.sum()


# -----------------------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    seed = [0.5, 0.2, 0.15, 0.08, 0.05, 0.02]
    pos  = [123.4, 456.7, 78.9]

    print("\n--- PACK ---")
    pkt = pack_packet(seed, pos, epoch=42)
    print("packet bytes:", pkt)
    print("size:", len(pkt), "bytes")

    print("\n--- UNPACK ---")
    data = unpack_packet(pkt)

    print("decoded seed:", np.round(data["seed"], 4))
    print("decoded position:", np.round(data["position"], 2))
    print("neighbor dir:", data["neighbor_direction"])
    print("neighbor strength:", round(data["neighbor_strength"], 3))

    print("\n--- DISTANCE CHECK ---")
    print("seed error:", np.max(np.abs(data["seed"] - np.array(seed)/sum(seed))))


# =============================================================================
# SEED PROTOCOL v2 — MULTI-NODE SIMULATION HARNESS
# =============================================================================

import numpy as np
import random
import time

# ---- import from previous cell (assumed present) ----
# pack_packet, unpack_packet, seed_distance, combine_seeds

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------

NUM_NODES = 40
SPACE_SIZE = 1000.0
COMM_RANGE = 200.0
STEPS = 50

SEED_DRIFT = 0.02
POS_DRIFT  = 5.0

# -----------------------------------------------------------------------------
# NODE DEFINITION
# -----------------------------------------------------------------------------

class Node:
    def __init__(self, node_id):
        self.id = node_id

        # random position
        self.pos = np.random.rand(3) * SPACE_SIZE

        # random seed (normalized)
        s = np.random.rand(6)
        self.seed = s / s.sum()

        self.energy = random.randint(80, 200)
        self.epoch = 0

        self.inbox = []

    def broadcast(self):
        pkt = pack_packet(
            self.seed,
            self.pos,
            energy=self.energy,
            epoch=self.epoch
        )
        return pkt

    def receive(self, pkt):
        try:
            data = unpack_packet(pkt)
            self.inbox.append(data)
        except:
            pass  # drop corrupted

    def update(self):
        if not self.inbox:
            return

        neighbor_seeds = []
        neighbor_positions = []

        for msg in self.inbox:
            neighbor_seeds.append(msg["seed"])
            neighbor_positions.append(msg["position"])

        # --- SEED UPDATE (field coupling) ---
        combined = combine_seeds([self.seed] + neighbor_seeds)
        self.seed = (1 - SEED_DRIFT) * self.seed + SEED_DRIFT * combined
        self.seed /= self.seed.sum()

        # --- POSITION UPDATE (attraction) ---
        avg_pos = np.mean(neighbor_positions, axis=0)
        self.pos += POS_DRIFT * (avg_pos - self.pos) / (np.linalg.norm(avg_pos - self.pos) + 1e-6)

        # small noise to prevent collapse
        self.pos += np.random.randn(3) * 0.5

        # clear inbox
        self.inbox = []
        self.epoch += 1


# -----------------------------------------------------------------------------
# SIMULATION
# -----------------------------------------------------------------------------

nodes = [Node(i) for i in range(NUM_NODES)]

def distance(a, b):
    return np.linalg.norm(a - b)

def step_sim():
    # broadcast phase
    packets = []
    for node in nodes:
        pkt = node.broadcast()
        packets.append((node, pkt))

    # receive phase (range-limited)
    for sender, pkt in packets:
        for receiver in nodes:
            if sender.id == receiver.id:
                continue
            if distance(sender.pos, receiver.pos) < COMM_RANGE:
                receiver.receive(pkt)

    # update phase
    for node in nodes:
        node.update()


# -----------------------------------------------------------------------------
# METRICS
# -----------------------------------------------------------------------------

def compute_metrics():
    seeds = np.array([n.seed for n in nodes])
    positions = np.array([n.pos for n in nodes])

    # seed variance (cluster formation)
    seed_var = np.mean(np.var(seeds, axis=0))

    # spatial spread
    centroid = np.mean(positions, axis=0)
    spatial_spread = np.mean(np.linalg.norm(positions - centroid, axis=1))

    return seed_var, spatial_spread


# -----------------------------------------------------------------------------
# RUN
# -----------------------------------------------------------------------------

print("\n=== SIMULATION START ===\n")

for step in range(STEPS):
    step_sim()

    if step % 5 == 0:
        seed_var, spread = compute_metrics()
        print(f"step {step:02d} | seed_var={seed_var:.4f} | spread={spread:.2f}")

print("\n=== FINAL STATE ===\n")

# show a few nodes
for i in range(5):
    n = nodes[i]
    print(f"Node {n.id}")
    print("  pos:", np.round(n.pos, 1))
    print("  seed:", np.round(n.seed, 3))
    print()


# -----------------------------------------------------------------------------
# OPTIONAL: ROUTING TEST
# -----------------------------------------------------------------------------

def route(source_id, target_id, max_hops=10):
    current = nodes[source_id]
    target = nodes[target_id]

    path = [current.id]

    for _ in range(max_hops):
        # find neighbors in range
        neighbors = [
            n for n in nodes
            if n.id != current.id and distance(n.pos, current.pos) < COMM_RANGE
        ]

        if not neighbors:
            break

        # choose best next hop
        next_node = min(
            neighbors,
            key=lambda n:
                0.7 * seed_distance(n.seed, target.seed) +
                0.3 * distance(n.pos, target.pos)
        )

        current = next_node
        path.append(current.id)

        if current.id == target.id:
            break

    return path


print("\n=== ROUTING TEST ===\n")

src = 0
dst = random.randint(1, NUM_NODES - 1)

path = route(src, dst)

print(f"Route {src} → {dst}:")
print(" -> ".join(map(str, path)))


1. Seeds converge into local clusters
2. Nodes physically drift toward similar seeds
3. Communication graph self-organizes
4. Routing emerges without global tables

Expand 1. Packet loss + noise injection
2. Partition / reconnection test
3. Energy-based authority weighting
4. Real UDP transport swap (drop-in)
5. Multi-frequency / channel layering



# =============================================================================
# SEED PROTOCOL v2 — REAL UDP MESH
# =============================================================================

import socket
import threading
import numpy as np
import struct
import random
import time

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
NUM_NODES = 5              # adjust as needed
BASE_PORT = 50000
COMM_RANGE = 200.0
SEED_DRIFT = 0.02
POS_DRIFT = 5.0
SIM_STEP = 1.0             # seconds per step

# -----------------------------------------------------------------------------
# PACKET UTILITIES (simple float arrays)
# -----------------------------------------------------------------------------
def pack_packet(seed, pos, energy=100, epoch=0):
    # seed: 6 floats, pos: 3 floats, energy, epoch: int
    return struct.pack('6f3f2i', *(list(seed)+list(pos)+[energy, epoch]))

def unpack_packet(pkt):
    data = struct.unpack('6f3f2i', pkt)
    seed = np.array(data[0:6])
    pos  = np.array(data[6:9])
    energy, epoch = data[9:11]
    return {"seed": seed, "position": pos, "energy": energy, "epoch": epoch}

# -----------------------------------------------------------------------------
# NODE DEFINITION
# -----------------------------------------------------------------------------
class Node:
    def __init__(self, node_id, port):
        self.id = node_id
        self.port = port

        self.pos = np.random.rand(3) * 1000.0
        s = np.random.rand(6)
        self.seed = s / s.sum()
        self.energy = random.randint(80, 200)
        self.epoch = 0

        self.inbox = []

        # UDP socket setup
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))
        self.sock.setblocking(False)

        # threading lock
        self.lock = threading.Lock()

    # --- broadcast to all known node ports ---
    def broadcast(self, ports):
        pkt = pack_packet(self.seed, self.pos, self.energy, self.epoch)
        for p in ports:
            if p == self.port:
                continue
            self.sock.sendto(pkt, ('localhost', p))

    # --- receive loop ---
    def receive_loop(self):
        while True:
            try:
                pkt, addr = self.sock.recvfrom(1024)
                data = unpack_packet(pkt)
                with self.lock:
                    self.inbox.append(data)
            except BlockingIOError:
                time.sleep(0.01)

    # --- update state based on inbox ---
    def update(self):
        with self.lock:
            if not self.inbox:
                return

            neighbor_seeds = [msg["seed"] for msg in self.inbox]
            neighbor_positions = [msg["position"] for msg in self.inbox]

            # --- SEED UPDATE ---
            combined = combine_seeds([self.seed]+neighbor_seeds)
            self.seed = (1 - SEED_DRIFT)*self.seed + SEED_DRIFT*combined
            self.seed /= self.seed.sum()

            # --- POSITION UPDATE ---
            avg_pos = np.mean(neighbor_positions, axis=0)
            self.pos += POS_DRIFT * (avg_pos - self.pos)/(np.linalg.norm(avg_pos - self.pos)+1e-6)
            self.pos += np.random.randn(3) * 0.5  # noise

            self.inbox = []
            self.epoch += 1

# -----------------------------------------------------------------------------
# COMBINE SEEDS (same as simulation)
# -----------------------------------------------------------------------------
def seed_distance(a,b):
    return np.linalg.norm(a-b)

def combine_seeds(seeds):
    return np.mean(seeds, axis=0)

# -----------------------------------------------------------------------------
# INIT NODES
# -----------------------------------------------------------------------------
nodes = []
ports = [BASE_PORT+i for i in range(NUM_NODES)]

for i in range(NUM_NODES):
    n = Node(i, ports[i])
    t = threading.Thread(target=n.receive_loop, daemon=True)
    t.start()
    nodes.append(n)

# -----------------------------------------------------------------------------
# RUN MESH
# -----------------------------------------------------------------------------
try:
    while True:
        for n in nodes:
            n.broadcast(ports)
        time.sleep(SIM_STEP)
        for n in nodes:
            n.update()
        # show metrics
        seed_var = np.mean([np.var(n.seed) for n in nodes])
        positions = np.array([n.pos for n in nodes])
        centroid = np.mean(positions, axis=0)
        spread = np.mean(np.linalg.norm(positions - centroid, axis=1))
        print(f"epoch {nodes[0].epoch} | seed_var={seed_var:.4f} | spread={spread:.2f}")
except KeyboardInterrupt:
    print("UDP mesh terminated.")



# =============================================================================
# SEED PROTOCOL v3 — RANGE-LIMITED UDP MESH WITH JITTER
# =============================================================================

import socket
import threading
import numpy as np
import struct
import random
import time

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
NUM_NODES = 5
BASE_PORT = 50000
COMM_RANGE = 200.0     # max distance for messages
SEED_DRIFT = 0.02
POS_DRIFT = 5.0
SIM_STEP = 1.0         # seconds per simulation step

PACKET_LOSS = 0.1      # 10% packet drop
JITTER = 0.05          # seconds of random delay

# -----------------------------------------------------------------------------
# PACKET UTILITIES
# -----------------------------------------------------------------------------
def pack_packet(seed, pos, energy=100, epoch=0):
    return struct.pack('6f3f2i', *(list(seed)+list(pos)+[energy, epoch]))

def unpack_packet(pkt):
    data = struct.unpack('6f3f2i', pkt)
    seed = np.array(data[0:6])
    pos  = np.array(data[6:9])
    energy, epoch = data[9:11]
    return {"seed": seed, "position": pos, "energy": energy, "epoch": epoch}

# -----------------------------------------------------------------------------
# SEED COMBINE
# -----------------------------------------------------------------------------
def combine_seeds(seeds):
    return np.mean(seeds, axis=0)

# -----------------------------------------------------------------------------
# NODE DEFINITION
# -----------------------------------------------------------------------------
class Node:
    def __init__(self, node_id, port):
        self.id = node_id
        self.port = port
        self.pos = np.random.rand(3) * 1000.0
        s = np.random.rand(6)
        self.seed = s / s.sum()
        self.energy = random.randint(80,200)
        self.epoch = 0
        self.inbox = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))
        self.sock.setblocking(False)
        self.lock = threading.Lock()

    # --- broadcast with range + loss/jitter ---
    def broadcast(self, nodes):
        pkt = pack_packet(self.seed, self.pos, self.energy, self.epoch)
        for n in nodes:
            if n.port == self.port:
                continue
            distance = np.linalg.norm(self.pos - n.pos)
            if distance > COMM_RANGE:
                continue
            if random.random() < PACKET_LOSS:
                continue
            # simulate jitter
            delay = random.uniform(0, JITTER)
            threading.Timer(delay, lambda: n.sock.sendto(pkt, ('localhost', n.port))).start()

    # --- receive loop ---
    def receive_loop(self):
        while True:
            try:
                pkt, addr = self.sock.recvfrom(1024)
                data = unpack_packet(pkt)
                with self.lock:
                    self.inbox.append(data)
            except BlockingIOError:
                time.sleep(0.01)

    # --- update state ---
    def update(self):
        with self.lock:
            if not self.inbox:
                return
            neighbor_seeds = [msg["seed"] for msg in self.inbox]
            neighbor_positions = [msg["position"] for msg in self.inbox]
            self.seed = (1-SEED_DRIFT)*self.seed + SEED_DRIFT*combine_seeds([self.seed]+neighbor_seeds)
            self.seed /= self.seed.sum()
            avg_pos = np.mean(neighbor_positions, axis=0)
            self.pos += POS_DRIFT * (avg_pos - self.pos)/(np.linalg.norm(avg_pos - self.pos)+1e-6)
            self.pos += np.random.randn(3) * 0.5
            self.inbox = []
            self.epoch += 1

# -----------------------------------------------------------------------------
# INIT NODES
# -----------------------------------------------------------------------------
nodes = []
ports = [BASE_PORT+i for i in range(NUM_NODES)]
for i in range(NUM_NODES):
    n = Node(i, ports[i])
    t = threading.Thread(target=n.receive_loop, daemon=True)
    t.start()
    nodes.append(n)

# -----------------------------------------------------------------------------
# RUN SIMULATION
# -----------------------------------------------------------------------------
try:
    while True:
        for n in nodes:
            n.broadcast(nodes)
        time.sleep(SIM_STEP)
        for n in nodes:
            n.update()
        seed_var = np.mean([np.var(n.seed) for n in nodes])
        positions = np.array([n.pos for n in nodes])
        centroid = np.mean(positions, axis=0)
        spread = np.mean(np.linalg.norm(positions - centroid, axis=1))
        print(f"epoch {nodes[0].epoch} | seed_var={seed_var:.4f} | spread={spread:.2f}")
except KeyboardInterrupt:
    print("UDP mesh terminated.")

# =============================================================================
# SEED PROTOCOL v4 — MULTI-MACHINE LAN UDP MESH
# =============================================================================

import socket
import struct
import threading
import numpy as np
import random
import time

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 50000

NUM_NODES_LOCAL = 1       # each machine runs 1 or more nodes
COMM_RANGE = 200.0        # virtual distance range (for filtering)
SEED_DRIFT = 0.02
POS_DRIFT = 5.0
SIM_STEP = 1.0             # seconds per simulation step
PACKET_LOSS = 0.05         # 5% packet drop
JITTER = 0.05              # seconds of random delay

# -----------------------------------------------------------------------------
# PACKET UTILITIES
# -----------------------------------------------------------------------------
def pack_packet(node_id, seed, pos, energy=100, epoch=0):
    return struct.pack('i6f3f2i', node_id, *(list(seed)+list(pos)+[energy, epoch]))

def unpack_packet(pkt):
    data = struct.unpack('i6f3f2i', pkt)
    node_id = data[0]
    seed = np.array(data[1:7])
    pos = np.array(data[7:10])
    energy, epoch = data[10:12]
    return {"id": node_id, "seed": seed, "position": pos, "energy": energy, "epoch": epoch}

def combine_seeds(seeds):
    return np.mean(seeds, axis=0)

# -----------------------------------------------------------------------------
# NODE DEFINITION
# -----------------------------------------------------------------------------
class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.pos = np.random.rand(3) * 1000.0
        s = np.random.rand(6)
        self.seed = s / s.sum()
        self.energy = random.randint(80, 200)
        self.epoch = 0
        self.inbox = []
        self.lock = threading.Lock()

    # --- broadcast to multicast group ---
    def broadcast(self, sock):
        pkt = pack_packet(self.id, self.seed, self.pos, self.energy, self.epoch)
        if random.random() < PACKET_LOSS:
            return
        delay = random.uniform(0, JITTER)
        threading.Timer(delay, lambda: sock.sendto(pkt, (MULTICAST_GROUP, MULTICAST_PORT))).start()

    # --- update node state from inbox ---
    def update(self):
        with self.lock:
            if not self.inbox:
                return
            neighbor_seeds = [msg["seed"] for msg in self.inbox if msg["id"] != self.id]
            neighbor_positions = [msg["position"] for msg in self.inbox if msg["id"] != self.id]
            if neighbor_seeds:
                self.seed = (1-SEED_DRIFT)*self.seed + SEED_DRIFT*combine_seeds([self.seed]+neighbor_seeds)
                self.seed /= self.seed.sum()
            if neighbor_positions:
                avg_pos = np.mean(neighbor_positions, axis=0)
                self.pos += POS_DRIFT * (avg_pos - self.pos)/(np.linalg.norm(avg_pos - self.pos)+1e-6)
                self.pos += np.random.randn(3) * 0.5
            self.inbox = []
            self.epoch += 1

# -----------------------------------------------------------------------------
# MULTICAST SOCKET
# -----------------------------------------------------------------------------
def create_multicast_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MULTICAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setblocking(False)
    return sock

# -----------------------------------------------------------------------------
# RECEIVE LOOP
# -----------------------------------------------------------------------------
def receive_loop(sock, nodes):
    while True:
        try:
            pkt, addr = sock.recvfrom(1024)
            data = unpack_packet(pkt)
            # range filtering (optional, virtual distance)
            for n in nodes:
                distance = np.linalg.norm(n.pos - data["position"])
                if distance <= COMM_RANGE:
                    with n.lock:
                        n.inbox.append(data)
        except BlockingIOError:
            time.sleep(0.01)

# -----------------------------------------------------------------------------
# INIT NODES
# -----------------------------------------------------------------------------
nodes = [Node(i) for i in range(NUM_NODES_LOCAL)]
sock = create_multicast_socket()

t = threading.Thread(target=receive_loop, args=(sock,nodes), daemon=True)
t.start()

# -----------------------------------------------------------------------------
# RUN SIMULATION
# -----------------------------------------------------------------------------
try:
    while True:
        for n in nodes:
            n.broadcast(sock)
        time.sleep(SIM_STEP)
        for n in nodes:
            n.update()
        seed_var = np.mean([np.var(n.seed) for n in nodes])
        positions = np.array([n.pos for n in nodes])
        centroid = np.mean(positions, axis=0)
        spread = np.mean(np.linalg.norm(positions - centroid, axis=1))
        print(f"epoch {nodes[0].epoch} | seed_var={seed_var:.4f} | spread={spread:.2f}")
except KeyboardInterrup

fieldlink to TRDAP repo and seed physics repo.  git clone for info

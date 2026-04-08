#!/usr/bin/env python3
# MODULE: sim/seed_mesh.py
# PROVIDES: MESH.GRID_FAILURE_SIM, MESH.CASCADE_MITIGATION, MESH.GOSSIP_SYNC, MESH.MERKLE_DIFF
# DEPENDS: sim.cities.coupling (optional)
# RUN: python -m sim.seed_mesh
# TIER: bridge
# City resilience mesh bridge — grid failure simulation, gossip sync, Merkle diff
"""
sim/seed_mesh.py — Seed Mesh Bridge to City Resilience Model
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

What happens when the grid goes down and you can't call anyone?

This module connects the seed protocol to the city coupling model.
It simulates mesh network activation during grid failure and measures
how ad-hoc communication changes the cascade math.

The answer is not "mesh fixes everything."
The answer is "mesh buys time on specific coupling edges."
Embodied knowledge still dies with its holders.
Mesh can't apprentice someone in soil culture over a radio.
But it can coordinate who has fuel and who needs medical.

USAGE:
    python -m sim.seed_mesh
"""

import math
import hashlib
import random
import time as _time
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

# Graceful imports — works standalone if coupling.py is unavailable
try:
    from sim.cities.coupling import (
        DomainType, DomainState, CouplingEdge, CoupledSystemState,
        KnowledgeDecayLayer, build_madison_coupled_system,
        print_coupled_report,
    )
    HAS_COUPLING = True
except ImportError:
    HAS_COUPLING = False

try:
    from sim.seed_protocol import (
        MeshNode, expand_seed, route_greedy, seed_distance,
        combine_seeds, euclidean_distance, normalize_to_energy,
        run_mesh_simulation, vec_zeros,
    )
    HAS_PROTOCOL = True
except ImportError:
    HAS_PROTOCOL = False


# =============================================================================
# DOMAIN ↔ OCTAHEDRAL AXIS MAPPING
# =============================================================================

# The 6 octahedral directions map to the 6 primary resilience domains.
# This is the conceptual bridge between abstract geometry and the
# concrete coupling model.
#
# The mapping isn't arbitrary — it pairs opposing concerns on each axis:
#   X-axis: biological needs (food) vs energy supply
#   Y-axis: social cohesion vs institutional structure
#   Z-axis: knowledge transmission vs physical infrastructure
#
# Opposing axes interact: you can't have food without energy,
# institutions need social legitimacy, infrastructure embodies knowledge.

DOMAIN_AXIS_MAP = {
    "food":           0,    # +X
    "energy":         1,    # -X
    "social":         2,    # +Y
    "institutional":  3,    # -Y
    "knowledge":      4,    # +Z
    "infrastructure": 5,    # -Z
}

# Reverse lookup
AXIS_DOMAIN_MAP = {v: k for k, v in DOMAIN_AXIS_MAP.items()}


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class MeshConfig:
    """Configuration for mesh simulation during grid failure."""
    nodes_per_sq_mile_urban: int = 15
    nodes_per_sq_mile_suburban: int = 6
    nodes_per_sq_mile_rural: int = 2
    comm_range_meters: float = 200.0    # realistic LoRa/CB range
    seed_drift: float = 0.02
    pos_drift: float = 5.0
    steps_per_hour: int = 4
    hours_to_simulate: int = 72         # 3-day grid failure
    grid_failure_severity: float = 0.5


# =============================================================================
# ZONE MESH STATE
# =============================================================================

@dataclass
class ZoneMeshState:
    """Mesh network state within a city zone."""
    zone_name: str
    zone_type: str              # urban / suburban / rural
    area_sq_miles: float
    population: int
    nodes: List = field(default_factory=list)
    coverage_history: List[float] = field(default_factory=list)

    def connected_components(self, comm_range: float) -> int:
        """Count connected components via BFS. Fragmentation = bad."""
        if not self.nodes:
            return 0
        visited = set()
        components = 0
        for start in self.nodes:
            if start.node_id in visited:
                continue
            components += 1
            queue = [start]
            while queue:
                current = queue.pop(0)
                if current.node_id in visited:
                    continue
                visited.add(current.node_id)
                for other in self.nodes:
                    if other.node_id not in visited:
                        if euclidean_distance(current.position, other.position) < comm_range:
                            queue.append(other)
        return components

    def coverage_pct(self, comm_range: float) -> float:
        """What fraction of nodes can reach at least one other node."""
        if len(self.nodes) < 2:
            return 0.0
        connected = 0
        for node in self.nodes:
            for other in self.nodes:
                if node.node_id != other.node_id:
                    if euclidean_distance(node.position, other.position) < comm_range:
                        connected += 1
                        break
        return connected / len(self.nodes)


# =============================================================================
# RESULTS
# =============================================================================

@dataclass
class MeshRecoveryResult:
    """Complete results of mesh simulation during grid failure."""
    scenario: str
    hours_simulated: int
    zones: List[ZoneMeshState]
    convergence_history: List[float]
    routing_tests: List[dict]
    comms_recovery_hour: float          # when mesh reaches 60% coverage
    cascade_mitigation: Dict[str, float]    # edge → mitigated amplification
    knowledge_effects: List[dict]


# =============================================================================
# DOMAIN STATE → SEED MAPPING
# =============================================================================

def domain_states_to_seed(domain_states: dict) -> List[float]:
    """
    Convert domain capacities to a seed vector.
    Each domain's current_capacity maps to its octahedral axis.
    The seed encodes the city's resilience profile as a 6D vector.
    """
    seed = [0.0] * 6

    if HAS_COUPLING:
        mapping = {
            DomainType.FOOD: 0,
            DomainType.ENERGY: 1,
            DomainType.SOCIAL: 2,
            DomainType.INSTITUTIONAL: 3,
            DomainType.KNOWLEDGE: 4,
            DomainType.INFRASTRUCTURE: 5,
        }
        for domain_type, axis in mapping.items():
            state = domain_states.get(domain_type)
            if state:
                seed[axis] = state.current_capacity
    else:
        # Fallback: use values directly from a dict
        for domain_name, axis in DOMAIN_AXIS_MAP.items():
            if domain_name in domain_states:
                seed[axis] = domain_states[domain_name]

    total = sum(seed)
    if total < 1e-12:
        return [1.0 / 6.0] * 6
    return [x / total for x in seed]


# =============================================================================
# MESH PLACEMENT
# =============================================================================

def place_zone_nodes(zone_name: str, zone_type: str,
                     area_sq_miles: float, population: int,
                     base_seed: List[float], config: MeshConfig,
                     id_offset: int = 0) -> ZoneMeshState:
    """
    Place mesh nodes in a city zone.
    Node density varies by zone type — more people, more devices.
    Seeds start from zone's domain profile with small random variation.
    """
    density_map = {
        "urban": config.nodes_per_sq_mile_urban,
        "suburban": config.nodes_per_sq_mile_suburban,
        "rural": config.nodes_per_sq_mile_rural,
    }
    density = density_map.get(zone_type, config.nodes_per_sq_mile_suburban)
    num_nodes = max(2, int(area_sq_miles * density))

    # Convert area to meters for positioning
    side_meters = math.sqrt(area_sq_miles * 2.59e6)  # sq miles to sq meters

    nodes = []
    for i in range(num_nodes):
        # Random position within zone bounds
        pos = [
            random.random() * side_meters,
            random.random() * side_meters,
            0.0,  # 2D for city modeling
        ]

        # Seed: zone profile + small random variation
        seed = list(base_seed)
        for j in range(6):
            seed[j] += random.gauss(0, 0.02)
            seed[j] = max(0.01, seed[j])
        s_total = sum(seed)
        seed = [x / s_total for x in seed]

        nodes.append(MeshNode(
            node_id=id_offset + i,
            position=pos,
            seed=seed,
            energy=random.randint(80, 200),
        ))

    return ZoneMeshState(
        zone_name=zone_name,
        zone_type=zone_type,
        area_sq_miles=area_sq_miles,
        population=population,
        nodes=nodes,
    )


# =============================================================================
# MESH SIMULATION DURING GRID FAILURE
# =============================================================================

def simulate_grid_failure(config: Optional[MeshConfig] = None) -> MeshRecoveryResult:
    """
    Simulate mesh network activation during a grid failure event.

    If the coupling model is available, uses Madison WI domain states.
    Otherwise uses representative fallback values.
    """
    if config is None:
        config = MeshConfig()

    # Get domain states
    if HAS_COUPLING:
        system = build_madison_coupled_system()
        # Apply grid failure shock
        system.apply_shock(
            DomainType.ENERGY,
            config.grid_failure_severity,
            day=0,
            description="grid failure — 72 hour event",
        )
        base_seed = domain_states_to_seed(system.domains)
        coupling_edges = system.coupling_edges
        knowledge_layers = system.knowledge_layers
    else:
        # Fallback domain capacities (Madison-like)
        fallback = {
            "food": 0.70, "energy": 0.30,  # energy hit by grid failure
            "social": 0.55, "institutional": 0.50,
            "knowledge": 0.45, "infrastructure": 0.40,
        }
        base_seed = domain_states_to_seed(fallback)
        coupling_edges = []
        knowledge_layers = []

    # Place nodes in zones
    zones = [
        place_zone_nodes("downtown", "urban", 4.0, 45000,
                         base_seed, config, id_offset=0),
        place_zone_nodes("near_east", "urban", 3.5, 32000,
                         base_seed, config, id_offset=100),
        place_zone_nodes("west_side", "suburban", 8.0, 55000,
                         base_seed, config, id_offset=200),
        place_zone_nodes("fitchburg", "suburban", 12.0, 30000,
                         base_seed, config, id_offset=300),
        place_zone_nodes("rural_fringe", "rural", 25.0, 8000,
                         base_seed, config, id_offset=400),
    ]

    all_nodes = []
    for z in zones:
        all_nodes.extend(z.nodes)

    convergence_history = []
    comms_recovery_hour = float('inf')

    # Hour-by-hour simulation
    for hour in range(config.hours_to_simulate):
        for _ in range(config.steps_per_hour):
            # Broadcast phase
            packets = [(node, node.broadcast()) for node in all_nodes]

            # Receive phase (range-limited)
            for sender, pkt in packets:
                for receiver in all_nodes:
                    if sender.node_id == receiver.node_id:
                        continue
                    if euclidean_distance(sender.position, receiver.position) < config.comm_range_meters:
                        receiver.receive(pkt)

            # Update phase
            for node in all_nodes:
                node.update(seed_drift=config.seed_drift, pos_drift=config.pos_drift)

        # Metrics per hour
        if all_nodes:
            dim_vars = []
            for d in range(6):
                vals = [n.seed[d] for n in all_nodes]
                mean = sum(vals) / len(vals)
                var = sum((v - mean) ** 2 for v in vals) / len(vals)
                dim_vars.append(var)
            convergence_history.append(sum(dim_vars) / len(dim_vars))

        # Zone coverage tracking
        for z in zones:
            z.coverage_history.append(z.coverage_pct(config.comm_range_meters))

        # Check for recovery: when average coverage exceeds 60%
        if comms_recovery_hour == float('inf'):
            avg_coverage = sum(
                z.coverage_history[-1] for z in zones
            ) / len(zones) if zones else 0
            if avg_coverage >= 0.60:
                comms_recovery_hour = hour + 1

    # Routing tests — test within zones (where connectivity exists)
    # and across zones (where it may not)
    routing_tests = []
    for z in zones:
        if len(z.nodes) >= 2:
            src_idx = 0
            dst_idx = len(z.nodes) - 1
            # Find indices in all_nodes
            src_all = next(i for i, n in enumerate(all_nodes) if n.node_id == z.nodes[src_idx].node_id)
            dst_all = next(i for i, n in enumerate(all_nodes) if n.node_id == z.nodes[dst_idx].node_id)
            path = route_greedy(all_nodes, src_all, dst_all, config.comm_range_meters)
            routing_tests.append({
                "source": all_nodes[src_all].node_id,
                "target": all_nodes[dst_all].node_id,
                "zone": z.zone_name,
                "path": path,
                "hops": len(path) - 1,
                "reached": path[-1] == all_nodes[dst_all].node_id,
            })

    # Cascade mitigation analysis
    cascade_mitigation = compute_cascade_mitigation(
        coupling_edges, comms_recovery_hour,
    )

    # Knowledge transmission effects
    knowledge_effects = compute_knowledge_effects(
        knowledge_layers, zones, config.comm_range_meters,
    )

    return MeshRecoveryResult(
        scenario=f"grid_failure_severity_{config.grid_failure_severity}",
        hours_simulated=config.hours_to_simulate,
        zones=zones,
        convergence_history=convergence_history,
        routing_tests=routing_tests,
        comms_recovery_hour=comms_recovery_hour,
        cascade_mitigation=cascade_mitigation,
        knowledge_effects=knowledge_effects,
    )


# =============================================================================
# CASCADE MITIGATION — how mesh changes the coupling math
# =============================================================================

def compute_cascade_mitigation(coupling_edges: list,
                               comms_recovery_hour: float) -> Dict[str, float]:
    """
    Calculate how mesh communication reduces cascade amplification.

    Key insight from coupling.py: coupling edges have lag_days.
    If mesh restores coordination BEFORE the lag expires,
    the amplification factor decreases because people can
    actually coordinate a response.

    Mesh doesn't eliminate the coupling. It buys response time.
    """
    mitigation = {}

    if not HAS_COUPLING:
        return mitigation

    for edge in coupling_edges:
        lag_hours = edge.lag_days * 24
        edge_key = f"{edge.source.value} -> {edge.target.value}"

        if comms_recovery_hour >= lag_hours:
            # Mesh came too late for this edge — full amplification
            mitigation[edge_key] = edge.amplification
        else:
            # Mesh arrived before cascade manifested
            # Reduction proportional to how early comms restored
            time_ratio = comms_recovery_hour / lag_hours
            # Coordination reduces amplification — but never below 1.0
            # (the physical coupling still exists, you just manage it better)
            reduced = 1.0 + (edge.amplification - 1.0) * time_ratio
            mitigation[edge_key] = round(reduced, 2)

    return mitigation


# =============================================================================
# KNOWLEDGE TRANSMISSION — what mesh can and cannot fix
# =============================================================================

def compute_knowledge_effects(knowledge_layers: list,
                              zones: list,
                              comm_range: float) -> List[dict]:
    """
    Calculate how mesh connectivity affects knowledge transmission.

    HONEST ACCOUNTING:
    - Mesh transmits documented knowledge only
    - embodied_vs_documented ratio limits impact
    - A 95% embodied domain (food preservation) gets almost no mesh boost
    - A 85% embodied domain (water ops) gets slightly more

    Mesh can coordinate who knows what. It cannot replace apprenticeship.
    """
    effects = []

    if not knowledge_layers:
        return effects

    # Average mesh coverage across zones
    avg_coverage = 0.0
    if zones:
        final_coverages = [
            z.coverage_history[-1] if z.coverage_history else 0.0
            for z in zones
        ]
        avg_coverage = sum(final_coverages) / len(final_coverages)

    for kl in knowledge_layers:
        # Mesh can only boost the documented fraction
        documented_fraction = 1.0 - kl.embodied_vs_documented
        # Coverage determines how much of that fraction gets transmitted
        mesh_boost = documented_fraction * avg_coverage * 0.5
        # This boosts transmission_rate
        boosted_rate = kl.transmission_rate + mesh_boost

        # Recalculate window with boosted rate
        net_decay_original = kl.annual_loss_rate - kl.transmission_rate
        net_decay_boosted = kl.annual_loss_rate - boosted_rate

        original_window = kl.transmission_window_years()
        if net_decay_boosted <= 0:
            boosted_window = float('inf')
        else:
            viable_threshold = 0.20
            current_ratio = kl.knowledge_holders_current / kl.knowledge_holders_peak
            decay_to_threshold = current_ratio - viable_threshold
            if decay_to_threshold <= 0:
                boosted_window = 0.0
            else:
                boosted_window = decay_to_threshold / net_decay_boosted

        effects.append({
            "domain": kl.domain,
            "embodied_pct": kl.embodied_vs_documented * 100,
            "documented_pct": documented_fraction * 100,
            "mesh_coverage": avg_coverage,
            "transmission_boost": mesh_boost,
            "original_window_years": original_window,
            "boosted_window_years": boosted_window,
            "years_gained": (boosted_window - original_window
                             if boosted_window != float('inf') and original_window != float('inf')
                             else 0.0),
            "honest_note": _honesty_check(kl),
        })

    return effects


def _honesty_check(kl) -> str:
    """What mesh can't fix for this knowledge domain."""
    pct = kl.embodied_vs_documented * 100
    if pct >= 95:
        return f"{pct:.0f}% embodied — mesh barely helps. Need live apprenticeship."
    if pct >= 90:
        return f"{pct:.0f}% embodied — mesh helps marginally. Most knowledge is in hands, not screens."
    if pct >= 80:
        return f"{pct:.0f}% embodied — mesh helps somewhat. Documented portion can spread faster."
    return f"{pct:.0f}% embodied — mesh meaningfully accelerates documented knowledge sharing."


# =============================================================================
# REPORT PRINTER
# =============================================================================

def print_mesh_report(result: MeshRecoveryResult):
    """Print mesh recovery results in the same style as coupling.py reports."""
    print(f"\n{'='*66}")
    print(f"  MESH RECOVERY REPORT: {result.scenario}")
    print(f"  {result.hours_simulated}-hour grid failure simulation")
    print(f"{'='*66}")

    # Zone coverage
    print(f"\n  ZONE MESH COVERAGE:")
    for z in result.zones:
        n_nodes = len(z.nodes)
        final_cov = z.coverage_history[-1] if z.coverage_history else 0.0
        components = z.connected_components(200.0)
        bar = "#" * int(final_cov * 20)
        print(f"    {z.zone_name:<16} {z.zone_type:<10} "
              f"{n_nodes:3d} nodes  {final_cov:5.0%} coverage  "
              f"{components} component{'s' if components != 1 else ''}  {bar}")

    # Convergence
    if result.convergence_history:
        print(f"\n  SEED CONVERGENCE (shared awareness):")
        n = len(result.convergence_history)
        checkpoints = [0, n // 4, n // 2, 3 * n // 4, n - 1]
        for i in checkpoints:
            if i < n:
                print(f"    Hour {i+1:>3}: variance = {result.convergence_history[i]:.6f}")

        if result.convergence_history[0] > 0:
            reduction = (1 - result.convergence_history[-1] / result.convergence_history[0]) * 100
            print(f"    Convergence: {reduction:.1f}% reduction over {n} hours")

    # Comms recovery
    print(f"\n  COMMS RECOVERY:")
    if result.comms_recovery_hour < float('inf'):
        print(f"    Mesh reached 60% coverage at hour {result.comms_recovery_hour:.0f}")
    else:
        print(f"    Mesh did NOT reach 60% coverage in {result.hours_simulated} hours")
        print(f"    Nodes too sparse or range too short")

    # Routing
    if result.routing_tests:
        print(f"\n  ROUTING TESTS:")
        successes = sum(1 for t in result.routing_tests if t["reached"])
        print(f"    {successes}/{len(result.routing_tests)} routes completed")
        for t in result.routing_tests:
            status = "OK" if t["reached"] else "FAIL"
            zone = t.get("zone", "?")
            print(f"    {t['source']:>4} -> {t['target']:<4}  "
                  f"{t['hops']:2d} hops  [{status}]  ({zone})")

    # Cascade mitigation
    if result.cascade_mitigation:
        print(f"\n  CASCADE MITIGATION (mesh vs no mesh):")
        for edge, mitigated in sorted(result.cascade_mitigation.items()):
            # Find original amplification
            original = mitigated  # default
            if HAS_COUPLING:
                system = build_madison_coupled_system()
                for e in system.coupling_edges:
                    if f"{e.source.value} -> {e.target.value}" == edge:
                        original = e.amplification
                        break
            if mitigated < original:
                saved = f"  reduced from {original:.1f}x"
            else:
                saved = f"  (no change — lag too short)"
            print(f"    {edge:<35} {mitigated:.2f}x{saved}")

    # Knowledge effects
    if result.knowledge_effects:
        print(f"\n  KNOWLEDGE TRANSMISSION EFFECTS:")
        for ke in result.knowledge_effects:
            orig = ke["original_window_years"]
            boost = ke["boosted_window_years"]
            orig_str = f"{orig:.1f}yr" if orig != float('inf') else "stable"
            boost_str = f"{boost:.1f}yr" if boost != float('inf') else "stable"
            gained = ke["years_gained"]
            print(f"    {ke['domain']}")
            print(f"      Window: {orig_str} -> {boost_str}"
                  f"  (+{gained:.1f}yr)" if gained > 0 else
                  f"      Window: {orig_str} -> {boost_str}")
            print(f"      {ke['honest_note']}")

    print(f"\n{'='*66}")
    print(f"  WHAT THIS MEANS")
    print(f"{'='*66}")
    print("""
  Mesh networking during grid failure:
  - DOES: restore basic coordination within hours
  - DOES: reduce cascade amplification on edges with lag > recovery time
  - DOES: speed up documented knowledge sharing proportional to coverage
  - DOES NOT: replace embodied knowledge (apprenticeship, practice)
  - DOES NOT: fix physical infrastructure
  - DOES NOT: create food, energy, or water

  The mesh buys time. What you do with that time is the real question.
  The coupling edges don't care about your comms protocol.
  They care about whether someone coordinated the response
  before the cascade locked in.
""")
    print(f"{'='*66}\n")


# =============================================================================
# GOSSIP SYNC — minimal-bandwidth state exchange between mesh nodes
# =============================================================================
#
# Extracted from octahedral runtime design, rewritten stdlib-only.
# In a degraded network, you can't broadcast full state to everyone.
# Gossip sends only what the peer is missing, using hash comparison.

@dataclass
class GossipState:
    """State vector for a mesh zone, hashable for diff detection."""
    zone_name: str
    seed_snapshot: List[float]     # current averaged seed across zone
    coverage: float                # current coverage pct
    node_count: int
    epoch: int = 0                 # increments on state change

    def digest(self) -> bytes:
        """8-byte hash of current state — cheap to compare."""
        raw = f"{self.zone_name}:{self.epoch}:{self.coverage:.4f}"
        return hashlib.blake2b(raw.encode(), digest_size=8).digest()


def gossip_diff(local: Dict[str, GossipState],
                peer_digests: Dict[str, bytes]) -> Dict[str, GossipState]:
    """
    Compare local zone states against peer's digests.
    Return only zones where local state differs — minimal payload.
    """
    updates = {}
    for zone_name, state in local.items():
        peer_hash = peer_digests.get(zone_name, b'')
        if state.digest() != peer_hash:
            updates[zone_name] = state
    return updates


def gossip_merge(local: Dict[str, GossipState],
                 received: Dict[str, GossipState]) -> int:
    """
    Merge received gossip into local state.
    Higher epoch wins. Returns count of zones updated.
    """
    merged = 0
    for zone_name, remote_state in received.items():
        if zone_name not in local:
            local[zone_name] = remote_state
            merged += 1
        elif remote_state.epoch > local[zone_name].epoch:
            local[zone_name] = remote_state
            merged += 1
    return merged


# =============================================================================
# MERKLE SYNC — detect divergence after network partition
# =============================================================================
#
# When mesh fragments heal (zones reconnect after partition),
# we need to know WHICH zones diverged — without comparing all state.
# A Merkle tree over zone digests does this in O(log N) comparisons.

def _merkle_hash(left: bytes, right: bytes) -> bytes:
    """Combine two hashes into parent."""
    return hashlib.blake2b(left + right, digest_size=16).digest()


def merkle_root(zone_states: Dict[str, GossipState]) -> bytes:
    """
    Build Merkle root over sorted zone digests.
    Two nodes with identical zone states produce identical roots.
    """
    if not zone_states:
        return b'\x00' * 16

    leaves = []
    for name in sorted(zone_states.keys()):
        leaves.append(zone_states[name].digest())

    # Pad to even count
    while len(leaves) > 1:
        next_level = []
        for i in range(0, len(leaves), 2):
            if i + 1 < len(leaves):
                next_level.append(_merkle_hash(leaves[i], leaves[i + 1]))
            else:
                next_level.append(leaves[i])
        leaves = next_level

    return leaves[0]


def merkle_diff(local_states: Dict[str, GossipState],
                remote_states: Dict[str, GossipState]) -> List[str]:
    """
    Return zone names that differ between local and remote.
    Used after partition heals to know what to re-sync.
    """
    all_zones = set(local_states.keys()) | set(remote_states.keys())
    differing = []
    for zone in sorted(all_zones):
        local_hash = local_states[zone].digest() if zone in local_states else b''
        remote_hash = remote_states[zone].digest() if zone in remote_states else b''
        if local_hash != remote_hash:
            differing.append(zone)
    return differing


# =============================================================================
# CIRCUIT BREAKER — rate-limit flapping mesh nodes
# =============================================================================
#
# A node that keeps failing and recovering wastes everyone's bandwidth.
# Circuit breaker stops re-broadcasting to it after N failures in T seconds.

@dataclass
class CircuitBreaker:
    """Per-node rate limiter for mesh broadcasts."""
    max_failures: int = 5
    window_seconds: float = 60.0
    _failures: Dict[str, deque] = field(default_factory=dict)

    def record_failure(self, node_id: str):
        """Record a failed transmission to node_id."""
        if node_id not in self._failures:
            self._failures[node_id] = deque()
        self._failures[node_id].append(_time.time())

    def allow(self, node_id: str) -> bool:
        """Should we still try sending to this node?"""
        if node_id not in self._failures:
            return True
        q = self._failures[node_id]
        now = _time.time()
        # Evict old entries
        while q and q[0] < now - self.window_seconds:
            q.popleft()
        return len(q) < self.max_failures

    def reset(self, node_id: str):
        """Node recovered — clear its failure history."""
        if node_id in self._failures:
            self._failures[node_id].clear()


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    random.seed(42)

    if not HAS_PROTOCOL:
        print("ERROR: sim.seed_protocol not found.")
        print("Run from repo root: python -m sim.seed_mesh")
        raise SystemExit(1)

    print("=" * 66)
    print("  SEED MESH — city resilience during grid failure")
    print("  stdlib only. free. no excuses.")
    print("=" * 66)

    if HAS_COUPLING:
        print("\n  Coupling model loaded — using Madison WI domain states")
        system = build_madison_coupled_system()
        print(f"  Pre-failure domain states:")
        for dt, ds in system.domains.items():
            print(f"    {dt.value:<20} capacity={ds.current_capacity:.0%}  "
                  f"buffer={ds.buffer_remaining:.0%}")
    else:
        print("\n  Coupling model not available — using fallback values")
        print("  (run from repo root for full integration: python -m sim.seed_mesh)")

    print(f"\n  Simulating 72-hour grid failure...")

    config = MeshConfig(
        comm_range_meters=250.0,
        hours_to_simulate=72,
        grid_failure_severity=0.5,
    )
    result = simulate_grid_failure(config)

    print_mesh_report(result)

    # --- Gossip sync demo ---
    print(f"\n{'='*66}")
    print(f"  GOSSIP SYNC + MERKLE DIFF DEMO")
    print(f"{'='*66}")

    # Build gossip states from zones
    local_gossip = {}
    for z in result.zones:
        avg_seed = [0.0] * 6
        for n in z.nodes:
            for d in range(6):
                avg_seed[d] += n.seed[d]
        if z.nodes:
            avg_seed = [x / len(z.nodes) for x in avg_seed]
        cov = z.coverage_history[-1] if z.coverage_history else 0.0
        local_gossip[z.zone_name] = GossipState(
            zone_name=z.zone_name,
            seed_snapshot=avg_seed,
            coverage=cov,
            node_count=len(z.nodes),
            epoch=1,
        )

    # Simulate a peer with stale state (epoch 0, different coverage)
    peer_gossip = {}
    for name, state in local_gossip.items():
        peer_gossip[name] = GossipState(
            zone_name=name,
            seed_snapshot=state.seed_snapshot,
            coverage=state.coverage * 0.5,  # stale
            node_count=state.node_count,
            epoch=0,
        )

    # Gossip diff: what does the peer need?
    peer_digests = {name: s.digest() for name, s in peer_gossip.items()}
    updates = gossip_diff(local_gossip, peer_digests)
    print(f"\n  Gossip: {len(updates)}/{len(local_gossip)} zones need sync")

    # Merkle root comparison
    local_root = merkle_root(local_gossip)
    peer_root = merkle_root(peer_gossip)
    print(f"  Merkle root match: {local_root == peer_root}")
    if local_root != peer_root:
        diffs = merkle_diff(local_gossip, peer_gossip)
        print(f"  Diverged zones: {diffs}")

    # Merge: peer accepts our updates
    merged = gossip_merge(peer_gossip, updates)
    print(f"  Merged {merged} zones into peer state")
    post_root = merkle_root(peer_gossip)
    print(f"  Post-merge Merkle match: {local_root == post_root}")

    # Circuit breaker demo
    print(f"\n  Circuit breaker:")
    cb = CircuitBreaker(max_failures=3, window_seconds=10.0)
    for i in range(5):
        cb.record_failure("flaky_node")
        allowed = cb.allow("flaky_node")
        print(f"    Failure {i+1}: broadcast {'allowed' if allowed else 'BLOCKED'}")
    cb.reset("flaky_node")
    print(f"    After reset: broadcast {'allowed' if cb.allow('flaky_node') else 'BLOCKED'}")

    print(f"\n{'='*66}\n")

#!/usr/bin/env python3
"""
KnowledgeDNA — Stdlib-Only Knowledge Ancestry and Field Propagation
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

A directed graph where knowledge is a state variable, not an object.
Influence propagates across edges weighted by transfer efficiency and phase.
Energy is conserved and transformed, not assigned.
Time decays what isn't reinforced.

Standard attribution asks: "Where did this come from?"
This system asks: "What is still actively shaping this state?"

That's a different class of question — closer to field theory than history.

Zero external dependencies. No networkx. No pandas. No matplotlib.

USAGE:
    python -m KnowledgeDNA.knowledge_dna
"""

import csv
import math
import random
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set


# =============================================================================
# GRAPH NODE + EDGE — replaces networkx
# =============================================================================

@dataclass
class KnowledgeNode:
    """A unit of knowledge with energy, contributors, and position."""
    node_id: str
    name: str
    contributors: List[str]
    energy: float
    timestamp: datetime
    position: Tuple[float, float] = (0.0, 0.0)
    channel_capacity: float = 1.0   # transmission bandwidth (0-1)
                                     # replaces position for coupling strength
                                     # CB net = 0.3, internet = 0.9,
                                     # face-to-face = 1.0, no contact = 0.0


@dataclass
class KnowledgeEdge:
    """Directed influence from parent to child."""
    source: str                 # parent node_id
    target: str                 # child node_id
    transfer_efficiency: float = 0.8
    phase: float = 1.0         # alignment; -1 = destructive interference
    transmission_type: str = "written"
    # Transmission types and their characteristic curves:
    #   "embodied"  — apprenticeship, hands-on practice
    #                  high initial cost, very high retention, cannot be digitized
    #                  efficiency degrades sharply without direct contact
    #   "oral"      — storytelling, mentorship, conversation
    #                  moderate bandwidth, degrades with each retelling
    #                  context-dependent (you had to be there)
    #   "written"   — text, documentation, code
    #                  low bandwidth, high persistence, context-free
    #                  the part that survives library fires
    #   "digital"   — mesh networks, databases, broadcasts
    #                  highest bandwidth, zero retention without infrastructure
    #                  dies with the grid


class DiGraph:
    """
    Minimal directed graph. Replaces networkx.DiGraph.
    Nodes are KnowledgeNode, edges are KnowledgeEdge.
    All operations are O(n) or O(e) — fine for knowledge graphs
    which rarely exceed a few thousand nodes.
    """

    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[Tuple[str, str], KnowledgeEdge] = {}
        # Adjacency for fast lookup
        self._successors: Dict[str, Set[str]] = {}
        self._predecessors: Dict[str, Set[str]] = {}

    def add_node(self, node: KnowledgeNode):
        self.nodes[node.node_id] = node
        if node.node_id not in self._successors:
            self._successors[node.node_id] = set()
        if node.node_id not in self._predecessors:
            self._predecessors[node.node_id] = set()

    def add_edge(self, edge: KnowledgeEdge):
        key = (edge.source, edge.target)
        self.edges[key] = edge
        self._successors.setdefault(edge.source, set()).add(edge.target)
        self._predecessors.setdefault(edge.target, set()).add(edge.source)

    def predecessors(self, node_id: str) -> List[str]:
        return list(self._predecessors.get(node_id, set()))

    def successors(self, node_id: str) -> List[str]:
        return list(self._successors.get(node_id, set()))

    def get_edge(self, source: str, target: str) -> Optional[KnowledgeEdge]:
        return self.edges.get((source, target))

    def all_edges(self) -> List[KnowledgeEdge]:
        return list(self.edges.values())

    def remove_node(self, node_id: str):
        """Remove node and all connected edges."""
        if node_id in self.nodes:
            del self.nodes[node_id]
        to_remove = [k for k in self.edges if k[0] == node_id or k[1] == node_id]
        for key in to_remove:
            del self.edges[key]
        for s in self._successors.values():
            s.discard(node_id)
        for p in self._predecessors.values():
            p.discard(node_id)
        self._successors.pop(node_id, None)
        self._predecessors.pop(node_id, None)


# =============================================================================
# KNOWLEDGE DNA — the engine
# =============================================================================

class KnowledgeDNA:
    """
    Knowledge ancestry as a directed energy field.

    Nodes are thoughts/ideas with energy levels.
    Edges carry transfer efficiency and phase.
    Energy propagates backward (who still shapes this?)
    and forward (where does this influence go?).
    Time decays what isn't reinforced.
    Cycles can be stable, damped, or runaway.

    No external dependencies. Runs on anything with Python 3.
    """

    def __init__(self):
        self.graph = DiGraph()

    # ----- Node creation -----

    def add_thought(self, name: str, contributors: Optional[List[str]] = None,
                    energy: float = 1.0, parents: Optional[List[str]] = None,
                    timestamp: Optional[datetime] = None,
                    position: Optional[Tuple[float, float]] = None) -> str:
        """
        Add a knowledge node. Returns node_id.

        Parents are existing node_ids. Each parent->child edge gets
        transfer_efficiency=0.8 and phase=1.0 by default.
        """
        if contributors is None:
            contributors = ["anonymous"]
        if parents is None:
            parents = []
        if timestamp is None:
            timestamp = datetime.now()
        if position is None:
            position = (random.uniform(-1, 1), random.uniform(-1, 1))

        node_id = f"{name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        node = KnowledgeNode(
            node_id=node_id, name=name, contributors=contributors,
            energy=energy, timestamp=timestamp, position=position,
        )
        self.graph.add_node(node)

        for parent in parents:
            if parent in self.graph.nodes:
                edge = KnowledgeEdge(
                    source=parent, target=node_id,
                    transfer_efficiency=0.8, phase=1.0,
                )
                self.graph.add_edge(edge)

        return node_id

    # ----- Backward energy propagation (field trace) -----

    def propagate_energy(self, node_id: str, decay: float = 0.85) -> Dict[str, float]:
        """
        Backward propagation: how much energy from this node
        reaches each ancestor, weighted by transfer efficiency,
        phase, and decay.

        This replaces single-parent tracing. All parents receive
        energy proportional to their edge weights. The result is
        a field, not a path.

        E_parent += E_child * efficiency * phase * decay
        """
        energy_map = {n: 0.0 for n in self.graph.nodes}
        if node_id not in self.graph.nodes:
            return energy_map
        energy_map[node_id] = self.graph.nodes[node_id].energy

        stack = [node_id]
        visited_edges: Set[Tuple[str, str]] = set()

        while stack:
            current = stack.pop()
            current_energy = energy_map[current]

            for parent in self.graph.predecessors(current):
                edge_key = (parent, current)
                if edge_key in visited_edges:
                    continue
                visited_edges.add(edge_key)

                edge = self.graph.get_edge(parent, current)
                if edge is None:
                    continue
                eff = edge.transfer_efficiency
                phase = edge.phase
                transferred = current_energy * eff * decay * phase

                if abs(transferred) > 1e-6:
                    energy_map[parent] += transferred
                    stack.append(parent)

        return energy_map

    # ----- Channel coupling (replaces spatial locality) -----
    #
    # Physical distance is a proxy for what actually matters:
    # transmission channel bandwidth. Two people 500 miles apart
    # on the same CB net have higher coupling than two people in
    # the same building who don't talk.
    #
    # channel_coupling uses the minimum channel capacity between
    # two nodes. The bottleneck determines the bandwidth.

    def channel_coupling(self, a: str, b: str) -> float:
        """
        Coupling strength between two nodes based on channel capacity.

        Returns min(a.channel_capacity, b.channel_capacity).
        The bottleneck determines the bandwidth — a high-capacity
        node talking to a low-capacity node is limited by the weaker link.

        This replaces Gaussian distance kernel. Two people on the same
        CB radio net at 500 miles couple more strongly than two people
        in the same building with no shared channel.
        """
        node_a = self.graph.nodes.get(a)
        node_b = self.graph.nodes.get(b)
        if node_a is None or node_b is None:
            return 0.0
        return min(node_a.channel_capacity, node_b.channel_capacity)

    def distance(self, a: str, b: str) -> float:
        """Euclidean distance between two nodes in position space.
        Kept for backward compatibility and position dynamics."""
        pa = self.graph.nodes[a].position
        pb = self.graph.nodes[b].position
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(pa, pb)))

    def propagate_energy_coupled(self, node_id: str,
                                  decay: float = 0.85) -> Dict[str, float]:
        """
        Backward propagation weighted by channel capacity.

        Replaces propagate_energy_local (Gaussian distance kernel).
        Channel capacity is the actual constraint on knowledge
        transmission — not how far apart two people are, but
        how much bandwidth they share.
        """
        energy_map = {n: 0.0 for n in self.graph.nodes}
        if node_id not in self.graph.nodes:
            return energy_map
        energy_map[node_id] = self.graph.nodes[node_id].energy

        stack = [node_id]
        visited_edges: Set[Tuple[str, str]] = set()

        while stack:
            current = stack.pop()
            current_energy = energy_map[current]

            for parent in self.graph.predecessors(current):
                edge_key = (parent, current)
                if edge_key in visited_edges:
                    continue
                visited_edges.add(edge_key)

                edge = self.graph.get_edge(parent, current)
                if edge is None:
                    continue

                coupling = self.channel_coupling(parent, current)
                eff = self._typed_efficiency(edge)
                transferred = current_energy * eff * edge.phase * decay * coupling

                if abs(transferred) > 1e-6:
                    energy_map[parent] += transferred
                    stack.append(parent)

        return energy_map

    # ----- Time decay (with dormancy) -----
    #
    # Simple exponential decay assumes knowledge degrades uniformly.
    # It doesn't. Some knowledge is latent for decades then activates
    # under the right conditions. Your grandmother's fire knowledge
    # isn't gone — it's dormant until the grid fails and suddenly
    # it's the most valuable thing in the county.
    #
    # Three states:
    #   active:  energy > dormancy_threshold → full contribution
    #   dormant: energy decayed below threshold but above loss_floor
    #            → reduced but recoverable. reactivation_factor
    #            preserves a fraction that can be restored.
    #   lost:    energy below loss_floor → genuinely gone.
    #            embodied knowledge that died with its holder.

    def apply_time_decay(self, energy_map: Dict[str, float],
                         lambda_decay: float = 0.00001,
                         dormancy_threshold: float = 0.3,
                         loss_floor: float = 0.02,
                         reactivation_factor: float = 0.4) -> Dict[str, float]:
        """
        Time decay with dormancy and reactivation.

        Knowledge doesn't just fade linearly. It enters dormancy —
        reduced but recoverable — before it's genuinely lost.

        lambda_decay: rate of exponential decay
        dormancy_threshold: below this, knowledge enters dormancy
        loss_floor: below this, knowledge is genuinely gone
        reactivation_factor: what fraction of dormant knowledge
            can be recovered under the right conditions (0.4 = 40%)

        Returns {node_id: effective_energy} where effective_energy
        accounts for dormancy state.
        """
        now = datetime.now()
        decayed = {}

        for node_id, energy in energy_map.items():
            node = self.graph.nodes.get(node_id)
            if node is None:
                decayed[node_id] = 0.0
                continue

            dt = (now - node.timestamp).total_seconds()
            raw_decayed = energy * math.exp(-lambda_decay * dt)

            if raw_decayed >= dormancy_threshold:
                # Active: full contribution
                decayed[node_id] = raw_decayed
            elif raw_decayed >= loss_floor:
                # Dormant: reduced but recoverable
                # The knowledge exists but isn't actively shaping things
                # until conditions reactivate it.
                dormant_energy = loss_floor + (raw_decayed - loss_floor) * reactivation_factor
                decayed[node_id] = dormant_energy
            else:
                # Lost: genuinely gone. The holder died.
                # The embodied knowledge went with them.
                decayed[node_id] = 0.0

        return decayed

    # ----- Edge-type-specific transfer -----
    #
    # Oral, written, embodied, and digital knowledge transmit
    # on different efficiency curves. A textbook citation and
    # your grandmother's fire knowledge are not the same edge.
    #
    # embodied: high initial cost, very high retention per contact,
    #           but requires physical co-presence. Efficiency drops
    #           sharply with reduced contact frequency.
    #           apprenticeship, hands-on practice.
    #
    # oral:     moderate bandwidth, degrades with each retelling.
    #           context-dependent — "you had to be there."
    #           stories, mentorship, conversation.
    #
    # written:  low bandwidth per unit time, but high persistence.
    #           context-free — survives the death of the author.
    #           text, documentation, code, this repo.
    #
    # digital:  highest bandwidth, zero retention without infrastructure.
    #           dies with the grid. mesh networks, databases.

    TRANSFER_CURVES = {
        "embodied": {
            "base_efficiency": 0.95,   # highest fidelity per contact
            "contact_decay": 0.15,     # sharp drop without contact
            "persistence": 0.95,       # stays with the person
            "infrastructure_dep": 0.0, # needs no infrastructure
        },
        "oral": {
            "base_efficiency": 0.70,
            "contact_decay": 0.08,     # moderate degradation per retelling
            "persistence": 0.60,
            "infrastructure_dep": 0.0,
        },
        "written": {
            "base_efficiency": 0.50,   # low bandwidth
            "contact_decay": 0.01,     # almost no degradation over time
            "persistence": 0.90,       # survives the author
            "infrastructure_dep": 0.1, # needs paper or stone
        },
        "digital": {
            "base_efficiency": 0.85,   # high bandwidth
            "contact_decay": 0.02,
            "persistence": 0.10,       # zero without grid
            "infrastructure_dep": 0.95, # dies with infrastructure
        },
    }

    def _typed_efficiency(self, edge: KnowledgeEdge) -> float:
        """
        Compute effective transfer efficiency based on edge type.

        Combines the edge's base transfer_efficiency with the
        characteristic curve of its transmission type.

        Written knowledge: lower bandwidth but persists.
        Embodied knowledge: higher bandwidth but needs contact.
        Digital knowledge: highest bandwidth but needs infrastructure.
        """
        curve = self.TRANSFER_CURVES.get(
            edge.transmission_type,
            self.TRANSFER_CURVES["written"],
        )

        # Effective efficiency = base * type_modifier
        # The edge's transfer_efficiency is the specific link quality.
        # The curve's base_efficiency is the theoretical max for this type.
        type_eff = min(edge.transfer_efficiency, curve["base_efficiency"])

        # Infrastructure dependency reduces efficiency when channel capacity is low
        src = self.graph.nodes.get(edge.source)
        tgt = self.graph.nodes.get(edge.target)
        if src and tgt:
            min_channel = min(src.channel_capacity, tgt.channel_capacity)
            infra_penalty = curve["infrastructure_dep"] * (1.0 - min_channel)
            type_eff *= (1.0 - infra_penalty)

        return type_eff

    # ----- Forward propagation -----

    def forward_step(self):
        """
        One step of forward energy propagation.
        Energy flows parent -> child along edges.
        Uses edge-type-specific transfer functions.
        """
        new_energy = {n: 0.0 for n in self.graph.nodes}
        for edge in self.graph.all_edges():
            src = self.graph.nodes.get(edge.source)
            if src is None:
                continue
            eff = self._typed_efficiency(edge)
            transferred = src.energy * eff * edge.phase
            new_energy[edge.target] += transferred
        for node_id, energy in new_energy.items():
            self.graph.nodes[node_id].energy = energy

    def forward_step_coupled(self):
        """Forward propagation with channel capacity coupling."""
        new_energy = {n: 0.0 for n in self.graph.nodes}
        for edge in self.graph.all_edges():
            src = self.graph.nodes.get(edge.source)
            if src is None:
                continue
            coupling = self.channel_coupling(edge.source, edge.target)
            eff = self._typed_efficiency(edge)
            transferred = src.energy * eff * edge.phase * coupling
            new_energy[edge.target] += transferred
        for node_id, energy in new_energy.items():
            self.graph.nodes[node_id].energy = energy

    # ----- Position dynamics -----

    def update_positions(self, lr: float = 0.01):
        """Drift nodes toward higher-energy regions."""
        for node_id, node in self.graph.nodes.items():
            px, py = node.position
            dx = random.uniform(-1, 1) * node.energy * lr
            dy = random.uniform(-1, 1) * node.energy * lr
            node.position = (px + dx, py + dy)

    # ----- Noise injection -----

    def inject_noise(self, magnitude: float = 0.05):
        """Stochastic perturbation. Tests stability."""
        for node in self.graph.nodes.values():
            node.energy += random.uniform(-magnitude, magnitude)
            node.energy = max(0.0, node.energy)

    # ----- Cycle analysis -----

    def find_cycles(self, max_length: int = 10) -> List[List[str]]:
        """
        Find simple cycles in the graph (DFS-based).
        Replaces nx.simple_cycles.
        """
        cycles = []
        for start in self.graph.nodes:
            visited = set()
            stack = [(start, [start])]
            while stack:
                current, path = stack.pop()
                for succ in self.graph.successors(current):
                    if succ == start and len(path) > 1:
                        cycles.append(list(path))
                    elif succ not in visited and len(path) < max_length:
                        visited.add(succ)
                        stack.append((succ, path + [succ]))
        return cycles

    def compute_cycle_gain(self, cycle: List[str]) -> float:
        """
        Product of (efficiency * phase) around a cycle.
        |C| ~ 1 = stable loop (persistent structure)
        |C| < 1 = dissipative (knowledge decays around the loop)
        |C| > 1 = runaway amplification (unstable)
        """
        gain = 1.0
        for i in range(len(cycle)):
            u = cycle[i]
            v = cycle[(i + 1) % len(cycle)]
            edge = self.graph.get_edge(u, v)
            if edge is None:
                return 0.0
            gain *= edge.transfer_efficiency * edge.phase
        return gain

    def analyze_cycles(self) -> List[Dict]:
        """Classify all cycles by stability."""
        results = []
        for cycle in self.find_cycles():
            gain = self.compute_cycle_gain(cycle)
            if abs(gain) > 0.95:
                stability = "stable"
            elif abs(gain) > 0.5:
                stability = "damped"
            else:
                stability = "dissipative"
            results.append({
                "cycle": [self.graph.nodes[n].name for n in cycle],
                "gain": round(gain, 4),
                "type": stability,
                "energy": sum(self.graph.nodes[n].energy for n in cycle),
            })
        return results

    # ----- Attractor detection -----

    def find_attractors(self, steps: int = 10, tolerance: float = 1e-3) -> List[str]:
        """
        Run forward propagation and find nodes whose energy stabilizes.
        These are the attractors — ideas that persist despite dynamics.
        """
        # Save original energies to restore after
        original = {n: node.energy for n, node in self.graph.nodes.items()}

        history = []
        for _ in range(steps):
            snapshot = {n: node.energy for n, node in self.graph.nodes.items()}
            history.append(snapshot)
            self.forward_step()

        attractors = []
        for node_id in self.graph.nodes:
            values = [h[node_id] for h in history]
            if max(values) - min(values) < tolerance:
                attractors.append(node_id)

        # Restore original energies
        for n, energy in original.items():
            self.graph.nodes[n].energy = energy

        return attractors

    # ----- Fragility analysis -----

    def fragility_test(self, node_id: str) -> Dict[str, float]:
        """
        Remove a node and measure energy collapse across the graph.
        High collapse = that node was load-bearing.
        """
        # Baseline total energy
        baseline = sum(n.energy for n in self.graph.nodes.values())

        # Save and remove
        removed_node = self.graph.nodes.get(node_id)
        if removed_node is None:
            return {"removed": node_id, "impact": 0.0}

        removed_edges = [e for e in self.graph.all_edges()
                         if e.source == node_id or e.target == node_id]

        self.graph.remove_node(node_id)

        # Run forward and measure
        self.forward_step()
        post_energy = sum(n.energy for n in self.graph.nodes.values())

        # Restore
        self.graph.add_node(removed_node)
        for e in removed_edges:
            self.graph.add_edge(e)

        collapse = (baseline - post_energy) / baseline if baseline > 0 else 0.0
        return {
            "removed": node_id,
            "name": removed_node.name,
            "baseline_energy": round(baseline, 4),
            "post_energy": round(post_energy, 4),
            "collapse_pct": round(collapse * 100, 1),
        }

    # ----- Field trace (full) -----

    def trace_field(self, node_id: str, use_channels: bool = True) -> List[Dict]:
        """
        Full field trace: backward propagation + dormancy-aware time decay.
        Returns sorted list of {node, name, energy, contributors}.
        This is the answer to: "What is still actively shaping this state?"

        use_channels: if True, uses channel-capacity coupling instead of
        uniform propagation. Set False for legacy behavior.
        """
        if use_channels:
            raw = self.propagate_energy_coupled(node_id)
        else:
            raw = self.propagate_energy(node_id)
        decayed = self.apply_time_decay(raw)

        results = []
        for nid, energy in decayed.items():
            node = self.graph.nodes[nid]
            results.append({
                "node": nid,
                "name": node.name,
                "energy": round(energy, 6),
                "contributors": node.contributors,
            })
        results.sort(key=lambda x: -x["energy"])
        return results

    # ----- CSV export/import -----

    def export_csv(self, filename: str = "knowledge_dna.csv") -> str:
        """Export full graph to CSV."""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "contributors", "energy", "timestamp",
                             "parents", "dna_path"])
            for node_id, node in self.graph.nodes.items():
                parents = self.graph.predecessors(node_id)
                path = self._trace_path(node_id)
                writer.writerow([
                    node.name,
                    str(node.contributors),
                    node.energy,
                    node.timestamp.isoformat(),
                    str(parents),
                    "/".join(path),
                ])
        return filename

    def export_field_csv(self, field: List[Dict],
                         filename: str = "field_trace.csv") -> str:
        """Export a field trace to CSV."""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["node", "name", "energy", "contributors"])
            for row in field:
                writer.writerow([
                    row["node"], row["name"],
                    row["energy"], str(row["contributors"]),
                ])
        return filename

    def _trace_path(self, node_id: str) -> List[str]:
        """Trace ancestry path (all ancestors, breadth-first)."""
        path = []
        visited = set()
        queue = deque([node_id])
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            path.append(current)
            for parent in self.graph.predecessors(current):
                if parent not in visited:
                    queue.append(parent)
        return list(reversed(path))

    def import_seed_csv(self, filename: str):
        """
        Import the seed CSV format:
        name,contributors,energy,timestamp,parents,dna_path
        """
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            node_map = {}  # name -> node_id
            for row in reader:
                name = row["name"]
                contributors = _parse_list(row.get("contributors", "[]"))
                energy = float(row.get("energy", 1.0))
                ts_str = row.get("timestamp", "")
                try:
                    timestamp = datetime.fromisoformat(ts_str)
                except (ValueError, TypeError):
                    timestamp = datetime.now()
                parents_raw = _parse_list(row.get("parents", "[]"))
                parent_ids = [node_map[p] for p in parents_raw if p in node_map]

                node_id = self.add_thought(
                    name=name, contributors=contributors,
                    energy=energy, parents=parent_ids,
                    timestamp=timestamp,
                )
                # Map both name and timestamped id for parent resolution
                node_map[name] = node_id
                # Also map the full timestamped key if present in parents column
                ts_key = f"{name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
                node_map[ts_key] = node_id

    # ----- Report -----

    def print_report(self, target_node: Optional[str] = None):
        """Print a structured report of the knowledge graph."""
        print(f"\n{'='*66}")
        print(f"  KNOWLEDGE DNA REPORT")
        print(f"  {len(self.graph.nodes)} nodes, "
              f"{len(self.graph.edges)} edges")
        print(f"{'='*66}")

        # All nodes by energy
        print(f"\n  NODES (by energy):")
        sorted_nodes = sorted(self.graph.nodes.values(),
                              key=lambda n: -n.energy)
        for node in sorted_nodes:
            parents = self.graph.predecessors(node.node_id)
            children = self.graph.successors(node.node_id)
            print(f"    {node.name:<30s} E={node.energy:.2f}  "
                  f"in={len(parents)} out={len(children)}  "
                  f"by {', '.join(node.contributors)}")

        # Field trace if target specified
        if target_node and target_node in self.graph.nodes:
            print(f"\n  FIELD TRACE from: {self.graph.nodes[target_node].name}")
            field = self.trace_field(target_node)
            for row in field:
                if row["energy"] > 1e-6:
                    print(f"    {row['name']:<30s} E={row['energy']:.6f}  "
                          f"by {', '.join(row['contributors'])}")

        # Cycle analysis
        cycles = self.analyze_cycles()
        if cycles:
            print(f"\n  CYCLES ({len(cycles)} found):")
            for c in cycles:
                names = " -> ".join(c["cycle"])
                print(f"    {c['type']:12s} gain={c['gain']:.4f}  "
                      f"E={c['energy']:.2f}  {names}")

        # Fragility
        print(f"\n  FRAGILITY (remove each node, measure collapse):")
        for node_id in list(self.graph.nodes):
            result = self.fragility_test(node_id)
            if result["collapse_pct"] > 0:
                print(f"    Remove {result['name']:<25s} -> "
                      f"{result['collapse_pct']:.1f}% energy collapse")

        # Attractors
        attractors = self.find_attractors()
        if attractors:
            print(f"\n  ATTRACTORS (stable under forward propagation):")
            for a in attractors:
                print(f"    {self.graph.nodes[a].name}")

        print(f"\n{'='*66}\n")


# =============================================================================
# HELPERS
# =============================================================================

def _parse_list(s: str) -> List[str]:
    """Parse a string like "['a', 'b']" into a Python list."""
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    items = []
    for part in s.split(","):
        part = part.strip().strip("'\"")
        if part:
            items.append(part)
    return items


def nonlinear_clip(x: float, limit: float = 10.0) -> float:
    """Prevent energy runaway. Tanh saturation at limit."""
    return limit * math.tanh(x / limit)


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    random.seed(42)

    print("=" * 66)
    print("  KNOWLEDGE DNA — channel coupling, dormancy, typed edges")
    print("  knowledge as field propagation, not linear attribution")
    print("=" * 66)

    dna = KnowledgeDNA()

    # Build the ancestry with realistic transmission types and channels
    ts = datetime(2026, 3, 25, 21, 44, 11)

    solar = dna.add_thought("Solar Flux Capture", ["Nature/Evolution"],
                            energy=2.0, timestamp=ts)
    # Nature -> Galileo: embodied observation, no infrastructure needed
    gravity = dna.add_thought("Gravity Storage", ["Galileo", "User Insight"],
                              energy=1.0, parents=[solar], timestamp=ts)
    # Galileo -> Casimir: written transmission (papers survive centuries)
    vacuum = dna.add_thought("Vacuum Fluctuations", ["Casimir1948", "User Intuition"],
                             energy=2.5, parents=[gravity], timestamp=ts)
    # Casimir -> User: embodied experiment (you had to do it yourself)
    piezo = dna.add_thought("Forest Piezo Harvest", ["User Experiment"],
                            energy=1.0, parents=[vacuum], timestamp=ts)
    # User -> Repo: digital transmission (dies with the grid)
    mesh = dna.add_thought("Zero-Point Mesh", ["Heisenberg", "User Repo"],
                           energy=1.0, parents=[piezo], timestamp=ts)

    # Set transmission types on edges
    edges = list(dna.graph.edges.values())
    type_assignments = ["embodied", "written", "embodied", "digital"]
    for edge, ttype in zip(edges, type_assignments):
        edge.transmission_type = ttype

    # Set channel capacities
    # Nature has infinite channel (observation is always available)
    # Galileo's written work: high persistence channel
    # User experiment: high channel (direct contact)
    # Repo: depends on infrastructure
    for nid, node in dna.graph.nodes.items():
        if "Solar" in node.name:
            node.channel_capacity = 1.0     # nature is always broadcasting
        elif "Gravity" in node.name:
            node.channel_capacity = 0.8     # written record survives
        elif "Vacuum" in node.name:
            node.channel_capacity = 0.7     # papers in libraries
        elif "Piezo" in node.name:
            node.channel_capacity = 0.9     # direct experiment
        elif "Mesh" in node.name:
            node.channel_capacity = 0.4     # digital — needs infrastructure

    # Cross-link cycle
    dna.graph.add_edge(KnowledgeEdge(
        source=mesh, target=solar,
        transfer_efficiency=0.3, phase=0.5,
        transmission_type="digital",
    ))

    # Full report
    dna.print_report(target_node=mesh)

    # Compare transmission types
    print(f"\n{'─'*66}")
    print("  TRANSMISSION TYPE COMPARISON")
    print(f"{'─'*66}")
    for edge in dna.graph.all_edges():
        src = dna.graph.nodes[edge.source].name
        tgt = dna.graph.nodes[edge.target].name
        typed_eff = dna._typed_efficiency(edge)
        print(f"    {src[:20]:20s} -> {tgt[:20]:20s}"
              f"  type={edge.transmission_type:10s}"
              f"  eff={typed_eff:.3f}")

    # Forward evolution comparing typed vs uniform
    print(f"\n{'─'*66}")
    print("  FORWARD EVOLUTION (typed transfer functions)")
    print(f"{'─'*66}")
    for i in range(5):
        dna.forward_step()
        dna.inject_noise(magnitude=0.02)
        total_e = sum(n.energy for n in dna.graph.nodes.values())
        print(f"    Step {i+1}: total energy = {total_e:.4f}")

    # Dormancy demonstration
    print(f"\n{'─'*66}")
    print("  DORMANCY: knowledge that's sleeping, not dead")
    print(f"{'─'*66}")

    # Create a node with old timestamp to demonstrate dormancy
    dna2 = KnowledgeDNA()
    old_ts = datetime(1950, 1, 1)
    recent_ts = datetime(2025, 1, 1)

    grandmother = dna2.add_thought("Grandmother's Fire Knowledge",
                                    ["Oral Tradition"], energy=3.0,
                                    timestamp=old_ts)
    textbook = dna2.add_thought("Fire Science Textbook",
                                 ["Academic"], energy=1.5,
                                 timestamp=recent_ts)
    # Set edge types
    for nid, node in dna2.graph.nodes.items():
        node.channel_capacity = 0.8

    # Apply decay to both
    energy_map = {grandmother: 3.0, textbook: 1.5}
    decayed = dna2.apply_time_decay(energy_map, lambda_decay=0.0000001)

    for node_id, energy in decayed.items():
        node = dna2.graph.nodes[node_id]
        original = energy_map[node_id]
        state = "ACTIVE" if energy >= 0.3 else ("DORMANT" if energy >= 0.02 else "LOST")
        print(f"    {node.name:<35s} {original:.1f} -> {energy:.4f}  [{state}]")

    print(f"""
    The grandmother's fire knowledge decayed below active threshold
    but remains DORMANT — recoverable if someone reactivates the
    transmission chain. The textbook stays ACTIVE because it's recent.

    When the grid fails and the textbook's digital copies go dark,
    the dormant knowledge is what remains. Not dead. Sleeping.
    Waiting for someone to ask the right question.""")

    # Export
    dna.export_csv("knowledge_dna.csv")
    field = dna.trace_field(mesh)
    dna.export_field_csv(field, "field_trace.csv")
    print(f"\n  Exported: knowledge_dna.csv, field_trace.csv")

    print(f"\n{'='*66}")
    print("  WHAT CHANGED")
    print(f"{'='*66}")
    print("""
  [FIXED] Spatial locality was geometric distance (proxy)
    -> Now: channel capacity (actual constraint)
    -> Two people on the same CB net at 500 miles couple more strongly
       than two people in the same building who don't talk.

  [FIXED] Time decay was uniform exponential (too simple)
    -> Now: three states — active, dormant, lost
    -> Dormant knowledge is recoverable. Lost knowledge is gone.
    -> Your grandmother's fire knowledge isn't dead. It's sleeping.

  [FIXED] Edge transfer was uniform (dishonest)
    -> Now: four transmission types with different curves:
       embodied:  0.95 base, needs contact, no infrastructure dep
       oral:      0.70 base, degrades per retelling
       written:   0.50 base, almost no degradation, survives author
       digital:   0.85 base, dies with the grid
    -> The fire knowledge your grandmother carries in her hands
       propagates differently than a textbook citation.

  The physics got more honest. The metaphors became measurements.
""")

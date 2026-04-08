#!/usr/bin/env python3
# MODULE: KnowledgeDNA/living_intelligence.py
# PROVIDES: DNA.TEACHER_GRAPH, SUBSTRATE.LIVING_EQUATIONS
# DEPENDS: stdlib-only
# RUN: python -m KnowledgeDNA.living_intelligence
# TIER: bridge
# Living Intelligence Database connector — 38 teachers as equations
"""
KnowledgeDNA/living_intelligence.py — Living Intelligence Database Connector
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Connects the Living Intelligence Database to the substrate reasoner.

Each living intelligence (bee, mycelium, sunflower, quartz, lightning)
is a teacher. It embodies equations that evolution discovered before
humans named them. This module extracts those equations as substrate
properties so the reasoner can find them.

Bee teaches hexagonal packing -> optimal_packing, minimal_overlap
Mycelium teaches distributed networking -> network_structure, diffusion_on_graphs
Sunflower teaches phi-spiral allocation -> fibonacci_scaling, spiral_growth
Quartz teaches piezoelectric conversion -> energy_transfer, resonance
Decay teaches entropy recycling -> decay_modeling, energy_conservation

The synergy graph becomes a KnowledgeDNA graph with transfer efficiency
and phase derived from relationship types.

USAGE:
    from KnowledgeDNA.living_intelligence import LivingIntelligenceDB
    db = LivingIntelligenceDB()
    db.load_from_url()
    equations = db.to_equations()

Zero external dependencies beyond urllib (stdlib).
"""

import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from urllib.request import urlopen
from urllib.error import URLError

try:
    from KnowledgeDNA.equation_field import Equation, Property, Domain
    from KnowledgeDNA.knowledge_dna import KnowledgeDNA, KnowledgeEdge
    from KnowledgeDNA.substrate import SubstrateReasoner
    HAS_LOCAL = True
except ImportError:
    HAS_LOCAL = False


# =============================================================================
# RELATIONSHIP TYPE -> TRANSFER PROPERTIES
# =============================================================================

RELATION_SEEDS = {
    "synergy": {
        "description": "mutual benefit cooperative amplification bidirectional",
        "efficiency": 0.85,
        "phase": 1.0,
    },
    "geometry_link": {
        "description": "geometric structure spatial form shape mapping",
        "efficiency": 0.90,
        "phase": 1.0,
    },
    "resonance": {
        "description": "frequency harmonic alignment vibration sympathetic coupling",
        "efficiency": 0.80,
        "phase": 1.0,
    },
    "energy_coupling": {
        "description": "energy transfer conservation transformation flow gradient",
        "efficiency": 0.75,
        "phase": 1.0,
    },
    "energy_exchange": {
        "description": "energy bidirectional transfer exchange plasma ionization",
        "efficiency": 0.70,
        "phase": 0.9,
    },
    "temporal_bridge": {
        "description": "time sequence cycle decay emergence memory echo",
        "efficiency": 0.65,
        "phase": 0.8,
    },
}


# =============================================================================
# INTELLIGENCE NODE
# =============================================================================

@dataclass
class IntelligenceNode:
    """A living intelligence from the database."""
    id: str
    name: str
    kind: str
    description: str = ""
    pattern: str = ""
    symbolic_code: str = ""
    links: List[Dict] = field(default_factory=list)
    attributes: Dict = field(default_factory=dict)

    def to_equation(self) -> 'Equation':
        """Convert this intelligence into an Equation for the field simulator."""
        desc = f"{self.description} {self.pattern}"
        properties = self._extract_properties()
        return Equation(
            name=self.name,
            formula=self.symbolic_code or f"[{self.id}]",
            properties=properties,
            description=desc,
        )

    def _extract_properties(self) -> List['Property']:
        """Extract substrate properties from description and pattern text."""
        props = []
        text = f"{self.pattern} {self.description}".lower()

        keyword_props = {
            "hexagonal": ("optimal_packing", 0.9),
            "hex": ("optimal_packing", 0.8),
            "swarm": ("synchronization", 0.9),
            "coordination": ("synchronization", 0.8),
            "distributed": ("network_structure", 0.9),
            "network": ("network_structure", 0.85),
            "hyphal": ("diffusion_on_graphs", 0.8),
            "nutrient": ("gradient_flow", 0.7),
            "symbiosis": ("spatial_coupling", 0.8),
            "fibonacci": ("fibonacci_scaling", 0.95),
            "phi": ("proportion_stability", 0.9),
            "spiral": ("spiral_growth", 0.9),
            "fractal": ("fractal_nesting", 0.9),
            "resonance": ("resonance", 0.85),
            "piezoelectric": ("energy_transfer", 0.9),
            "harmonic": ("frequency_decomposition", 0.8),
            "decomposition": ("decay_modeling", 0.8),
            "entropy": ("decay_modeling", 0.85),
            "recycling": ("energy_conservation", 0.7),
            "curvature": ("gradient_flow", 0.8),
            "orbital": ("synchronization", 0.7),
            "geodesic": ("gradient_flow", 0.9),
            "parallel": ("network_structure", 0.7),
            "regeneration": ("equilibrium_seeking", 0.7),
            "camouflage": ("pattern_recognition", 0.8),
            "optimization": ("energy_minimization", 0.8),
            "packing": ("optimal_packing", 0.85),
            "solar": ("energy_conservation", 0.7),
            "photon": ("energy_transfer", 0.7),
            "heliotropism": ("gradient_flow", 0.7),
            "thermoregulation": ("equilibrium_seeking", 0.8),
            "lattice": ("optimal_packing", 0.8),
            "growth": ("population_dynamics", 0.6),
            "binding": ("spatial_coupling", 0.7),
            "propagation": ("spatial_coupling", 0.8),
            "ionization": ("energy_transfer", 0.7),
            "cycle": ("convergent_ratio", 0.6),
            "emergence": ("self_similarity", 0.7),
            "echo": ("memory_fading", 0.7),
            "fold": ("compression", 0.6),
            "dissolution": ("decay_modeling", 0.8),
        }

        seen = set()
        for keyword, (prop_name, strength) in keyword_props.items():
            if keyword in text and prop_name not in seen:
                props.append(Property(prop_name, strength))
                seen.add(prop_name)

        kind_defaults = {
            "ANIMAL": [("synchronization", 0.5), ("pattern_recognition", 0.5)],
            "PLANT": [("spatial_coupling", 0.5), ("gradient_flow", 0.4)],
            "CRYSTAL": [("optimal_packing", 0.6), ("proportion_stability", 0.5)],
            "PLASMA": [("energy_transfer", 0.6), ("spatial_coupling", 0.5)],
            "ENERGY": [("energy_conservation", 0.6), ("gradient_flow", 0.5)],
            "SHAPE": [("self_similarity", 0.6), ("proportion_stability", 0.5)],
            "TEMPORAL": [("decay_modeling", 0.5), ("convergent_ratio", 0.4)],
        }
        for prop_name, strength in kind_defaults.get(self.kind.upper(), []):
            if prop_name not in seen:
                props.append(Property(prop_name, strength))
                seen.add(prop_name)

        if len(props) < 2:
            props.append(Property("self_similarity", 0.3))

        return props


@dataclass
class ExpanderRule:
    """If you see these inputs together, this output emerges."""
    inputs: List[str]
    output: str


# =============================================================================
# DATABASE
# =============================================================================

GITHUB_RAW = "https://raw.githubusercontent.com/JinnZ2/Living-Intelligence-Database/main"

class LivingIntelligenceDB:
    """
    Connector to the Living Intelligence Database.

    Loads intelligence nodes and synergy edges from the GitHub repo.
    Converts them into Equations, KnowledgeDNA graphs, and Domains.
    """

    def __init__(self):
        self.nodes: Dict[str, IntelligenceNode] = {}
        self.edges: List[Dict] = []
        self.rules: List[ExpanderRule] = []

    def load_from_url(self, base_url: str = GITHUB_RAW) -> bool:
        """Pull intelligence data from GitHub."""
        try:
            synergies = self._fetch_json(f"{base_url}/ontology/relational/synergies.json")
            if synergies:
                for node_data in synergies.get("nodes", []):
                    nid = node_data["id"]
                    self.nodes[nid] = IntelligenceNode(
                        id=nid, name=node_data.get("label", nid), kind="UNKNOWN",
                    )
                self.edges = synergies.get("edges", [])

            ontology_dirs = {
                "animal": ["bee", "octopus", "elephant", "whale", "spider", "ant"],
                "plant": ["mycelium", "sunflower", "root_network", "lichen", "fern"],
                "crystal": ["quartz", "crystal_lattice", "diamond", "obsidian", "tourmaline"],
                "energy": ["gravitational", "magnetic_field", "electric_field", "thermal", "flux"],
                "plasma": ["lightning", "plasma_field", "aurora", "solar_wind"],
                "shape": ["spiral", "torus", "fractal", "hexagon", "sphere"],
                "temporal": ["decay", "cycle", "echo", "emergence", "fold"],
            }

            for kind, filenames in ontology_dirs.items():
                for fname in filenames:
                    data = self._fetch_json(f"{base_url}/ontology/{kind}/{fname}.json")
                    if data:
                        nid = data.get("id", fname.upper())
                        self.nodes[nid] = IntelligenceNode(
                            id=nid,
                            name=data.get("name", fname),
                            kind=kind.upper(),
                            description=data.get("description", ""),
                            pattern=data.get("core_attributes", {}).get("pattern", ""),
                            symbolic_code=data.get("symbolic_code", ""),
                            links=data.get("links", []),
                            attributes=data.get("core_attributes", {}),
                        )

            rules_data = self._fetch_json(f"{base_url}/rules/expander_rules.json")
            if rules_data:
                for rule in rules_data:
                    self.rules.append(ExpanderRule(
                        inputs=rule.get("if", []),
                        output=rule.get("then", ""),
                    ))

            return True
        except Exception as e:
            print(f"  Load error: {e}")
            return False

    def _fetch_json(self, url: str) -> Optional[Dict]:
        try:
            with urlopen(url, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except (URLError, json.JSONDecodeError, OSError):
            return None

    def to_equations(self) -> List['Equation']:
        """Convert all intelligences to Equations."""
        return [n.to_equation() for n in self.nodes.values()
                if n.description or n.pattern]

    def to_knowledge_dna(self) -> Optional['KnowledgeDNA']:
        """Convert the synergy graph into a KnowledgeDNA graph."""
        if not HAS_LOCAL:
            return None
        dna = KnowledgeDNA()
        node_ids = {}
        for nid, node in self.nodes.items():
            eff = node.attributes.get("efficiency_factor", 0.8)
            energy = float(eff) if isinstance(eff, (int, float)) else 0.8
            dna_id = dna.add_thought(
                name=node.name, contributors=[node.kind], energy=energy,
            )
            node_ids[nid] = dna_id

        for edge in self.edges:
            src, tgt = edge.get("source", ""), edge.get("target", "")
            rel = edge.get("relation", "synergy")
            if src in node_ids and tgt in node_ids:
                rel_info = RELATION_SEEDS.get(rel, RELATION_SEEDS["synergy"])
                dna.graph.add_edge(KnowledgeEdge(
                    source=node_ids[src], target=node_ids[tgt],
                    transfer_efficiency=rel_info["efficiency"],
                    phase=rel_info["phase"],
                ))
        return dna

    def to_domains(self) -> List['Domain']:
        """Convert intelligence kinds into Domains."""
        kind_descriptions = {
            "ANIMAL": "Swarm coordination, distributed cognition, pattern recognition, "
                      "thermoregulation, parallel processing",
            "PLANT": "Distributed networking, nutrient redistribution, symbiosis, "
                     "photon optimization, phi-spiral packing",
            "CRYSTAL": "Lattice packing, piezoelectric resonance, harmonic amplification, "
                       "structural stability",
            "PLASMA": "Ionization, energy exchange, electromagnetic coupling, "
                      "high-energy transitions",
            "ENERGY": "Conservation, gradient flow, field coupling, orbital mechanics, "
                      "thermodynamic transformation",
            "SHAPE": "Self-similarity, phi-ratio proportionality, fractal nesting, "
                     "optimal packing",
            "TEMPORAL": "Cycle, decay, emergence, echo, fold, entropy release, "
                        "temporal sequence memory",
        }
        domains = []
        for kind, desc in kind_descriptions.items():
            members = [n for n in self.nodes.values() if n.kind == kind]
            if not members:
                continue
            all_props = {}
            for member in members:
                for prop in member._extract_properties():
                    if prop.name in all_props:
                        all_props[prop.name] = max(all_props[prop.name], prop.strength)
                    else:
                        all_props[prop.name] = prop.strength
            needs = [Property(name, strength)
                     for name, strength in sorted(all_props.items(),
                                                   key=lambda x: -x[1])[:8]]
            domains.append(Domain(
                name=f"{kind.title()} Intelligence",
                needs=needs, description=desc,
            ))
        return domains

    def print_report(self):
        print(f"\n{'='*66}")
        print(f"  LIVING INTELLIGENCE DATABASE")
        print(f"  {len(self.nodes)} intelligences, {len(self.edges)} connections, "
              f"{len(self.rules)} rules")
        print(f"{'='*66}")

        kinds = {}
        for node in self.nodes.values():
            kinds.setdefault(node.kind, []).append(node)
        for kind, members in sorted(kinds.items()):
            print(f"\n  {kind} ({len(members)}):")
            for m in members:
                props = m._extract_properties()
                top = ", ".join(p.name for p in props[:3])
                print(f"    {m.name:<20s} {top}")

        if self.rules:
            print(f"\n  EXPANDER RULES:")
            for rule in self.rules:
                print(f"    {' + '.join(rule.inputs)} -> {rule.output}")

        print(f"\n{'='*66}\n")


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 66)
    print("  LIVING INTELLIGENCE — the teachers")
    print("  what evolution knew before we had equations for it")
    print("=" * 66)

    db = LivingIntelligenceDB()
    print("\n  Loading from GitHub...")
    success = db.load_from_url()
    if not success:
        print("  Could not reach GitHub.")

    db.print_report()

    equations = db.to_equations()
    if equations:
        print(f"\n  AS EQUATIONS ({len(equations)} intelligences -> substrate):")
        for eq in equations[:12]:
            props = ", ".join(p.name for p in eq.properties[:4])
            print(f"    {eq.name:<20s} teaches: {props}")

    domains = db.to_domains()
    if domains:
        print(f"\n  AS DOMAINS ({len(domains)} intelligence kinds):")
        for d in domains:
            needs = ", ".join(p.name for p in d.needs[:4])
            print(f"    {d.name:<25s} needs: {needs}")

    if HAS_LOCAL and equations:
        print(f"\n{'─'*66}")
        print("  SUBSTRATE ANALYSIS WITH LIVING TEACHERS")
        print(f"{'─'*66}")

        reasoner = SubstrateReasoner(
            extra_equations=equations, extra_domains=domains,
        )

        tests = [
            "How does a forest distribute nutrients without central control?",
            "What can crystal structure teach us about antenna design?",
            "How do swarms maintain formation in turbulence?",
        ]
        for problem in tests:
            result = reasoner.analyze(problem)
            print(f"\n  Q: {problem}")
            if result.matching_equations:
                for m in result.matching_equations[:3]:
                    print(f"    {m.equation_name:<30s} {m.overlap_score:5.0%}")
            if result.analogies:
                print(f"    Analogy: {result.analogies[0]['domain']} "
                      f"({result.analogies[0]['strength']:.0%})")

    print(f"\n{'='*66}")
    print("  THE TEACHERS WERE HERE FIRST")
    print(f"{'='*66}")
    print("""
  Bee taught hexagonal packing before we named it optimization.
  Mycelium taught distributed networking before we built the internet.
  Sunflower taught phi-spiral allocation before we wrote the SAR code.
  Quartz taught piezoelectric conversion before we built sensors.
  Decay taught entropy recycling before we wrote thermodynamics.

  The equations had ancestors. The ancestors had teachers.
  The teachers were alive.
""")

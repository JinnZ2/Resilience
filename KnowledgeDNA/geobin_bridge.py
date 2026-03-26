#!/usr/bin/env python3
"""
KnowledgeDNA/geobin_bridge.py — Geometric-to-Binary ↔ Substrate Bridge
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Connects the GEIS (Geometric Encoding Identity System) from
geometric-to-binary to the substrate reasoning engine.

The fieldlink.json defines how repos share patterns:
  - Octahedral vertex bits (000-111) = 6 directions
  - Operators (O, I, X, Δ) = transformations
  - phi_coherence = golden ratio alignment
  - bridges = which domains a pattern activates

These map directly to:
  - seed_protocol.py octahedral directions
  - equation_field.py properties
  - substrate.py reasoning vectors

This module bridges them so patterns discovered in one repo
(Mandala, Rosetta, Polyhedral, BioGrid) automatically become
substrate properties the reasoner can use.

The geometric encoding IS the substrate. The binary IS the signal.
The bridge just makes them talk to each other.

USAGE:
    from KnowledgeDNA.geobin_bridge import GeoBinBridge
    bridge = GeoBinBridge()
    props = bridge.pattern_to_properties("100|O", phi_coherence=0.97)

Zero dependencies. Stdlib only.
"""

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime

# Graceful imports
try:
    from KnowledgeDNA.substrate import SubstrateReasoner, VectorSynthesizer
    from KnowledgeDNA.equation_field import (
        Equation, Property, Domain, EquationField,
        build_equation_library, build_domain_library,
    )
    HAS_SUBSTRATE = True
except ImportError:
    HAS_SUBSTRATE = False

try:
    from sim.seed_protocol import (
        OCTAHEDRAL_DIRS, encode_seed, decode_seed,
        expand_seed, seed_distance,
    )
    HAS_SEED = True
except ImportError:
    HAS_SEED = False


# =============================================================================
# GEIS ENCODING — the geometric identity layer
# =============================================================================

# Octahedral vertex bits → direction mapping
# Same 6 directions as seed_protocol.py and equation_field.py
VERTEX_MAP = {
    "000": {"direction": "+X", "index": 0, "axis": "food_water"},
    "001": {"direction": "-X", "index": 1, "axis": "energy"},
    "010": {"direction": "+Y", "index": 2, "axis": "social"},
    "011": {"direction": "-Y", "index": 3, "axis": "institutional"},
    "100": {"direction": "+Z", "index": 4, "axis": "knowledge"},
    "101": {"direction": "-Z", "index": 5, "axis": "infrastructure"},
    # Extended: compound directions (edges, faces)
    "110": {"direction": "+X+Y", "index": -1, "axis": "food_social"},
    "111": {"direction": "+X+Y+Z", "index": -1, "axis": "convergent"},
}

# Operators and their substrate properties
OPERATOR_MAP = {
    "O": {
        "name": "origin",
        "properties": ["self_similarity", "equilibrium_seeking", "energy_conservation"],
        "description": "Radial symmetric attractor. Collapse to center.",
    },
    "I": {
        "name": "identity",
        "properties": ["proportion_stability", "convergent_ratio", "self_similarity"],
        "description": "Invariant under transformation. What persists.",
    },
    "X": {
        "name": "exchange",
        "properties": ["spatial_coupling", "energy_transfer", "synchronization"],
        "description": "Bidirectional flow. Coupling between domains.",
    },
    "Δ": {
        "name": "delta",
        "properties": ["gradient_flow", "decay_modeling", "pressure_dynamics"],
        "description": "Change operator. Gradient, difference, transformation.",
    },
}

# Bridge names → substrate property clusters
BRIDGE_PROPERTY_MAP = {
    "consciousness": ["pattern_recognition", "information_measure", "memory_fading",
                       "self_similarity"],
    "wave": ["frequency_decomposition", "resonance", "synchronization",
             "spatial_coupling"],
    "structure": ["optimal_packing", "proportion_stability", "fractal_nesting",
                  "self_similarity"],
    "flow": ["gradient_flow", "diffusion_on_graphs", "spatial_coupling",
             "pressure_dynamics"],
    "growth": ["population_dynamics", "carrying_capacity", "spiral_growth",
               "fibonacci_scaling"],
    "decay": ["decay_modeling", "half_life", "memory_fading"],
    "network": ["network_structure", "community_detection", "diffusion_on_graphs",
                "synchronization"],
    "energy": ["energy_conservation", "energy_minimization", "energy_transfer",
               "budget_constraint"],
    "information": ["information_measure", "compression", "pattern_recognition",
                    "uncertainty_quantification"],
    "symmetry": ["self_similarity", "proportion_stability", "resonance_avoidance",
                 "fractal_nesting"],
}


# =============================================================================
# PATTERN
# =============================================================================

@dataclass
class GEISPattern:
    """A geometric encoding identity pattern."""
    pattern_id: str             # sha256 of geometric_encoding
    geometric_encoding: str     # e.g. "100|O"
    vertex_bits: str            # e.g. "100"
    operator: str               # e.g. "O"
    symbol: str                 # e.g. "O"
    phi_coherence: float        # 0-1
    dimension: int              # expansion depth
    bridges: List[str]          # domain bridge names
    cultural_labels: Dict[str, str] = field(default_factory=dict)

    @staticmethod
    def from_encoding(encoding: str, phi_coherence: float = 0.5,
                      dimension: int = 1, bridges: Optional[List[str]] = None,
                      cultural_labels: Optional[Dict[str, str]] = None) -> 'GEISPattern':
        """Create a pattern from a GEIS encoding string."""
        parts = encoding.split("|")
        vertex_bits = parts[0] if len(parts) > 0 else "000"
        operator = parts[1] if len(parts) > 1 else "O"
        symbol = parts[2] if len(parts) > 2 else operator

        pattern_id = hashlib.sha256(encoding.encode()).hexdigest()

        return GEISPattern(
            pattern_id=pattern_id,
            geometric_encoding=encoding,
            vertex_bits=vertex_bits,
            operator=operator,
            symbol=symbol,
            phi_coherence=phi_coherence,
            dimension=dimension,
            bridges=bridges or [],
            cultural_labels=cultural_labels or {},
        )

    def to_dict(self) -> Dict:
        return {
            "pattern_id": self.pattern_id,
            "geometric_encoding": self.geometric_encoding,
            "vertex_bits": self.vertex_bits,
            "operator": self.operator,
            "symbol": self.symbol,
            "phi_coherence": self.phi_coherence,
            "dimension": self.dimension,
            "bridges": self.bridges,
            "cultural_labels": self.cultural_labels,
        }


# =============================================================================
# BRIDGE — connects geometric encoding to substrate reasoning
# =============================================================================

class GeoBinBridge:
    """
    Bridges geometric-to-binary GEIS patterns to substrate properties.

    A GEIS pattern encodes identity as:
        [vertex_bits] | [operator] | [symbol]

    This bridge translates that into substrate properties:
        vertex_bits → octahedral direction → domain axis
        operator    → transformation type → property cluster
        bridges     → domain connections → property expansion
        phi_coherence → weight modifier on phi-family properties

    The result is a property vector the substrate reasoner can use.
    Patterns from any repo in the fieldlink become reasoning inputs.

    Usage:
        bridge = GeoBinBridge()

        # Pattern → properties
        props = bridge.pattern_to_properties("100|O", phi_coherence=0.97)

        # Properties → pattern (reverse: find encoding for a substrate)
        pattern = bridge.properties_to_pattern(
            ["self_similarity", "resonance_avoidance"], phi_coherence=0.9
        )

        # Pattern → seed protocol vector
        seed = bridge.pattern_to_seed("100|O")

        # Full analysis: pattern through substrate reasoner
        analysis = bridge.analyze_pattern("100|O", phi_coherence=0.97,
                                          bridges=["consciousness", "wave"])
    """

    def __init__(self):
        self.reasoner = SubstrateReasoner() if HAS_SUBSTRATE else None

    # ----- Pattern → Substrate Properties -----

    def pattern_to_properties(self, encoding: str,
                               phi_coherence: float = 0.5,
                               bridges: Optional[List[str]] = None,
                               dimension: int = 1) -> Dict[str, float]:
        """
        Convert a GEIS encoding to a weighted property vector.

        Three signal sources:
        1. Vertex bits → axis properties
        2. Operator → transformation properties
        3. Bridge names → domain property clusters

        phi_coherence amplifies phi-family properties.
        dimension scales expansion-related properties.
        """
        parts = encoding.split("|")
        vertex_bits = parts[0] if len(parts) > 0 else "000"
        operator = parts[1] if len(parts) > 1 else "O"
        if bridges is None:
            bridges = []

        properties: Dict[str, float] = {}

        # Signal 1: Vertex direction
        vertex_info = VERTEX_MAP.get(vertex_bits, VERTEX_MAP["000"])
        axis = vertex_info.get("axis", "")
        # Each axis maps to domain-related properties
        axis_properties = self._axis_to_properties(axis)
        for prop, weight in axis_properties.items():
            properties[prop] = properties.get(prop, 0) + weight

        # Signal 2: Operator
        op_info = OPERATOR_MAP.get(operator, OPERATOR_MAP["O"])
        for prop in op_info["properties"]:
            properties[prop] = properties.get(prop, 0) + 1.0

        # Signal 3: Bridges
        for bridge_name in bridges:
            bridge_props = BRIDGE_PROPERTY_MAP.get(bridge_name, [])
            for prop in bridge_props:
                properties[prop] = properties.get(prop, 0) + 0.7

        # Phi coherence amplifier: high coherence boosts phi-related properties
        phi_props = ["self_similarity", "optimal_packing", "fibonacci_scaling",
                     "spiral_growth", "resonance_avoidance", "proportion_stability",
                     "fractal_nesting", "phyllotaxis", "irrational_spacing",
                     "minimal_overlap", "convergent_ratio", "energy_minimization"]
        for prop in phi_props:
            if prop in properties:
                properties[prop] *= (1 + phi_coherence)
            elif phi_coherence > 0.7:
                # High phi coherence introduces phi properties even if not explicit
                properties[prop] = phi_coherence * 0.5

        # Dimension scaling: higher dimension = more expansion properties
        expansion_props = ["spiral_growth", "population_dynamics",
                           "carrying_capacity", "fibonacci_scaling"]
        for prop in expansion_props:
            if prop in properties:
                properties[prop] *= (1 + 0.2 * (dimension - 1))

        # Normalize to 0-1
        if properties:
            max_val = max(properties.values())
            if max_val > 0:
                properties = {p: round(v / max_val, 4) for p, v in properties.items()}

        return properties

    def _axis_to_properties(self, axis: str) -> Dict[str, float]:
        """Map an octahedral axis name to substrate properties."""
        axis_map = {
            "food_water": {
                "carrying_capacity": 0.9, "population_dynamics": 0.8,
                "decay_modeling": 0.7, "resource_competition": 0.8,
            },
            "energy": {
                "energy_conservation": 1.0, "gradient_flow": 0.8,
                "budget_constraint": 0.7, "synchronization": 0.5,
            },
            "social": {
                "synchronization": 0.8, "community_detection": 0.7,
                "network_structure": 0.6, "diversity_measure": 0.5,
            },
            "institutional": {
                "equilibrium_seeking": 0.7, "uncertainty_quantification": 0.6,
                "budget_constraint": 0.5, "community_detection": 0.5,
            },
            "knowledge": {
                "decay_modeling": 0.9, "memory_fading": 0.8,
                "diffusion_on_graphs": 0.7, "network_structure": 0.6,
                "half_life": 0.5,
            },
            "infrastructure": {
                "network_structure": 0.9, "spatial_coupling": 0.8,
                "pressure_dynamics": 0.6, "gradient_flow": 0.5,
            },
            "food_social": {
                "carrying_capacity": 0.7, "community_detection": 0.6,
                "resource_competition": 0.5, "synchronization": 0.5,
            },
            "convergent": {
                "self_similarity": 0.8, "convergent_ratio": 0.7,
                "equilibrium_seeking": 0.6, "energy_conservation": 0.5,
            },
        }
        return axis_map.get(axis, {})

    # ----- Properties → Pattern (reverse) -----

    def properties_to_pattern(self, properties: List[str],
                               phi_coherence: float = 0.5) -> GEISPattern:
        """
        Given substrate properties, find the best GEIS encoding.
        Reverse of pattern_to_properties.
        """
        # Find best operator
        best_op = "O"
        best_op_score = 0
        for op, info in OPERATOR_MAP.items():
            score = len(set(info["properties"]) & set(properties))
            if score > best_op_score:
                best_op = op
                best_op_score = score

        # Find best vertex
        best_vertex = "000"
        best_vertex_score = 0
        for bits, info in VERTEX_MAP.items():
            axis_props = self._axis_to_properties(info.get("axis", ""))
            score = len(set(axis_props.keys()) & set(properties))
            if score > best_vertex_score:
                best_vertex = bits
                best_vertex_score = score

        # Find bridges
        bridges = []
        for bridge_name, bridge_props in BRIDGE_PROPERTY_MAP.items():
            if len(set(bridge_props) & set(properties)) >= 2:
                bridges.append(bridge_name)

        encoding = f"{best_vertex}|{best_op}"
        return GEISPattern.from_encoding(
            encoding, phi_coherence=phi_coherence,
            bridges=bridges,
        )

    # ----- Pattern → Seed Protocol Vector -----

    def pattern_to_seed(self, encoding: str,
                         phi_coherence: float = 0.5) -> List[float]:
        """
        Convert a GEIS pattern to a 6D seed protocol vector.

        The vertex bits determine the primary direction.
        phi_coherence scales the amplitude.
        Other directions get residual energy based on operator type.
        """
        parts = encoding.split("|")
        vertex_bits = parts[0] if len(parts) > 0 else "000"
        operator = parts[1] if len(parts) > 1 else "O"

        # Base: uniform
        seed = [0.1] * 6

        # Primary direction from vertex bits
        vertex_info = VERTEX_MAP.get(vertex_bits, VERTEX_MAP["000"])
        idx = vertex_info["index"]
        if 0 <= idx < 6:
            seed[idx] = 0.5 + 0.3 * phi_coherence

        # Operator modifies distribution
        if operator == "O":
            # Origin: energy concentrates in primary
            pass
        elif operator == "X":
            # Exchange: energy distributes to neighbors
            for i in range(6):
                if i != idx:
                    seed[i] += 0.15
        elif operator == "Δ":
            # Delta: gradient toward primary
            opposite = idx ^ 1  # flip least significant bit
            if 0 <= opposite < 6:
                seed[opposite] = 0.05
        elif operator == "I":
            # Identity: preserves current proportions
            seed = [0.167] * 6  # uniform = stable identity
            if 0 <= idx < 6:
                seed[idx] = 0.25

        # Normalize
        total = sum(seed)
        return [round(s / total, 4) for s in seed]

    # ----- Full Analysis -----

    def analyze_pattern(self, encoding: str, phi_coherence: float = 0.5,
                         bridges: Optional[List[str]] = None,
                         dimension: int = 1) -> Dict:
        """
        Full substrate analysis of a GEIS pattern.

        1. Convert to properties
        2. Run through substrate reasoner
        3. Map to seed vector
        4. Return unified result
        """
        pattern = GEISPattern.from_encoding(
            encoding, phi_coherence=phi_coherence,
            dimension=dimension, bridges=bridges,
        )

        properties = self.pattern_to_properties(
            encoding, phi_coherence=phi_coherence,
            bridges=bridges, dimension=dimension,
        )

        seed = self.pattern_to_seed(encoding, phi_coherence)

        # Substrate analysis
        substrate_result = None
        if self.reasoner:
            prop_list = sorted(properties.keys(), key=lambda p: -properties[p])
            result = self.reasoner.reason_from_properties(prop_list[:10])
            substrate_result = self.reasoner.to_dict(result)

        return {
            "pattern": pattern.to_dict(),
            "properties": properties,
            "seed_vector": seed,
            "substrate_analysis": substrate_result,
        }

    # ----- Fieldlink Integration -----

    def load_fieldlink(self, fieldlink_data: Dict) -> Dict[str, List[str]]:
        """
        Parse a fieldlink.json and extract cross-repo entity relationships.
        Returns {entity_type: [property_names]} mapping.
        """
        entities = {}
        for source in fieldlink_data.get("sources", []):
            consumed = source.get("entities_consumed", [])
            exported = source.get("entities_exported", [])
            name = source.get("name", "unknown")

            for entity in consumed + exported:
                # Parse entity format: "SHAPE.OCTA", "CONST.PHI", etc.
                parts = entity.split(".")
                category = parts[0] if len(parts) > 0 else ""
                specific = parts[1] if len(parts) > 1 else ""

                props = self._entity_to_properties(category, specific)
                entities[entity] = props

        return entities

    def _entity_to_properties(self, category: str, specific: str) -> List[str]:
        """Map fieldlink entity types to substrate properties."""
        category_map = {
            "SHAPE": ["self_similarity", "optimal_packing", "proportion_stability"],
            "CONST": ["convergent_ratio", "proportion_stability"],
            "CAP": ["spiral_growth", "fibonacci_scaling", "energy_conservation"],
            "PROTO": ["network_structure", "synchronization", "compression"],
            "GEIS": ["pattern_recognition", "compression", "information_measure"],
            "BRIDGE": ["spatial_coupling", "network_structure", "gradient_flow"],
            "TOPO": ["network_structure", "fractal_nesting", "self_similarity"],
        }

        specific_map = {
            "OCTA": ["optimal_packing", "resonance_avoidance", "self_similarity"],
            "PHI": ["fibonacci_scaling", "resonance_avoidance", "spiral_growth",
                     "irrational_spacing", "proportion_stability"],
            "SEED_EXPANSION": ["spiral_growth", "energy_conservation",
                               "fibonacci_scaling"],
            "ENCODING": ["compression", "information_measure", "pattern_recognition"],
            "BINARY": ["compression", "information_measure"],
            "VORTEX_MEMORY": ["memory_fading", "self_similarity", "fractal_nesting"],
        }

        props = set()
        props.update(category_map.get(category, []))
        props.update(specific_map.get(specific, []))
        return sorted(props)

    # ----- Report -----

    def print_analysis(self, encoding: str, phi_coherence: float = 0.5,
                        bridges: Optional[List[str]] = None):
        """Human-readable pattern analysis."""
        result = self.analyze_pattern(encoding, phi_coherence, bridges)
        pattern = result["pattern"]
        props = result["properties"]

        print(f"\n{'='*66}")
        print(f"  GEIS PATTERN ANALYSIS")
        print(f"{'='*66}")

        print(f"\n  Encoding: {pattern['geometric_encoding']}")
        print(f"  Vertex:   {pattern['vertex_bits']} → "
              f"{VERTEX_MAP.get(pattern['vertex_bits'], {}).get('direction', '?')} "
              f"({VERTEX_MAP.get(pattern['vertex_bits'], {}).get('axis', '?')})")
        print(f"  Operator: {pattern['operator']} → "
              f"{OPERATOR_MAP.get(pattern['operator'], {}).get('name', '?')}")
        print(f"  Phi:      {pattern['phi_coherence']:.2f}")
        if pattern['bridges']:
            print(f"  Bridges:  {', '.join(pattern['bridges'])}")

        print(f"\n  SUBSTRATE PROPERTIES ({len(props)}):")
        sorted_props = sorted(props.items(), key=lambda x: -x[1])
        for prop, weight in sorted_props[:12]:
            bar = "#" * max(1, int(weight * 10))
            print(f"    {prop:<35s} {weight:.2f}  {bar}")

        print(f"\n  SEED VECTOR: {result['seed_vector']}")

        if result.get("substrate_analysis"):
            sa = result["substrate_analysis"]
            if sa.get("equations"):
                print(f"\n  MATCHING EQUATIONS:")
                for eq in sa["equations"][:5]:
                    print(f"    {eq['name']:<30s} {eq['overlap']:.0%}  "
                          f"via {', '.join(eq['matched'][:3])}")
            if sa.get("analogies"):
                print(f"\n  ANALOGIES:")
                for a in sa["analogies"][:4]:
                    print(f"    {a['domain']:<30s} {a['strength']:.0%} shared")

        print(f"\n{'='*66}\n")


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":

    print("=" * 66)
    print("  GEOBIN BRIDGE — geometric identity ↔ substrate reasoning")
    print("  octahedral bits become property vectors become equations")
    print("=" * 66)

    bridge = GeoBinBridge()

    # Test patterns from the fieldlink schema
    patterns = [
        ("100|O",  0.97, ["consciousness", "wave"],
         "Mandala — radial symmetric attractor"),
        ("001|Δ",  0.60, ["energy", "flow"],
         "Energy gradient — delta operator on energy axis"),
        ("100|X",  0.85, ["network", "information"],
         "Knowledge exchange — bidirectional on knowledge axis"),
        ("111|I",  0.92, ["symmetry", "structure"],
         "Convergent identity — all axes, invariant"),
        ("010|X",  0.70, ["wave", "network"],
         "Social coupling — exchange on social axis"),
    ]

    for encoding, phi, bridges, description in patterns:
        print(f"\n  --- {description} ---")
        bridge.print_analysis(encoding, phi_coherence=phi, bridges=bridges)

    # Fieldlink entity mapping
    print(f"\n{'─'*66}")
    print("  FIELDLINK ENTITY → SUBSTRATE MAPPING")
    print(f"{'─'*66}")

    fieldlink = {
        "sources": [{
            "name": "mandala",
            "entities_consumed": ["SHAPE.OCTA", "CONST.PHI",
                                  "CAP.SEED_EXPANSION", "PROTO.MANDALA_COMPUTE"],
            "entities_exported": ["GEIS.ENCODING", "BRIDGE.BINARY",
                                  "TOPO.VORTEX_MEMORY"],
        }]
    }
    entities = bridge.load_fieldlink(fieldlink)
    for entity, props in entities.items():
        print(f"\n  {entity}")
        print(f"    → {', '.join(props)}")

    # Reverse: properties → pattern
    print(f"\n{'─'*66}")
    print("  REVERSE: substrate properties → GEIS encoding")
    print(f"{'─'*66}")

    test_props = [
        ["gradient_flow", "decay_modeling", "network_structure"],
        ["self_similarity", "resonance_avoidance", "optimal_packing"],
        ["synchronization", "community_detection", "network_structure"],
    ]
    for props in test_props:
        pattern = bridge.properties_to_pattern(props, phi_coherence=0.8)
        print(f"\n  {props}")
        print(f"    → {pattern.geometric_encoding}  "
              f"bridges={pattern.bridges}")

    print(f"\n{'='*66}")
    print("  THE BRIDGE")
    print(f"{'='*66}")
    print("""
  geometric-to-binary encodes identity as octahedral vertex bits.
  seed_protocol.py encodes resilience state as octahedral amplitudes.
  equation_field.py maps equations to domain properties.
  substrate.py reasons from properties to equations.

  This bridge connects them:
    GEIS pattern → substrate properties → equations → domains
    domains → properties → GEIS pattern (reverse)

  A pattern discovered in Mandala-Computing becomes a substrate
  the reasoner can match against any domain in Resilience.
  A property vector from the substrate reasoner becomes a GEIS
  encoding that any repo in the fieldlink can consume.

  The geometry IS the protocol. The binary IS the signal.
  The substrate IS the reasoning. They're the same thing
  viewed from different altitudes.
""")

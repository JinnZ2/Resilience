#!/usr/bin/env python3
"""
KnowledgeDNA/substrate.py — Substrate-First Reasoning Module
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

A reasoning scaffold for any system (AI or human) that wants to
think from physics upward instead of from domains sideways.

Most reasoning is siloed:
    "I have a food problem → search food literature → food answer"

Substrate reasoning:
    "I have a food problem → what equation governs it? →
     where else does that equation appear? →
     what solved it there? → adapt that solution"

This is how biology works. This is how a truck driver connects
soil culture to antenna design. Start at the math. Work up.

The module provides:
    1. decompose()  — break a problem into substrate properties
    2. propagate()  — find all domains those substrates touch
    3. bridge()     — discover non-obvious cross-domain connections
    4. compose()    — find minimum equations for maximum coverage
    5. gaps()       — honest accounting of what's NOT covered

Import it. Feed it a problem. Get back a substrate map.

USAGE:
    from KnowledgeDNA.substrate import SubstrateReasoner
    reasoner = SubstrateReasoner()
    analysis = reasoner.analyze("How do we distribute food after grid failure?")

    # Or programmatically:
    result = reasoner.reason_from_properties([
        "gradient_flow", "decay_modeling", "network_structure",
        "carrying_capacity", "spatial_coupling"
    ])

Zero dependencies. Stdlib only.
"""

import math
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set

from KnowledgeDNA.equation_field import (
    EquationField, Equation, Property, Domain, FieldOverlap, ReusePlan,
    build_equation_library, build_domain_library,
)


# =============================================================================
# SUBSTRATE DECOMPOSITION — break problems into physics
# =============================================================================

# Property keyword map: natural language → substrate properties
# This is the bridge between how people describe problems
# and what equations actually govern them
KEYWORD_MAP = {
    # Flow / transport
    "flow": ["gradient_flow", "spatial_coupling"],
    "distribute": ["gradient_flow", "network_structure", "spatial_coupling"],
    "spread": ["diffusion_on_graphs", "gradient_flow", "spatial_coupling"],
    "transport": ["gradient_flow", "pressure_dynamics", "spatial_coupling"],
    "route": ["network_structure", "gradient_flow"],
    "move": ["gradient_flow", "pressure_dynamics"],
    "deliver": ["gradient_flow", "network_structure"],

    # Decay / loss
    "decay": ["decay_modeling", "half_life", "memory_fading"],
    "lose": ["decay_modeling", "memory_fading"],
    "fade": ["decay_modeling", "memory_fading"],
    "die": ["decay_modeling", "population_dynamics"],
    "deplete": ["decay_modeling", "resource_competition"],
    "erode": ["decay_modeling", "gradient_flow"],
    "forget": ["memory_fading", "decay_modeling"],

    # Growth / population
    "grow": ["population_dynamics", "carrying_capacity", "spiral_growth"],
    "reproduce": ["population_dynamics", "fibonacci_scaling"],
    "scale": ["carrying_capacity", "saturation", "fibonacci_scaling"],
    "expand": ["spiral_growth", "population_dynamics"],
    "saturate": ["saturation", "carrying_capacity", "diminishing_returns"],
    "limit": ["carrying_capacity", "saturation", "budget_constraint"],

    # Structure / network
    "connect": ["network_structure", "spatial_coupling", "community_detection"],
    "network": ["network_structure", "diffusion_on_graphs", "community_detection"],
    "cluster": ["community_detection", "network_structure"],
    "organize": ["self_similarity", "network_structure", "synchronization"],
    "coordinate": ["synchronization", "network_structure"],
    "mesh": ["network_structure", "spatial_coupling", "minimal_overlap"],

    # Conservation / balance
    "conserve": ["energy_conservation", "budget_constraint"],
    "balance": ["energy_conservation", "equilibrium_seeking"],
    "budget": ["budget_constraint", "energy_conservation"],
    "sustain": ["energy_conservation", "carrying_capacity"],
    "efficient": ["energy_minimization", "optimal_packing", "budget_constraint"],
    "optimize": ["energy_minimization", "optimal_packing", "budget_constraint"],

    # Information / signal
    "signal": ["information_measure", "frequency_decomposition", "compression"],
    "communicate": ["information_measure", "compression", "network_structure"],
    "encode": ["compression", "information_measure", "pattern_recognition"],
    "detect": ["pattern_recognition", "frequency_decomposition"],
    "measure": ["information_measure", "uncertainty_quantification"],
    "noise": ["information_measure", "uncertainty_quantification"],

    # Stability / resilience
    "stable": ["proportion_stability", "resonance_avoidance", "equilibrium_seeking"],
    "resilient": ["resonance_avoidance", "diversity_measure", "energy_conservation"],
    "robust": ["resonance_avoidance", "proportion_stability"],
    "fail": ["decay_modeling", "network_structure", "synchronization"],
    "recover": ["equilibrium_seeking", "energy_conservation"],
    "adapt": ["convergent_ratio", "equilibrium_seeking"],

    # Spatial / geometric
    "pack": ["optimal_packing", "minimal_overlap"],
    "cover": ["uniform_coverage", "minimal_overlap", "optimal_packing"],
    "spiral": ["spiral_growth", "minimal_overlap", "irrational_spacing"],
    "tile": ["optimal_packing", "fractal_nesting", "self_similarity"],
    "pattern": ["self_similarity", "pattern_recognition", "fractal_nesting"],
    "fractal": ["fractal_nesting", "self_similarity"],

    # Competition / economics
    "compete": ["resource_competition", "carrying_capacity"],
    "scarce": ["resource_competition", "budget_constraint"],
    "allocate": ["budget_constraint", "optimal_packing", "minimal_overlap"],
    "price": ["resource_competition", "convergent_ratio"],
    "market": ["fibonacci_scaling", "convergent_ratio", "resource_competition"],
    "trade": ["gradient_flow", "network_structure", "resource_competition"],

    # Synchronization / coupling
    "sync": ["synchronization", "spatial_coupling", "resonance"],
    "couple": ["spatial_coupling", "synchronization"],
    "resonate": ["resonance", "frequency_decomposition", "synchronization"],
    "oscillate": ["synchronization", "resonance", "frequency_decomposition"],
    "cascade": ["spatial_coupling", "network_structure", "decay_modeling"],

    # Bio-specific
    "food": ["carrying_capacity", "population_dynamics", "decay_modeling",
             "resource_competition", "spatial_coupling"],
    "energy": ["energy_conservation", "gradient_flow", "budget_constraint",
               "synchronization"],
    "water": ["gradient_flow", "pressure_dynamics", "carrying_capacity",
              "decay_modeling"],
    "soil": ["population_dynamics", "decay_modeling", "carrying_capacity",
             "phyllotaxis"],
    "knowledge": ["decay_modeling", "memory_fading", "diffusion_on_graphs",
                  "network_structure", "half_life"],
}


# =============================================================================
# RESULT STRUCTURES
# =============================================================================

@dataclass
class SubstrateDecomposition:
    """What a problem looks like at the equation level."""
    input_text: str
    keywords_found: List[str]
    substrate_properties: List[str]       # unique properties extracted
    property_weights: Dict[str, float]    # how many keywords point to each


@dataclass
class SubstrateMatch:
    """An equation that matches the substrate."""
    equation_name: str
    formula: str
    overlap_score: float
    matched_properties: List[str]
    excess_properties: List[str]          # what else this equation can do


@dataclass
class SubstrateBridge:
    """A non-obvious connection through shared substrate."""
    equation: str
    from_domain: str
    to_domain: str
    shared_substrate: List[str]
    bridge_type: str                      # "structural" or "partial"


@dataclass
class SubstrateAnalysis:
    """Complete substrate-first analysis of a problem."""
    decomposition: SubstrateDecomposition
    matching_equations: List[SubstrateMatch]
    reuse_plans: List[ReusePlan]
    bridges: List[SubstrateBridge]
    gaps: List[str]                       # properties no equation covers
    composition: Dict[str, List[str]]     # minimum equations → properties covered
    analogies: List[Dict]                 # "this is like X because Y"


# =============================================================================
# SUBSTRATE REASONER — the main interface
# =============================================================================

class SubstrateReasoner:
    """
    Substrate-first reasoning engine.

    Feed it a problem (text or property list).
    It decomposes to physics, searches for equations,
    finds overlaps and bridges, and returns a structured analysis.

    This is not an AI. It's a lens.
    The equations are the knowledge. The reasoner just propagates.

    Usage:
        reasoner = SubstrateReasoner()

        # From text:
        result = reasoner.analyze("How do we distribute food after grid failure?")

        # From properties:
        result = reasoner.reason_from_properties([
            "gradient_flow", "decay_modeling", "network_structure"
        ])

        # Print human-readable:
        reasoner.print_analysis(result)

        # Get JSON for another system:
        data = reasoner.to_dict(result)
    """

    def __init__(self, extra_equations: Optional[List[Equation]] = None,
                 extra_domains: Optional[List[Domain]] = None):
        """
        Initialize with the standard equation and domain libraries.
        Add custom equations/domains for your specific field.
        """
        self.field = EquationField()

        for eq in build_equation_library():
            self.field.add_equation(eq)
        for domain in build_domain_library():
            self.field.add_domain(domain)

        if extra_equations:
            for eq in extra_equations:
                self.field.add_equation(eq)
        if extra_domains:
            for domain in extra_domains:
                self.field.add_domain(domain)

        self.field.propagate()

    # ----- Decomposition -----

    def decompose(self, text: str) -> SubstrateDecomposition:
        """
        Break natural language into substrate properties.

        Tokenizes the text, matches against the keyword map,
        and returns weighted properties. More keyword hits = higher weight.
        """
        words = text.lower().split()
        # Strip punctuation
        words = [w.strip(".,;:!?()[]{}\"'") for w in words]

        keywords_found = []
        property_counts: Dict[str, int] = {}

        for word in words:
            if word in KEYWORD_MAP:
                keywords_found.append(word)
                for prop in KEYWORD_MAP[word]:
                    property_counts[prop] = property_counts.get(prop, 0) + 1

        # Also check bigrams
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            # No bigram map yet, but the structure supports it

        # Normalize weights
        max_count = max(property_counts.values()) if property_counts else 1
        property_weights = {
            prop: count / max_count
            for prop, count in property_counts.items()
        }

        unique_props = sorted(property_counts.keys(),
                              key=lambda p: -property_counts[p])

        return SubstrateDecomposition(
            input_text=text,
            keywords_found=keywords_found,
            substrate_properties=unique_props,
            property_weights=property_weights,
        )

    # ----- Matching -----

    def match_equations(self, properties: List[str],
                        weights: Optional[Dict[str, float]] = None,
                        min_score: float = 0.1) -> List[SubstrateMatch]:
        """
        Find equations whose properties overlap with the given set.
        Returns sorted by overlap score (best match first).
        """
        if weights is None:
            weights = {p: 1.0 for p in properties}

        matches = []
        for eq in self.field.equations.values():
            eq_props = eq.property_vector()

            matched = []
            score = 0.0
            total_weight = sum(weights.get(p, 1.0) for p in properties)

            for prop in properties:
                if prop in eq_props:
                    w = weights.get(prop, 1.0)
                    score += min(eq_props[prop], 1.0) * w
                    matched.append(prop)

            if total_weight > 0:
                score /= total_weight

            excess = [p for p in eq_props if p not in properties]

            if score >= min_score:
                matches.append(SubstrateMatch(
                    equation_name=eq.name,
                    formula=eq.formula,
                    overlap_score=score,
                    matched_properties=matched,
                    excess_properties=excess,
                ))

        matches.sort(key=lambda m: -m.overlap_score)
        return matches

    # ----- Composition -----

    def compose_minimum(self, properties: List[str]) -> Dict[str, List[str]]:
        """
        Find the minimum set of equations that covers all properties.

        Greedy set cover: repeatedly pick the equation that covers
        the most uncovered properties until all are covered (or no
        equation covers any remaining property).

        This is how biology solves it: minimum structures,
        maximum coverage. ATP, not a unique molecule per reaction.
        """
        uncovered = set(properties)
        composition = {}

        while uncovered:
            best_eq = None
            best_covered = set()

            for eq in self.field.equations.values():
                eq_props = set(eq.property_vector().keys())
                covered = uncovered & eq_props
                if len(covered) > len(best_covered):
                    best_eq = eq.name
                    best_covered = covered

            if not best_eq or not best_covered:
                break

            composition[best_eq] = sorted(best_covered)
            uncovered -= best_covered

        return composition

    # ----- Analogy generation -----

    def find_analogies(self, properties: List[str]) -> List[Dict]:
        """
        Find domains that share substrate with the given properties.
        Each match is a potential analogy: "your problem is like X
        because both are governed by Y."

        This is the bridge from physics to insight.
        """
        analogies = []
        for domain in self.field.domains.values():
            domain_needs = set(domain.need_vector().keys())
            shared = set(properties) & domain_needs

            if len(shared) >= 2:  # need at least 2 shared properties for analogy
                analogies.append({
                    "domain": domain.name,
                    "shared_substrate": sorted(shared),
                    "analogy": (f"Your problem shares substrate with {domain.name} "
                                f"through: {', '.join(sorted(shared))}"),
                    "strength": len(shared) / len(set(properties)),
                    "domain_description": domain.description,
                })

        analogies.sort(key=lambda a: -a["strength"])
        return analogies

    # ----- Gap analysis -----

    def find_gaps(self, properties: List[str]) -> List[str]:
        """Properties that no equation in the library covers."""
        all_eq_props = set()
        for eq in self.field.equations.values():
            all_eq_props.update(eq.property_vector().keys())
        return sorted(set(properties) - all_eq_props)

    # ----- Main interface -----

    def analyze(self, text: str, min_match: float = 0.1) -> SubstrateAnalysis:
        """
        Full substrate analysis from natural language.

        1. Decompose text to properties
        2. Match equations
        3. Find minimum composition
        4. Generate analogies
        5. Discover bridges
        6. Identify gaps
        """
        decomp = self.decompose(text)

        if not decomp.substrate_properties:
            return SubstrateAnalysis(
                decomposition=decomp,
                matching_equations=[], reuse_plans=[],
                bridges=[], gaps=[], composition={}, analogies=[],
            )

        matches = self.match_equations(
            decomp.substrate_properties,
            decomp.property_weights,
            min_score=min_match,
        )

        composition = self.compose_minimum(decomp.substrate_properties)
        analogies = self.find_analogies(decomp.substrate_properties)
        gaps = self.find_gaps(decomp.substrate_properties)

        # Find bridges through matching equations
        bridges = []
        for match in matches[:5]:  # top 5 equations
            eq_overlaps = [o for o in self.field.overlaps
                           if o.equation == match.equation_name
                           and o.overlap_score >= 0.2]
            for i in range(len(eq_overlaps)):
                for j in range(i + 1, len(eq_overlaps)):
                    d1 = self.field.domains.get(eq_overlaps[i].domain)
                    d2 = self.field.domains.get(eq_overlaps[j].domain)
                    if d1 and d2:
                        needs_1 = set(d1.need_vector().keys())
                        needs_2 = set(d2.need_vector().keys())
                        direct = needs_1 & needs_2
                        if len(direct) < 2:
                            bridges.append(SubstrateBridge(
                                equation=match.equation_name,
                                from_domain=d1.name,
                                to_domain=d2.name,
                                shared_substrate=(eq_overlaps[i].matched_properties +
                                                  eq_overlaps[j].matched_properties),
                                bridge_type="structural" if not direct else "partial",
                            ))

        # Reuse plans for matching equations
        reuse_plans = []
        for match in matches[:5]:
            plan = self.field.find_reuse_plan(match.equation_name, min_overlap=0.2)
            if plan and len(plan.domains_served) > 1:
                reuse_plans.append(plan)

        return SubstrateAnalysis(
            decomposition=decomp,
            matching_equations=matches,
            reuse_plans=reuse_plans,
            bridges=bridges,
            gaps=gaps,
            composition=composition,
            analogies=analogies,
        )

    def reason_from_properties(self, properties: List[str],
                                min_match: float = 0.1) -> SubstrateAnalysis:
        """
        Same as analyze() but starting from known properties
        instead of natural language.
        """
        decomp = SubstrateDecomposition(
            input_text=f"[properties: {', '.join(properties)}]",
            keywords_found=[],
            substrate_properties=properties,
            property_weights={p: 1.0 for p in properties},
        )

        matches = self.match_equations(properties, min_score=min_match)
        composition = self.compose_minimum(properties)
        analogies = self.find_analogies(properties)
        gaps = self.find_gaps(properties)

        bridges = []
        reuse_plans = []
        for match in matches[:5]:
            plan = self.field.find_reuse_plan(match.equation_name, min_overlap=0.2)
            if plan and len(plan.domains_served) > 1:
                reuse_plans.append(plan)

        return SubstrateAnalysis(
            decomposition=decomp,
            matching_equations=matches,
            reuse_plans=reuse_plans,
            bridges=bridges,
            gaps=gaps,
            composition=composition,
            analogies=analogies,
        )

    # ----- Output -----

    def print_analysis(self, result: SubstrateAnalysis):
        """Human-readable output."""
        d = result.decomposition

        print(f"\n{'='*70}")
        print(f"  SUBSTRATE ANALYSIS")
        print(f"{'='*70}")
        print(f"\n  Input: {d.input_text}")

        if d.keywords_found:
            print(f"  Keywords: {', '.join(d.keywords_found)}")

        print(f"  Substrate properties ({len(d.substrate_properties)}):")
        for prop in d.substrate_properties[:10]:
            w = d.property_weights.get(prop, 0)
            bar = "#" * max(1, int(w * 10))
            print(f"    {prop:<35s} {w:.2f}  {bar}")

        if result.matching_equations:
            print(f"\n  MATCHING EQUATIONS (by overlap):")
            for m in result.matching_equations[:8]:
                print(f"    {m.equation_name:<30s} {m.overlap_score:5.0%}  "
                      f"via {', '.join(m.matched_properties)}")
                if m.excess_properties:
                    print(f"      also provides: {', '.join(m.excess_properties[:5])}")

        if result.composition:
            total_eq = len(result.composition)
            total_props = sum(len(v) for v in result.composition.values())
            print(f"\n  MINIMUM COMPOSITION ({total_eq} equations -> "
                  f"{total_props} properties):")
            for eq, props in result.composition.items():
                print(f"    {eq:<30s} covers: {', '.join(props)}")

        if result.analogies:
            print(f"\n  ANALOGIES (shared substrate -> insight):")
            for a in result.analogies[:6]:
                print(f"    {a['domain']:<30s} "
                      f"({a['strength']:.0%} shared)")
                print(f"      {a['analogy']}")

        if result.bridges:
            print(f"\n  STRUCTURAL BRIDGES:")
            seen = set()
            for b in result.bridges[:5]:
                key = (b.equation, b.from_domain, b.to_domain)
                if key not in seen:
                    seen.add(key)
                    print(f"    {b.equation} bridges "
                          f"{b.from_domain} <-> {b.to_domain}")

        if result.gaps:
            print(f"\n  GAPS (no equation covers):")
            for g in result.gaps:
                print(f"    {g}")

        print(f"\n{'='*70}\n")

    def to_dict(self, result: SubstrateAnalysis) -> Dict:
        """Machine-readable output for other AI systems."""
        return {
            "input": result.decomposition.input_text,
            "substrate_properties": result.decomposition.substrate_properties,
            "property_weights": result.decomposition.property_weights,
            "equations": [
                {
                    "name": m.equation_name,
                    "formula": m.formula,
                    "overlap": round(m.overlap_score, 4),
                    "matched": m.matched_properties,
                    "excess": m.excess_properties,
                }
                for m in result.matching_equations
            ],
            "composition": result.composition,
            "analogies": [
                {
                    "domain": a["domain"],
                    "shared": a["shared_substrate"],
                    "strength": round(a["strength"], 4),
                }
                for a in result.analogies
            ],
            "gaps": result.gaps,
        }


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":

    print("=" * 70)
    print("  SUBSTRATE REASONER — physics up, not domains sideways")
    print("  a reasoning lens for any system that wants to see the math")
    print("=" * 70)

    reasoner = SubstrateReasoner()

    # --- Test 1: natural language ---
    problems = [
        "How do we distribute food after grid failure in rural Wisconsin?",
        "Knowledge is dying with the elders faster than we can transmit it",
        "We need to coordinate 50 drones in a blizzard with 30% dropout",
        "How do you design an antenna that works across all frequencies?",
        "The soil microbiome is collapsing and nobody who knows how to fix it is under 60",
    ]

    for problem in problems:
        result = reasoner.analyze(problem)
        reasoner.print_analysis(result)

    # --- Test 2: direct property query ---
    print(f"\n{'─'*70}")
    print("  DIRECT PROPERTY QUERY")
    print(f"{'─'*70}")

    result = reasoner.reason_from_properties([
        "self_similarity", "resonance_avoidance", "optimal_packing",
        "energy_minimization", "spiral_growth",
    ])
    reasoner.print_analysis(result)

    # --- Test 3: JSON output for other systems ---
    print(f"\n{'─'*70}")
    print("  JSON OUTPUT (for other AI systems)")
    print(f"{'─'*70}")

    result = reasoner.analyze("How does a mesh network self-organize?")
    data = reasoner.to_dict(result)
    print(f"\n  {json.dumps(data, indent=2)[:1000]}...")

    print(f"\n{'='*70}")
    print("  HOW TO USE THIS")
    print(f"{'='*70}")
    print("""
  For humans:
    reasoner = SubstrateReasoner()
    result = reasoner.analyze("your problem in plain English")
    reasoner.print_analysis(result)

  For AI systems:
    data = reasoner.to_dict(result)
    # data["equations"] = what math governs this
    # data["analogies"] = what other domains share substrate
    # data["composition"] = minimum equations for coverage
    # data["gaps"] = what no equation covers (be honest)

  The point:
    Don't search within the domain.
    Decompose to substrate.
    Let the field tell you where the equation already solved it.
    Adapt the solution from wherever it landed.

  That's substrate reasoning. Physics up, not domains sideways.
""")

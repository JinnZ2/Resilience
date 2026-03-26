#!/usr/bin/env python3
"""
KnowledgeDNA/equation_field.py — Equation Field Overlap Simulator
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Start with one equation. Propagate its field across domains.
Find where it constructively interferes with other structures.
Let multi-purpose overlaps emerge — the way biology reuses the
same molecule for dozens of functions instead of inventing a
new one each time.

Biology doesn't build a unique enzyme for every reaction.
It finds equations (binding geometries, energy gradients)
that solve multiple problems simultaneously. ATP doesn't
power muscles OR neurons — it powers both, because the
underlying equation (phosphate bond energy release) maps
onto both domains.

This simulator does the same thing with any equation:
- Define the equation's properties (what it conserves, transforms, couples)
- Define a set of domains (what needs those properties)
- Propagate the equation's field across domains
- Find constructive overlaps (where one equation serves multiple purposes)
- Measure the efficiency gain from reuse vs single-purpose design

The result is a map of how a single mathematical structure
can serve multiple functions — exactly how evolved systems
minimize resource cost by maximizing structural reuse.

Zero external dependencies. Stdlib only.

USAGE:
    python -m KnowledgeDNA.equation_field
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set


# =============================================================================
# CORE STRUCTURES
# =============================================================================

@dataclass
class Property:
    """
    A named property that an equation can provide or a domain can need.

    Examples:
      - "energy_conservation" (provided by E=mc^2, needed by thermodynamics)
      - "wave_propagation" (provided by wave equation, needed by acoustics, optics, EM)
      - "gradient_descent" (provided by calculus, needed by optimization, evolution, water flow)
    """
    name: str
    strength: float = 1.0   # how strongly this property is expressed (0-1)
    category: str = ""      # grouping: "conservation", "symmetry", "coupling", etc.


@dataclass
class Equation:
    """
    A mathematical structure with properties that can serve multiple domains.

    The equation itself is the seed. Its properties define what it can do.
    The field propagation discovers WHERE it can do those things.
    """
    name: str
    formula: str                          # human-readable formula
    properties: List[Property]            # what this equation provides
    energy_cost: float = 1.0              # cost to instantiate/maintain
    description: str = ""

    def property_vector(self) -> Dict[str, float]:
        """Properties as a named vector for overlap computation."""
        return {p.name: p.strength for p in self.properties}


@dataclass
class Domain:
    """
    A context that needs certain properties to function.

    Biology: "muscle contraction" needs energy_release + cyclic_binding
    Engineering: "heat exchanger" needs gradient_flow + surface_area_scaling
    Logistics: "routing" needs graph_traversal + optimization
    """
    name: str
    needs: List[Property]                 # what this domain requires
    current_solutions: int = 0            # how many separate equations currently serve it
    description: str = ""

    def need_vector(self) -> Dict[str, float]:
        """Needs as a named vector for overlap computation."""
        return {p.name: p.strength for p in self.needs}


@dataclass
class FieldOverlap:
    """
    Where an equation's field constructively interferes with a domain's needs.
    High overlap = the equation naturally serves this domain.
    """
    equation: str
    domain: str
    overlap_score: float       # 0-1, how well the equation matches the domain
    matched_properties: List[str]   # which properties overlap
    unmet_needs: List[str]          # what the domain still needs
    excess_properties: List[str]    # what the equation provides that this domain doesn't use


@dataclass
class ReusePlan:
    """
    A multi-purpose deployment of one equation across several domains.
    This is the biological strategy: one structure, many functions.
    """
    equation: str
    domains_served: List[str]
    total_overlap: float       # sum of overlap scores
    efficiency_gain: float     # how much cheaper than single-purpose solutions
    shared_properties: List[str]  # properties used by multiple domains
    coverage_gaps: List[Tuple[str, List[str]]]  # (domain, unmet_needs) pairs


# =============================================================================
# FIELD PROPAGATION ENGINE
# =============================================================================

class EquationField:
    """
    Propagate an equation's properties across a set of domains.
    Find constructive overlaps. Compute multi-purpose efficiency.

    The core insight: if two domains need the same property,
    one equation can serve both. The overlap score quantifies
    how much of each domain's needs are met. The efficiency
    gain measures how much you save compared to building
    a separate solution for each domain.

    This is exactly how biological systems evolve efficiency:
    not by designing optimal single-purpose tools, but by
    discovering structures that naturally map onto multiple needs.
    """

    def __init__(self):
        self.equations: Dict[str, Equation] = {}
        self.domains: Dict[str, Domain] = {}
        self.overlaps: List[FieldOverlap] = []

    def add_equation(self, eq: Equation):
        self.equations[eq.name] = eq

    def add_domain(self, domain: Domain):
        self.domains[domain.name] = domain

    # ----- Field computation -----

    def compute_overlap(self, eq: Equation, domain: Domain) -> FieldOverlap:
        """
        How well does this equation's field overlap with this domain's needs?

        Overlap = sum of min(eq_strength, domain_need) for matching properties
                  / sum of domain needs

        Perfect overlap (1.0) means the equation provides everything
        the domain needs at full strength.
        """
        eq_props = eq.property_vector()
        domain_needs = domain.need_vector()

        matched = []
        match_score = 0.0
        total_need = 0.0

        for prop_name, need_strength in domain_needs.items():
            total_need += need_strength
            if prop_name in eq_props:
                contribution = min(eq_props[prop_name], need_strength)
                match_score += contribution
                matched.append(prop_name)

        unmet = [p for p in domain_needs if p not in eq_props]
        excess = [p for p in eq_props if p not in domain_needs]

        overlap_score = match_score / total_need if total_need > 0 else 0.0

        return FieldOverlap(
            equation=eq.name, domain=domain.name,
            overlap_score=overlap_score,
            matched_properties=matched,
            unmet_needs=unmet,
            excess_properties=excess,
        )

    def propagate(self):
        """
        Compute overlap between every equation and every domain.
        This is the field propagation step — the equation's properties
        radiate outward and we measure where they land.
        """
        self.overlaps.clear()
        for eq in self.equations.values():
            for domain in self.domains.values():
                overlap = self.compute_overlap(eq, domain)
                if overlap.overlap_score > 0:
                    self.overlaps.append(overlap)

    # ----- Multi-purpose analysis -----

    def find_reuse_plan(self, eq_name: str,
                        min_overlap: float = 0.3) -> Optional[ReusePlan]:
        """
        Given an equation, find all domains it can serve (above threshold).
        Compute the efficiency gain from multi-purpose deployment.

        Efficiency = domains_served / (1 + unique_solutions_replaced)

        Biology achieves efficiency ratios of 5-20x through reuse.
        Engineering rarely exceeds 2-3x because it designs single-purpose.
        """
        eq = self.equations.get(eq_name)
        if eq is None:
            return None

        relevant = [o for o in self.overlaps
                    if o.equation == eq_name and o.overlap_score >= min_overlap]

        if not relevant:
            return None

        domains_served = [o.domain for o in relevant]
        total_overlap = sum(o.overlap_score for o in relevant)

        # Find properties shared across multiple domains
        prop_counts: Dict[str, int] = {}
        for o in relevant:
            for p in o.matched_properties:
                prop_counts[p] = prop_counts.get(p, 0) + 1
        shared = [p for p, count in prop_counts.items() if count > 1]

        # Coverage gaps
        gaps = [(o.domain, o.unmet_needs) for o in relevant if o.unmet_needs]

        # Efficiency: how many single-purpose solutions does this replace?
        # Each domain would otherwise need its own equation (cost = 1 each)
        # Multi-purpose deployment costs 1 equation for N domains
        single_purpose_cost = len(domains_served) * eq.energy_cost
        reuse_cost = eq.energy_cost  # one equation serves all
        efficiency = single_purpose_cost / reuse_cost if reuse_cost > 0 else 1.0

        return ReusePlan(
            equation=eq_name,
            domains_served=domains_served,
            total_overlap=total_overlap,
            efficiency_gain=efficiency,
            shared_properties=shared,
            coverage_gaps=gaps,
        )

    def find_all_reuse(self, min_overlap: float = 0.3) -> List[ReusePlan]:
        """Find reuse plans for all equations."""
        plans = []
        for eq_name in self.equations:
            plan = self.find_reuse_plan(eq_name, min_overlap)
            if plan and len(plan.domains_served) > 1:
                plans.append(plan)
        plans.sort(key=lambda p: -p.efficiency_gain)
        return plans

    # ----- Emergent overlap discovery -----

    def discover_bridges(self, min_shared: int = 2) -> List[Dict]:
        """
        Find equations that bridge domains which seem unrelated.

        Two domains are "bridged" if they share no properties in their
        need vectors but are both served by the same equation through
        different properties.

        This is how non-obvious connections emerge:
        the Fourier transform bridges signal processing AND quantum
        mechanics AND heat transfer — not because those domains are
        similar, but because the same mathematical structure maps
        onto all three through different property matches.
        """
        bridges = []
        plans = self.find_all_reuse(min_overlap=0.2)

        for plan in plans:
            if len(plan.domains_served) < 2:
                continue

            # Check which domain pairs are bridged (share no direct needs)
            served_domains = [self.domains[d] for d in plan.domains_served
                              if d in self.domains]
            for i in range(len(served_domains)):
                for j in range(i + 1, len(served_domains)):
                    d1, d2 = served_domains[i], served_domains[j]
                    needs_1 = set(d1.need_vector().keys())
                    needs_2 = set(d2.need_vector().keys())
                    direct_overlap = needs_1 & needs_2

                    if len(direct_overlap) < min_shared:
                        # These domains don't directly overlap — the equation bridges them
                        eq = self.equations[plan.equation]
                        # What properties does the equation use for each?
                        o1 = next((o for o in self.overlaps
                                   if o.equation == plan.equation and o.domain == d1.name), None)
                        o2 = next((o for o in self.overlaps
                                   if o.equation == plan.equation and o.domain == d2.name), None)
                        if o1 and o2:
                            bridges.append({
                                "equation": plan.equation,
                                "domain_1": d1.name,
                                "domain_2": d2.name,
                                "d1_properties": o1.matched_properties,
                                "d2_properties": o2.matched_properties,
                                "direct_overlap": list(direct_overlap),
                                "bridge_type": "structural" if not direct_overlap else "partial",
                            })

        return bridges

    # ----- Domain gap analysis -----

    def unserved_needs(self) -> Dict[str, List[str]]:
        """
        For each domain, what needs are not met by any equation?
        These are the gaps — where new equations or adaptations are needed.
        """
        gaps = {}
        for domain in self.domains.values():
            all_matched = set()
            for o in self.overlaps:
                if o.domain == domain.name:
                    all_matched.update(o.matched_properties)
            unmet = [p.name for p in domain.needs if p.name not in all_matched]
            if unmet:
                gaps[domain.name] = unmet
        return gaps

    # ----- Report -----

    def print_report(self):
        print(f"\n{'='*70}")
        print(f"  EQUATION FIELD OVERLAP REPORT")
        print(f"  {len(self.equations)} equations, {len(self.domains)} domains, "
              f"{len(self.overlaps)} overlaps")
        print(f"{'='*70}")

        # Overlap matrix
        print(f"\n  OVERLAP MATRIX (equation x domain):")
        eq_names = sorted(self.equations.keys())
        dom_names = sorted(self.domains.keys())

        # Header
        header = f"  {'':30s}"
        for d in dom_names:
            header += f" {d[:10]:>10s}"
        print(header)

        for eq_name in eq_names:
            row = f"  {eq_name:30s}"
            for dom_name in dom_names:
                o = next((x for x in self.overlaps
                          if x.equation == eq_name and x.domain == dom_name), None)
                if o and o.overlap_score > 0:
                    bar = "#" * max(1, int(o.overlap_score * 5))
                    row += f" {o.overlap_score:>9.0%} "
                else:
                    row += f" {'---':>10s}"
            print(row)

        # Multi-purpose reuse
        plans = self.find_all_reuse(min_overlap=0.2)
        if plans:
            print(f"\n  MULTI-PURPOSE REUSE (biology-style efficiency):")
            for plan in plans:
                print(f"\n    {plan.equation}")
                print(f"      Serves: {', '.join(plan.domains_served)}")
                print(f"      Efficiency: {plan.efficiency_gain:.1f}x "
                      f"(vs {len(plan.domains_served)} single-purpose solutions)")
                print(f"      Shared properties: {', '.join(plan.shared_properties)}")
                if plan.coverage_gaps:
                    for domain, gaps in plan.coverage_gaps:
                        print(f"      Gap in {domain}: needs {', '.join(gaps)}")

        # Bridges
        bridges = self.discover_bridges(min_shared=1)
        if bridges:
            print(f"\n  STRUCTURAL BRIDGES (non-obvious connections):")
            for b in bridges:
                print(f"    {b['equation']} bridges:")
                print(f"      {b['domain_1']} (via {', '.join(b['d1_properties'])})")
                print(f"      {b['domain_2']} (via {', '.join(b['d2_properties'])})")
                if b['direct_overlap']:
                    print(f"      Direct overlap: {', '.join(b['direct_overlap'])}")
                else:
                    print(f"      No direct overlap — pure structural bridge")

        # Gaps
        gaps = self.unserved_needs()
        if gaps:
            print(f"\n  UNSERVED NEEDS (where new equations are needed):")
            for domain, needs in gaps.items():
                print(f"    {domain}: {', '.join(needs)}")

        print(f"\n{'='*70}\n")


# =============================================================================
# EQUATION LIBRARY — seed equations with real properties
# =============================================================================

def build_equation_library() -> List[Equation]:
    """
    A starter set of fundamental equations and their properties.
    Each equation carries multiple properties that can serve
    different domains — exactly how nature reuses structures.
    """
    return [
        Equation(
            name="Conservation of Energy",
            formula="dE/dt = 0 (closed system)",
            properties=[
                Property("energy_conservation", 1.0, "conservation"),
                Property("state_tracking", 0.8, "bookkeeping"),
                Property("symmetry_time", 0.9, "symmetry"),
                Property("budget_constraint", 0.7, "optimization"),
            ],
            description="Energy neither created nor destroyed. "
                        "Noether's theorem: time symmetry = energy conservation.",
        ),
        Equation(
            name="Diffusion Equation",
            formula="du/dt = D * nabla^2(u)",
            properties=[
                Property("gradient_flow", 1.0, "transport"),
                Property("smoothing", 0.9, "regularization"),
                Property("equilibrium_seeking", 0.8, "dynamics"),
                Property("spatial_coupling", 0.7, "coupling"),
                Property("decay_modeling", 0.6, "temporal"),
            ],
            description="Things flow from high concentration to low. "
                        "Heat, chemicals, information, influence.",
        ),
        Equation(
            name="Fourier Transform",
            formula="F(w) = integral f(t) * e^(-iwt) dt",
            properties=[
                Property("frequency_decomposition", 1.0, "analysis"),
                Property("pattern_recognition", 0.8, "sensing"),
                Property("compression", 0.7, "encoding"),
                Property("convolution", 0.9, "coupling"),
                Property("symmetry_translation", 0.6, "symmetry"),
            ],
            description="Any signal is a sum of frequencies. "
                        "Bridges time and frequency domains.",
        ),
        Equation(
            name="Exponential Decay",
            formula="N(t) = N0 * e^(-lambda*t)",
            properties=[
                Property("decay_modeling", 1.0, "temporal"),
                Property("half_life", 0.9, "temporal"),
                Property("memory_fading", 0.7, "cognition"),
                Property("risk_assessment", 0.6, "decision"),
                Property("population_dynamics", 0.5, "ecology"),
            ],
            description="Things decay proportional to what remains. "
                        "Radioactive isotopes, knowledge holders, trust.",
        ),
        Equation(
            name="Logistic Growth",
            formula="dN/dt = r*N*(1 - N/K)",
            properties=[
                Property("population_dynamics", 1.0, "ecology"),
                Property("carrying_capacity", 0.9, "limits"),
                Property("saturation", 0.8, "nonlinear"),
                Property("resource_competition", 0.7, "economics"),
                Property("S_curve_adoption", 0.6, "social"),
            ],
            description="Growth slows as capacity is reached. "
                        "Populations, markets, technologies, infections.",
        ),
        Equation(
            name="Navier-Stokes (simplified)",
            formula="rho(dv/dt) = -nabla(p) + mu*nabla^2(v) + f",
            properties=[
                Property("gradient_flow", 0.9, "transport"),
                Property("pressure_dynamics", 1.0, "mechanics"),
                Property("viscous_dissipation", 0.8, "thermodynamics"),
                Property("turbulence", 0.7, "complexity"),
                Property("spatial_coupling", 0.8, "coupling"),
                Property("boundary_effects", 0.6, "geometry"),
            ],
            description="How fluids move. Also how traffic flows, "
                        "crowds move, and supply chains propagate.",
        ),
        Equation(
            name="Shannon Entropy",
            formula="H = -sum(p_i * log(p_i))",
            properties=[
                Property("information_measure", 1.0, "information"),
                Property("compression", 0.8, "encoding"),
                Property("uncertainty_quantification", 0.9, "decision"),
                Property("equilibrium_seeking", 0.6, "dynamics"),
                Property("diversity_measure", 0.7, "ecology"),
            ],
            description="How much information is in a message. "
                        "Also measures disorder, diversity, uncertainty.",
        ),
        Equation(
            name="Coupled Oscillator",
            formula="d^2x/dt^2 + w0^2*x = k*(y - x)",
            properties=[
                Property("synchronization", 1.0, "dynamics"),
                Property("resonance", 0.9, "amplification"),
                Property("spatial_coupling", 0.8, "coupling"),
                Property("frequency_decomposition", 0.5, "analysis"),
                Property("energy_transfer", 0.7, "transport"),
            ],
            description="Two systems linked by a spring. "
                        "Pendulums, neurons, power grids, social contagion.",
        ),
        Equation(
            name="Michaelis-Menten",
            formula="v = Vmax * [S] / (Km + [S])",
            properties=[
                Property("saturation", 1.0, "nonlinear"),
                Property("resource_competition", 0.8, "economics"),
                Property("carrying_capacity", 0.6, "limits"),
                Property("dose_response", 0.9, "pharmacology"),
                Property("diminishing_returns", 0.7, "optimization"),
            ],
            description="Enzyme kinetics. Also describes any process "
                        "that saturates: soil nutrient uptake, CPU utilization, "
                        "attention spans.",
        ),
        Equation(
            name="Graph Laplacian",
            formula="L = D - A (degree - adjacency)",
            properties=[
                Property("network_structure", 1.0, "topology"),
                Property("diffusion_on_graphs", 0.9, "transport"),
                Property("community_detection", 0.8, "clustering"),
                Property("synchronization", 0.6, "dynamics"),
                Property("spatial_coupling", 0.7, "coupling"),
                Property("smoothing", 0.5, "regularization"),
            ],
            description="The structure of connections. "
                        "Social networks, power grids, food webs, "
                        "knowledge transmission chains.",
        ),
        # ---- Phi family ----
        Equation(
            name="Golden Ratio (phi)",
            formula="phi = (1 + sqrt(5)) / 2 = 1.618...",
            properties=[
                Property("self_similarity", 1.0, "geometry"),
                Property("optimal_packing", 0.9, "geometry"),
                Property("minimal_overlap", 0.95, "allocation"),
                Property("fibonacci_scaling", 0.9, "growth"),
                Property("irrational_spacing", 1.0, "number_theory"),
                Property("convergent_ratio", 0.8, "dynamics"),
                Property("spiral_growth", 0.9, "morphology"),
                Property("resonance_avoidance", 0.85, "stability"),
                Property("energy_minimization", 0.7, "thermodynamics"),
                Property("fractal_nesting", 0.8, "geometry"),
                Property("phyllotaxis", 0.9, "biology"),
                Property("proportion_stability", 0.85, "structure"),
            ],
            description="The most irrational number. Maximally avoids resonance. "
                        "Shows up everywhere not because of mysticism but because "
                        "systems that avoid commensurability survive longer.",
        ),
        Equation(
            name="Fibonacci Sequence",
            formula="F(n) = F(n-1) + F(n-2), F(n)/F(n-1) -> phi",
            properties=[
                Property("fibonacci_scaling", 1.0, "growth"),
                Property("population_dynamics", 0.7, "ecology"),
                Property("convergent_ratio", 0.9, "dynamics"),
                Property("self_similarity", 0.7, "geometry"),
                Property("resource_competition", 0.4, "economics"),
                Property("spiral_growth", 0.8, "morphology"),
            ],
            description="Each term is the sum of the two before. Converges to phi. "
                        "Rabbit populations, tree branching, shell spirals.",
        ),
        Equation(
            name="Golden Angle",
            formula="theta = 2*pi*(1 - 1/phi) = 137.507...",
            properties=[
                Property("minimal_overlap", 1.0, "allocation"),
                Property("optimal_packing", 1.0, "geometry"),
                Property("phyllotaxis", 1.0, "biology"),
                Property("irrational_spacing", 0.9, "number_theory"),
                Property("uniform_coverage", 0.95, "allocation"),
                Property("resonance_avoidance", 0.9, "stability"),
                Property("spiral_growth", 1.0, "morphology"),
            ],
            description="The angular analog of phi. Why sunflower seeds pack perfectly. "
                        "Why our drone spiral has no gaps.",
        ),
        Equation(
            name="Penrose Tiling",
            formula="aperiodic tiling with phi-ratio rhombi",
            properties=[
                Property("self_similarity", 1.0, "geometry"),
                Property("fractal_nesting", 1.0, "geometry"),
                Property("minimal_overlap", 0.7, "allocation"),
                Property("pattern_recognition", 0.6, "sensing"),
                Property("compression", 0.5, "encoding"),
                Property("optimal_packing", 0.8, "geometry"),
                Property("proportion_stability", 0.9, "structure"),
            ],
            description="Fills a plane without repeating. Quasicrystals. "
                        "Order without periodicity. Structure without pattern lock.",
        ),
    ]


def build_domain_library() -> List[Domain]:
    """
    Domains that need mathematical structures to function.
    These span the Resilience project's scope:
    food, energy, logistics, cognition, institutions.
    """
    return [
        Domain(
            name="Food System",
            needs=[
                Property("population_dynamics", 0.9),
                Property("carrying_capacity", 0.8),
                Property("decay_modeling", 0.7),
                Property("spatial_coupling", 0.6),
                Property("resource_competition", 0.8),
                Property("saturation", 0.5),
            ],
            description="Crop yield, soil nutrient cycling, spoilage, distribution.",
        ),
        Domain(
            name="Energy Grid",
            needs=[
                Property("energy_conservation", 1.0),
                Property("gradient_flow", 0.9),
                Property("synchronization", 0.8),
                Property("pressure_dynamics", 0.5),
                Property("network_structure", 0.7),
                Property("budget_constraint", 0.6),
            ],
            description="Generation, transmission, storage, load balancing.",
        ),
        Domain(
            name="Knowledge Transmission",
            needs=[
                Property("decay_modeling", 1.0),
                Property("network_structure", 0.8),
                Property("memory_fading", 0.7),
                Property("diffusion_on_graphs", 0.9),
                Property("community_detection", 0.5),
                Property("half_life", 0.6),
            ],
            description="How knowledge spreads, persists, and dies. "
                        "The countdown clock from coupling.py.",
        ),
        Domain(
            name="Supply Chain Logistics",
            needs=[
                Property("gradient_flow", 0.9),
                Property("network_structure", 0.8),
                Property("budget_constraint", 0.7),
                Property("spatial_coupling", 0.6),
                Property("pressure_dynamics", 0.5),
                Property("saturation", 0.4),
            ],
            description="Moving goods from A to B. Routing, warehousing, last-mile.",
        ),
        Domain(
            name="Institutional Resilience",
            needs=[
                Property("synchronization", 0.7),
                Property("energy_conservation", 0.5),
                Property("equilibrium_seeking", 0.6),
                Property("uncertainty_quantification", 0.8),
                Property("diversity_measure", 0.6),
                Property("community_detection", 0.5),
            ],
            description="How institutions maintain function under stress. "
                        "Legitimacy, coordination, decision-making.",
        ),
        Domain(
            name="Ecosystem Health",
            needs=[
                Property("population_dynamics", 1.0),
                Property("carrying_capacity", 0.9),
                Property("diversity_measure", 0.8),
                Property("spatial_coupling", 0.7),
                Property("decay_modeling", 0.5),
                Property("resource_competition", 0.6),
            ],
            description="Biodiversity, trophic cascades, soil microbiome.",
        ),
        Domain(
            name="Communication Network",
            needs=[
                Property("network_structure", 1.0),
                Property("compression", 0.8),
                Property("information_measure", 0.7),
                Property("synchronization", 0.6),
                Property("spatial_coupling", 0.5),
                Property("frequency_decomposition", 0.4),
            ],
            description="LoRa mesh, CB radio, seed protocol packets.",
        ),
        Domain(
            name="Cognitive Load",
            needs=[
                Property("memory_fading", 0.9),
                Property("uncertainty_quantification", 0.7),
                Property("pattern_recognition", 0.8),
                Property("information_measure", 0.6),
                Property("saturation", 0.7),
                Property("diminishing_returns", 0.5),
            ],
            description="Human decision-making under stress. "
                        "Attention, working memory, crisis response.",
        ),
        # ---- Domains where phi shows up ----
        Domain(
            name="Antenna Design",
            needs=[
                Property("resonance_avoidance", 0.9),
                Property("frequency_decomposition", 0.7),
                Property("optimal_packing", 0.6),
                Property("fibonacci_scaling", 0.5),
                Property("self_similarity", 0.8),
            ],
            description="Broadband antennas use phi-spacing to avoid resonance "
                        "at any particular frequency. Log-periodic, fractal.",
        ),
        Domain(
            name="Structural Engineering",
            needs=[
                Property("proportion_stability", 0.9),
                Property("energy_minimization", 0.8),
                Property("fractal_nesting", 0.5),
                Property("optimal_packing", 0.7),
                Property("self_similarity", 0.4),
            ],
            description="Load distribution, column spacing, material efficiency.",
        ),
        Domain(
            name="Market Dynamics",
            needs=[
                Property("fibonacci_scaling", 0.8),
                Property("convergent_ratio", 0.7),
                Property("resonance_avoidance", 0.5),
                Property("proportion_stability", 0.6),
                Property("S_curve_adoption", 0.4),
            ],
            description="Fibonacci retracements in price action. Not because markets "
                        "are mystical but because feedback systems avoid resonance.",
        ),
        Domain(
            name="Morphogenesis",
            needs=[
                Property("phyllotaxis", 1.0),
                Property("spiral_growth", 0.9),
                Property("fibonacci_scaling", 0.8),
                Property("self_similarity", 0.7),
                Property("optimal_packing", 0.8),
                Property("energy_minimization", 0.6),
            ],
            description="How organisms grow form. Leaf arrangement, shell spirals, "
                        "branching patterns. The original phi computer.",
        ),
        Domain(
            name="Mesh Network Allocation",
            needs=[
                Property("minimal_overlap", 1.0),
                Property("uniform_coverage", 0.9),
                Property("optimal_packing", 0.8),
                Property("resonance_avoidance", 0.5),
                Property("spiral_growth", 0.6),
                Property("irrational_spacing", 0.4),
            ],
            description="Drone waypoint spacing, sensor placement, "
                        "seed protocol node distribution. The SAR spiral.",
        ),
        Domain(
            name="Music / Acoustics",
            needs=[
                Property("resonance_avoidance", 0.7),
                Property("proportion_stability", 0.8),
                Property("fibonacci_scaling", 0.5),
                Property("convergent_ratio", 0.6),
                Property("frequency_decomposition", 0.4),
            ],
            description="Room acoustics, instrument design, diffuser panels. "
                        "Phi-ratio dimensions prevent standing waves.",
        ),
        Domain(
            name="Quasicrystal Materials",
            needs=[
                Property("self_similarity", 1.0),
                Property("fractal_nesting", 0.9),
                Property("optimal_packing", 0.8),
                Property("proportion_stability", 0.7),
                Property("minimal_overlap", 0.6),
            ],
            description="Alloys with phi-ratio atomic spacing. Harder, "
                        "more corrosion resistant. Discovered 1982, Nobel 2011.",
        ),
    ]


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    random.seed(42)

    print("=" * 70)
    print("  EQUATION FIELD OVERLAP — multi-purpose structural reuse")
    print("  how biology conserves resources: same equation, many functions")
    print("=" * 70)

    field = EquationField()

    # Load libraries
    for eq in build_equation_library():
        field.add_equation(eq)
    for domain in build_domain_library():
        field.add_domain(domain)

    # Propagate
    field.propagate()

    # Full report
    field.print_report()

    # Deep dive: pick the most reusable equation
    plans = field.find_all_reuse(min_overlap=0.2)
    if plans:
        best = plans[0]
        eq = field.equations[best.equation]
        print(f"  MOST REUSABLE: {best.equation}")
        print(f"  Formula: {eq.formula}")
        print(f"  {eq.description}")
        print(f"\n  Serves {len(best.domains_served)} domains at "
              f"{best.efficiency_gain:.1f}x efficiency:")
        for domain_name in best.domains_served:
            overlap = next(o for o in field.overlaps
                           if o.equation == best.equation and o.domain == domain_name)
            print(f"    {domain_name:<30s} {overlap.overlap_score:5.0%}  "
                  f"via {', '.join(overlap.matched_properties)}")

    print(f"\n{'='*70}")
    print("  WHY THIS MATTERS")
    print(f"{'='*70}")
    print("""
  Biology doesn't design single-purpose tools.
  It discovers equations that map onto multiple problems.

  ATP powers muscles AND neurons AND membrane transport
  because phosphate bond energy release is a multi-purpose equation.

  The Fourier transform bridges signal processing AND quantum mechanics
  AND heat conduction — not because those fields are similar,
  but because the underlying math maps onto all three.

  Exponential decay describes radioactive isotopes AND knowledge loss
  AND trust erosion AND drug metabolism — same equation, different
  substrates.

  This simulator finds those overlaps automatically.
  Start with any equation. The field shows you where it lands.

  The most efficient systems aren't the most complex.
  They're the ones that found the fewest equations
  that solve the most problems.

  That's what evolved systems know and engineered systems forget.
""")

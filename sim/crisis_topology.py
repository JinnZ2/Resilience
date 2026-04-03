#!/usr/bin/env python3
# MODULE: sim/crisis_topology.py
# PROVIDES: RESILIENCE.CRISIS_TOPOLOGY
# DEPENDS: stdlib-only
# RUN: python -m sim.crisis_topology
# TIER: domain
# Problem topology mapping interface failures between coupled systems
"""
sim/crisis_topology.py — Problem Topology: Where Leverage Actually Lives
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Every crisis is an interface problem between two systems that
depend on each other. Energy needs water for cooling. Water needs
energy for pumping. When one fails, the other fails. The cascade
is the crisis, not the individual failure.

This module maps the interface topology:
  Energy <-> Water (compete for same resource in crisis)
  Energy <-> Food (lose power -> lose cold chain -> lose food)
  Energy <-> Health (grid failure = hospital failure)
  Energy <-> Communication (no power = no coordination)
  Water <-> Migration (aquifer fails -> people move)
  Food <-> Migration (crops fail -> people move)

And models how geothermal transduction breaks the feedback loops:
  Water pipe flow IS an energy source (streaming potential)
  -> water system generates its own baseline power
  -> doesn't need external grid to pump
  -> loop broken

Data is the real product. Power is the byproduct.
Information prevents crises. Energy responds to them.

Links to: sim/crisis_geology.py (borehole transducers)
          sim/urban_grid.py (infrastructure retrofit)
          sim/cities/coupling.py (cascade amplification)

USAGE:
    python -m sim.crisis_topology
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

try:
    from sim.cities.coupling import DomainType
    HAS_COUPLING = True
except ImportError:
    HAS_COUPLING = False


# =============================================================================
# INTERFACE — where two systems meet and break each other
# =============================================================================

@dataclass
class CrisisInterface:
    """
    The connection between two systems that creates cascading failure.
    The interface IS the vulnerability, not either system alone.
    """
    system_a: str
    system_b: str
    failure_mode: str               # what happens when the interface breaks
    current_dependency: str         # how they depend on each other now
    cascade_amplification: float    # how much worse B gets when A fails (1.0 = no amp)
    lag_days: float                 # how long before cascade manifests
    population_exposed: str         # who gets hit
    transduction_break: str         # how geothermal transduction breaks the loop
    data_value: str                 # what the sensor network tells you
    early_warning_weeks: float      # how much lead time the network provides

    def cascade_risk(self) -> str:
        if self.cascade_amplification >= 2.0:
            return "CRITICAL"
        if self.cascade_amplification >= 1.5:
            return "HIGH"
        if self.cascade_amplification >= 1.2:
            return "MODERATE"
        return "LOW"


def build_interfaces() -> List[CrisisInterface]:
    """The interface topology of interconnected crises."""
    return [
        CrisisInterface(
            system_a="Energy", system_b="Water",
            failure_mode="Can't pump water without power. Can't cool power plants without water.",
            current_dependency="Power plants use water for cooling. Water treatment needs power. "
                              "Desalination needs massive power.",
            cascade_amplification=2.0,
            lag_days=1,
            population_exposed="All urban populations",
            transduction_break="Water pipe flow IS an energy source (streaming potential). "
                              "Treatment plants generate own baseline power. "
                              "Every water system becomes an energy system.",
            data_value="Which aquifers are stratifying. Which pipes are stressed. "
                       "Water quality in real time without lab tests.",
            early_warning_weeks=4,
        ),
        CrisisInterface(
            system_a="Energy", system_b="Food",
            failure_mode="Lose power -> lose cold chain -> lose food. "
                        "No refrigeration, no processing, no distribution.",
            current_dependency="Agriculture needs irrigation (pumping). "
                              "Food needs refrigeration (transport, storage). "
                              "Processing needs power.",
            cascade_amplification=1.8,
            lag_days=3,
            population_exposed="5-10B (everyone on industrial food system)",
            transduction_break="Irrigation becomes distributed (each region powers pumping). "
                              "Local refrigeration for small-scale processing. "
                              "Food storage in geothermal caves (constant temp).",
            data_value="Crop stress 4 weeks before visible. Soil moisture from "
                       "thermal gradient. Cold chain integrity from pipe temp sensors.",
            early_warning_weeks=4,
        ),
        CrisisInterface(
            system_a="Energy", system_b="Health",
            failure_mode="Grid failure = hospital failure = cascading deaths. "
                        "Life support, vaccines, diagnostics all need power.",
            current_dependency="Hospitals need power for everything. "
                              "Clean water needs power for treatment. "
                              "Telemedicine needs communication needs power.",
            cascade_amplification=2.5,
            lag_days=0.25,  # 6 hours
            population_exposed="All hospital patients, immunocompromised",
            transduction_break="Hospitals have independent baseline power from building "
                              "transducers. Water treatment at hospital site. "
                              "Cold chain for medicines doesn't depend on grid.",
            data_value="Disease outbreak precursors from water quality shifts. "
                       "Hospital infrastructure stress before failure.",
            early_warning_weeks=2,
        ),
        CrisisInterface(
            system_a="Energy", system_b="Communication",
            failure_mode="Communication network fails with grid. "
                        "Without coordination, crisis becomes collapse.",
            current_dependency="Every communication system needs power. "
                              "Cell towers, internet backbone, radio repeaters.",
            cascade_amplification=1.5,
            lag_days=0.5,  # 12 hours
            population_exposed="All populations in affected grid area",
            transduction_break="LoRa mesh is low-power (transducers can sustain it). "
                              "Every water pipe, building, tunnel is a node. "
                              "Network is redundant (no single point of failure). "
                              "Seed protocol: 21-byte packets, 30km range.",
            data_value="The communication network IS the sensor network. "
                       "Same device that measures temperature also relays messages.",
            early_warning_weeks=0,  # communication is immediate
        ),
        CrisisInterface(
            system_a="Water", system_b="Migration",
            failure_mode="Aquifer fails -> crops die -> people move. "
                        "Migration overloads destination infrastructure.",
            current_dependency="People live where water is. When water fails, "
                              "they move. Mass migration overwhelms receiving cities.",
            cascade_amplification=1.6,
            lag_days=90,
            population_exposed="200M+ in water-stressed regions",
            transduction_break="Aquifer monitored in real time (1000-node network). "
                              "Temperature anomalies visible weeks before depletion. "
                              "Migration becomes planned, not panicked.",
            data_value="Aquifer state: level, temperature, flow direction. "
                       "Which wells are drawing down fastest. "
                       "Which regions can still support population.",
            early_warning_weeks=8,
        ),
        CrisisInterface(
            system_a="Food", system_b="Migration",
            failure_mode="Crops fail -> food prices spike -> people move. "
                        "Agricultural workers become refugees.",
            current_dependency="People live where food grows. When yields collapse, "
                              "rural-to-urban migration accelerates.",
            cascade_amplification=1.5,
            lag_days=120,
            population_exposed="2B+ agricultural workers globally",
            transduction_break="Soil temperature gradient predicts crop stress. "
                              "Distributed irrigation doesn't depend on grid. "
                              "Local food storage in geothermal-stable caves.",
            data_value="Soil thermal stress correlates with yield loss 4-6 weeks "
                       "before harvest. Moisture deficit from thermal anomaly.",
            early_warning_weeks=6,
        ),
        CrisisInterface(
            system_a="Energy", system_b="Migration",
            failure_mode="Cities become uninhabitable (heat, no power). "
                        "Energy crisis creates migration creates energy crisis.",
            current_dependency="Feedback loop: migration without energy = refugee crisis. "
                              "Energy without capacity = blackouts.",
            cascade_amplification=1.7,
            lag_days=180,
            population_exposed="1B+ in heat-vulnerable urban areas",
            transduction_break="Every location has geothermal baseline. "
                              "Early warning tells people when to move, not emergency. "
                              "Small towns + transducers = resilient nodes.",
            data_value="Urban heat island mapping from sensor network. "
                       "Which neighborhoods will be uninhabitable next summer. "
                       "Where to invest in cooling infrastructure.",
            early_warning_weeks=12,
        ),
        CrisisInterface(
            system_a="Knowledge", system_b="All Systems",
            failure_mode="Knowledge holders die. Transmission chains break. "
                        "Nobody knows how to operate without industrial infrastructure.",
            current_dependency="90%+ of critical knowledge is embodied (not written). "
                              "When holders die, knowledge dies with them. "
                              "YouTube is not apprenticeship.",
            cascade_amplification=1.9,
            lag_days=730,  # 2 years
            population_exposed="All populations dependent on specialized knowledge",
            transduction_break="Sensor network validates local knowledge holders. "
                              "Their observations correlate with geothermal data. "
                              "Expertise becomes measurable, not just oral. "
                              "Data preserves what text cannot.",
            data_value="Correlation between elder observations and sensor readings. "
                       "Which knowledge domains are most at risk (from coupling.py "
                       "knowledge decay layers).",
            early_warning_weeks=52,
        ),
    ]


# =============================================================================
# CORRIDOR CASE STUDY — Superior to Tomah WI
# =============================================================================

@dataclass
class CorridorPhase:
    """One phase of deployment in the test corridor."""
    name: str
    years: str
    nodes: int
    cost_usd: float
    power_output: str
    data_products: List[str]
    lives_impact: str


def build_corridor_plan() -> List[CorridorPhase]:
    """The Superior-to-Tomah WI deployment plan."""
    return [
        CorridorPhase(
            name="Phase 1: Water system integration",
            years="Year 1",
            nodes=100,
            cost_usd=75_000,
            power_output="5-20 mW (borehole transducers, natural pyrite)",
            data_products=[
                "Real-time water quality (temperature + conductivity)",
                "Leak detection (pressure anomaly, 2-4 week lead)",
                "Aquifer state monitoring (aggregate thermal trends)",
            ],
            lives_impact="Detect infrastructure failure before it happens. "
                        "Save $500K per prevented water main break.",
        ),
        CorridorPhase(
            name="Phase 2: Building + agricultural integration",
            years="Years 2-3",
            nodes=300,
            cost_usd=250_000,
            power_output="15-50 mW (buildings + soil sensors)",
            data_products=[
                "Subsurface temperature (groundwater flow mapping)",
                "Soil thermal stress (crop failure prediction)",
                "Structural health (foundation + basement monitoring)",
            ],
            lives_impact="4-week lead time on drought. Agriculture gets "
                        "planning window, not crisis response.",
        ),
        CorridorPhase(
            name="Phase 3: LoRa mesh + early warning",
            years="Years 3-5",
            nodes=500,
            cost_usd=500_000,
            power_output="50-200 mW (full network, self-powered)",
            data_products=[
                "Early warning: drought, flooding, infrastructure failure",
                "Migration trigger detection (agricultural stress)",
                "Full corridor thermal + pressure + seismic map",
                "Knowledge holder validation (observation correlation)",
            ],
            lives_impact="280K population covered. Emergency response "
                        "becomes planned transition. The 7 knowledge holders "
                        "become validated decision-makers.",
        ),
    ]


# =============================================================================
# LEVERAGE ANALYSIS — where intervention has most effect
# =============================================================================

def compute_leverage(interfaces: List[CrisisInterface]) -> List[Dict]:
    """
    Rank interfaces by leverage: where does intervention help most?

    Leverage = (cascade_amplification * population_factor) / lag_days
    High amplification + short lag + large population = high leverage.
    That's where you deploy first.
    """
    results = []
    for iface in interfaces:
        # Rough population factor from text like "5-10B", "200M+"
        pop = iface.population_exposed
        try:
            # Extract first number from strings like "5-10B", "200M+", "280K"
            num_str = ""
            for ch in pop:
                if ch.isdigit() or ch == '.':
                    num_str += ch
                elif num_str:
                    break
            num = float(num_str) if num_str else 1.0
            if "B" in pop:
                pop_factor = num * 10
            elif "M" in pop:
                pop_factor = num * 0.01
            elif "K" in pop:
                pop_factor = num * 0.00001
            else:
                pop_factor = 1.0
        except ValueError:
            pop_factor = 1.0

        lag = max(0.1, iface.lag_days)
        leverage = (iface.cascade_amplification * pop_factor) / math.log(1 + lag)

        results.append({
            "interface": f"{iface.system_a} <-> {iface.system_b}",
            "leverage": round(leverage, 2),
            "risk": iface.cascade_risk(),
            "early_warning_weeks": iface.early_warning_weeks,
            "amplification": iface.cascade_amplification,
        })

    results.sort(key=lambda x: -x["leverage"])
    return results


# =============================================================================
# REPORT
# =============================================================================

def print_report():
    interfaces = build_interfaces()
    corridor = build_corridor_plan()
    leverage = compute_leverage(interfaces)

    print(f"\n{'='*70}")
    print(f"  PROBLEM TOPOLOGY — Where Leverage Actually Lives")
    print(f"  Every crisis is an interface problem between two dependent systems")
    print(f"{'='*70}")

    # Interface map
    print(f"\n  CRISIS INTERFACES ({len(interfaces)}):")
    for iface in interfaces:
        risk = iface.cascade_risk()
        print(f"\n    {iface.system_a} <-> {iface.system_b}  [{risk}]")
        print(f"      Amplification: {iface.cascade_amplification}x  "
              f"Lag: {iface.lag_days} days  "
              f"Warning: {iface.early_warning_weeks} weeks")
        print(f"      Failure: {iface.failure_mode[:80]}")
        print(f"      Break:   {iface.transduction_break[:80]}")

    # Leverage ranking
    print(f"\n  LEVERAGE RANKING (where to deploy first):")
    for i, lev in enumerate(leverage):
        marker = ">>>" if i == 0 else "   "
        print(f"    {marker} {lev['interface']:<30s} leverage={lev['leverage']:>8.2f}  "
              f"[{lev['risk']}]  "
              f"amp={lev['amplification']}x  "
              f"warning={lev['early_warning_weeks']}wk")

    best = leverage[0]
    print(f"\n    HIGHEST LEVERAGE: {best['interface']}")
    print(f"    Deploy here first. Prove it works. Then scale.")

    # Corridor
    print(f"\n  CORRIDOR CASE STUDY: Superior to Tomah, WI (280K pop)")
    total_cost = 0
    total_nodes = 0
    for phase in corridor:
        total_cost += phase.cost_usd
        total_nodes += phase.nodes
        print(f"\n    {phase.name} ({phase.years})")
        print(f"      Nodes: {phase.nodes}  Cost: ${phase.cost_usd:,.0f}")
        print(f"      Power: {phase.power_output}")
        for dp in phase.data_products:
            print(f"      - {dp}")
        print(f"      Impact: {phase.lives_impact[:80]}")

    print(f"\n    CORRIDOR TOTAL: {total_nodes} nodes, ${total_cost:,.0f}")
    print(f"    If it works here, it works everywhere with similar geology.")
    print(f"    Which is: most of North America.")

    # The real leverage
    print(f"\n{'='*70}")
    print(f"  WHERE THE REAL LEVERAGE IS")
    print(f"{'='*70}")
    print("""
  Not in generating more power.
  Power is just the measurable output.

  The real leverage is in INFORMATION.

  Every problem in the topology is actually an information problem:
    Water crisis: didn't see the aquifer was failing
    Migration crisis: didn't know where to go
    Food crisis: didn't know crops would fail
    Health crisis: didn't see the outbreak coming
    Communication failure: no way to coordinate
    Knowledge loss: didn't know who knew what

  The geothermal transduction network solves ALL of these
  by making invisible problems visible.

  Power is the byproduct.
  Data is the product.

  The network that knows:
    groundwater level (aquifer state)
    thermal stress (crop failure, heat stress)
    infrastructure strain (pipe pressure, building vibration)
    geomagnetic coupling (ionospheric -> weather patterns)
    seismic activity (movement of earth and structures)

  ...can coordinate decisions that prevent crises
  instead of responding to them.

  Pick one interface. Solve it completely.
  Prove it. Then scale the proof.

  Don't build everything at once.
  Build proof. Then scale proof.
""")


if __name__ == "__main__":
    print_report()

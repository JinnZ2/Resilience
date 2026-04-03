#!/usr/bin/env python3
# MODULE: sim/inversion_tools.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: —
# TIER: tool
# Inversion analysis tools for system state assessment
"""
sim/inversion_tools.py — Integrated Tools from Inversion Repository
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Clean stdlib integration of concepts from github.com/JinnZ2/Inversion:
  - Zero-infrastructure environmental alerts
  - Geometric desalination vectors (Water crisis interface)
  - Salvage reclamation (circular material flow)
  - Dependency audit (structural vulnerability mapping)
  - Energy wisdom (multi-origin practice weaving)

The original scripts lost Python indentation in phone transfer.
This module rebuilds them clean and connects to existing Resilience modules.

USAGE:
    python -m sim.inversion_tools
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum


# =============================================================================
# ZERO-INFRASTRUCTURE ALERTS
# =============================================================================
# Environmental signals detectable without any infrastructure.
# Connects to: Rescue/rescue.py (low-signal navigation)

@dataclass
class EnvironmentalSignal:
    """A signal detectable without infrastructure."""
    name: str
    source: str
    detection_method: str
    what_it_indicates: List[str]
    range_meters: float
    reliability: float          # 0-1
    requires_power: bool


ZERO_INFRA_SIGNALS = [
    EnvironmentalSignal(
        "wind_shift", "atmosphere", "skin + flag/smoke observation",
        ["storm approach", "temperature front", "fire direction"], 50000, 0.7, False,
    ),
    EnvironmentalSignal(
        "animal_behavior", "fauna", "visual observation of flight/herding patterns",
        ["seismic precursor", "storm approach", "predator presence"], 5000, 0.5, False,
    ),
    EnvironmentalSignal(
        "water_color_change", "hydrology", "visual turbidity assessment",
        ["upstream contamination", "erosion event", "algal bloom onset"], 100, 0.8, False,
    ),
    EnvironmentalSignal(
        "ground_vibration", "geology", "barefoot or hand contact with ground",
        ["seismic activity", "heavy vehicle approach", "structural failure"], 1000, 0.4, False,
    ),
    EnvironmentalSignal(
        "smell_change", "chemistry", "olfactory detection",
        ["gas leak", "fire", "sewage breach", "chemical spill"], 500, 0.6, False,
    ),
    EnvironmentalSignal(
        "insect_swarm_pattern", "entomology", "visual observation",
        ["rain within 24h", "temperature drop", "humidity shift"], 10000, 0.5, False,
    ),
    EnvironmentalSignal(
        "star_visibility", "atmosphere", "naked eye observation",
        ["air quality", "humidity level", "approaching weather front"], 100000, 0.6, False,
    ),
    EnvironmentalSignal(
        "plant_wilt_timing", "botany", "visual observation of leaf state",
        ["soil moisture deficit", "heat stress", "root damage"], 50, 0.7, False,
    ),
    EnvironmentalSignal(
        "acoustic_anomaly", "physics", "ear or simple resonator",
        ["structural crack", "water leak", "mechanical failure"], 200, 0.5, False,
    ),
    EnvironmentalSignal(
        "static_charge", "physics", "hair/skin sensation",
        ["lightning imminent", "dry air extreme", "dust storm"], 10000, 0.4, False,
    ),
]


# =============================================================================
# GEOMETRIC DESALINATION
# =============================================================================
# Desalination as coupled vectors — ties to Energy<->Water interface
# Connects to: sim/crisis_topology.py

class DesalinationVector(Enum):
    ENERGY_INPUT = "energy_input"
    WATER_OUTPUT = "water_output"
    BRINE_MANAGEMENT = "brine_management"
    MINERAL_EXTRACTION = "mineral_extraction"
    MARINE_ECOLOGY = "marine_ecology"
    WASTE_HEAT = "waste_heat"
    RENEWABLE_COUPLING = "renewable_coupling"
    ATMOSPHERIC_HARVEST = "atmospheric_harvest"
    PASSIVE_THERMAL = "passive_thermal"
    WAVE_ENERGY = "wave_energy"
    SOLAR_STILL = "solar_still"
    BIOSALINE_AGRICULTURE = "biosaline_agriculture"


@dataclass
class DesalinationSystem:
    """A desalination approach modeled as coupled vectors."""
    name: str
    vectors: List[DesalinationVector]
    energy_input_kw: float
    water_output_liters_day: float
    brine_ratio: float              # liters brine per liter fresh
    cost_per_liter: float           # USD
    infrastructure_required: str
    works_without_grid: bool

    def efficiency(self) -> float:
        """Liters per kWh."""
        kwh_per_day = self.energy_input_kw * 24
        return self.water_output_liters_day / kwh_per_day if kwh_per_day > 0 else 0


DESALINATION_SYSTEMS = [
    DesalinationSystem(
        "Reverse Osmosis (industrial)",
        [DesalinationVector.ENERGY_INPUT, DesalinationVector.WATER_OUTPUT,
         DesalinationVector.BRINE_MANAGEMENT],
        energy_input_kw=3.0, water_output_liters_day=1000,
        brine_ratio=1.5, cost_per_liter=0.001,
        infrastructure_required="grid power, membranes, pumps", works_without_grid=False,
    ),
    DesalinationSystem(
        "Solar still (passive)",
        [DesalinationVector.SOLAR_STILL, DesalinationVector.PASSIVE_THERMAL,
         DesalinationVector.WATER_OUTPUT],
        energy_input_kw=0.0, water_output_liters_day=5,
        brine_ratio=3.0, cost_per_liter=0.0,
        infrastructure_required="glass/plastic sheet, basin", works_without_grid=True,
    ),
    DesalinationSystem(
        "Atmospheric harvest (fog net)",
        [DesalinationVector.ATMOSPHERIC_HARVEST, DesalinationVector.WATER_OUTPUT],
        energy_input_kw=0.0, water_output_liters_day=10,
        brine_ratio=0.0, cost_per_liter=0.0,
        infrastructure_required="mesh fabric, frame, collection vessel", works_without_grid=True,
    ),
    DesalinationSystem(
        "Wave-powered desalination",
        [DesalinationVector.WAVE_ENERGY, DesalinationVector.WATER_OUTPUT,
         DesalinationVector.BRINE_MANAGEMENT, DesalinationVector.RENEWABLE_COUPLING],
        energy_input_kw=0.5, water_output_liters_day=200,
        brine_ratio=2.0, cost_per_liter=0.003,
        infrastructure_required="wave converter, membrane, coastal mount", works_without_grid=True,
    ),
    DesalinationSystem(
        "Geothermal + membrane",
        [DesalinationVector.WASTE_HEAT, DesalinationVector.WATER_OUTPUT,
         DesalinationVector.MINERAL_EXTRACTION, DesalinationVector.RENEWABLE_COUPLING],
        energy_input_kw=0.2, water_output_liters_day=500,
        brine_ratio=1.0, cost_per_liter=0.002,
        infrastructure_required="geothermal well, membrane", works_without_grid=True,
    ),
]


# =============================================================================
# SALVAGE RECLAMATION
# =============================================================================
# When components fail, what can be recovered?
# Connects to: Rescue/energy_efficient_ai.py (constrained operations)

@dataclass
class SalvageProfile:
    """What a failed component yields for the next iteration."""
    component: str
    recoverable_materials: Dict[str, float]    # material -> kg
    reusable_parts: List[str]
    tools_required: List[str]
    salvage_fraction: float                     # 0-1 recoverable
    entropy_capture_w: float = 0.0              # waste heat capturable

    def effective_salvage(self, available_tools: Set[str]) -> float:
        """Salvage gated by available tooling."""
        if not self.tools_required:
            return self.salvage_fraction
        coverage = len(available_tools & set(self.tools_required))
        ratio = coverage / len(self.tools_required)
        return self.salvage_fraction * ratio


SALVAGE_PROFILES = [
    SalvageProfile("solar_panel", {"silicon": 15, "aluminum": 3, "glass": 10, "copper": 0.5},
                   ["junction_box", "frame"], ["screwdriver", "multimeter"], 0.7, 2.0),
    SalvageProfile("car_battery", {"lead": 10, "sulfuric_acid": 3, "plastic": 1},
                   ["terminals", "casing"], ["wrench", "acid_container"], 0.85, 0.0),
    SalvageProfile("wind_turbine_blade", {"fiberglass": 200, "resin": 50},
                   ["hub_mount"], ["crane", "saw"], 0.3, 0.0),
    SalvageProfile("electric_motor", {"copper": 5, "steel": 8, "magnets": 0.3},
                   ["bearings", "shaft", "housing"], ["wrench", "puller"], 0.9, 1.0),
    SalvageProfile("lora_node", {"pcb": 0.02, "copper": 0.01, "plastic": 0.05},
                   ["antenna", "mcu", "sensor"], ["soldering_iron"], 0.6, 0.0),
    SalvageProfile("transducer_stack", {"quartz": 2, "magnetite": 1, "copper_wire": 0.1},
                   ["piezo_element", "thermocouple"], ["multimeter"], 0.8, 0.5),
]


# =============================================================================
# DEPENDENCY AUDIT
# =============================================================================
# Map structural vulnerabilities. What depends on what?
# Connects to: sim/crisis_topology.py (interface problems)

class DependencyRisk(Enum):
    CRITICAL = "critical"       # < 10 years remaining
    HIGH = "high"               # 10-20 years
    MODERATE = "moderate"       # 20-50 years
    LOW = "low"                 # > 50 years

class DependencySource(Enum):
    PUBLIC_INFRASTRUCTURE = "public_infrastructure"
    PRIVATE_MONOPOLY = "private_monopoly"
    COMMONS = "commons"
    NATURAL_CAPITAL = "natural_capital"
    SOCIAL_CAPITAL = "social_capital"


@dataclass
class Dependency:
    """One thing a system depends on."""
    name: str
    source: DependencySource
    risk: DependencyRisk
    years_remaining: float
    replacement_exists: bool
    replacement_cost: str           # qualitative
    hidden_subsidy: str             # what's not being priced in
    cascade_domains: List[str]      # what else breaks when this fails


INFRASTRUCTURE_DEPENDENCIES = [
    Dependency("Grid electricity", DependencySource.PUBLIC_INFRASTRUCTURE,
               DependencyRisk.HIGH, 15,
               True, "high — distributed generation",
               "Fossil fuel externalities not priced",
               ["water_pumping", "food_cold_chain", "communication", "hospital"]),
    Dependency("Municipal water", DependencySource.PUBLIC_INFRASTRUCTURE,
               DependencyRisk.HIGH, 12,
               True, "moderate — local wells + treatment",
               "Aquifer depletion rate not in pricing",
               ["food_production", "sanitation", "industrial", "fire_suppression"]),
    Dependency("Diesel fuel supply", DependencySource.PRIVATE_MONOPOLY,
               DependencyRisk.CRITICAL, 8,
               True, "high — electrification transition",
               "Military protection of supply routes not priced",
               ["trucking", "farming", "emergency_generators", "heating"]),
    Dependency("Internet backbone", DependencySource.PRIVATE_MONOPOLY,
               DependencyRisk.MODERATE, 25,
               True, "moderate — mesh networks",
               "Submarine cable vulnerability not priced",
               ["commerce", "coordination", "education", "telemedicine"]),
    Dependency("Topsoil", DependencySource.NATURAL_CAPITAL,
               DependencyRisk.CRITICAL, 6,
               False, "impossible — formation takes centuries",
               "Erosion rate exceeds formation rate 10-100x",
               ["food_production", "water_filtration", "carbon_storage"]),
    Dependency("Pollinator populations", DependencySource.NATURAL_CAPITAL,
               DependencyRisk.CRITICAL, 8,
               False, "impossible — no artificial replacement at scale",
               "Pesticide damage not in food pricing",
               ["fruit_production", "seed_production", "ecosystem_function"]),
    Dependency("Elder knowledge holders", DependencySource.SOCIAL_CAPITAL,
               DependencyRisk.CRITICAL, 5,
               False, "impossible — embodied knowledge dies with holder",
               "Institutional assumption that knowledge is in textbooks",
               ["food_preservation", "water_management", "equipment_repair", "soil_culture"]),
    Dependency("Community trust networks", DependencySource.SOCIAL_CAPITAL,
               DependencyRisk.HIGH, 10,
               False, "very slow — trust rebuilds over generations",
               "Social fragmentation rate accelerating",
               ["crisis_coordination", "resource_sharing", "knowledge_transmission"]),
]


def audit_dependencies(deps: List[Dependency]) -> Dict:
    """Run a dependency audit. Returns risk summary."""
    critical = [d for d in deps if d.risk == DependencyRisk.CRITICAL]
    no_replacement = [d for d in deps if not d.replacement_exists]

    # Cascade analysis: which domains appear most in cascade lists?
    cascade_counts: Dict[str, int] = {}
    for d in deps:
        for domain in d.cascade_domains:
            cascade_counts[domain] = cascade_counts.get(domain, 0) + 1

    most_vulnerable = sorted(cascade_counts.items(), key=lambda x: -x[1])

    return {
        "total_dependencies": len(deps),
        "critical_count": len(critical),
        "critical_items": [d.name for d in critical],
        "no_replacement": [d.name for d in no_replacement],
        "shortest_timeline": min(d.years_remaining for d in deps),
        "most_vulnerable_domains": most_vulnerable[:5],
    }


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  INVERSION TOOLS — integrated from Inversion repository")
    print("=" * 60)

    # Zero-infrastructure alerts
    print(f"\n  ZERO-INFRASTRUCTURE ALERTS ({len(ZERO_INFRA_SIGNALS)} signals):")
    for s in ZERO_INFRA_SIGNALS:
        power = "no power" if not s.requires_power else "needs power"
        print(f"    {s.name:<25s} {s.detection_method[:40]:<42s} "
              f"r={s.reliability:.0%} ({power})")

    # Desalination
    print(f"\n  DESALINATION SYSTEMS ({len(DESALINATION_SYSTEMS)}):")
    for d in DESALINATION_SYSTEMS:
        grid = "OFF-GRID" if d.works_without_grid else "needs grid"
        print(f"    {d.name:<35s} {d.water_output_liters_day:>6.0f} L/day  "
              f"${d.cost_per_liter:.3f}/L  {grid}")

    # Salvage
    print(f"\n  SALVAGE PROFILES ({len(SALVAGE_PROFILES)}):")
    basic_tools = {"screwdriver", "wrench", "multimeter"}
    for s in SALVAGE_PROFILES:
        eff = s.effective_salvage(basic_tools)
        materials = ", ".join(f"{k}:{v:.1f}kg" for k, v in s.recoverable_materials.items())
        print(f"    {s.component:<22s} salvage={eff:.0%} (basic tools)  {materials}")

    # Dependency audit
    print(f"\n  DEPENDENCY AUDIT:")
    audit = audit_dependencies(INFRASTRUCTURE_DEPENDENCIES)
    print(f"    Total dependencies: {audit['total_dependencies']}")
    print(f"    CRITICAL: {audit['critical_count']} "
          f"({', '.join(audit['critical_items'])})")
    print(f"    No replacement exists: {', '.join(audit['no_replacement'])}")
    print(f"    Shortest timeline: {audit['shortest_timeline']} years")
    print(f"\n    Most vulnerable domains:")
    for domain, count in audit['most_vulnerable_domains']:
        print(f"      {domain:<30s} exposed by {count} dependencies")

    print(f"\n{'='*60}")
    print("  WHAT THIS TELLS YOU")
    print(f"{'='*60}")
    print("""
  Zero-infrastructure alerts: 10 signals detectable by a human
  body with no technology. Wind shift predicts storms. Animal
  behavior predicts earthquakes. Water color predicts contamination.

  Desalination: 5 approaches from industrial RO to passive solar
  still. The ones that work without grid produce less water but
  survive the crisis. 5 liters/day from a glass sheet and a basin.

  Salvage: when a solar panel fails, 70% of materials are
  recoverable with basic tools. When a transducer stack fails,
  80%. Nothing is waste if you have the right tools.

  Dependencies: topsoil (6 years), elder knowledge (5 years),
  and pollinators (8 years) are CRITICAL with NO REPLACEMENT.
  Diesel (8 years) and grid (15 years) are critical but have
  replacements. The irreplaceable ones are the real emergency.
""")

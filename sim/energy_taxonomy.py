#!/usr/bin/env python3
"""
sim/energy_taxonomy.py — First-Principles Energy Taxonomy
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Every energy capture method is one of:
  dMechanical -> Electrical (piezo, vibration, pressure)
  dThermal -> Electrical/Mechanical (Seebeck, expansion)
  dRadiative -> Electrical/Thermal (solar, IR)
  dChemical -> Electrical/Thermal (combustion, bio)
  dField -> Electrical (electrostatic, magnetic gradients)

Most "new energy ideas" are not new sources. They are new ways
of intercepting transfer before it degrades into thermal/diffusive loss.

The practical filter for any energy idea:
  1. Which interaction carries the energy?
  2. Is this source, storage, or transfer?
  3. Am I intercepting before dissipation?
  4. Or recovering already degraded energy?

If the answer to #4 is yes, your efficiency ceiling is Carnot.
If #3, you can beat Carnot-equivalent by avoiding the thermal step.

USAGE:
    python -m sim.energy_taxonomy
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum


# =============================================================================
# CLASSIFICATION
# =============================================================================

class EnergyRole(Enum):
    SOURCE = "source"           # true energy origin (nuclear, stellar, tidal)
    STORAGE = "storage"         # holds energy for later (gravity, chemical, thermal)
    TRANSFER = "transfer"       # moves energy between forms (EM, mechanical, fluid)
    LOSS = "loss"               # degradation channel (thermalization, diffusion, turbulence)


class InteractionType(Enum):
    # Fundamental
    STRONG = "strong"           # nuclear binding (fission/fusion)
    WEAK = "weak"               # radioactive decay
    ELECTROMAGNETIC = "electromagnetic"
    GRAVITATIONAL = "gravitational"
    # Emergent/effective (macroscopic)
    THERMAL = "thermal"         # statistical EM (degraded)
    MECHANICAL = "mechanical"   # bulk EM forces
    CHEMICAL = "chemical"       # electron configurations
    RADIATIVE = "radiative"     # photon flux
    FLUID = "fluid_dynamic"     # pressure + velocity fields
    HARMONIC = "harmonic"       # oscillatory / resonant
    ELASTIC = "elastic"         # strain energy
    PHASE_CHANGE = "phase_change"  # latent heat boundary
    DIFFUSIVE = "diffusive"     # concentration gradient
    MAGNETIC = "magnetic"       # flux routing
    ELECTROSTATIC = "electrostatic"  # charge separation
    CORIOLIS = "coriolis"       # rotational frame effects


@dataclass
class EnergyLayer:
    """One layer in the energy taxonomy."""
    name: str
    interaction: InteractionType
    role: EnergyRole
    gradient_type: str          # what gradient drives it
    scale: str                  # spatial scale
    density: str                # energy density (qualitative)
    harvestable: bool           # can we extract useful work?
    harvest_method: str         # how to extract
    constraint: str             # what limits extraction
    efficiency_ceiling: str     # theoretical max
    notes: str = ""

    def practical_filter(self) -> Dict[str, str]:
        """The 4-question filter for any energy idea."""
        return {
            "1_interaction": f"{self.interaction.value} carries the energy",
            "2_role": f"This is {self.role.value}",
            "3_intercept": "YES — intercepting before dissipation" if self.role in (EnergyRole.SOURCE, EnergyRole.TRANSFER) else "NO — recovering degraded energy",
            "4_ceiling": self.efficiency_ceiling,
        }


# =============================================================================
# THE TAXONOMY
# =============================================================================

def build_taxonomy() -> List[EnergyLayer]:
    """The complete first-principles energy taxonomy."""
    return [
        # --- SOURCES (true energy origin) ---
        EnergyLayer("Nuclear fission", InteractionType.STRONG, EnergyRole.SOURCE,
                     "binding energy (nuclear potential)", "subatomic (fm)",
                     "very high (MeV/nucleon)", True,
                     "controlled chain reaction", "requires enriched fuel + containment",
                     "~33% thermal conversion",
                     "High-density stored reservoir. Not directly accessible without regime shift."),
        EnergyLayer("Nuclear fusion", InteractionType.STRONG, EnergyRole.SOURCE,
                     "binding energy (light nuclei)", "subatomic (fm)",
                     "extreme (17.6 MeV per D-T)", False,
                     "plasma confinement (not yet practical)", "Lawson criterion not met at scale",
                     "theoretical ~40%"),
        EnergyLayer("Radioactive decay", InteractionType.WEAK, EnergyRole.SOURCE,
                     "nuclear instability", "subatomic",
                     "low power density, high persistence", True,
                     "radioisotope thermoelectric generator", "low rate, limited isotopes",
                     "~7% (RTG)",
                     "Low-rate autonomous release. Voyager probes still running."),
        EnergyLayer("Solar radiation", InteractionType.RADIATIVE, EnergyRole.SOURCE,
                     "photon flux from stellar fusion", "planetary",
                     "1361 W/m2 at Earth orbit", True,
                     "photovoltaic, thermal, photosynthesis", "intermittent, diffuse",
                     "~33% PV, ~60% concentrated thermal",
                     "Primary input for almost all Earth energy systems."),
        EnergyLayer("Tidal forcing", InteractionType.GRAVITATIONAL, EnergyRole.SOURCE,
                     "Earth-Moon gravitational gradient", "planetary",
                     "low (~2.5 TW global)", True,
                     "tidal barrage, tidal stream", "site-specific, ecological impact",
                     "~25% practical"),

        # --- STORAGE ---
        EnergyLayer("Gravitational potential", InteractionType.GRAVITATIONAL, EnergyRole.STORAGE,
                     "E = mgh", "meters to km",
                     "low (2.7 kJ/ton/meter)", True,
                     "pumped hydro, gravity batteries, elevated mass", "requires pre-existing energy to lift",
                     "~80% round-trip (pumped hydro)",
                     "Gravity is storage/mediator, not a source. Needs a cycle."),
        EnergyLayer("Chemical bonds", InteractionType.CHEMICAL, EnergyRole.STORAGE,
                     "chemical potential (d_mu)", "molecular",
                     "medium (batteries: 0.5-1 MJ/kg, fuel: 45 MJ/kg)", True,
                     "combustion, electrochemistry, metabolism", "reaction kinetics, material limits",
                     "varies: 25% engine to 90% fuel cell"),
        EnergyLayer("Thermal mass", InteractionType.THERMAL, EnergyRole.STORAGE,
                     "temperature difference (dT)", "cm to km",
                     "rho*c*dT (rock: 2.5 MJ/m3/K)", True,
                     "sensible heat, phase change materials", "Carnot limit on conversion back",
                     "Carnot: 1 - T_cold/T_hot",
                     "Degraded energy field (high entropy). Still useful if gradients exist."),
        EnergyLayer("Elastic strain", InteractionType.ELASTIC, EnergyRole.STORAGE,
                     "deformation field", "mm to meters",
                     "medium (springs, compressed gas)", True,
                     "springs, flywheels, compressed air", "material fatigue, leakage",
                     "~70-90%",
                     "Short-term storage + fast release."),
        EnergyLayer("Phase change latent heat", InteractionType.PHASE_CHANGE, EnergyRole.STORAGE,
                     "latent heat boundary", "molecular",
                     "high (water: 334 kJ/kg melting, 2260 kJ/kg boiling)", True,
                     "PCM storage, ice storage", "temperature-specific, hysteresis",
                     "~85-95% thermal round-trip",
                     "High-density thermal buffer at fixed temperature."),

        # --- TRANSFER / STRUCTURING ---
        EnergyLayer("Electromagnetic transfer", InteractionType.ELECTROMAGNETIC, EnergyRole.TRANSFER,
                     "charge, field, radiation (dV, dE-field)", "atomic to macroscopic",
                     "varies enormously", True,
                     "generators, transformers, antennas", "impedance matching, losses",
                     "~95% (transformer) to ~20% (wireless)",
                     "Primary transfer + conversion domain. Most accessible."),
        EnergyLayer("Mechanical coupling", InteractionType.MECHANICAL, EnergyRole.TRANSFER,
                     "stress, pressure, velocity (dP, dv)", "mm to km",
                     "structured, low-entropy", True,
                     "gears, shafts, hydraulics, piezoelectric", "friction, fatigue",
                     "~85-95% (gears)",
                     "Structured, low-entropy transfer. Highly harvestable."),
        EnergyLayer("Fluid dynamics", InteractionType.FLUID, EnergyRole.TRANSFER,
                     "pressure, velocity fields", "mm to planetary",
                     "distributed", True,
                     "turbines, sails, heat exchangers", "turbulence losses",
                     "~45% (wind) to ~90% (hydro)",
                     "Transport + distribution layer. Not a source, but shapes access."),
        EnergyLayer("Harmonic/resonant", InteractionType.HARMONIC, EnergyRole.TRANSFER,
                     "periodic energy exchange (KE <-> PE)", "mm to km",
                     "concentrated at resonance", True,
                     "lock into resonance, amplify, couple out", "narrow bandwidth, detunes under load",
                     "Q-factor dependent",
                     "Temporal structuring / amplification. Requires stable frequency."),
        EnergyLayer("Magnetic routing", InteractionType.MAGNETIC, EnergyRole.TRANSFER,
                     "magnetic field / flux gradient", "mm to planetary",
                     "varies", True,
                     "inductors, transformers, magnetostrictive", "hysteresis, eddy currents",
                     "~95%+ (low-loss transfer)",
                     "Coupling + routing mechanism. Low-loss at low frequency."),
        EnergyLayer("Coriolis effects", InteractionType.CORIOLIS, EnergyRole.TRANSFER,
                     "apparent force from rotation: F = -2m(Omega x v)", "km to planetary",
                     "small unless large scale", False,
                     "redirect flows, induce asymmetry, separate phases", "magnitude small at human scale",
                     "N/A (not a source)",
                     "Directional bias, not energy. Use for structuring, not generation."),

        # --- LOSS / DISSIPATION ---
        EnergyLayer("Thermalization", InteractionType.THERMAL, EnergyRole.LOSS,
                     "all gradients decay toward thermal equilibrium", "universal",
                     "final state of all energy", False,
                     "partially recoverable via Carnot", "second law",
                     "Carnot limit",
                     "Where all energy ends up. The tax on every conversion."),
        EnergyLayer("Diffusion", InteractionType.DIFFUSIVE, EnergyRole.LOSS,
                     "concentration gradient (dC)", "molecular to km",
                     "slow equalization", False,
                     "intercept before equilibration", "slow, distributed",
                     "limited by gradient magnitude",
                     "Slow equalization process. Often a loss channel unless intercepted."),
        EnergyLayer("Turbulence", InteractionType.FLUID, EnergyRole.LOSS,
                     "velocity field breakdown", "mm to km",
                     "dissipative", False,
                     "not directly recoverable", "cascades to thermal",
                     "N/A",
                     "Structured flow breaking down into heat. Irreversible."),
    ]


# =============================================================================
# ANALYSIS TOOLS
# =============================================================================

def classify_idea(idea_description: str, taxonomy: List[EnergyLayer]) -> List[Dict]:
    """
    Given an energy idea, find which taxonomy layers it touches.
    Uses simple keyword matching (substrate reasoner does this better).
    """
    keywords = idea_description.lower().split()
    matches = []
    for layer in taxonomy:
        text = f"{layer.name} {layer.gradient_type} {layer.harvest_method} {layer.notes}".lower()
        score = sum(1 for kw in keywords if kw in text and len(kw) > 3)
        if score > 0:
            matches.append({
                "layer": layer.name,
                "role": layer.role.value,
                "interaction": layer.interaction.value,
                "score": score,
                "filter": layer.practical_filter(),
            })
    matches.sort(key=lambda x: -x["score"])
    return matches


def find_harvest_opportunities(taxonomy: List[EnergyLayer]) -> List[Dict]:
    """Find all harvestable layers grouped by role."""
    opportunities = []
    for layer in taxonomy:
        if layer.harvestable:
            opportunities.append({
                "name": layer.name,
                "role": layer.role.value,
                "method": layer.harvest_method,
                "ceiling": layer.efficiency_ceiling,
                "constraint": layer.constraint,
            })
    return opportunities


# =============================================================================
# REPORT
# =============================================================================

def print_report():
    taxonomy = build_taxonomy()

    print(f"\n{'='*70}")
    print(f"  FIRST-PRINCIPLES ENERGY TAXONOMY")
    print(f"  Every capture method classified by what it actually is")
    print(f"{'='*70}")

    for role in EnergyRole:
        layers = [l for l in taxonomy if l.role == role]
        print(f"\n  {role.value.upper()} ({len(layers)}):")
        for l in layers:
            h = "harvestable" if l.harvestable else "not harvestable"
            print(f"    {l.name:<30s} [{l.interaction.value}]")
            print(f"      Gradient: {l.gradient_type}")
            print(f"      Density: {l.density}")
            print(f"      Ceiling: {l.efficiency_ceiling}  ({h})")
            if l.notes:
                print(f"      {l.notes}")

    # Practical filter demo
    print(f"\n{'─'*70}")
    print("  PRACTICAL FILTER — test any energy idea")
    print(f"{'─'*70}")

    test_ideas = [
        "piezoelectric road harvesting from vehicle vibration",
        "thermoelectric generator on waste heat from data center",
        "gravity battery in abandoned mine shaft",
        "pyrite thermocouple in geothermal borehole",
        "atmospheric electrostatic charge capture",
        "algae biofuel from CO2 capture",
    ]

    for idea in test_ideas:
        matches = classify_idea(idea, taxonomy)
        if matches:
            top = matches[0]
            f = top["filter"]
            print(f"\n    \"{idea}\"")
            print(f"      -> {f['1_interaction']}")
            print(f"      -> {f['2_role']}")
            print(f"      -> {f['3_intercept']}")
            print(f"      -> Ceiling: {f['4_ceiling']}")

    print(f"\n{'='*70}")
    print("  THE KEY INSIGHT")
    print(f"{'='*70}")
    print("""
  Most "new energy ideas" are not new sources.

  They are: new ways of intercepting transfer
  before it degrades into thermal/diffusive loss.

  The 4-question filter:
    1. Which interaction carries the energy?
    2. Is this source, storage, or transfer?
    3. Am I intercepting before dissipation?
    4. Or recovering already degraded energy?

  If #4: your ceiling is Carnot.
  If #3: you can beat Carnot-equivalent by avoiding
         the thermal step entirely.

  Piezo on a road? Transfer layer. Intercepting mechanical
  before it thermalizes. Good.

  Thermoelectric on waste heat? Loss recovery. Already degraded.
  Carnot-limited. Still worth doing, but know the ceiling.

  Pyrite thermocouple in a borehole? Transfer layer.
  Natural thermal gradient, not yet degraded. Can exceed
  what a heat engine would get from the same gradient
  because Seebeck doesn't go through a thermal cycle.

  That's the taxonomy. Source, storage, transfer, loss.
  Everything else is marketing.
""")


if __name__ == "__main__":
    print_report()
